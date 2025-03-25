"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/25 17:19
Project    : FeatureMatchingBackend
FilePath   : apis/matching.py
Description:
"""
import os
import time
import uuid

import cv2
import numpy as np
from flask import Blueprint, request, Response, jsonify, after_this_request, send_file
from flask import current_app
from werkzeug.utils import secure_filename

from services.matching import LoFTR, SuperGlue, BF, FLANN, ELoFTR, DKM
from utils.Res import res
from utils.checkFileType import allowed_pic_file, allowed_video_file

matching_api = Blueprint('matching_api', __name__)


# ----------- 图片对 ------------
# 上传
@matching_api.post('/upload_image')
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
                dir_path = os.path.join(static_folder, "matching")
                os.makedirs(dir_path, exist_ok=True)
                dir_path = os.path.join(dir_path, "pair")
                os.makedirs(dir_path, exist_ok=True)
                dir_path = os.path.join(dir_path, uid)
                os.makedirs(dir_path, exist_ok=True)

            file_path = os.path.join(dir_path, filename)
            file_path_url = current_app.root_path + "/src/assets/matching/pair/" + uid + '/' + filename

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


# 匹配
@matching_api.post('/image')
def matching_image():
    try:
        K = np.array([
            [1978.06, 0., 540.],
            [0., 1978.06, 960.],
            [0., 0., 1.]
        ])

        path = request.json.get('path')
        dir_name = request.json.get('dir_name')
        leftpath = request.json.get('leftpath')
        rightpath = request.json.get('rightpath')
        form = request.json.get('form')

        save_path_url = current_app.root_path + "/src/assets/matching/pair/" + dir_name + '/res/'

        cls = form['class']
        if cls == '稀疏':
            kptMethod = form['kptmethod']
            matchMethod = form['matchmethod']
            if matchMethod == 'SuperGlue':
                scene = form['scene']
                save_path, save_matches_path, save_poses_path = SuperGlue.matching_pair(path, leftpath, rightpath, K,
                                                                                        scene)
            elif matchMethod == 'LoFTR':
                scene = form['scene']
            elif matchMethod == 'BF':
                save_path, save_matches_path, save_poses_path = BF.matching_BF_pair(path, leftpath, rightpath,
                                                                                    kptMethod, K)
            elif matchMethod == 'FLANN':
                save_path, save_matches_path, save_poses_path = FLANN.matching_FLANN_pair(path, leftpath, rightpath,
                                                                                          kptMethod, K)
        elif cls == '半稀疏':
            matchMethod = form['matchmethod']
            if matchMethod == 'LoFTR':
                scene = form['scene']
                save_path, save_matches_path, save_poses_path = LoFTR.withoutKpts_pair(path, leftpath, rightpath, K,
                                                                                       scene)
            # if matchMethod == 'ELoFTR':
            #     save_path, save_matches_path, save_poses_path = ELoFTR.matching_pair(path, leftpath, rightpath, K,
            #                                                                          model_type=form['model_type'],
            #                                                                          precision=form['precision'])
        elif cls == '稠密':
            matchMethod = form['matchmethod']
            if matchMethod == 'DKM':
                scene = form['scene']
                save_path, save_matches_path, save_poses_path = DKM.matching_pair(path, leftpath, rightpath, K,
                                                                                        scene)

        save_path_url = save_path_url + os.path.basename(save_path)
        return res(200, msg='特征匹配成功', data={
            'save_path': save_path,
            'save_path_url': save_path_url,
            'save_matches_path': save_matches_path,
            'save_poses_path': save_poses_path
        })
    except Exception as e:
        return res(code='500', msg='特征匹配失败', data=str(e))


# ----------- 多张图片 ----------
# 上传
@matching_api.post('/upload_images')
def upload_images():
    try:
        filelist = request.files.getlist('file')

        if len(filelist) == 0:
            res(code=300, msg='图片上传失败', data='服务器获取到 0 张图片')

        # 构造文件名及文件路径
        uid = str(uuid.uuid4())
        static_folder = current_app.static_folder
        dir_path = os.path.join(static_folder, "matching")
        os.makedirs(dir_path, exist_ok=True)
        dir_path = os.path.join(dir_path, "images")
        os.makedirs(dir_path, exist_ok=True)
        dir_path = os.path.join(dir_path, uid)
        os.makedirs(dir_path, exist_ok=True)

        info = {
            'path': dir_path,
            'dir_name': uid,
            'files': []
        }

        for file in filelist:
            filename = secure_filename(os.path.basename(file.filename))
            if allowed_pic_file(filename):
                file_path = os.path.join(dir_path, filename)
                file_path_url = current_app.root_path + "/src/assets/matching/images/" + uid + '/' + filename

                file.save(file_path, buffer_size=1000000000)

                # 返回信息
                info['files'].append({
                    'file_path': file_path,
                    'file_path_url': file_path_url,
                    'filename': filename
                })

        return res(msg='上传成功', data=info)
    except Exception as e:
        return res(code='500', msg='图片上传失败', data=str(e))


# 删除
@matching_api.delete('/upload_images')
def delete_images():
    try:
        path = request.json.get('path')
        name = request.json.get('name')
        filename = os.path.join(path, name)
        if os.path.exists(filename):
            os.remove(filename)

        remaining_files = os.listdir(path)

        if len(remaining_files) == 0:
            os.rmdir(path)

        return res(msg='删除成功')
    except Exception as e:
        return res(code='500', msg='图片删除失败，建议刷新网页后重试', data=str(e))


# ---------- 视频 ----------
# 上传
@matching_api.post('/upload_video')
def upload_video():
    try:
        file = request.files['file']
        filename = secure_filename(file.filename)

        if not file or not allowed_video_file(filename):
            return res(code='300', msg='图片上传失败', data='不允许的图片类型')
        else:
            uid = str(uuid.uuid4())

            static_folder = current_app.static_folder
            dir_path = os.path.join(static_folder, "matching")
            os.makedirs(dir_path, exist_ok=True)
            dir_path = os.path.join(dir_path, "video")
            os.makedirs(dir_path, exist_ok=True)
            dir_path = os.path.join(dir_path, uid)
            os.makedirs(dir_path, exist_ok=True)

            file_path = os.path.join(dir_path, filename)
            file_path_url = current_app.root_path + "/src/assets/matching/video/" + uid + '/' + filename

            # 文件保存
            file.save(file_path, buffer_size=1000000000)

            # 返回信息
            info = {
                'filepath': file_path,
                'filepath_url': file_path_url,
                'uid': uid,
                'dir_path': dir_path,
            }
            return res(msg='上传视频成功', data=info)
    except Exception as e:
        return res(code='500', msg='视频上传失败', data=str(e))


# 匹配
@matching_api.post('/images')
def matching_images():
    try:
        K = np.array([
            [1978.06, 0., 540.],
            [0., 1978.06, 960.],
            [0., 0., 1.]
        ])

        path = request.json.get('path')
        dir_name = request.json.get('dir_name')
        type = request.json.get('type')
        form = request.json.get('form')
        skip = form['skip']
        fix = form['fix']
        if fix == '首张作为基准':
            fix = True
        else:
            fix = False

        if type == '多张图片':
            save_path_url = current_app.root_path + "/src/assets/matching/images/" + dir_name + '/res/'
        else:
            save_path_url = current_app.root_path + "/src/assets/matching/video/" + dir_name + '/res/'

        cls = form['class']
        if cls == '稀疏':
            kptMethod = form['kptmethod']
            matchMethod = form['matchmethod']
            if matchMethod == 'SuperGlue':
                scene = form['scene']
                save_path, save_matches_path, save_poses_path = SuperGlue.matching_images(path, scene, K, fix, type,
                                                                                          skip=skip)
            elif matchMethod == 'LoFTR':
                scene = form['scene']
            elif matchMethod == 'BF':
                save_path, save_matches_path, save_poses_path = BF.matching_BF_images(path, kptMethod, K, fix, type,
                                                                                      skip=skip)
            elif matchMethod == 'FLANN':
                save_path, save_matches_path, save_poses_path = FLANN.matching_FLANN_images(path, kptMethod, K, fix,
                                                                                            type, skip=skip)
        elif cls == '半稀疏':
            matchMethod = form['matchmethod']
            if matchMethod == 'LoFTR':
                scene = form['scene']
                save_path, save_matches_path, save_poses_path = LoFTR.withoutKpts_images(path, K, scene, fix, type,
                                                                                         skip=skip)
        elif cls == '稠密':
            matchMethod = form['matchmethod']
            if matchMethod == 'DKM':
                scene = form['scene']
                save_path, save_matches_path, save_poses_path = DKM.matching_images(path, K, scene, fix, type,
                                                                                    skip=skip)

        save_path_url = save_path_url + os.path.basename(save_path)
        return res(200, msg='特征匹配成功', data={
            'save_path': save_path,
            'save_path_url': save_path_url,
            'save_matches_path': save_matches_path,
            'save_poses_path': save_poses_path
        })
    except Exception as e:
        return res(code='500', msg='特征匹配失败', data=str(e))


## 实时
CAP = None


def getRealTimeImage():
    global CAP
    CAP = cv2.VideoCapture(0)
    fps = 10
    while True:
        return_value, frame = CAP.read()
        if not return_value:
            break

        # 将原始帧和处理后的帧编码为 JPEG
        _, original_image = cv2.imencode('.jpg', frame)

        # 生成原始帧的 HTTP 响应格式
        original_frame = (
                b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + original_image.tobytes() + b'\r\n'
        )

        yield original_frame
        time.sleep(1 / fps)


@matching_api.route('/video_feed')
def video_feed():
    return Response(getRealTimeImage(), mimetype='multipart/x-mixed-replace; boundary=frame')


@matching_api.delete('/video_feed')
def closeCamera():
    global CAP
    if CAP is not None:
        CAP.release()
        CAP = None
    return res(code='200')


@matching_api.post('/download')
def download():
    try:
        dfilepath = request.json.get('dfilepath')
        print(dfilepath)
        download_name = os.path.basename(dfilepath)
        print(download_name)

        if not os.path.exists(dfilepath):
            return res(code='300', msg='下载失败', data="文件找不到了")

        @after_this_request
        def add_headers(response):
            response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response

        return send_file(dfilepath, as_attachment=True, download_name=download_name)
    except Exception as e:
        return res(code='500', msg='下载失败', data=str(e))
