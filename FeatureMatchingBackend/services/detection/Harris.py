"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/11 11:53
Project    : FeatureMatchingBackend
FilePath   : services/detection/Harris.py
Description:  使用 Harris 检测的业务方法
"""
import cv2
import numpy as np


def detection_Harris(img, blockSize=2, ksize=3, k=0.04):
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    dst = cv2.cornerHarris(gray_img, blockSize, ksize, k)

    threshold = 0.02 * dst.max()
    corners = dst > threshold
    corner_coords = np.argwhere(corners)
    img[corners] = [0, 0, 255]

    num_corners = len(corner_coords)

    return img, num_corners, corner_coords
