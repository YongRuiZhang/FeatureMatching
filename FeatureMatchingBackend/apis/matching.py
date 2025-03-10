"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/25 17:19
Project    : FeatureMatchingBackend
FilePath   : apis/matching.py
Description:
"""
import os
import uuid

from flask import Blueprint, request
from flask import current_app
from werkzeug.utils import secure_filename

from services.matching import LoFTR, SuperGlue, BF, FLANN
from utils.Res import res
from utils.checkFileType import allowed_pic_file

matching_api = Blueprint('matching_api', __name__)


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
            print(uid, dir_path)
            if uid == '' or uid is None:  # 无目录，创建目录
                uid = str(uuid.uuid4())

                static_folder = current_app.static_folder
                dir_path = os.path.join(static_folder, "matching")
                os.makedirs(dir_path, exist_ok=True)
                dir_path = os.path.join(dir_path, uid)
                os.makedirs(dir_path, exist_ok=True)

            file_path = os.path.join(dir_path, filename)
            file_path_url = current_app.root_path + "/src/assets/matching/" + uid + '/' + filename


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


@matching_api.post('image')
def matching_image():
    try:
        path = request.json.get('path')
        dir_name = request.json.get('dir_name')
        leftpath = request.json.get('leftpath')
        rightpath = request.json.get('rightpath')
        form = request.json.get('form')

        save_path_url = current_app.root_path + "/src/assets/matching/" + dir_name + '/res/'

        cls = form['class']
        if cls == '稀疏':
            kptMethod = form['kptmethod']
            matchMethod = form['matchmethod']
            if matchMethod == 'SuperGlue':
                scene = form['scene']
                # save_path = SuperGlue.matching_images(path, scene)
            elif matchMethod == 'LoFTR':
                scene = form['scene']
            elif matchMethod == 'BF':
                pass
                # save_path = BF.matching_BF_images(path, kptMethod)
            elif matchMethod == 'FLANN':
                save_path = FLANN.matching_FLANN_pair(path, leftpath, rightpath, kptMethod)
        elif cls == '半稀疏':
            matchMethod = form['matchmethod']
            scene = form['scene']
            # save_path = LoFTR.withoutKpts_images(path, scene)

        save_path_url = save_path_url + os.path.basename(save_path)
        return res(200, msg='特征匹配成功', data={'save_path': save_path, 'save_path_url': save_path_url})
    except Exception as e:
        return res(code='500', msg='特征匹配失败', data=str(e))

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
                file_path_url = current_app.root_path + "/src/assets/matching/" + uid + '/' + filename

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


@matching_api.delete('/upload_images')
def delete_images():
    try:
        path = request.json.get('path')
        dir_name = request.json.get('dir_name')
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


@matching_api.post('/images')
def matching_images():
    try:
        path = request.json.get('path')
        dir_name = request.json.get('dir_name')
        form = request.json.get('form')
        fix = form['fix']
        if fix == '首张作为基准':
            fix = True
        else:
            fix = False

        save_path_url = current_app.root_path + "/src/assets/matching/" + dir_name + '/res/'

        cls = form['class']
        if cls == '稀疏':
            kptMethod = form['kptmethod']
            matchMethod = form['matchmethod']
            if matchMethod == 'SuperGlue':
                scene = form['scene']
                save_path = SuperGlue.matching_images(path, scene, fix)
            elif matchMethod == 'LoFTR':
                scene = form['scene']
            elif matchMethod == 'BF':
                save_path = BF.matching_BF_images(path, kptMethod, fix)
            elif matchMethod == 'FLANN':
                save_path = FLANN.matching_FLANN_images(path, kptMethod, fix)
        elif cls == '半稀疏':
            matchMethod = form['matchmethod']
            scene = form['scene']
            save_path = LoFTR.withoutKpts_images(path, scene, fix)

        save_path_url = save_path_url + os.path.basename(save_path)
        return res(200, msg='特征匹配成功', data={'save_path': save_path, 'save_path_url': save_path_url})
    except Exception as e:
        return res(code='500', msg='特征匹配失败', data=str(e))
