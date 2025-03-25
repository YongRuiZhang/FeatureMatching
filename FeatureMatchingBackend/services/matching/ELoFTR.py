"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/23 16:47
Project    : FeatureMatchingBackend
FilePath   : services/matching/ELoFTR.py
Description:
"""
import os
from copy import deepcopy

import cv2
import imageio
import numpy as np
import torch
from matplotlib import cm

from DLModels.ELoFTR import LoFTR, full_default_cfg, opt_default_cfg, reparameter
from utils.matching_utils import (AverageTimer, VideoStreamer,
                                  frame2tensor, make_matching_plot_fast, process_resize, estimate_pose,
                                  scale_intrinsics)


def matching_pair(path, img1_path, img2_path, K, model_type='full', precision='fp32', is_save=True, is_process=True,
                  timer=None):
    device = 'cpu'

    if model_type == 'full':
        _default_cfg = deepcopy(full_default_cfg)
    elif model_type == 'opt':
        _default_cfg = deepcopy(opt_default_cfg)

    if precision == 'mp':
        _default_cfg['mp'] = True
    elif precision == 'fp16':
        _default_cfg['half'] = True

    print(1)

    matcher = LoFTR(config=_default_cfg)
    matcher.load_state_dict(torch.load("weights/ELoFTR/eloftr_outdoor.ckpt", map_location=device)['state_dict'])
    print(3)
    matcher = reparameter(matcher)
    print(4)

    if precision == 'fp16':
        matcher = matcher.half()

    matcher = matcher.eval()

    print(1)

    if timer is None:
        timer = AverageTimer()

    if is_save:
        img1 = cv2.imread(img1_path, 0)
        img2 = cv2.imread(img2_path, 0)
        w, h = img1.shape[1], img1.shape[0]
        w_new, h_new = process_resize(w, h, [640, 480])
        scales = (float(w) / float(w_new), float(h) / float(h_new))
        img1 = cv2.resize(img1, (w_new, h_new), interpolation=cv2.INTER_AREA)
        img2 = cv2.resize(img2, (w_new, h_new), interpolation=cv2.INTER_AREA)
        K_scale = scale_intrinsics(K, scales)
    else:
        img1 = img1_path
        img2 = img2_path
        K_scale = K
    img1_tensor = frame2tensor(img1, device, precision == 'fp16')
    img2_tensor = frame2tensor(img2, device, precision == 'fp16')
    timer.update('process images')

    batch = {'image0': img1_tensor, 'image1': img2_tensor}

    with torch.no_grad():
        if precision == 'mp':
            with torch.autocast(enabled=True, device_type=device):
                matcher(batch)
        else:
            matcher(batch)
        mkpts0 = batch['mkpts0_f'].cpu().numpy()
        mkpts1 = batch['mkpts1_f'].cpu().numpy()
        mconf = batch['mconf'].cpu().numpy()
        out_matches = {
            'mkpts0': mkpts0,
            'mkpts1': mkpts1,
            'mconf': mconf,
        }
    timer.update('matching')

    if is_save:
        thresh = 1.
        res, E = estimate_pose(mkpts0, mkpts1, K_scale, K_scale, thresh)
        if res is not None:
            R, t, inliers = res

            out_poses = {
                'E': E,
                'R': R,
                't': t,
                'inliers': inliers,
            }

        save_dir = os.path.join(path, 'res')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "LoFTR_{}_viz.png".format(scene))
        save_matches_path = os.path.join(save_dir, "LoFTR_{}_matches.npz".format(scene))
        save_poses_path = os.path.join(save_dir, "LoFTR_{}_pose.npz".format(scene))

        if res is not None:
            np.savez(save_matches_path, matches=out_matches)
            np.savez(save_poses_path, poses=out_poses)

        color = cm.jet(mconf)
        text = [
            'LoFTR',
            'Matches: {}'.format(len(mkpts0)),
        ]
        small_text = timer.print(small_text=[
            'R: {}'.format(R[0, :]),
            '   {}'.format(R[1, :]),
            '   {}'.format(R[2, :]),
            't: {}'.format(str(t)),
            'inliers: {}'.format(len(inliers)),
        ])

        img1_name = os.path.basename(img1_path)
        img2_name = os.path.basename(img2_path)
        small_text.append('matches_{}_{}'.format(img1_name, img2_name))

        out = make_matching_plot_fast(
            img1, img2, mkpts0=mkpts0, mkpts1=mkpts1, color=color, text=text,
            path=save_path, show_keypoints=False, small_text=small_text, margin=0)

        return save_path, save_matches_path, save_poses_path
    else:
        return mkpts0, mkpts1
