"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/25 19:09
Project    : FeatureMatchingBackend
FilePath   : services/matching/ASpanFormer.py
Description:
"""
import os

import cv2
import imageio
import numpy as np
import torch
from matplotlib import cm

from DLModels.ASpanFormer.aspanformer import ASpanFormer
from DLModels.ASpanFormer.config.default import get_cfg_defaults
from DLModels.ASpanFormer.utils.misc import lower_config

from utils.matching_utils import (AverageTimer, VideoStreamer,
                                  frame2tensor, make_matching_plot_fast, process_resize, estimate_pose,
                                  scale_intrinsics)


def matching_pair(path, img1_path, img2_path, K, scene, is_save=True, is_process=True, timer=None):
    device = 'cpu'

    if scene == '室内':
        scene = 'indoor'
        config = get_cfg_defaults()
        config.merge_from_file('DLModels/AspanFormer/configs/aspan/indoor/aspan_test.py')
        _config = lower_config(config)
        matcher = ASpanFormer(config=_config['aspan'])
        state_dict = torch.load('weights/ASpanFormer/indoor.ckpt', map_location='cpu')['state_dict']
        matcher.load_state_dict(state_dict, strict=False)
        matcher = matcher.eval()
    elif scene == '室外':
        scene = 'outdoor'
        config = get_cfg_defaults()
        config.merge_from_file('DLModels/AspanFormer/configs/aspan/outdoor/aspan_test.py')
        _config = lower_config(config)
        matcher = ASpanFormer(config=_config['aspan'])
        state_dict = torch.load('weights/ASpanFormer/outdoor.ckpt', map_location='cpu')['state_dict']
        matcher.load_state_dict(state_dict, strict=False)
        matcher = matcher.eval()

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
    img1_tensor = frame2tensor(img1, device)
    img2_tensor = frame2tensor(img2, device)
    timer.update('process images')

    batch = {'image0': img1_tensor, 'image1': img2_tensor}

    with torch.no_grad():
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
        save_path = os.path.join(save_dir, "ASpanFormer_{}_viz.png".format(scene))
        save_matches_path = os.path.join(save_dir, "ASpanFormer_{}_matches.npz".format(scene))
        save_poses_path = os.path.join(save_dir, "ASpanFormer_{}_pose.npz".format(scene))

        if res is not None:
            np.savez(save_matches_path, matches=out_matches)
            np.savez(save_poses_path, poses=out_poses)

        color = cm.jet(mconf)
        text = [
            'ASpanFormer',
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


def matching_images(path, K, scene, fix=True, type='多张图片', image_glob=None, skip=1, max_length=1000000,
                    resize=None,
                    fps=1):
    if image_glob is None:
        image_glob = ['*.png', '*.jpg', '*.jpeg']
    if resize is None:
        resize = [640, 480]

    device = 'cpu'

    if scene == '室内':
        scene = 'indoor'
        config = get_cfg_defaults()
        config.merge_from_file('DLModels/AspanFormer/configs/aspan/indoor/aspan_test.py')
        _config = lower_config(config)
        matcher = ASpanFormer(config=_config['aspan'])
        state_dict = torch.load('weights/ASpanFormer/indoor.ckpt', map_location='cpu')['state_dict']
        matcher.load_state_dict(state_dict, strict=False)
        matcher = matcher.eval()
    elif scene == '室外':
        scene = 'outdoor'
        config = get_cfg_defaults()
        config.merge_from_file('DLModels/AspanFormer/configs/aspan/outdoor/aspan_test.py')
        _config = lower_config(config)
        matcher = ASpanFormer(config=_config['aspan'])
        state_dict = torch.load('weights/ASpanFormer/outdoor.ckpt', map_location='cpu')['state_dict']
        matcher.load_state_dict(state_dict, strict=False)
        matcher = matcher.eval()

    result_images = []
    out_matches = []
    out_poses = []
    save_dir = os.path.join(path, 'res')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "ASpanFormer_{}_viz.mp4".format(scene))
    save_matches_path = os.path.join(save_dir, "ASpanFormer_{}_matches.npz".format(scene))
    save_poses_path = os.path.join(save_dir, "ASpanFormer_{}_pose.npz".format(scene))

    if type == '多张图片':
        vs = VideoStreamer(path, resize=resize,
                           skip=skip, image_glob=image_glob, max_length=max_length)
    elif type == '视频':
        file_names = os.listdir(path)
        file_path = \
            [os.path.join(path, file_name) for file_name in file_names if
             os.path.isfile(os.path.join(path, file_name))][0]
        vs = VideoStreamer(file_path, resize=resize,
                           skip=skip, image_glob=image_glob, max_length=max_length)
    frame, _ = vs.next_frame()
    K_scale = scale_intrinsics(K, vs.scales)
    last_frame_tensor = frame2tensor(frame, device)
    last_frame = frame
    last_image_id = 0

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
            out_match = {
                'mkpts0_' + str(stem1): mkpts0,
                'mkpts1_' + str(stem1): mkpts1,
                'mconf_' + str(stem1): mconf,
            }
            out_matches.append(out_match)
        timer.update('matching')

        thresh = 1.
        res, E = estimate_pose(mkpts0, mkpts1, K_scale, K_scale, thresh)
        if res is None:
            continue
        R, t, inliers = res

        out_pose = {
            'E_' + str(stem1): E,
            'R_' + str(stem1): R,
            't_' + str(stem1): t,
            'inliers_' + str(stem1): inliers,
        }
        out_poses.append(out_pose)

        color = cm.jet(mconf)
        text = [
            'ASpanFormer',
            'Matches: {}'.format(len(mkpts0)),
        ]
        small_text = timer.print(small_text=[
            'R: {}'.format(R[0, :]),
            '   {}'.format(R[1, :]),
            '   {}'.format(R[2, :]),
            't: {}'.format(str(t)),
            'inliers: {}'.format(len(inliers)),
            'matches_{:06}_{:06}'.format(stem0, stem1)
        ])
        out = make_matching_plot_fast(
            last_frame, frame, mkpts0=mkpts0, mkpts1=mkpts1, color=color, text=text,
            path=None, show_keypoints=False, small_text=small_text, margin=0)
        result_images.append(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

        if not fix:
            last_frame = frame
            last_frame_tensor = new_frame_tensor

    imageio.mimsave(save_path, result_images, format="MP4", fps=fps)
    np.savez(save_matches_path, out_matches)
    np.savez(save_poses_path, out_poses)

    return save_path, save_matches_path, save_poses_path
