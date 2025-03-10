import torch
import torch.nn as nn
import torch.nn.functional as F
from einops.einops import rearrange

INF = 1e9


def mask_border(m, b: int, v):
    """ Mask borders with value
    Args:
        m (torch.Tensor): [N, H0, W0, H1, W1]
        b (int)
        v (m.dtype)
    """
    if b <= 0:
        return

    m[:, :b] = v
    m[:, :, :b] = v
    m[:, :, :, :b] = v
    m[:, :, :, :, :b] = v
    m[:, -b:] = v
    m[:, :, -b:] = v
    m[:, :, :, -b:] = v
    m[:, :, :, :, -b:] = v


def mask_border_with_padding(m, bd, v, p_m0, p_m1):
    if bd <= 0:
        return

    m[:, :bd] = v
    m[:, :, :bd] = v
    m[:, :, :, :bd] = v
    m[:, :, :, :, :bd] = v

    h0s, w0s = p_m0.sum(1).max(-1)[0].int(), p_m0.sum(-1).max(-1)[0].int()
    h1s, w1s = p_m1.sum(1).max(-1)[0].int(), p_m1.sum(-1).max(-1)[0].int()
    for b_idx, (h0, w0, h1, w1) in enumerate(zip(h0s, w0s, h1s, w1s)):
        m[b_idx, h0 - bd:] = v
        m[b_idx, :, w0 - bd:] = v
        m[b_idx, :, :, h1 - bd:] = v
        m[b_idx, :, :, :, w1 - bd:] = v


def compute_max_candidates(p_m0, p_m1):
    """Compute the max candidates of all pairs within a batch
    
    Args:
        p_m0, p_m1 (torch.Tensor): padded masks
    """
    h0s, w0s = p_m0.sum(1).max(-1)[0], p_m0.sum(-1).max(-1)[0]
    h1s, w1s = p_m1.sum(1).max(-1)[0], p_m1.sum(-1).max(-1)[0]
    max_cand = torch.sum(
        torch.min(torch.stack([h0s * w0s, h1s * w1s], -1), -1)[0])
    return max_cand


class CoarseMatching(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        # general config
        self.thr = config['thr']  # 0.2
        self.border_rm = config['border_rm']  # 2
        # -- # for trainig fine-level LoFTR
        self.train_coarse_percent = config['train_coarse_percent']  # 0.4
        self.train_pad_num_gt_min = config['train_pad_num_gt_min']  # 200

        # we provide 2 options for differentiable matching
        self.match_type = config['match_type']  # 'dual_softmax'
        if self.match_type == 'dual_softmax':  # 使用双softmax
            self.temperature = config['dsmax_temperature']  # 0.1
        elif self.match_type == 'sinkhorn':  # 使用 OT 问题的 sinkhorn
            try:
                from .superglue import log_optimal_transport
            except ImportError:
                raise ImportError("download superglue.py first!")
            self.log_optimal_transport = log_optimal_transport
            self.bin_score = nn.Parameter(
                torch.tensor(config['skh_init_bin_score'], requires_grad=True))  # 1.0 垃圾箱维数
            self.skh_iters = config['skh_iters']
            self.skh_prefilter = config['skh_prefilter']
        else:
            raise NotImplementedError()

    def forward(self, feat_c0, feat_c1, data, mask_c0=None, mask_c1=None):
        """
        Args:
            feat0 (torch.Tensor): [N, L, C]
            feat1 (torch.Tensor): [N, S, C]
            data (dict)
            mask_c0 (torch.Tensor): [N, L] (optional)
            mask_c1 (torch.Tensor): [N, S] (optional)
        Update:
            data (dict): {
                'b_ids' (torch.Tensor): [M'],
                'i_ids' (torch.Tensor): [M'],
                'j_ids' (torch.Tensor): [M'],
                'gt_mask' (torch.Tensor): [M'],
                'mkpts0_c' (torch.Tensor): [M, 2],
                'mkpts1_c' (torch.Tensor): [M, 2],
                'mconf' (torch.Tensor): [M]}
            NOTE: M' != M during training.
        """
        N, L, S, C = feat_c0.size(0), feat_c0.size(1), feat_c1.size(1), feat_c0.size(2)  # N: 1, L: 4800(H_0/8*W_0/8), S: 4800(H_1/8*W_1/8), C: 256

        # normalize
        feat_c0, feat_c1 = map(lambda feat: feat / feat.shape[-1] ** .5,
                               [feat_c0, feat_c1])  # feat_c0: (N, L, C), feat_c1: (N, S, C)

        if self.match_type == 'dual_softmax':
            sim_matrix = torch.einsum("nlc,nsc->nls", feat_c0,
                                      feat_c1) / self.temperature  # 在通道维度上进行矩阵乘法，再除以 0.1。得到相似度矩阵 (N, L, S)
            if mask_c0 is not None:
                # 根据掩码矩阵的真值（为真）则填充负无穷大数
                sim_matrix.masked_fill_(
                    ~(mask_c0[..., None] * mask_c1[:, None]).bool(),
                    -INF)
            conf_matrix = F.softmax(sim_matrix, 1) * F.softmax(sim_matrix, 2)  # 分别对 L 和 S 进行两次 softmax

        elif self.match_type == 'sinkhorn':
            # sinkhorn, dustbin included
            sim_matrix = torch.einsum("nlc,nsc->nls", feat_c0, feat_c1)  # 在通道维度上进行矩阵乘法
            if mask_c0 is not None:
                sim_matrix[:, :L, :S].masked_fill_(
                    ~(mask_c0[..., None] * mask_c1[:, None]).bool(),
                    -INF)

            # build uniform prior & use sinkhorn
            log_assign_matrix = self.log_optimal_transport(
                sim_matrix, self.bin_score, self.skh_iters)
            assign_matrix = log_assign_matrix.exp()
            conf_matrix = assign_matrix[:, :-1, :-1]

            # filter prediction with dustbin score (only in evaluation mode)
            if not self.training and self.skh_prefilter:
                filter0 = (assign_matrix.max(dim=2)[1] == S)[:, :-1]  # [N, L]
                filter1 = (assign_matrix.max(dim=1)[1] == L)[:, :-1]  # [N, S]
                conf_matrix[filter0[..., None].repeat(1, 1, S)] = 0
                conf_matrix[filter1[:, None].repeat(1, L, 1)] = 0

            if self.config['sparse_spvs']:
                data.update({'conf_matrix_with_bin': assign_matrix.clone()})

        # 更新 confidence matrix
        data.update({'conf_matrix': conf_matrix})

        # predict coarse matches from conf_matrix
        data.update(**self.get_coarse_match(conf_matrix, data))

    @torch.no_grad()
    def get_coarse_match(self, conf_matrix, data):
        """
        Args:
            conf_matrix (torch.Tensor): [N, L, S]
            data (dict): with keys ['hw0_i', 'hw1_i', 'hw0_c', 'hw1_c']
        Returns:
            coarse_matches (dict): {
                'b_ids' (torch.Tensor): [M'],
                'i_ids' (torch.Tensor): [M'],
                'j_ids' (torch.Tensor): [M'],
                'gt_mask' (torch.Tensor): [M'],
                'm_bids' (torch.Tensor): [M],
                'mkpts0_c' (torch.Tensor): [M, 2],
                'mkpts1_c' (torch.Tensor): [M, 2],
                'mconf' (torch.Tensor): [M]
            }
        """
        # {'h0c': 60, 'h1c': 60, 'w0c': 80, 'w1c': 80}
        axes_lengths = {
            'h0c': data['hw0_c'][0],
            'w0c': data['hw0_c'][1],
            'h1c': data['hw1_c'][0],
            'w1c': data['hw1_c'][1]
        }
        _device = conf_matrix.device
        # 1. confidence thresholding
        mask = conf_matrix > self.thr  # (N, h0c, w0c, h1c, w0c)
        mask = rearrange(mask, 'b (h0c w0c) (h1c w1c) -> b h0c w0c h1c w1c',
                         **axes_lengths)

        if 'mask0' not in data:
            # self.border_rm = 2 即对 mask 填充宽度为2 的值（False）
            mask_border(mask, self.border_rm, False)
        else:
            # 对 data['mask0'] 和 data['mask1'] 的有效区域周围填充宽度为2的 False
            mask_border_with_padding(mask, self.border_rm, False,
                                     data['mask0'], data['mask1'])
        mask = rearrange(mask, 'b h0c w0c h1c w1c -> b (h0c w0c) (h1c w1c)',
                         **axes_lengths)  # (N, h0c*w0c, h1c*w1c)

        # 2. mutual nearest  元素为True表示该位置既是所在行的最大值，又是所在列的最大值
        mask = mask \
               * (conf_matrix == conf_matrix.max(dim=2, keepdim=True)[0]) \
               * (conf_matrix == conf_matrix.max(dim=1, keepdim=True)[0])

        # 3. find all valid coarse matches
        # this only works when at most one `True` in each row
        mask_v, all_j_ids = mask.max(dim=2)  # 根据 mask 的第三个维度(按行)找 True, mask_v 为该行的 最大值(N, h1c*w1c)； all_j_ids 为最大值的索引(第j列)
        b_ids, i_ids = torch.where(mask_v)  # 找到最大值所在的b和行
        j_ids = all_j_ids[b_ids, i_ids]
        mconf = conf_matrix[b_ids, i_ids, j_ids]  # 获得最大值所在位置的置信度

        # 4. Random sampling of training samples for fine-level LoFTR
        # (optional) pad samples with gt coarse-level matches
        if self.training:
            # NOTE:
            # The sampling is performed across all pairs in a batch without manually balancing
            # #samples for fine-level increases w.r.t. batch_size
            if 'mask0' not in data:
                num_candidates_max = mask.size(0) * max(
                    mask.size(1), mask.size(2))
            else:
                num_candidates_max = compute_max_candidates(
                    data['mask0'], data['mask1'])
            num_matches_train = int(num_candidates_max *
                                    self.train_coarse_percent)
            num_matches_pred = len(b_ids)
            assert self.train_pad_num_gt_min < num_matches_train, "min-num-gt-pad should be less than num-train-matches"

            # pred_indices is to select from prediction
            if num_matches_pred <= num_matches_train - self.train_pad_num_gt_min:
                pred_indices = torch.arange(num_matches_pred, device=_device)
            else:
                pred_indices = torch.randint(
                    num_matches_pred,
                    (num_matches_train - self.train_pad_num_gt_min,),
                    device=_device)

            # gt_pad_indices is to select from gt padding. e.g. max(3787-4800, 200)
            gt_pad_indices = torch.randint(
                len(data['spv_b_ids']),
                (max(num_matches_train - num_matches_pred,
                     self.train_pad_num_gt_min),),
                device=_device)
            mconf_gt = torch.zeros(len(data['spv_b_ids']), device=_device)  # set conf of gt paddings to all zero

            b_ids, i_ids, j_ids, mconf = map(
                lambda x, y: torch.cat([x[pred_indices], y[gt_pad_indices]],
                                       dim=0),
                *zip([b_ids, data['spv_b_ids']], [i_ids, data['spv_i_ids']],
                     [j_ids, data['spv_j_ids']], [mconf, mconf_gt]))

        # These matches select patches that feed into fine-level network
        coarse_matches = {'b_ids': b_ids, 'i_ids': i_ids, 'j_ids': j_ids}

        # 4. Update with matches in original image resolution
        scale = data['hw0_i'][0] / data['hw0_c'][0]  # scale: 8.0
        scale0 = scale * data['scale0'][b_ids] if 'scale0' in data else scale
        scale1 = scale * data['scale1'][b_ids] if 'scale1' in data else scale
        mkpts0_c = torch.stack(
            [i_ids % data['hw0_c'][1], i_ids // data['hw0_c'][1]],
            dim=1) * scale0
        mkpts1_c = torch.stack(
            [j_ids % data['hw1_c'][1], j_ids // data['hw1_c'][1]],
            dim=1) * scale1

        # These matches are the current prediction (for visualization)
        coarse_matches.update({
            'gt_mask': mconf == 0,
            'm_bids': b_ids[mconf != 0],  # mconf == 0 => gt matches
            'mkpts0_c': mkpts0_c[mconf != 0],
            'mkpts1_c': mkpts1_c[mconf != 0],
            'mconf': mconf[mconf != 0]
        })

        return coarse_matches
