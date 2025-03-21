"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/16 09:33
Project    : FeatureMatchingBackend
FilePath   : utils/load_npy.py
Description:
"""
import numpy as np
with np.load('LoFTR__pose.npz; filename_=UTF-8LoFTR_%E5%AE%A4%E5%86%85_pose.npz', allow_pickle=True) as data:

    print(data['poses'])