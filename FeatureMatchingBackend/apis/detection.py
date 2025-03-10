"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/10 09:30
Project    : FeatureMatchingBackend
FilePath   : apis/detection.py
Description: 检测器相关 api
"""
import os
import datetime
import uuid

import cv2
import numpy as np
from flask import Blueprint, request, current_app, send_file, after_this_request
from flask_jwt_extended import jwt_required

from services.detection import Harris, Shi_Tomasi, SIFT, ORB, SuperPoint
from utils.Res import res
from utils.checkFileType import allowed_pic_file
from models import User, Detection, db

detection_api = Blueprint('detection_api', __name__)

RESKPTS = None
FILENAME = ""
RESFILEPATH = ""
RESFILENAME = ""


def init():
    RESKPTS = None
    FILENAME = ""
    RESFILEPATH = ""
    RESFILENAME = ""


@detection_api.post('/upload')
def upload():
    init()
    try:
        global FILENAME
        file = request.files.get('file')

        if not file or not allowed_pic_file(file.filename):
            return res(code='300', msg='图片上传失败', data='不允许的图片类型')
        else:
            static_folder = current_app.static_folder
            dir_path = os.path.join(static_folder, "detection")
            os.makedirs(dir_path, exist_ok=True)

            # 构造文件名及文件路径
            uid = str(uuid.uuid4())
            FILENAME = uid + "_" + file.filename
            file_path = os.path.join(dir_path, FILENAME)
            file_path_url = current_app.root_path + "/src/assets/detection/" + FILENAME

            # 文件保存
            file.save(file_path, buffer_size=1000000000)

            # 返回信息
            info = {
                'originName': file.filename,
                'filename': FILENAME,
                'filepath': file_path,
                'filepath_url': file_path_url,
            }
            return res(msg='上传成功', data=info)
    except Exception as e:
        return res(code='500', msg='图片上传失败', data=str(e))


@detection_api.post('/detect')
def detect():
    try:
        global RESKPTS
        global RESFILEPATH
        global RESFILENAME

        # 获取表单数据
        method = request.form.get('method')
        filename = request.form.get('filename')
        filepath = request.form.get('filepath')

        ALGORITHM = method

        if filepath == "":
            return res(code='300', msg='检测失败', data="未上传图片")

        # 结果路径
        response = {}
        descriptors_path = ''
        scores_path = ''
        static_folder = current_app.static_folder
        dir_path = os.path.join(static_folder, "detection")
        RESFILENAME = "res_{}_".format(method) + filename
        img_path = os.path.join(static_folder, 'detection/img')
        RESFILEPATH = os.path.join(img_path, RESFILENAME)
        resFilePath_url = current_app.root_path + "/src/assets/detection/img/" + RESFILENAME

        kpts_dir_path = os.path.join(static_folder, "detection/kpts")
        os.makedirs(kpts_dir_path, exist_ok=True)
        desc_dir_path = os.path.join(static_folder, "detection/desc")
        os.makedirs(desc_dir_path, exist_ok=True)
        scores_dir_path = os.path.join(static_folder, "detection/scores")
        os.makedirs(scores_dir_path, exist_ok=True)
        filename = RESFILENAME.split(".")[0]
        kpts_file_path = os.path.join(kpts_dir_path, filename + '.npy')
        desc_file_path = os.path.join(desc_dir_path, filename + '.npy')
        scores_file_path = os.path.join(scores_dir_path, filename + '.npy')

        # 图像读取
        img = cv2.imread(filepath)
        height, width = img.shape[:2]

        startTime = datetime.datetime.now()
        # 执行业务
        if method == "Harris":
            blocksize = int(request.form.get('config[blocksize]'))
            ksize = int(request.form.get('config[ksize]'))
            k = float(request.form.get('config[k]'))
            img, num_kpts, RESKPTS = Harris.detection_Harris(img, blocksize, ksize, k)
            descriptors_path = ''
        elif method == "Shi_Tomasi":
            maxCorners = int(request.form.get('config[maxCorners]'))
            qualityLevel = float(request.form.get('config[qualityLevel]'))
            minDistance = float(request.form.get('config[minDistance]'))
            img, num_kpts, RESKPTS = Shi_Tomasi.detection_shi_tomasi(img, maxCorners, qualityLevel, minDistance)
            descriptors_path = ''
        elif method == "SIFT":
            img, num_kpts, RESKPTS, des, _ = SIFT.detection_SIFT(img)

            if not os.path.exists(desc_file_path):
                np.save(desc_file_path, des)
                descriptors_path = desc_file_path
            else:
                descriptors_path = ''
        elif method == "ORB":
            img, num_kpts, RESKPTS, des, _ = ORB.detection_ORB(img)

            if not os.path.exists(desc_file_path):
                np.save(desc_file_path, des)
                print(desc_file_path)
                descriptors_path = desc_file_path
            else:
                descriptors_path = ''
        elif method == "SuperPoint":
            img, num_kpts, RESKPTS, des, scores = SuperPoint.detection_SuperPoint(img)

            if not os.path.exists(desc_file_path):
                np.save(desc_file_path, des)
                descriptors_path = desc_file_path
            else:
                descriptors_path = ''

            if not os.path.exists(scores_file_path):
                np.save(scores_file_path, scores)
                scores_path = scores_file_path
            else:
                scores_path = ''
        else:
            return res(code='300', msg='算法选择错误')

        endTime = datetime.datetime.now()

        # 保存结果
        cv2.imwrite(RESFILEPATH, img)
        if not os.path.exists(kpts_file_path):
            np.save(kpts_file_path, RESKPTS)

        response = {
            'resImagePath': RESFILEPATH,
            'resImagePath_url': resFilePath_url,
            'width': width,
            'height': height,
            'detectionTimes': (endTime - startTime).microseconds,
            'num_kpts': num_kpts,
            'kpts_path': kpts_file_path,
            'scores_path': scores_path,
            'descriptors_path': descriptors_path,
        }
        return res(msg='检测完成', data=response)
    except Exception as e:
        return res(code='500', msg='检测失败', data=str(e))


@detection_api.post('/download')
def download():
    try:
        dfilename = request.json.get('dfilename')
        dfilepath = request.json.get('dfilepath')
        type = request.json.get('type')
        download_name = ''
        if type == "image":
            download_name = dfilename
        elif type == "numpy":
            download_name = dfilename.split('.')[0] + '.npy'

        if dfilename is None or not os.path.exists(dfilepath):
            return res(code='300', msg='下载失败', data="文件找不到了")

        @after_this_request
        def add_headers(response):
            response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response

        return send_file(dfilepath, as_attachment=True, download_name=download_name)
    except Exception as e:
        return res(code='500', msg='下载失败', data=str(e))


@detection_api.get('/download/<string:id>/<string:type>')
def download_id(id, type):
    try:
        detection = Detection.query.filter_by(id=id).first()
        if detection is None:
            return res(300, '下载失败', '该条记录已被删除或未保存成功')

        if type == "image":
            dfilepath = detection.res_image_path
        elif type == "kpts":
            dfilepath = detection.res_kpts_path
        elif type == "descriptors":
            dfilepath = detection.res_descriptors_path
        elif type == "scores":
            dfilepath = detection.res_scores_path
        else:
            return res(300, '下载失败', '下载任务出错')
        dfilename = os.path.basename(dfilepath)

        @after_this_request
        def add_headers(response):
            response.headers['Access-Control-Expose-Headers'] = 'Content-Disposition'
            return response

        return send_file(dfilepath, as_attachment=True, download_name=dfilename)
    except Exception as e:
        return res(code='500', msg='下载失败', data=str(e))


# 记录 增
@detection_api.post('/record')
@jwt_required()
def add_record():
    try:
        username = request.json.get('username')
        user = User.query.filter_by(username=username).first()

        origin_image_name = request.json.get('origin_image_name')
        origin_image_url = request.json.get('origin_image_url')
        origin_image_path = request.json.get('origin_image_path')
        algorithm = request.json.get('algorithm')
        config = request.json.get('config')
        image_width = request.json.get('image_width')
        image_height = request.json.get('image_height')
        elapsed_time = request.json.get('elapsed_time')
        res_image_url = request.json.get('res_image_url')
        res_image_path = request.json.get('res_image_path')
        res_kpts_num = request.json.get('res_kpts_num')
        res_kpts_path = request.json.get('res_kpts_path')
        res_scores_path = request.json.get('res_scores_path')
        res_descriptors_path = request.json.get('res_descriptors_path')

        detection = Detection(user_id=user.id, origin_image_name=origin_image_name, origin_image_url=origin_image_url,
                              origin_image_path=origin_image_path, algorithm=algorithm, config=config,
                              image_width=image_width, image_height=image_height, elapsed_time=elapsed_time,
                              res_image_url=res_image_url, res_image_path=res_image_path,
                              res_kpts_num=res_kpts_num, res_kpts_path=res_kpts_path, res_scores_path=res_scores_path,
                              res_descriptors_path=res_descriptors_path)
        detection.generate_id()
        detection.set_record_date()
        db.session.add(detection)
        db.session.commit()
        return res(200, '已添加记录', data='可以在用户功能模块中查找本次记录')

    except Exception as e:
        return res(500, '添加记录失败', data=str(e))


# 记录 查条数
@detection_api.get('/total/<string:user_id>')
@jwt_required()
def get_users_total(user_id):
    try:
        detections_num = Detection.query.order_by(Detection.record_date).filter_by(user_id=user_id).count()
        if detections_num is None:
            return res(300, '查询失败', '没有记录信息')
        else:
            return res(200, '查询成功', data=detections_num)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@detection_api.get('/<string:user_id>/<int:pageSize>/<int:page>')
@jwt_required()
def get_records(user_id, pageSize, page):
    try:
        offset = pageSize * (page - 1)
        records = Detection.query.order_by(Detection.record_date.desc()).filter_by(user_id=user_id).offset(
            offset).limit(pageSize).all()
        if records is None:
            return res(300, '查询失败', '没有记录信息')
        else:
            resList = []
            for record in records:
                resList.append(record.to_json())
            return res(200, '查询成功', data=resList)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@detection_api.delete('/<string:id>/<string:user_id>')
@jwt_required()
def delete_record(id, user_id):
    try:
        detection = Detection.query.filter_by(id=id, user_id=user_id).first()
        origin_image_path = detection.origin_image_path
        res_image_path = detection.res_image_path
        res_kpts_path = detection.res_kpts_path
        res_scores_path = detection.res_scores_path
        res_descriptors_path = detection.res_descriptors_path

        if Detection.query.filter_by(origin_image_path=origin_image_path).count() == 1:
            if os.path.exists(origin_image_path) and os.path.isfile(origin_image_path):
                os.remove(origin_image_path)
        if os.path.exists(res_image_path) and os.path.isfile(res_image_path):
            os.remove(res_image_path)
        if os.path.exists(res_kpts_path) and os.path.isfile(res_kpts_path):
            os.remove(res_kpts_path)
        if os.path.exists(res_scores_path) and os.path.isfile(res_scores_path):
            os.remove(res_scores_path)
        if os.path.exists(res_descriptors_path) and os.path.isfile(res_descriptors_path):
            os.remove(res_descriptors_path)

        db.session.delete(detection)

        db.session.commit()
        return res(200, '删除成功')
    except Exception as e:
        return res(500, '删除失败', data=str(e))


@detection_api.delete('/')
@jwt_required()
def delete_some_records():
    try:
        deleteIds = request.json.get('deleteIds')
        user_id = request.json.get('user_id')
        for id in deleteIds:

            detection = Detection.query.filter_by(id=id, user_id=user_id).first()
            origin_image_path = detection.origin_image_path
            res_image_path = detection.res_image_path
            res_kpts_path = detection.res_kpts_path
            res_scores_path = detection.res_scores_path
            res_descriptors_path = detection.res_descriptors_path

            if Detection.query.filter_by(origin_image_path=origin_image_path).count() == 1:
                if os.path.exists(origin_image_path) and os.path.isfile(origin_image_path):
                    os.remove(origin_image_path)
            if os.path.exists(res_image_path) and os.path.isfile(res_image_path):
                os.remove(res_image_path)
            if os.path.exists(res_kpts_path) and os.path.isfile(res_kpts_path):
                os.remove(res_kpts_path)
            if os.path.exists(res_scores_path) and os.path.isfile(res_scores_path):
                os.remove(res_scores_path)
            if os.path.exists(res_descriptors_path) and os.path.isfile(res_descriptors_path):
                os.remove(res_descriptors_path)

            db.session.delete(detection)
            db.session.commit()
        return res(code=200, msg='批量删除成功')
    except Exception as e:
        return res(code='500', msg='批量删除失败', data=str(e))
