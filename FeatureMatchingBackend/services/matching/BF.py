"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/8 10:55
Project    : FeatureMatchingBackend
FilePath   : services/matching/BF.py
Description: BF 实现特征匹配的业务方法
"""
import os

import cv2
import imageio
import numpy as np

from services.detection.ORB import detection_ORB
from services.detection.SIFT import detection_SIFT
from services.detection.SuperPoint import detection_SuperPoint
from utils.matching_utils import (AverageTimer, VideoStreamer, process_resize)


def detection_BF(frame1, frame2, kptsMethod):
    if kptsMethod == 'SIFT':
        _, _, _, des1, kpts1 = detection_SIFT(frame1)
        _, _, _, des2, kpts2 = detection_SIFT(frame2)
    elif kptsMethod == 'ORB':
        _, _, _, des1, kpts1 = detection_ORB(frame1)
        _, _, _, des2, kpts2 = detection_ORB(frame2)
    elif kptsMethod == 'SuperPoint':
        _, _, kpts1, des1, _ = detection_SuperPoint(frame1)
        _, _, kpts2, des2, _ = detection_SuperPoint(frame2)
        kpts1_list = []
        for i in range(kpts1.shape[0]):
            x = kpts1[i, 0]
            y = kpts1[i, 1]
            keypoint = cv2.KeyPoint(x, y, 1)
            kpts1_list.append(keypoint)
        kpts1 = kpts1_list
        kpts2_list = []
        for i in range(kpts2.shape[0]):
            x = kpts2[i, 0]
            y = kpts2[i, 1]
            keypoint = cv2.KeyPoint(x, y, 1)
            kpts2_list.append(keypoint)
        kpts2 = kpts2_list
        des1 = des1.astype(np.float32).T
        des2 = des2.astype(np.float32).T

    return kpts1, kpts2, des1, des2


def matching_BF(bf, des1, des2):
    return bf.match(des1, des2)


def draw_matching(frame1, frame2, kpts1, kpts2, matches, kptsMethod, small_text):
    out = cv2.drawMatches(frame1, kpts1, frame2, kpts2, matches, None)

    H0, _ = frame1.shape
    H1, _ = frame2.shape
    H = max(H0, H1)
    sc = min(H / 640., 2.0)
    Ht = int(30 * sc)  # text height
    txt_color_fg = (255, 255, 255)
    txt_color_bg = (0, 0, 0)
    text = [
        'BF_{}'.format(kptsMethod),
        'kpts:{}:{}'.format(len(kpts1), len(kpts2)),
        'Matches: {}'.format(len(matches)),
    ]
    for i, t in enumerate(text):
        cv2.putText(out, t, (int(8 * sc), Ht * (i + 1)), cv2.FONT_HERSHEY_DUPLEX,
                    1.0 * sc, txt_color_bg, 2, cv2.LINE_AA)
        cv2.putText(out, t, (int(8 * sc), Ht * (i + 1)), cv2.FONT_HERSHEY_DUPLEX,
                    1.0 * sc, txt_color_fg, 1, cv2.LINE_AA)

    # Small text.
    Ht = int(18 * sc)  # text height
    for i, t in enumerate(reversed(small_text)):
        cv2.putText(out, t, (int(8 * sc), int(H - Ht * (i + .6))), cv2.FONT_HERSHEY_DUPLEX,
                    0.5 * sc, txt_color_bg, 2, cv2.LINE_AA)
        cv2.putText(out, t, (int(8 * sc), int(H - Ht * (i + .6))), cv2.FONT_HERSHEY_DUPLEX,
                    0.5 * sc, txt_color_fg, 1, cv2.LINE_AA)

    return out


def matching_BF_pair(path, img1_path, img2_path, kptsMethod, is_save=True, is_process=True, timer=None):
    bf = cv2.BFMatcher(cv2.NORM_L2, True)

    if timer is None:
        timer = AverageTimer()
    if is_process:
        img1 = cv2.imread(img1_path, 0)
        img2 = cv2.imread(img2_path, 0)
        w, h = img1.shape[1], img1.shape[0]
        w_new, h_new = process_resize(w, h, [640, 480])
        img1 = cv2.resize(img1, (w_new, h_new), interpolation=cv2.INTER_AREA)
        img2 = cv2.resize(img2, (w_new, h_new), interpolation=cv2.INTER_AREA)
    else:
        img1 = img1_path
        img2 = img2_path
    timer.update('process images')

    kpts1, kpts2, des1, des2 = detection_BF(img1, img2, kptsMethod)
    timer.update('detect')

    matches = matching_BF(bf, des1, des2)
    timer.update('matching')

    if is_save:
        small_text = timer.print(small_text=[])
        out = draw_matching(img1, img2, kpts1, kpts2, matches, kptsMethod, small_text)

        save_dir = os.path.join(path, 'res')
        os.makedirs(save_dir, exist_ok=True)
        save_path = os.path.join(save_dir, "BF_{}.png".format(kptsMethod))
        cv2.imwrite(save_path, out)

        return save_path
    else:
        return kpts1, kpts2, des1, des2, matches


def matching_BF_images(path, kptsMethod, fix=True, type='多张图片', image_glob=None, skip=1, max_length=1000000, resize=None, fps=1):
    if image_glob is None:
        image_glob = ['*.png', '*.jpg', '*.jpeg']
    if resize is None:
        resize = [640, 480]

    bf = cv2.BFMatcher(cv2.NORM_L2, True)

    if type == '多张图片':
        vs = VideoStreamer(path, resize=resize,
                       skip=skip, image_glob=image_glob, max_length=max_length)
    elif type == '视频':
        file_names = os.listdir(path)
        file_path = \
        [os.path.join(path, file_name) for file_name in file_names if os.path.isfile(os.path.join(path, file_name))][0]
        vs = VideoStreamer(file_path, resize=resize,
                           skip=skip, image_glob=image_glob, max_length=max_length)
    frame, _ = vs.next_frame()
    last_frame = frame
    last_image_id = 0

    matching_images = []

    timer = AverageTimer()

    while True:
        frame, ret = vs.next_frame()
        if not ret:
            print('Finished')
            break
        timer.update('process images')
        stem0, stem1 = last_image_id, vs.i - 1

        kpts1, kpts2, des1, des2 = detection_BF(last_frame, frame, kptsMethod)
        timer.update('detect')

        matches = matching_BF(bf, des1, des2)
        timer.update('matching')

        small_text = timer.print(small_text=[])
        out = draw_matching(last_frame, frame, kpts1, kpts2, matches, kptsMethod, small_text)

        matching_images.append(cv2.cvtColor(out, cv2.COLOR_BGR2RGB))

        if not fix:
            last_frame = frame

    save_dir = os.path.join(path, 'res')
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, "BF_{}.mp4".format(kptsMethod))
    imageio.mimsave(save_path, matching_images, format="MP4", fps=fps)

    return save_path