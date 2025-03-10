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
import torch
from matplotlib import cm

from DLModels.SuperGlue.matching import Matching
from utils.matching_utils import (AverageTimer, VideoStreamer,
                                  frame2tensor, make_matching_plot_fast, process_resize)


def matching_pair(path, img1_path, img2_path, scene,
                   max_keypoints=-1,
                   keypoint_threshold=0.005,
                   nms_radius=4,
                   sinkhorn_iterations=20,
                   match_threshold=0.2, fps=1):

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

    timer = AverageTimer(newline=True)

    img1 = cv2.imread(img1_path, 0)
    img2 = cv2.imread(img2_path, 0)
    w, h = img1.shape[1], img1.shape[0]
    w_new, h_new = process_resize(w, h, [640, 480])
    img1 = cv2.resize(img1, (w_new, h_new), interpolation=cv2.INTER_AREA)
    img2 = cv2.resize(img2, (w_new, h_new), interpolation=cv2.INTER_AREA)
    img1_tensor = frame2tensor(img1, device)
    img2_tensor = frame2tensor(img2, device)
    timer.update('process images')

    with torch.no_grad():
        pred = matching({'image0': img1_tensor, 'image1': img2_tensor})
        kpts0 = pred['keypoints0'][0].cpu().numpy()
        kpts1 = pred['keypoints1'][0].cpu().numpy()
        matches = pred['matches0'][0].cpu().numpy()
        confidence = pred['matching_scores0'][0].cpu().numpy()
    timer.update('forward')

    valid = matches > -1
    mkpts0 = kpts0[valid]
    mkpts1 = kpts1[matches[valid]]
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
        'Keypoint Threshold: {:.4f}'.format(k_thresh),
        'Match Threshold: {:.2f}'.format(m_thresh),
        'Image Pair: {}:{}'.format(img1_name, img2_name),
    ]
    save_dir = os.path.join(path, 'res')
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, "SuperPoint_SuperGlue_{}.png".format(scene))
    out = make_matching_plot_fast(
        img1, img2, mkpts0, mkpts1, color, text, kpts0, kpts1,
        path=save_path, show_keypoints=True, small_text=small_text)

    return save_path


def matching_images(path, scene, fix=True, image_glob=None, skip=1, max_length=1000000, resize=None, max_keypoints=-1,
                    keypoint_threshold=0.005,
                    nms_radius=4,
                    sinkhorn_iterations=20,
                    match_threshold=0.2, fps=1):
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

    vs = VideoStreamer(path, resize, skip, image_glob, max_length)
    frame, _ = vs.next_frame()

    last_frame_tensor = frame2tensor(frame, device)
    last_frame = frame
    last_image_id = 0

    matching_images = []
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
        timer.update('forward')

        valid = matches > -1
        mkpts0 = kpts0[valid]
        mkpts1 = kpts1[matches[valid]]
        color = cm.jet(confidence[valid])
        text = [
            'SuperPoint_SuperGlue',
            'Keypoints: {}:{}'.format(len(kpts0), len(kpts1)),
            'Matches: {}'.format(len(mkpts0))
        ]
        k_thresh = matching.superpoint.config['keypoint_threshold']
        m_thresh = matching.superglue.config['match_threshold']
        small_text = [
            'Keypoint Threshold: {:.4f}'.format(k_thresh),
            'Match Threshold: {:.2f}'.format(m_thresh),
            'Image Pair: {:06}:{:06}'.format(stem0, stem1),
        ]
        out = make_matching_plot_fast(
            last_frame, frame, mkpts0, mkpts1, color, text, kpts0, kpts1,
            path=None, show_keypoints=True, small_text=small_text)
        matching_images.append(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

        if not fix:
            last_frame = frame
            last_frame_tensor = frame_tensor
    save_dir = os.path.join(path, 'res')
    os.makedirs(save_dir, exist_ok=True)

    save_path = os.path.join(save_dir, "SuperPoint_SuperGlue_{}.mp4".format(scene))
    imageio.mimsave(save_path, matching_images, format="MP4", fps=fps)

    return save_path
