"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/10 08:24
Project    : FeatureMatchingBackend
FilePath   : services/mosaic/mosaic.py
Description:
"""
import cv2
import numpy as np

from services.detection.ORB import detection_ORB
from services.detection.SIFT import detection_SIFT
from utils.matching_utils import VideoStreamer, process_resize


def get_homo(kpts1, kpts2, matches, min_matches=8):
    """
    获取单应性矩阵
    """
    if len(matches) >= min_matches:
        src_pts = np.float32([kpts1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kpts2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        H, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

        return H
    else:
        print("特征点数量不够")


def stitch_img(img1, img2, H):
    """
    进行图像拼接
    """
    # 1. 获取第二张图片的四个角点
    w1, h1 = img1.shape[:2]
    w2, h2 = img2.shape[:2]
    img2_corners = np.float32([[0, 0], [0, h2], [w2, h2], [w2, 0]]).reshape(-1, 1, 2)

    # 2. 对第二张图片进行变换, 获得新的四个角点
    img2_transform = cv2.perspectiveTransform(img2_corners, H)

    # 3. 计算平移的距离，创建一个大图，对图像进行平移
    [x_min, y_min] = np.int32(img2_transform.min(axis=0).ravel() - 0.5)
    [x_max, y_max] = np.int32(img2_transform.max(axis=0).ravel() + 0.5)
    # 平移的距离
    t = [-x_min, -y_min]

    # 构造齐次坐标
    H_transform = np.array([[1, 0, t[0]],
                            [0, 1, t[1]],
                            [0, 0, 1]])

    new_w = max(w1 + x_max - x_min, w2)
    new_h = max(h1, y_max - y_min)
    result_img = cv2.warpPerspective(img1, H_transform.dot(H), (new_w, new_h))

    # 4. 实现两张图片的拼接
    # 计算img2在result_img中的位置
    start_x = max(0, t[0])
    start_y = max(0, t[1])
    end_x = min(start_x + w2, new_w)
    end_y = min(start_y + h2, new_h)

    # 确保start_x, start_y, end_x, end_y是有效的
    if start_x < end_x and start_y < end_y:
        result_img[start_x:end_x, start_y:end_y] = img2

    return result_img


def mosaic(img1, img2, kptsMethod, matchMethod):
    w, h = img1.shape[1], img2.shape[0]
    w_new, h_new = process_resize(w, h, [640, 480])
    img1 = cv2.resize(img1, (w_new, h_new), interpolation=cv2.INTER_AREA)
    img2 = cv2.resize(img2, (w_new, h_new), interpolation=cv2.INTER_AREA)

    if kptsMethod == 'SIFT':
        _, _, _, des1, kpts1 = detection_SIFT(img1)
        _, _, _, des2, kpts2 = detection_SIFT(img2)
    elif kptsMethod == 'ORB':
        _, _, _, des1, kpts1 = detection_ORB(img1)
        _, _, _, des2, kpts2 = detection_ORB(img2)

    if matchMethod == 'BF':
        bf = cv2.BFMatcher(cv2.NORM_L2, True)
        matches = bf.match(des1, des2)
    elif matchMethod == 'FLANN':
        index_params = dict(algorithm=1, trees=5)
        search_params = dict(checks=50)
        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)

    H = get_homo(kpts1, kpts2, matches)

    out = stitch_img(img1, img2, H)

    return out


