"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/12 22:05
Project    : FeatureMatchingBackend
FilePath   : services/detection/Shi_Tomasi.py
Description: 使用 Shi-Tomasi 检测的业务方法
"""
import cv2
import numpy as np


def detection_shi_tomasi(img, maxCorners=1000, qualityLevel=0.01, minDistance=10):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    corners = cv2.goodFeaturesToTrack(gray_img, maxCorners, qualityLevel, minDistance)
    corners = np.int64(corners)
    for i in corners:
        x, y = i.ravel()
        cv2.circle(img, (x, y), 3, (0, 0, 255), -1)

    return img, corners.shape[0], corners
