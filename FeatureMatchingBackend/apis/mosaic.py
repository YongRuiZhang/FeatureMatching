"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/10 08:20
Project    : FeatureMatchingBackend
FilePath   : apis/mosaic.py
Description: 图像拼接接口
"""
import cv2
from flask import Blueprint, request
from services.mosaic import mosaic
from utils.Res import res

mosaic_api = Blueprint('mosaic', __name__, url_prefix='/mosaic')


@mosaic_api.post('/')
def mosaic():
    try:
        image1 = request.json.get('image1')
        image2 = request.json.get('image2')
        kptsMethod = request.json.get('kptsMethod')
        matchMethod = request.json.get('matchMethod')

        img1 = cv2.imread(image1, 0)
        img2 = cv2.imread(image2, 0)

        out = mosaic(img1, img2, kptsMethod=kptsMethod, matchMethod=matchMethod)
        # 保存

        return res(200, msg='图像拼接成功', data={'save_path': '123'})
    except Exception as e:
        return res(500, msg='图像拼接失败',data=str(e))
