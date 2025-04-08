"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/3/10 08:20
Project    : FeatureMatchingBackend
FilePath   : apis/mosaic.py
Description: 图像拼接接口
"""
import datetime
import os
import shutil
import uuid

from flask import Blueprint, request, current_app, after_this_request, send_file
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

from models import User, Mosaic, UploadData, db
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
        startTime = datetime.datetime.now()
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
        save_path, ret = mosaic_pair(path, leftpath, rightpath, cls, kptMethod, matchMethod, scene, scale)

        if not ret:
            return res(300, msg='图像拼接失败', data='检测到匹配对太少')

        save_path_url = save_path_url + os.path.basename(save_path)
        endTime = datetime.datetime.now()
        mosaicTimes = (endTime - startTime).microseconds
        return res(200, msg='图像拼接成功', data={
            'save_path': save_path,
            'save_path_url': save_path_url,
            'mosaicTimes': mosaicTimes,
        })
    except Exception as e:
        return res(500, msg='图像拼接失败', data=str(e))


@mosaic_api.post('/download')
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


@mosaic_api.post('/record')
@jwt_required()
def add_record():
    try:
        username = request.json.get('username')
        user = User.query.filter_by(username=username).first()

        algorithm_type = request.json.get('algorithm_type')
        algorithm = request.json.get('algorithm')
        scene = request.json.get('scene')
        elapsed_time = request.json.get('elapsed_time')
        save_path = request.json.get('save_path')
        save_path_url = request.json.get('save_path_url')
        save_matches_path = request.json.get('save_matches_path')
        save_poses_path = request.json.get('save_poses_path')
        path = request.json.get('path')
        left_url = request.json.get('left_url')
        right_url = request.json.get('right_url')

        data = UploadData(path=path, left_url=left_url, right_url=right_url)
        data.generate_id()
        db.session.add(data)
        db.session.commit()

        mosaic = Mosaic(user_id=user.id, data_id=data.id, algorithm_type=algorithm_type,
                            algorithm=algorithm, scene=scene, elapsed_time=elapsed_time,
                            save_path=save_path, save_path_url=save_path_url)

        mosaic.generate_id()
        mosaic.set_record_date()
        db.session.add(mosaic)
        db.session.commit()
        return res(200, '已添加记录', data='可以在用户功能模块中查找本次记录')

    except Exception as e:
        db.session.rollback()
        return res(500, '添加记录失败', data=str(e))


# 记录 查条数
@mosaic_api.get('/total/<string:user_id>')
@jwt_required()
def get_users_total(user_id):
    try:
        mosaics_num = Mosaic.query.order_by(Mosaic.record_date).filter_by(user_id=user_id).count()
        if mosaics_num is None:
            return res(300, '查询失败', '没有记录信息')
        else:
            return res(200, '查询成功', data=mosaics_num)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@mosaic_api.get('/<string:user_id>/<int:pageSize>/<int:page>')
@jwt_required()
def get_records(user_id, pageSize, page):
    try:
        offset = pageSize * (page - 1)
        records = Mosaic.query.order_by(Mosaic.record_date.desc()).filter_by(user_id=user_id).offset(
            offset).limit(pageSize).all()
        if records is None:
            return res(300, '查询失败', '没有记录信息')
        else:
            resList = []
            for record in records:
                r = record.to_json()
                data = UploadData.query.get(record.data_id)
                r['left_url'] = data.left_url
                r['right_url'] = data.right_url
                resList.append(r)
            return res(200, '查询成功', data=resList)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@mosaic_api.delete('/<string:id>/<string:user_id>')
@jwt_required()
def delete_record(id, user_id):
    try:
        mosaic = Mosaic.query.filter_by(id=id, user_id=user_id).first()

        data_id = mosaic.data_id

        data = UploadData.query.get(data_id)
        path = data.path
        res_dir = os.path.join(path, 'res')

        if mosaic.algorithm_type == '稀疏':
            if mosaic.algorithm != 'SuperGlue_SuperPoint':
                viz = os.path.join(res_dir, mosaic.algorithm + '.png')
            else:
                viz = os.path.join(res_dir, mosaic.algorithm + '_' + mosaic.scene +  '.png')
        else:
            viz = os.path.join(res_dir, mosaic.algorithm + '_' + mosaic.scene + '.png')

        if os.path.exists(viz) and os.path.isfile(viz):
            os.remove(viz)

        if os.path.exists(res_dir) and os.listdir(res_dir).__len__() == 0:
            shutil.rmtree(path)

        db.session.delete(mosaic)
        db.session.commit()
        return res(200, '删除成功')
    except Exception as e:
        return res(500, '删除失败', data=str(e))


@mosaic_api.delete('/')
@jwt_required()
def delete_some_records():
    try:
        deleteIds = request.json.get('deleteIds')
        user_id = request.json.get('user_id')
        for id in deleteIds:
            mosaic = Mosaic.query.filter_by(id=id, user_id=user_id).first()

            data_id = mosaic.data_id

            data = UploadData.query.get(data_id)
            path = data.path
            res_dir = os.path.join(path, 'res')

            if mosaic.algorithm_type == '稀疏':
                if mosaic.algorithm != 'SuperGlue_SuperPoint':
                    viz = os.path.join(res_dir, mosaic.algorithm + '.png')
                else:
                    viz = os.path.join(res_dir, mosaic.algorithm + '_' + mosaic.scene + '.png')
            else:
                viz = os.path.join(res_dir, mosaic.algorithm + '_' + mosaic.scene + '.png')

            if os.path.exists(viz) and os.path.isfile(viz):
                os.remove(viz)

            if os.path.exists(res_dir) and os.listdir(res_dir).__len__() == 0:
                shutil.rmtree(path)

            db.session.delete(mosaic)
            db.session.commit()
        return res(code=200, msg='批量删除成功')
    except Exception as e:
        return res(code='500', msg='批量删除失败', data=str(e))