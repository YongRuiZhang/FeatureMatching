"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/25 17:19
Project    : FeatureMatchingBackend
FilePath   : apis/matching.py
Description:
"""
import json
import os
import shutil
import uuid
import datetime

import numpy as np
from flask import Blueprint, request, after_this_request, send_file
from flask import current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from models import User, Matching, UploadData, db
from services.matching import LoFTR, SuperGlue, BF, FLANN, ASpanFormer, DKM
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
        startTime = datetime.datetime.now()
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
        config = request.json.get('config')

        save_path_url = current_app.root_path + "/src/assets/matching/pair/" + dir_name + '/res/'

        cls = form['class']
        if cls == '稀疏':
            kptMethod = form['kptmethod']
            matchMethod = form['matchmethod']
            if matchMethod == 'SuperGlue':
                scene = config['scene']
                save_path, save_matches_path, save_poses_path = SuperGlue.matching_pair(path, leftpath, rightpath, K,
                                                                                        scene)
            elif matchMethod == 'LoFTR':
                scene = config['scene']
            elif matchMethod == 'BF':
                save_path, save_matches_path, save_poses_path = BF.matching_BF_pair(path, leftpath, rightpath,
                                                                                    kptMethod, K)
            elif matchMethod == 'FLANN':
                save_path, save_matches_path, save_poses_path = FLANN.matching_FLANN_pair(path, leftpath, rightpath,
                                                                                          kptMethod, K)
        elif cls == '半稀疏':
            matchMethod = form['matchmethod']
            if matchMethod == 'LoFTR':
                scene = config['scene']
                save_path, save_matches_path, save_poses_path = LoFTR.withoutKpts_pair(path, leftpath, rightpath, K,
                                                                                       scene)
            elif matchMethod == 'ASpanFormer':
                scene = config['scene']
                save_path, save_matches_path, save_poses_path = ASpanFormer.matching_pair(path, leftpath, rightpath, K,
                                                                                          scene)
        elif cls == '稠密':
            matchMethod = form['matchmethod']
            if matchMethod == 'DKM':
                scene = config['scene']
                save_path, save_matches_path, save_poses_path = DKM.matching_pair(path, leftpath, rightpath, K,
                                                                                  scene)

        save_path_url = save_path_url + os.path.basename(save_path)

        endTime = datetime.datetime.now()
        matchingTimes = (endTime - startTime).microseconds
        return res(200, msg='特征匹配成功', data={
            'save_path': save_path,
            'save_path_url': save_path_url,
            'save_matches_path': save_matches_path,
            'save_poses_path': save_poses_path,
            'matchingTimes': matchingTimes,
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
                info['files'].append(file_path_url)

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
        startTime = datetime.datetime.now()
        K = np.array([
            [1978.06, 0., 540.],
            [0., 1978.06, 960.],
            [0., 0., 1.]
        ])

        path = request.json.get('path')
        dir_name = request.json.get('dir_name')
        origin_type = request.json.get('type')
        form = request.json.get('form')
        config = request.json.get('config')
        skip = config['skip']
        fps = config['fps']
        fix = config['fix']
        if fix == '首张作为基准':
            fix = True
        else:
            fix = False

        if origin_type == '多张图片':
            save_path_url = current_app.root_path + "/src/assets/matching/images/" + dir_name + '/res/'
        else:
            save_path_url = current_app.root_path + "/src/assets/matching/video/" + dir_name + '/res/'

        cls = form['class']
        if cls == '稀疏':
            kptMethod = form['kptmethod']
            matchMethod = form['matchmethod']
            if matchMethod == 'SuperGlue':
                scene = config['scene']
                save_path, save_matches_path, save_poses_path = SuperGlue.matching_images(path, scene, K, fix, origin_type,
                                                                                          skip=skip, fps=fps)
            elif matchMethod == 'LoFTR':
                scene = config['scene']
            elif matchMethod == 'BF':
                save_path, save_matches_path, save_poses_path = BF.matching_BF_images(path, kptMethod, K, fix, origin_type,
                                                                                      skip=skip, fps=fps)
            elif matchMethod == 'FLANN':
                save_path, save_matches_path, save_poses_path = FLANN.matching_FLANN_images(path, kptMethod, K, fix,
                                                                                            origin_type, skip=skip, fps=fps)
        elif cls == '半稀疏':
            matchMethod = form['matchmethod']
            if matchMethod == 'LoFTR':
                scene = config['scene']
                save_path, save_matches_path, save_poses_path = LoFTR.withoutKpts_images(path, K, scene, fix, origin_type,
                                                                                         skip=skip, fps=fps)
            elif matchMethod == 'ASpanFormer':
                scene = config['scene']
                save_path, save_matches_path, save_poses_path = ASpanFormer.matching_images(path, K, scene, fix, origin_type,
                                                                                            skip=skip, fps=fps)
        elif cls == '稠密':
            matchMethod = form['matchmethod']
            if matchMethod == 'DKM':
                scene = config['scene']
                save_path, save_matches_path, save_poses_path = DKM.matching_images(path, K, scene, fix, origin_type,
                                                                                    skip=skip, fps=fps)

        save_path_url = save_path_url + os.path.basename(save_path)

        endTime = datetime.datetime.now()
        matchingTimes = (endTime - startTime).microseconds
        return res(200, msg='特征匹配成功', data={
            'save_path': save_path,
            'save_path_url': save_path_url,
            'save_matches_path': save_matches_path,
            'save_poses_path': save_poses_path,
            'matchingTimes': matchingTimes,
        })
    except Exception as e:
        return res(code='500', msg='特征匹配失败', data=str(e))


@matching_api.post('/download')
def download():
    try:
        dfilepath = request.json.get('dfilepath')
        download_name = os.path.basename(dfilepath)

        if not os.path.exists(dfilepath):
            return res(code='300', msg='下载失败', data="文件找不到了")

        @after_this_request
        def add_headers(response):
            response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response

        return send_file(dfilepath, as_attachment=True, download_name=download_name)
    except Exception as e:
        return res(code='500', msg='下载失败', data=str(e))


# =========== 记录
# 增
@matching_api.post('/record')
@jwt_required()
def add_record():
    try:
        username = request.json.get('username')
        user = User.query.filter_by(username=username).first()

        origin_type = request.json.get('origin_type')
        algorithm_type = request.json.get('algorithm_type')
        algorithm = request.json.get('algorithm')
        config = request.json.get('config')
        elapsed_time = request.json.get('elapsed_time')
        save_path = request.json.get('save_path')
        save_path_url = request.json.get('save_path_url')
        save_matches_path = request.json.get('save_matches_path')
        save_poses_path = request.json.get('save_poses_path')
        if origin_type == '两张图片':
            path = request.json.get('path')
            left_url = request.json.get('left_url')
            right_url = request.json.get('right_url')
            data = UploadData(path=path, left_url=left_url, right_url=right_url)
        elif origin_type == '多张图片':
            path = request.json.get('path')
            data = UploadData(path=path)
        elif origin_type == '视频':
            path = request.json.get('path')
            video_url = request.json.get('video_url')
            data = UploadData(path=path, video_url=video_url)

        data.generate_id()
        db.session.add(data)
        db.session.commit()

        matching = Matching(user_id=user.id, data_id=data.id, origin_type=origin_type, algorithm_type=algorithm_type,
                            algorithm=algorithm, config=config, elapsed_time=elapsed_time,
                            save_path=save_path, save_path_url=save_path_url,
                            save_matches_path=save_matches_path, save_poses_path=save_poses_path)

        matching.generate_id()
        matching.set_record_date()
        db.session.add(matching)
        db.session.commit()
        return res(200, '已添加记录', data='可以在用户功能模块中查找本次记录')

    except Exception as e:
        db.session.rollback()
        return res(500, '添加记录失败', data=str(e))


# 记录 查条数
@matching_api.get('/total/<string:user_id>')
@jwt_required()
def get_users_total(user_id):
    try:
        matchings_num = Matching.query.order_by(Matching.record_date).filter_by(user_id=user_id).count()
        if matchings_num is None:
            return res(300, '查询失败', '没有记录信息')
        else:
            return res(200, '查询成功', data=matchings_num)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@matching_api.get('/<string:user_id>/<int:pageSize>/<int:page>')
@jwt_required()
def get_records(user_id, pageSize, page):
    try:
        offset = pageSize * (page - 1)
        records = Matching.query.order_by(Matching.record_date.desc()).filter_by(user_id=user_id).offset(
            offset).limit(pageSize).all()
        if records is None:
            return res(300, '查询失败', '没有记录信息')
        else:
            resList = []
            for record in records:
                r = record.to_json()
                data = UploadData.query.get(record.data_id)
                if record.origin_type == '两张图片':
                    r['viz_path'] = json.dumps([data.left_url, data.right_url])
                elif record.origin_type == '多张图片':
                    directory = data.path
                    dirname = os.path.basename(directory)
                    if not os.path.exists(directory):
                        return res(300, '查询失败', data='有数据源确缺失')

                    picture_files = []
                    for entry in os.listdir(directory):
                        entry_path = os.path.join(directory, entry)
                        if os.path.isfile(entry_path):
                            if allowed_pic_file(entry):
                                picture_files.append(
                                    current_app.root_path + "/src/assets/matching/images/" + dirname + "/" + entry)
                    r['viz_path'] = json.dumps(picture_files)
                elif record.origin_type == '视频':
                    r['viz_path'] = json.dumps(data.video_url)
                resList.append(r)
            return res(200, '查询成功', data=resList)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@matching_api.delete('/<string:id>/<string:user_id>')
@jwt_required()
def delete_record(id, user_id):
    try:
        matching = Matching.query.filter_by(id=id, user_id=user_id).first()

        data_id = matching.data_id
        config = json.loads(matching.config)

        data = UploadData.query.get(data_id)
        path = data.path
        res_dir = os.path.join(path, 'res')

        if matching.algorithm_type == '稀疏':
            if matching.algorithm != 'SuperGlue_SuperPoint':
                if matching.origin_type == '两张图片':
                    viz = os.path.join(res_dir, matching.algorithm + '_viz.png')
                else:
                    viz = os.path.join(res_dir, matching.algorithm + '_viz.mp4')
                matches = os.path.join(res_dir, matching.algorithm + '_matches.npz')
                poses = os.path.join(res_dir, matching.algorithm + '_pose.npz')
            else:
                if config['scene'] == '室内':
                    scene = 'indoor'
                else:
                    scene = 'outdoor'
                if matching.origin_type == '两张图片':
                    viz = os.path.join(res_dir, matching.algorithm + '_' + scene + '_viz.png')
                else:
                    viz = os.path.join(res_dir, matching.algorithm + '_' + scene + '_viz.mp4')
                matches = os.path.join(res_dir, matching.algorithm + '_' + scene + '_matches.npz')
                poses = os.path.join(res_dir, matching.algorithm + '_' + scene + '_pose.npz')
        else:
            if matching.algorithm == 'ASpanFormer':
                if config['scene'] == '室内':
                    scene = 'indoor'
                else:
                    scene = 'outdoor'
                if matching.origin_type == '两张图片':
                    viz = os.path.join(res_dir, matching.algorithm + '_' + scene + '_viz.png')
                else:
                    viz = os.path.join(res_dir, matching.algorithm + '_' + scene + '_viz.mp4')
                matches = os.path.join(res_dir, matching.algorithm + '_' + scene + '_matches.npz')
                poses = os.path.join(res_dir, matching.algorithm + '_' + scene + '_pose.npz')
            else:
                if matching.origin_type == '两张图片':
                    viz = os.path.join(res_dir, matching.algorithm + '_' + config['scene'] + '_viz.png')
                else:
                    viz = os.path.join(res_dir, matching.algorithm + '_' + config['scene'] + '_viz.mp4')
                matches = os.path.join(res_dir, matching.algorithm + '_' + config['scene'] + '_matches.npz')
                poses = os.path.join(res_dir, matching.algorithm + '_' + config['scene'] + '_pose.npz')

        if os.path.exists(viz) and os.path.isfile(viz):
            os.remove(viz)
        if os.path.exists(matches) and os.path.isfile(matches):
            os.remove(matches)
        if os.path.exists(poses) and os.path.isfile(poses):
            os.remove(poses)

        if os.path.exists(res_dir) and os.listdir(res_dir).__len__() == 0:
            shutil.rmtree(path)

        db.session.delete(matching)
        db.session.commit()
        return res(200, '删除成功')
    except Exception as e:
        return res(500, '删除失败', data=str(e))


@matching_api.delete('/')
@jwt_required()
def delete_some_records():
    try:
        deleteIds = request.json.get('deleteIds')
        user_id = request.json.get('user_id')
        for id in deleteIds:
            matching = Matching.query.filter_by(id=id, user_id=user_id).first()
            data_id = matching.data_id
            config = json.loads(matching.config)

            data = UploadData.query.get(data_id)
            path = data.path
            res_dir = os.path.join(path, 'res')

            if matching.algorithm_type == '稀疏':
                if matching.algorithm != 'SuperGlue_SuperPoint':
                    if matching.origin_type == '两张图片':
                        viz = os.path.join(res_dir, matching.algorithm + '_viz.png')
                    else:
                        viz = os.path.join(res_dir, matching.algorithm + '_viz.mp4')
                    matches = os.path.join(res_dir, matching.algorithm + '_matches.npz')
                    poses = os.path.join(res_dir, matching.algorithm + '_pose.npz')
                else:
                    if config['scene'] == '室内':
                        scene = 'indoor'
                    else:
                        scene = 'outdoor'
                    if matching.origin_type == '两张图片':
                        viz = os.path.join(res_dir, matching.algorithm + '_' + scene + '_viz.png')
                    else:
                        viz = os.path.join(res_dir, matching.algorithm + '_' + scene + '_viz.mp4')
                    matches = os.path.join(res_dir, matching.algorithm + '_' + scene + '_matches.npz')
                    poses = os.path.join(res_dir, matching.algorithm + '_' + scene + '_pose.npz')
            else:
                if matching.algorithm == 'ASpanFormer':
                    if config['scene'] == '室内':
                        scene = 'indoor'
                    else:
                        scene = 'outdoor'
                    if matching.origin_type == '两张图片':
                        viz = os.path.join(res_dir, matching.algorithm + '_' + scene + '_viz.png')
                    else:
                        viz = os.path.join(res_dir, matching.algorithm + '_' + scene + '_viz.mp4')
                    matches = os.path.join(res_dir, matching.algorithm + '_' + scene + '_matches.npz')
                    poses = os.path.join(res_dir, matching.algorithm + '_' + scene + '_pose.npz')
                else:
                    if matching.origin_type == '两张图片':
                        viz = os.path.join(res_dir, matching.algorithm + '_' + config['scene'] + '_viz.png')
                    else:
                        viz = os.path.join(res_dir, matching.algorithm + '_' + config['scene'] + '_viz.mp4')
                    matches = os.path.join(res_dir, matching.algorithm + '_' + config['scene'] + '_matches.npz')
                    poses = os.path.join(res_dir, matching.algorithm + '_' + config['scene'] + '_pose.npz')

            if os.path.exists(viz) and os.path.isfile(viz):
                os.remove(viz)
            if os.path.exists(matches) and os.path.isfile(matches):
                os.remove(matches)
            if os.path.exists(poses) and os.path.isfile(poses):
                os.remove(poses)

            if os.path.exists(res_dir) and os.listdir(res_dir).__len__() == 0:
                shutil.rmtree(path)

            db.session.delete(matching)
            db.session.commit()
        return res(code=200, msg='批量删除成功')
    except Exception as e:
        return res(code='500', msg='批量删除失败', data=str(e))
