"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/9 10:25
Project    : FeatureMatchingBackend
FilePath   : services/matching/SuperGlue.py
Description: SuperGlue 实现特征匹配的业务方法
"""
import os

import cv2
import imageio
import numpy as np
import torch
from matplotlib import cm

from DLModels.SuperGlue.matching import Matching
from utils.matching_utils import (AverageTimer, VideoStreamer,
                                  frame2tensor, make_matching_plot_fast, process_resize, estimate_pose,
                                  scale_intrinsics)


def matching_pair(path, img1_path, img2_path, K,
                  scene, sinkhorn_iterations=20, match_threshold=0.2,
                  nms_radius=4, max_keypoints=-1, keypoint_threshold=0.005,
                  fps=1, is_save=True, is_process=True, timer=None):
    device = 'cpu'

    if scene == '室内':
        scene = 'indoor'
    elif scene == '室外':
        scene = 'outdoor'

    config = {
        'superpoint': {
            'nms_radius': nms_radius,
            'keypoint_threshold': keypoint_threshold,
            'max_keypoints': max_keypoints
        },
        'superglue': {
            'weights': scene,
            'sinkhorn_iterations': sinkhorn_iterations,
            'match_threshold': match_threshold,
        }
    }

    matching = Matching(config).eval().to(device)
    keys = ['keypoints', 'scores', 'descriptors']

    if timer is None:
        timer = AverageTimer(newline=True)

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
    img1_tensor = frame2tensor(img1, device)
    img2_tensor = frame2tensor(img2, device)

    timer.update('process images')

    with torch.no_grad():
        pred = matching({'image0': img1_tensor, 'image1': img2_tensor})
        kpts0 = pred['keypoints0'][0].cpu().numpy()
        kpts1 = pred['keypoints1'][0].cpu().numpy()
        matches = pred['matches0'][0].cpu().numpy()
        confidence = pred['matching_scores0'][0].cpu().numpy()
        out_matches = {'keypoints0': kpts0, 'keypoints1': kpts1,
                       'matches': matches, 'match_confidence': confidence}
    timer.update('Matching')

    valid = matches > -1
    mkpts0 = kpts0[valid]
    mkpts1 = kpts1[matches[valid]]

    if is_save:
        thresh = 1.
        ret, E = estimate_pose(mkpts0, mkpts1, K_scale, K_scale, thresh)
        if ret is not None:
            R, t, inliers = ret

            out_poses = {
                'E': E,
                'R': R,
                't': t,
                'inliers': inliers,
            }

        save_dir = os.path.join(path, 'res')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "SuperPoint_SuperGlue_{}_viz.png".format(scene))
        save_matches_path = os.path.join(save_dir, "SuperPoint_SuperGlue_{}_matches.npz".format(scene))
        save_pose_path = os.path.join(save_dir, "SuperPoint_SuperGlue_{}_pose.npz".format(scene))
        if ret is not None:
            np.savez(save_matches_path, **out_matches)
            np.savez(save_pose_path, **out_poses)

        color = cm.jet(confidence[valid])
        text = [
            'SuperPoint_SuperGlue',
            'Keypoints: {}:{}'.format(len(kpts0), len(kpts1)),
            'Matches: {}'.format(len(mkpts0))
        ]
        k_thresh = matching.superpoint.config['keypoint_threshold']
        m_thresh = matching.superglue.config['match_threshold']
        img1_name = os.path.basename(img1_path)
        img2_name = os.path.basename(img2_path)
        small_text = [
            'R: {}'.format(R[0, :]),
            '   {}'.format(R[1, :]),
            '   {}'.format(R[2, :]),
            't: {}'.format(str(t)),
            'inliers: {}'.format(len(inliers)),
            'Keypoint Threshold: {:.4f}'.format(k_thresh),
            'Match Threshold: {:.2f}'.format(m_thresh),
            'Image Pair: {}:{}'.format(img1_name, img2_name),
        ]
        out = make_matching_plot_fast(
            img1, img2, mkpts0, mkpts1, color, text, kpts0, kpts1,
            path=save_path, show_keypoints=True, small_text=small_text)

        return save_path, save_matches_path, save_pose_path
    else:
        return kpts0, kpts1, mkpts0, mkpts1


def matching_images(path, scene, K, fix=True, type='多张图片',
                    image_glob=None, skip=1, resize=None, max_length=1000000,
                    max_keypoints=-1, keypoint_threshold=0.005, nms_radius=4,
                    sinkhorn_iterations=20, match_threshold=0.2,
                    fps=1):
    if image_glob is None:
        image_glob = ['*.png', '*.jpg', '*.jpeg']
    if resize is None:
        resize = [640, 480]

    device = 'cpu'

    if scene == '室内':
        scene = 'indoor'
    elif scene == '室外':
        scene = 'outdoor'

    config = {
        'superpoint': {
            'nms_radius': nms_radius,
            'keypoint_threshold': keypoint_threshold,
            'max_keypoints': max_keypoints
        },
        'superglue': {
            'weights': scene,
            'sinkhorn_iterations': sinkhorn_iterations,
            'match_threshold': match_threshold,
        }
    }

    matching = Matching(config).eval().to(device)
    keys = ['keypoints', 'scores', 'descriptors']

    save_dir = os.path.join(path, 'res')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "SuperPoint_SuperGlue_{}_viz.mp4".format(scene))
    save_matches_path = os.path.join(save_dir, "SuperPoint_SuperGlue_{}_matches.npz".format(scene))
    save_pose_path = os.path.join(save_dir, "SuperPoint_SuperGlue_{}_pose.npz".format(scene))

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

    result_images = []
    out_matches = []
    out_poses = []
    timer = AverageTimer(newline=True)

    while True:
        frame, ret = vs.next_frame()
        if not ret:
            print('Finished')
            break
        timer.update('data')
        stem0, stem1 = last_image_id, vs.i - 1

        frame_tensor = frame2tensor(frame, device)
        with torch.no_grad():
            pred = matching({'image0': last_frame_tensor, 'image1': frame_tensor})
            kpts0 = pred['keypoints0'][0].cpu().numpy()
            kpts1 = pred['keypoints1'][0].cpu().numpy()
            matches = pred['matches0'][0].cpu().numpy()
            confidence = pred['matching_scores0'][0].cpu().numpy()
            print(1)
            out_match = {'keypoints0_' + str(stem1): kpts0, 'keypoints1_' + str(stem1): kpts1,
                           'matches_' + str(stem1): matches, 'match_confidence_' + str(stem1): confidence}
            out_matches.append(out_match)
            print(2)
        timer.update('matching')

        valid = matches > -1
        mkpts0 = kpts0[valid]
        mkpts1 = kpts1[matches[valid]]
        mconf = confidence[valid]

        thresh = 1.
        ret, E = estimate_pose(mkpts0, mkpts1, K_scale, K_scale, thresh)
        if ret is None:
            continue
        R, t, inliers = ret

        out_pose = {
            'E_' + str(stem1): E,
            'R_' + str(stem1): R,
            't_' + str(stem1): t,
            'inliers' + str(stem1): inliers,
        }
        out_poses.append(out_pose)

        # 可视化
        color = cm.jet(confidence[valid])
        text = [
            'SuperPoint_SuperGlue',
            'Keypoints: {}:{}'.format(len(kpts0), len(kpts1)),
            'Matches: {}'.format(len(mkpts0)),
        ]
        k_thresh = matching.superpoint.config['keypoint_threshold']
        m_thresh = matching.superglue.config['match_threshold']
        small_text = [
            'R: {}'.format(R[0, :]),
            '   {}'.format(R[1, :]),
            '   {}'.format(R[2, :]),
            't: {}'.format(str(t)),
            'inliers: {}'.format(len(inliers)),
            'Keypoint Threshold: {:.4f}'.format(k_thresh),
            'Match Threshold: {:.2f}'.format(m_thresh),
            'Image Pair: {:06}:{:06}'.format(stem0, stem1),
        ]
        out = make_matching_plot_fast(
            last_frame, frame, mkpts0, mkpts1, color, text, kpts0, kpts1,
            path=None, show_keypoints=True, small_text=small_text)
        result_images.append(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

        if not fix:
            last_frame = frame
            last_frame_tensor = frame_tensor

    imageio.mimsave(save_path, result_images, format="MP4", fps=fps)
    np.savez(save_pose_path, out_poses)
    np.savez(save_matches_path, out_matches)

    return save_path, save_matches_path, save_pose_path
