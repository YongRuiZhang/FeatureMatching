"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/6 20:35
Project    : FeatureMatchingBackend
FilePath   : services/matching/LoFTR.py
Description: LoFTR 相关业务实现
"""
import os
from copy import deepcopy

import cv2
import imageio
import torch
from matplotlib import cm

from DLModels.LoFTR import LoFTR
from DLModels.LoFTR.utils.cvpr_ds_config import default_cfg
from utils.matching_utils import (AverageTimer, VideoStreamer,
                                  frame2tensor, make_matching_plot_fast)


def withoutKpts_images(path, scene, fix=True, image_glob=None, skip=1, max_length=1000000, resize=None, fps=1):
    if image_glob is None:
        image_glob = ['*.png', '*.jpg', '*.jpeg']
    if resize is None:
        resize = [640, 480]

    device = 'cpu'

    if scene == '室内':
        _default_cfg = deepcopy(default_cfg)
        _default_cfg['coarse']['temp_bug_fix'] = True
        matcher = LoFTR(config=_default_cfg)
        matcher.load_state_dict(torch.load("weights/LoFTR/indoor_ds_new.ckpt")['state_dict'])
        matcher = matcher.eval()
    elif scene == '室外':
        matcher = LoFTR(config=default_cfg)
        matcher.load_state_dict(torch.load("weights/LoFTR/outdoor_ds.ckpt")['state_dict'])
        matcher = matcher.eval()

    vs = VideoStreamer(path, resize=resize,
                       skip=skip, image_glob=image_glob, max_length=max_length)
    frame, _ = vs.next_frame()
    last_frame_tensor = frame2tensor(frame, device)
    last_frame = frame
    last_image_id = 0

    matching_images = []

    timer = AverageTimer()

    while True:
        frame, ret = vs.next_frame()
        if not ret:
            print('Finished')
            break
        timer.update('load data')
        stem0, stem1 = last_image_id, vs.i - 1

        new_frame_tensor = frame2tensor(frame, device)
        batch = {'image0': last_frame_tensor, 'image1': new_frame_tensor}

        with torch.no_grad():
            matcher(batch)
            mkpts0 = batch['mkpts0_f'].cpu().numpy()
            mkpts1 = batch['mkpts1_f'].cpu().numpy()
            mconf = batch['mconf'].cpu().numpy()
        timer.update('matching')
        color = cm.jet(mconf)
        text = [
            'LoFTR',
            'Matches: {}'.format(len(mkpts0)),
        ]
        small_text = timer.print(small_text=[])
        stem = 'matches_{:06}_{:06}'.format(stem0, stem1)
        out = make_matching_plot_fast(
            last_frame, frame, mkpts0=mkpts0, mkpts1=mkpts1, color=color, text=text,
            path=None, show_keypoints=False, small_text=small_text, margin=0)
        matching_images.append(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

        if not fix:
            last_frame = frame
            last_frame_tensor = new_frame_tensor
    save_dir = os.path.join(path, 'res')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "LoFTR_{}.mp4".format(scene))
    imageio.mimsave(save_path, matching_images, format="MP4", fps=fps)

    return save_path
