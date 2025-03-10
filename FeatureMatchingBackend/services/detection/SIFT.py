"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/12 22:08
Project    : FeatureMatchingBackend
FilePath   : services/detection/SIFT.py
Description: 使用 SIFT 检测的业务方法
"""

import cv2
import numpy as np


def detection_SIFT(img):
    if len(img.shape) > 2:
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray_img = img

    sift = cv2.SIFT_create()
    kpts, des = sift.detectAndCompute(gray_img, None)
    cv2.drawKeypoints(gray_img, kpts, img)

    keypoints = np.array([(kp.pt[0], kp.pt[1], kp.size, kp.angle) for kp in kpts])

    return img, len(keypoints), keypoints, des, kpts
