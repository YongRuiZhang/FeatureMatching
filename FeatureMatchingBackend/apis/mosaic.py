"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/10 08:20
Project    : FeatureMatchingBackend
FilePath   : apis/mosaic.py
Description: 图像拼接接口
"""
import os
import uuid

import cv2
from flask import Blueprint, request, current_app
from werkzeug.utils import secure_filename

from services.mosaic.mosaic import mosaic_pair
from utils.Res import res
from utils.checkFileType import allowed_pic_file

mosaic_api = Blueprint('mosaic', __name__, url_prefix='/mosaic')


@mosaic_api.post('/upload_image')
def upload_image():
    try:
        file = request.files['file']
        filename = secure_filename(file.filename)

        if not file or not allowed_pic_file(filename):
            return res(code='300', msg='图片上传失败', data='不允许的图片类型')
        else:
            uid = request.form.get('uid')
            dir_path = request.form.get('dir_path')

            if uid == '' or uid is None:  # 无目录，创建目录
                uid = str(uuid.uuid4())

                static_folder = current_app.static_folder
                dir_path = os.path.join(static_folder, "mosaic")
                os.makedirs(dir_path, exist_ok=True)
                dir_path = os.path.join(dir_path, "pair")
                os.makedirs(dir_path, exist_ok=True)
                dir_path = os.path.join(dir_path, uid)
                os.makedirs(dir_path, exist_ok=True)

            file_path = os.path.join(dir_path, filename)
            file_path_url = current_app.root_path + "/src/assets/mosaic/pair/" + uid + '/' + filename

            # 文件保存
            file.save(file_path, buffer_size=1000000000)

            # 返回信息
            info = {
                'filepath': file_path,
                'filepath_url': file_path_url,
                'uid': uid,
                'dir_path': dir_path,
            }
            return res(msg='上传成功', data=info)
    except Exception as e:
        return res(code='500', msg='图片上传失败', data=str(e))


@mosaic_api.post('/')
def mosaic():
    try:
        path = request.json.get('path')
        dir_name = request.json.get('dir_name')
        leftpath = request.json.get('leftpath')
        rightpath = request.json.get('rightpath')
        form = request.json.get('form')

        save_path_url = current_app.root_path + "/src/assets/mosaic/pair/" + dir_name + '/res/'

        cls = form['class']
        kptMethod = form['kptmethod']
        matchMethod = form['matchmethod']
        scene = form['scene']
        scale = form['scale']
        print(path, leftpath, rightpath, cls, kptMethod, matchMethod, scene, scale)
        save_path, ret = mosaic_pair(path, leftpath, rightpath, cls, kptMethod, matchMethod, scene, scale)

        if not ret:
            return res(300, msg='图像拼接失败', data='检测到匹配对太少')

        save_path_url = save_path_url + os.path.basename(save_path)
        return res(200, msg='图像拼接成功', data={'save_path': save_path, 'save_path_url': save_path_url})
    except Exception as e:
        return res(500, msg='图像拼接失败', data=str(e))
