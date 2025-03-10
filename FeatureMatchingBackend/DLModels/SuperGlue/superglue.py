# %BANNER_BEGIN%
# ---------------------------------------------------------------------
# %COPYRIGHT_BEGIN%
#
#  Magic Leap, Inc. ("COMPANY") CONFIDENTIAL
#
#  Unpublished Copyright (c) 2020
#  Magic Leap, Inc., All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains the property
# of COMPANY. The intellectual and technical concepts contained herein
# are proprietary to COMPANY and may be covered by U.S. and Foreign
# Patents, patents in process, and are protected by trade secret or
# copyright law.  Dissemination of this information or reproduction of
# this material is strictly forbidden unless prior written permission is
# obtained from COMPANY.  Access to the source code contained herein is
# hereby forbidden to anyone except current COMPANY employees, managers
# or contractors who have executed Confidentiality and Non-disclosure
# agreements explicitly covering such access.
#
# The copyright notice above does not evidence any actual or intended
# publication or disclosure  of  this source code, which includes
# information that is confidential and/or proprietary, and is a trade
# secret, of  COMPANY.   ANY REPRODUCTION, MODIFICATION, DISTRIBUTION,
# PUBLIC  PERFORMANCE, OR PUBLIC DISPLAY OF OR THROUGH USE  OF THIS
# SOURCE CODE  WITHOUT THE EXPRESS WRITTEN CONSENT OF COMPANY IS
# STRICTLY PROHIBITED, AND IN VIOLATION OF APPLICABLE LAWS AND
# INTERNATIONAL TREATIES.  THE RECEIPT OR POSSESSION OF  THIS SOURCE
# CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR IMPLY ANY RIGHTS
# TO REPRODUCE, DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE,
# USE, OR SELL ANYTHING THAT IT  MAY DESCRIBE, IN WHOLE OR IN PART.
#
# %COPYRIGHT_END%
# ----------------------------------------------------------------------
# %AUTHORS_BEGIN%
#
#  Originating Authors: Paul-Edouard Sarlin
#
# %AUTHORS_END%
# --------------------------------------------------------------------*/
# %BANNER_END%

from copy import deepcopy
from pathlib import Path
from typing import List, Tuple

import torch
from torch import nn


def MLP(channels: List[int], do_bn: bool = True) -> nn.Module:
    """ Multi-layer perceptron """
    """ channels: [3, 32, 64, 128, 256, 256] """
    n = len(channels)
    layers = []
    for i in range(1, n):
        layers.append(
            nn.Conv1d(channels[i - 1], channels[i], kernel_size=1, bias=True))
        if i < (n-1):
            if do_bn:
                layers.append(nn.BatchNorm1d(channels[i]))
            layers.append(nn.ReLU())
    return nn.Sequential(*layers)


def normalize_keypoints(kpts, image_shape):
    """ Normalize key points locations based on image image_shape """
    _, _, height, width = image_shape
    one = kpts.new_tensor(1)
    size = torch.stack([one*width, one*height])[None]
    center = size / 2
    scaling = size.max(1, keepdim=True).values * 0.7
    return (kpts - center[:, None, :]) / scaling[:, None, :]


class KeypointEncoder(nn.Module):
    """ Joint encoding of visual appearance and location using MLPs"""
    """ feature_dim: 256, layers: [32, 64, 128, 256] """
    def __init__(self, feature_dim: int, layers: List[int]) -> None:
        super().__init__()
        self.encoder = MLP([3] + layers + [feature_dim])  # MLP([3, 32, 64, 128, 256, 256])
        nn.init.constant_(self.encoder[-1].bias, 0.0)

    def forward(self, kpts, scores):
        """
        kpts: Tensor(1, M, 2); scores: Tensor(1, M)  (M是该图像的兴趣点个数)
        """
        inputs = [kpts.transpose(1, 2), scores.unsqueeze(1)]  # [Tensor(1, 2, M), Tensor(1, 1, M)]
        return self.encoder(torch.cat(inputs, dim=1))  # Tensor(1, 3, M)


def attention(query: torch.Tensor, key: torch.Tensor, value: torch.Tensor) -> Tuple[torch.Tensor,torch.Tensor]:
    """ query: Tensor(1, 64, 4, M); key: Tensor(1, 64, 4, M); value: Tensor(1, 64, 4, M) """
    dim = query.shape[1]  # dim: 64
    # bdhn: batch_size, dim_head, head_nums, N
    # bdhm: batch_size, dim_head, head_nums, M
    # bhnm: batch_size, head_nums, N, M
    scores = torch.einsum('bdhn,bdhm->bhnm', query, key) / dim**.5  # 等同于 scores = torch.matmul(query.permute(0, 2, 3, 1), key.permute(0, 2, 1, 3)) / dim**.5
    prob = torch.nn.functional.softmax(scores, dim=-1)  # 在 scores 的最后一个维度上使用 softmax
    return torch.einsum('bhnm,bdhm->bdhn', prob, value), prob  # 等同于 torch.matmul(prob, value), prob


class MultiHeadedAttention(nn.Module):
    """ Multi-head attention to increase model expressive """
    def __init__(self, num_heads: int, d_model: int):
        """ num_heads: 4; d_model: 256 """
        super().__init__()
        assert d_model % num_heads == 0
        self.dim = d_model // num_heads  # 64 (256/4 = 64)
        self.num_heads = num_heads  # 4
        self.merge = nn.Conv1d(d_model, d_model, kernel_size=1)
        self.proj = nn.ModuleList([deepcopy(self.merge) for _ in range(3)])

    def forward(self, query: torch.Tensor, key: torch.Tensor, value: torch.Tensor) -> torch.Tensor:
        """ query: Tensor(1, 256, M); key: (1, 256, N); value: Tensor(1, 256, N) """
        batch_dim = query.size(0)  # 1
        # 将输入的 query、key 和 value 分别通过三个线性层进行投影，然后将投影后的结果reshape成适当的形状以供后续计算使用
        query, key, value = [l(x).view(batch_dim, self.dim, self.num_heads, -1)
                             for l, x in zip(self.proj, (query, key, value))]
        # query: Tensor(1, 64, 4, M); key: Tensor(1, 64, 4, M); value: Tensor(1, 64, 4, M)
        x, _ = attention(query, key, value)  # x: Tensor(1, 64, 4, M)
        return self.merge(x.contiguous().view(batch_dim, self.dim*self.num_heads, -1))  # 还原维度 Tensor(1, 256, M)


class AttentionalPropagation(nn.Module):
    def __init__(self, feature_dim: int, num_heads: int):
        """ feature_dim: 256; num_heads: 4 """
        super().__init__()
        self.attn = MultiHeadedAttention(num_heads, feature_dim)
        self.mlp = MLP([feature_dim*2, feature_dim*2, feature_dim])  # [512, 512, 256]
        nn.init.constant_(self.mlp[-1].bias, 0.0)  # 将 mlp 的最后一个全连接层的偏置项（bias）初始化为常数0.0

    def forward(self, x: torch.Tensor, source: torch.Tensor) -> torch.Tensor:
        """ x: (1, 256, M); source: (1, 256, N) """
        message = self.attn(x, source, source) # message: Tensor(1, 256, M)
        return self.mlp(torch.cat([x, message], dim=1))  # [x, message]: Tensor(1, 512, M) --mlp-> Tensor(1, 256, M)


class AttentionalGNN(nn.Module):
    def __init__(self, feature_dim: int, layer_names: List[str]) -> None:
        """ feature_dim: 256; layer_names: ['self', 'cross'] * 9 """
        super().__init__()
        self.layers = nn.ModuleList([
            AttentionalPropagation(feature_dim, 4)
            for _ in range(len(layer_names))])
        self.names = layer_names  # ['self', 'cross', 'self', 'cross', 'self', 'cross', 'self', 'cross', 'self', 'cross', 'self', 'cross', 'self', 'cross', 'self', 'cross', 'self', 'cross']

    def forward(self, desc0: torch.Tensor, desc1: torch.Tensor) -> Tuple[torch.Tensor,torch.Tensor]:
        """ desc0: (1, 256, M); desc1: (1, 256, N) """
        for layer, name in zip(self.layers, self.names):
            """ layer: AttentionalPropagation; name: 'self'/'cross' """
            if name == 'cross':
                src0, src1 = desc1, desc0
            else:  # if name == 'self':
                src0, src1 = desc0, desc1
            delta0, delta1 = layer(desc0, src0), layer(desc1, src1)  # 求得各自的注意力权重delta
            desc0, desc1 = (desc0 + delta0), (desc1 + delta1)  # 修改最终的 Keypoint
        return desc0, desc1


def log_sinkhorn_iterations(Z: torch.Tensor, log_mu: torch.Tensor, log_nu: torch.Tensor, iters: int) -> torch.Tensor:
    """ Perform Sinkhorn Normalization in Log-space for stability """
    """ Z: \bar{S} (1, M+1, N+1); log_mu: (1, M+1); log_nu: (1, N+1); iters: 20 """
    u, v = torch.zeros_like(log_mu), torch.zeros_like(log_nu)  # 让 u 的形状与 log_mu 相同，值为0。v 一样
    for _ in range(iters):
        u = log_mu - torch.logsumexp(Z + v.unsqueeze(1), dim=2)  # v.unsqueeze(1): 在第1维上增加一个维度 => v(1, 1, M+1)。再按第2维指数和的对数
        v = log_nu - torch.logsumexp(Z + u.unsqueeze(2), dim=1)
    return Z + u.unsqueeze(2) + v.unsqueeze(1)


def log_optimal_transport(scores: torch.Tensor, alpha: torch.Tensor, iters: int) -> torch.Tensor:
    """ Perform Differentiable Optimal Transport in Log-space for stability"""
    """ scores: Tensor(b, M, N); alpha: Parameter(1, ); iters: Integer=20 """
    b, m, n = scores.shape
    one = scores.new_tensor(1)  # Tensor(1.)
    ms, ns = (m*one).to(scores), (n*one).to(scores)  # ns: Tensor(M.); ms: Tensor(N.)。再移动到与 scores 相同的设备上

    # 初始化 dustbins， 对应的值为可训练的 alpha
    bins0 = alpha.expand(b, m, 1)  # Tensor(1, M, 1)
    bins1 = alpha.expand(b, 1, n)  # Tensor(1, 1, N)
    alpha = alpha.expand(b, 1, 1)  # Tensor(1, 1, 1)
    # 拼接形成 \bar{S}
    couplings = torch.cat([torch.cat([scores, bins0], -1),
                           torch.cat([bins1, alpha], -1)], 1)

    # 看这段代码其实忽略掉 log() 容易看懂一点（因为还是会还原）
    norm = - (ms + ns).log()  # - ln(M.+N.)
    log_mu = torch.cat([norm.expand(m), ns.log()[None] + norm])  # Tensor(M+1,) 前M个元素值为norm，最后一个元素值为ln(N)+norm
    log_nu = torch.cat([norm.expand(n), ms.log()[None] + norm])  # Tensor(N+1,) 前N个元素值为norm，最后一个元素值为ln(M)+norm
    log_mu, log_nu = log_mu[None].expand(b, -1), log_nu[None].expand(b, -1)  # Tensor(b, M+1); Tensor(b, N+1)

    Z = log_sinkhorn_iterations(couplings, log_mu, log_nu, iters)  # 调用对数化 sinkhorn 迭代算法
    Z = Z - norm  # multiply probabilities by M+N
    return Z


def arange_like(x, dim: int):
    """ x: Tensor(1, M), dim: 1 """
    return x.new_ones(x.shape[dim]).cumsum(0) - 1  # tensor([0, 1, 2, ... , M-1])


class SuperGlue(nn.Module):
    """SuperGlue feature matching middle-end

    Given two sets of keypoints and locations, we determine the
    correspondences by:
      1. Keypoint Encoding (normalization + visual feature and location fusion)
      2. Graph Neural Network with multiple self and cross-attention layers
      3. Final projection layer
      4. Optimal Transport Layer (a differentiable Hungarian matching algorithm)
      5. Thresholding matrix based on mutual exclusivity and a match_threshold

    The correspondence ids use -1 to indicate non-matching points.

    Paul-Edouard Sarlin, Daniel DeTone, Tomasz Malisiewicz, and Andrew
    Rabinovich. SuperGlue: Learning Feature Matching with Graph Neural
    Networks. In CVPR, 2020. https://arxiv.org/abs/1911.11763

    """
    default_config = {
        'descriptor_dim': 256,
        'weights': 'indoor',
        'keypoint_encoder': [32, 64, 128, 256],
        'GNN_layers': ['self', 'cross'] * 9,
        'sinkhorn_iterations': 100,
        'match_threshold': 0.2,
    }

    def __init__(self, config):
        super().__init__()
        self.config = {**self.default_config, **config}

        self.kenc = KeypointEncoder(
            self.config['descriptor_dim'], self.config['keypoint_encoder'])

        self.gnn = AttentionalGNN(
            feature_dim=self.config['descriptor_dim'], layer_names=self.config['GNN_layers'])

        self.final_proj = nn.Conv1d(
            self.config['descriptor_dim'], self.config['descriptor_dim'],
            kernel_size=1, bias=True)

        bin_score = torch.nn.Parameter(torch.tensor(1.))
        self.register_parameter('bin_score', bin_score)

        # 加载权重
        assert self.config['weights'] in ['indoor', 'outdoor']

        path = 'weights/SuperGlue/superglue_{}.pth'.format(self.config['weights'])
        self.load_state_dict(torch.load(str(path)))

    def forward(self, data):
        """Run SuperGlue on a pair of keypoints and descriptors"""
        desc0, desc1 = data['descriptors0'], data['descriptors1']
        kpts0, kpts1 = data['keypoints0'], data['keypoints1']

        if kpts0.shape[1] == 0 or kpts1.shape[1] == 0:  # no keypoints
            shape0, shape1 = kpts0.shape[:-1], kpts1.shape[:-1]
            return {
                'matches0': kpts0.new_full(shape0, -1, dtype=torch.int),
                'matches1': kpts1.new_full(shape1, -1, dtype=torch.int),
                'matching_scores0': kpts0.new_zeros(shape0),
                'matching_scores1': kpts1.new_zeros(shape1),
            }

        # Keypoint normalization.
        kpts0 = normalize_keypoints(kpts0, data['image0'].shape)
        kpts1 = normalize_keypoints(kpts1, data['image1'].shape)

        # Keypoint MLP encoder.
        desc0 = desc0 + self.kenc(kpts0, data['scores0'])  # 图 A
        desc1 = desc1 + self.kenc(kpts1, data['scores1'])  # 图 B

        # Multi-layer Transformer network.
        desc0, desc1 = self.gnn(desc0, desc1)

        # Final MLP projection.
        mdesc0, mdesc1 = self.final_proj(desc0), self.final_proj(desc1)

        # Compute matching descriptor distance.
        # bdn: batch_size, dim, N; bdm: batch_size, dim, M
        scores = torch.einsum('bdn,bdm->bnm', mdesc0, mdesc1)  # 相当于 torch.mm(mdesc0.transpose(-2, -1), mdesc1)
        scores = scores / self.config['descriptor_dim']**.5

        # Run the optimal transport.
        scores = log_optimal_transport(scores, self.bin_score, iters=self.config['sinkhorn_iterations'])  # Tensor(b, M+1, N+1)

        # Get the matches with score above "match_threshold".
        max0, max1 = scores[:, :-1, :-1].max(2), scores[:, :-1, :-1].max(1)  # max0：按列求最大值(b, M)；max1：按行求最大值(b, N)（都忽略了dustbins）
        indices0, indices1 = max0.indices, max1.indices  # 求得对应的最大值的索引
        temp1 = arange_like(indices0, 1)  # tensor([0, 1, 2, ..., M-1])
        # arange_like(indices0, 1)[None]  # Tensor(1, M), 添加一个维度
        mutual0 = arange_like(indices0, 1)[None] == indices1.gather(1, indices0)  # Tensor(1, M) 值为 True 或 False。 True 为匹配
        mutual1 = arange_like(indices1, 1)[None] == indices0.gather(1, indices1)  # Tensor(1, N)
        zero = scores.new_tensor(0)  # tensor(0.) 设备与 scores 相同
        mscores0 = torch.where(mutual0, max0.values.exp(), zero)  # 如果 mutual0 中的某个位置为True，那么mscores0在该位置的值将是max0.values.exp()对应位置的值；否则，它将是0
        mscores1 = torch.where(mutual1, mscores0.gather(1, indices1), zero)  # # 如果 mutual1 中的某个位置为True，那么mscores1在该位置的值将是mscores0.gather(1, indices1)对应位置的值；否则，它将是0
        valid0 = mutual0 & (mscores0 > self.config['match_threshold'])  # 对应值大于给定阈值才认为合法
        valid1 = mutual1 & valid0.gather(1, indices1)
        # 获取合法值索引，不合法为 -1
        indices0 = torch.where(valid0, indices0, indices0.new_tensor(-1))
        indices1 = torch.where(valid1, indices1, indices1.new_tensor(-1))

        return {
            'matches0': indices0, # use -1 for invalid match
            'matches1': indices1, # use -1 for invalid match
            'matching_scores0': mscores0,
            'matching_scores1': mscores1,
        }
