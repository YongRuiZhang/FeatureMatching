"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/10 08:24
Project    : FeatureMatchingBackend
FilePath   : services/mosaic/mosaic.py
Description:
"""
import os

import cv2
import numpy as np

from services.detection.ORB import detection_ORB
from services.detection.SIFT import detection_SIFT
from services.detection.SuperPoint import detection_SuperPoint
from services.matching.BF import matching_BF_pair
from services.matching.FLANN import matching_FLANN_pair
from services.matching.LoFTR import withoutKpts_pair
from services.matching.SuperGlue import matching_pair
from utils.matching_utils import process_resize, AverageTimer


def get_homo_BF_FLANN(kpts1, kpts2, matches, min_matches=8):
    if len(matches) >= min_matches:
        src_points = np.float32([kpts1[m.queryIdx].pt for m in matches]).reshape(-1, 2)
        dst_points = np.float32([kpts2[m.trainIdx].pt for m in matches]).reshape(-1, 2)
        H, mask = cv2.findHomography(dst_points, src_points, cv2.RANSAC, 4.0)
        return H, True
    else:
        return '特征点数量不够', False

def get_homo_SuperGlue_LoFTR(mkpts1, mkpts2, min_matches=8):
    if len(mkpts1) >= min_matches:
        # src_points = np.float32([kpts1[m.queryIdx].pt for m in matches]).reshape(-1, 2)
        # dst_points = np.float32([kpts2[m.trainIdx].pt for m in matches]).reshape(-1, 2)
        print(mkpts1[0], mkpts2[0])
        mkpts1 = mkpts1.astype(np.float32)
        mkpts2 = mkpts2.astype(np.float32)
        H, mask = cv2.findHomography(mkpts2, mkpts1, cv2.RANSAC, 4.0)
        return H, True
    else:
        return '特征点数量不够', False


# 图像拼接
def warp_image(image, H, output_shape):
    return cv2.warpPerspective(image, H, output_shape)


# 去除黑边
def crop_black_edges(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(thresh)
    x, y, w, h = cv2.boundingRect(coords)
    cropped_image = image[y:y + h, x:x + w]
    return cropped_image


def detection(frame1, frame2, kptsMethod):
    if kptsMethod == 'SIFT':
        _, _, _, des1, kpts1 = detection_SIFT(frame1)
        _, _, _, des2, kpts2 = detection_SIFT(frame2)
    elif kptsMethod == 'ORB':
        _, _, _, des1, kpts1 = detection_ORB(frame1)
        _, _, _, des2, kpts2 = detection_ORB(frame2)
        des1 = des1.astype(np.float32)
        des2 = des2.astype(np.float32)
    elif kptsMethod == 'SuperPoint':
        _, _, kpts1, des1, _ = detection_SuperPoint(frame1)
        _, _, kpts2, des2, _ = detection_SuperPoint(frame2)
        des1 = des1.astype(np.float32).T
        des2 = des2.astype(np.float32).T

    return kpts1, kpts2, des1, des2


def matching(matcher, des1, des2, k=0.7):
    matches = matcher.knnMatch(des1, des2, 2)
    good_matches = []
    for match_pair in matches:
        if len(match_pair) == 2:
            m, n = match_pair
            if m.distance < k * n.distance:
                good_matches.append(m)

    return good_matches


def mosaic_pair(path, img1, img2, cls, kptsMethod, matchMethod, scence, scale):
    timer = AverageTimer()

    image1 = cv2.imread(img1)
    image2 = cv2.imread(img2)

    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    if scale == '不保留':
        w, h = image1.shape[1], image1.shape[0]
        w_new, h_new = process_resize(w, h, [640, 480])
        image1 = cv2.resize(image1, (w_new, h_new), interpolation=cv2.INTER_AREA)
        image2 = cv2.resize(image2, (w_new, h_new), interpolation=cv2.INTER_AREA)
        gray1 = cv2.resize(gray1, (w_new, h_new), interpolation=cv2.INTER_AREA)
        gray2 = cv2.resize(gray2, (w_new, h_new), interpolation=cv2.INTER_AREA)

    timer.update('process images')

    if matchMethod == 'FLANN':
        kpts1, kpts2, des1, des2, matches = matching_FLANN_pair('', gray1, gray2, kptsMethod, is_save=False,
                                                                is_process=False, timer=timer)
        H, ret = get_homo_BF_FLANN(kpts1, kpts2, matches, min_matches=8)
    elif matchMethod == 'BF':
        kpts1, kpts2, des1, des2, matches = matching_BF_pair('', gray1, gray2, kptsMethod, is_save=False,
                                                             is_process=False, timer=timer)
        H, ret = get_homo_BF_FLANN(kpts1, kpts2, matches, min_matches=8)
    elif matchMethod == 'SuperGlue':
        kpts1, kpts2, mkpts1, mkpts2 = matching_pair('', gray1, gray2, scence, is_save=False, is_process=False, timer=timer)
        H, ret = get_homo_SuperGlue_LoFTR(mkpts1, mkpts2, min_matches=8)
    elif matchMethod == 'LoFTR':
        mkpts1, mkpts2 = withoutKpts_pair('', gray1, gray2, scence, is_save=False, is_process=False, timer=timer)
        H, ret = get_homo_SuperGlue_LoFTR(mkpts1, mkpts2, min_matches=8)

    print(H, ret)

    if not ret:
        return '', False

    # 定义输出尺寸
    output_shape = (image1.shape[1] + image2.shape[1], image1.shape[0])

    # 使用单应性矩阵对第二幅图像进行透视变换
    warped_image2 = warp_image(image2, H, output_shape)

    # 拼接两幅图像
    panorama = np.copy(warped_image2)
    cv2.imwrite('pan_{}_{}.png'.format(kptsMethod, matchMethod), panorama)
    panorama[0:image1.shape[0], 0:image1.shape[1]] = image1
    cv2.imwrite('panorama_{}_{}.png'.format(kptsMethod, matchMethod), panorama)

    # 去除黑色边缘
    out = crop_black_edges(panorama)

    timer.update('stitch')

    H, _, _ = out.shape
    if scale == '不保留':
        sc = min(H / 640., 2.0)
    else:
        sc = 2.0
    Ht = int(30 * sc)  # text height
    txt_color_fg = (0, 255, 0)
    txt_color_bg = (0, 0, 0)
    text = []
    if matchMethod == 'LoFTR':
        text.append('LoFTR')
    else:
        text.append('{}_{}'.format(matchMethod, kptsMethod))
        text.append('kpts:{}:{}'.format(len(kpts1), len(kpts2)),)
    if matchMethod == 'FLANN' or matchMethod == 'BF':
        text.append('matches:{}'.format(len(matches)))
    elif matchMethod == 'SuperGlue':
        text.append('matches:{}'.format(len(mkpts1)))

    for i, t in enumerate(text):
        cv2.putText(out, t, (int(8 * sc), Ht * (i + 1)), cv2.FONT_HERSHEY_DUPLEX,
                    1.0 * sc, txt_color_bg, 2, cv2.LINE_AA)
        cv2.putText(out, t, (int(8 * sc), Ht * (i + 1)), cv2.FONT_HERSHEY_DUPLEX,
                    1.0 * sc, txt_color_fg, 1, cv2.LINE_AA)

    # Small text.
    Ht = int(18 * sc)  # text height
    small_text = timer.print(small_text=[])
    for i, t in enumerate(reversed(small_text)):
        cv2.putText(out, t, (int(8 * sc), int(H - Ht * (i + .6))), cv2.FONT_HERSHEY_DUPLEX,
                    0.5 * sc, txt_color_bg, 2, cv2.LINE_AA)
        cv2.putText(out, t, (int(8 * sc), int(H - Ht * (i + .6))), cv2.FONT_HERSHEY_DUPLEX,
                    0.5 * sc, txt_color_fg, 1, cv2.LINE_AA)

    save_dir = os.path.join(path, 'res')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "{}_{}.png".format(matchMethod, kptsMethod))
    cv2.imwrite(save_path, out)

    return save_path, True
