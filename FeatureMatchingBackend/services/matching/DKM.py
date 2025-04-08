"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/25 11:09
Project    : FeatureMatchingBackend
FilePath   : services/matching/DKM.py
Description:
"""
import os

import cv2
import imageio
import numpy as np
import torch
from PIL import Image
from matplotlib import cm

from DLModels.DKM import DKMv3_indoor, DKMv3_outdoor
from utils.matching_utils import estimate_pose, make_matching_plot_fast, VideoStreamer, AverageTimer, process_resize, \
    scale_intrinsics


def sample(dense_matches, dense_certainty, max_num=10000):
    dense_certainty = dense_certainty ** (1 / 3)

    # 筛选置信度大于0.7的匹配点
    mask = dense_certainty > 0.7
    dense_matches = dense_matches[mask]
    dense_certainty = dense_certainty[mask]

    if len(dense_matches) == 0:
        return torch.empty(0, 4), torch.empty(0)

    # 如果匹配点数量超过最大值，则随机采样
    if len(dense_matches) > max_num:
        indices = torch.randperm(len(dense_matches))[:max_num]
        dense_matches = dense_matches[indices]
        dense_certainty = dense_certainty[indices]

    return dense_matches, dense_certainty


def matching_pair(path, img1_path, img2_path, K, scene,
                  fps=1, is_save=True, is_process=True, timer=None):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    if scene == '室内':
        dkm_model = DKMv3_indoor()
    else:
        dkm_model = DKMv3_outdoor()

    if timer is None:
        timer = AverageTimer()

    if is_process:
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
    timer.update('process images')

    img1 = Image.fromarray(cv2.cvtColor(img1, cv2.COLOR_BGR2RGB))
    img2 = Image.fromarray(cv2.cvtColor(img2, cv2.COLOR_BGR2RGB))
    warp, certainty = dkm_model.match(img1, img2, device=device)
    matches, certainty = sample(warp, certainty)
    kpts1, kpts2 = dkm_model.to_pixel_coordinates(matches, 640, 480, 640, 480)
    kpts1 = kpts1.cpu().numpy()
    kpts2 = kpts2.cpu().numpy()
    out_matches = {
        'kpts1': kpts1,
        'kpts2': kpts2,
        'matches': matches,
        'certainty': certainty,
    }
    timer.update('Matching')

    if is_save:
        save_dir = os.path.join(path, 'res')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "DKM_{}_viz.png".format(scene))
        save_matches_path = os.path.join(save_dir, "DKM_{}_matches.npz".format(scene))
        save_pose_path = os.path.join(save_dir, "DKM_{}_pose.npz".format(scene))

        thresh = 1.
        res, E = estimate_pose(kpts1, kpts2, K, K, thresh)
        if res is not None:
            R, t, inliers = res

            out_poses = {
                'E': E,
                'R': R,
                't': t,
                'inliers': inliers,
            }
            np.savez(save_matches_path, **out_matches)
            np.savez(save_pose_path, **out_poses)

        color = cm.jet(certainty)
        text = [
            'DKM',
            'Matches: {}'.format(len(kpts1)),
        ]
        small_text = timer.print(small_text=[
            'R: {}'.format(R[0, :]),
            '   {}'.format(R[1, :]),
            '   {}'.format(R[2, :]),
            't: {}'.format(str(t)),
            'inliers: {}'.format(len(inliers)),
        ])
        out = make_matching_plot_fast(
            cv2.cvtColor(np.asarray(img1), cv2.COLOR_RGB2GRAY),
            cv2.cvtColor(np.asarray(img2), cv2.COLOR_RGB2GRAY), mkpts0=kpts1, mkpts1=kpts2, color=color, text=text,
            path=save_path, show_keypoints=False, small_text=small_text, margin=0)

        return save_path, save_matches_path, save_pose_path
    else:
        return kpts1, kpts2


def matching_images(path, K, scene, fix=True, type='多张图片', image_glob=None, skip=1, max_num=10000, resize=None,
                    fps=1,
                    max_length=100000):
    if image_glob is None:
        image_glob = ['*.png', '*.jpg', '*.jpeg']
    if resize is None:
        resize = [640, 480]

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    if scene == '室内':
        dkm_model = DKMv3_indoor()
    else:
        dkm_model = DKMv3_outdoor()

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

    timer = AverageTimer()

    result_images = []
    out_matches = []
    out_poses = []
    save_dir = os.path.join(path, 'res')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "DKM_{}_viz.mp4".format(scene))
    save_matches_path = os.path.join(save_dir, "DKM_{}_matches.npz".format(scene))
    save_poses_path = os.path.join(save_dir, "DKM_{}_pose.npz".format(scene))

    frame, _ = vs.next_frame()
    last_frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    last_image_id = 0

    while True:
        frame, ret = vs.next_frame()
        if not ret:
            break
        timer.update('load data')
        stem0, stem1 = last_image_id, vs.i - 1

        frame = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        warp, certainty = dkm_model.match(last_frame, frame, device=device)
        matches, certainty = sample(warp, certainty)
        kpts1, kpts2 = dkm_model.to_pixel_coordinates(matches, 640, 480, 640, 480)
        kpts1 = kpts1.cpu().numpy()
        kpts2 = kpts2.cpu().numpy()
        timer.update('Matching')
        out_match = {
            'kpts1': kpts1,
            'kpts2': kpts2,
            'matches': matches,
            'certainty': certainty,
        }

        thresh = 1.
        res, E = estimate_pose(kpts1, kpts2, K, K, thresh)
        if res is None:
            continue
        R, t, inliers = res

        out_pose = {
            'E_' + str(stem1): E,
            'R_' + str(stem1): R,
            't_' + str(stem1): t,
            'inliers_' + str(stem1): inliers,
        }

        out_matches.append(out_match)
        out_poses.append(out_pose)

        color = cm.jet(certainty)
        text = [
            'DKM',
            'Matches: {}'.format(len(kpts1)),
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
            cv2.cvtColor(np.asarray(last_frame), cv2.COLOR_RGB2GRAY),
            cv2.cvtColor(np.asarray(frame), cv2.COLOR_RGB2GRAY), mkpts0=kpts1, mkpts1=kpts2, color=color, text=text,
            path=None, show_keypoints=False, small_text=small_text, margin=0)

        result_images.append(out)

        if not fix:
            last_frame = frame

    imageio.mimsave(save_path, result_images, format="MP4", fps=fps)
    np.savez(save_matches_path, out_matches)
    np.savez(save_poses_path, out_poses)

    return save_path, save_matches_path, save_poses_path
