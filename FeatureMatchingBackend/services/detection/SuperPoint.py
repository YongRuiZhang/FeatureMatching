"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/24 16:41
Project    : FeatureMatchingBackend
FilePath   : services/detection/SuperPoint.py
Description: SuperPoint 实现特征检测
"""
import os

import cv2
import numpy as np
import torch
from DLModels.SuperPoint.superpoint import SuperPoint
from utils.matching_utils import process_resize, frame2tensor


def detection_SuperPoint(img, max_keypoints=-1, keypoint_threshold=0.005, nms_radius=4, resize=None):
    if resize is None:
        resize = [640, 480]
    config = {
        'superpoint': {
            'nms_radius': nms_radius,
            'keypoint_threshold': keypoint_threshold,
            'max_keypoints': max_keypoints
        }
    }
    device = 'cpu'
    superpoint = SuperPoint(config.get('superpoint', {})).eval().to(device)

    if len(img.shape) > 2:
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray_img = img
    w, h = gray_img.shape[1], gray_img.shape[0]
    w_new, h_new = process_resize(w, h, resize)
    gray_img = cv2.resize(gray_img, (w_new, h_new), interpolation=cv2.INTER_AREA)
    frame_tensor = frame2tensor(gray_img, device)
    with torch.no_grad():
        pred = superpoint({'image': frame_tensor})
        kpts = pred['keypoints'][0].cpu().numpy()
        des = pred['descriptors'][0].cpu().numpy()
        scores = pred['scores'][0].cpu().numpy()

    # 可视化
    H, W = gray_img.shape

    out = 255 * np.ones((H, W), np.uint8)
    out[:H, :W] = gray_img
    kpts0 = np.round(kpts).astype(int)
    white = (255, 255, 255)
    black = (0, 0, 0)
    for x, y in kpts0:
        cv2.circle(out, (x, y), 2, black, -1, lineType=cv2.LINE_AA)
        cv2.circle(out, (x, y), 1, white, -1, lineType=cv2.LINE_AA)

    return out, kpts.shape[0], kpts, des, scores
