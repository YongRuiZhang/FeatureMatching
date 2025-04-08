"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/17 09:18
Project    : FeatureMatchingBackend
FilePath   : /DLModels.py
Description:
"""
import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Nullable

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 't_user'  # 指定表名
    id = db.Column(db.String(128), primary_key=True)  # 整数类型，主健，自增
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)  # 最多8个汉字，唯一，索引，非空
    password = db.Column(db.String(128), nullable=False, comment="密码")  # 非空
    role = db.Column(db.String(64), nullable=False, default='guest', comment="角色")  # 身份，非空
    register_date = db.Column(db.DateTime, nullable=False)

    email = db.Column(db.String(128), index=True, default="", comment="邮箱地址")  # 索引，唯一，默认为空
    birthday = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(16), nullable=False, default='male')

    def generate_id(self):
        self.id = str(uuid.uuid4())

    def set_register_data(self):
        self.register_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'birthday': self.birthday,
            'gender': self.gender,
            'role': self.role,
            'register_date': self.register_date,
        }


class Detection(db.Model):
    __tablename__ = 't_detection'
    id = db.Column(db.String(128), primary_key=True)
    user_id = db.Column(db.String(128), db.ForeignKey('t_user.id'), nullable=False)
    record_date = db.Column(db.DateTime, nullable=False, comment="产生记录的时间")

    origin_image_name = db.Column(db.String(128), nullable=False, comment="原图片名（无uuid）")
    origin_image_url = db.Column(db.String(256), nullable=False, comment="原图片url，用于显示")
    origin_image_path = db.Column(db.String(256), nullable=False, comment="原图片Path")

    algorithm = db.Column(db.String(64), comment="使用算法", nullable=False)
    config = db.Column(db.String(256), comment="参数", nullable=False)

    image_width = db.Column(db.Integer, nullable=False)
    image_height = db.Column(db.Integer, nullable=False)
    elapsed_time = db.Column(db.Float, nullable=False)
    res_image_url = db.Column(db.String(256), nullable=False, comment="结果图片url")
    res_image_path = db.Column(db.String(256), nullable=False, comment="结果图片路径，用于下载")
    res_kpts_num = db.Column(db.Integer, nullable=False, comment="kpts数量")
    res_kpts_path = db.Column(db.String(256), nullable=False, comment="结果kpts路径，用于下载")
    res_scores_path = db.Column(db.String(256), comment="结果分数路径，用于下载")
    res_descriptors_path = db.Column(db.String(256), comment="结果描述子路径，用于下载")

    def generate_id(self):
        self.id = str(uuid.uuid4())

    def set_record_date(self):
        self.record_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'origin_image_name': self.origin_image_name,
            'origin_image_url': self.origin_image_url,
            'origin_image_path': self.origin_image_path,
            'algorithm': self.algorithm,
            'config': self.config,
            'image_width': self.image_width,
            'image_height': self.image_height,
            'elapsed_time': self.elapsed_time,
            'res_image_url': self.res_image_url,
            'res_image_path': self.res_image_path,
            'res_kpts_num': self.res_kpts_num,
            'res_kpts_path': self.res_kpts_path,
            'res_scores_path': self.res_scores_path,
            'res_descriptors_path': self.res_descriptors_path,
            'detection_date': self.record_date,
        }


class UploadData(db.Model):
    __tablename__ = 't_upload_data'
    id = db.Column(db.String(128), primary_key=True)
    path = db.Column(db.String(256), nullable=False, comment="路径")
    left_url = db.Column(db.String(256), comment="左图片url")
    right_url = db.Column(db.String(256), comment="右图片url")
    video_url = db.Column(db.String(256), comment="视频url")

    def generate_id(self):
        self.id = str(uuid.uuid4())

    def pair(self):
        return {
            'id': self.id,
            'path': self.path,
            'left_url': self.left_url,
            'right_url': self.right_url,
        }

    def images(self):
        return {
            'id': self.id,
            'path': self.path,
        }

    def video(self):
        return {
            'id': self.id,
            'path': self.path,
            'video_url': self.video_url,
        }


class Matching(db.Model):
    __tablename__ = 't_matching'
    id = db.Column(db.String(128), primary_key=True)
    user_id = db.Column(db.String(128), db.ForeignKey('t_user.id'), nullable=False)
    record_date = db.Column(db.DateTime, nullable=False, comment="产生记录的时间")

    data_id = db.Column(db.String(128), db.ForeignKey('t_upload_data.id'), nullable=False)
    origin_type = db.Column(db.String(64), nullable=False, comment="数据源类型")

    algorithm_type = db.Column(db.String(64), nullable=False, comment="使用算法类型")  # 稀疏、半稀疏、稠密
    algorithm = db.Column(db.String(64), nullable=False, comment="使用算法")
    config = db.Column(db.String(256), nullable=False, comment="参数")

    elapsed_time = db.Column(db.Float, nullable=False, comment="耗时")
    save_path = db.Column(db.String(256), nullable=False, comment="可视化结果路径，用于下载")
    save_path_url = db.Column(db.String(256), nullable=False, comment="可视化结果url，用于预览")
    save_matches_path = db.Column(db.String(256), nullable=False, comment="结果matches路径，用于下载")
    save_poses_path = db.Column(db.String(256), comment="结果poses路径，用于下载")

    def generate_id(self):
        self.id = str(uuid.uuid4())

    def set_record_date(self):
        self.record_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'matching_date': self.record_date,
            'data_id': self.data_id,
            'origin_type': self.origin_type,
            'algorithm_type': self.algorithm_type,
            'algorithm': self.algorithm,
            'config': self.config,
            'elapsed_time': self.elapsed_time,
            'save_path': self.save_path,
            'save_path_url': self.save_path_url,
            'save_matches_path': self.save_matches_path,
            'save_poses_path': self.save_poses_path,
        }


class Mosaic(db.Model):
    __tablename__ = 't_mosaic'
    id = db.Column(db.String(128), primary_key=True)
    user_id = db.Column(db.String(128), db.ForeignKey('t_user.id'), nullable=False)
    record_date = db.Column(db.DateTime, nullable=False, comment="产生记录的时间")

    data_id = db.Column(db.String(128), db.ForeignKey('t_upload_data.id'), nullable=False)

    algorithm_type = db.Column(db.String(64), nullable=False, comment="使用算法类型")  # 稀疏、半稀疏、稠密
    algorithm = db.Column(db.String(64), nullable=False, comment="使用算法")
    scene = db.Column(db.String(256), nullable=False, comment="场景")

    elapsed_time = db.Column(db.Float, nullable=False, comment="耗时")
    save_path = db.Column(db.String(256), nullable=False, comment="可视化结果路径，用于下载")
    save_path_url = db.Column(db.String(256), nullable=False, comment="可视化结果url，用于预览")

    def generate_id(self):
        self.id = str(uuid.uuid4())

    def set_record_date(self):
        self.record_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'mosaic_date': self.record_date,
            'data_id': self.data_id,
            'algorithm_type': self.algorithm_type,
            'algorithm': self.algorithm,
            'scene': self.scene,
            'elapsed_time': self.elapsed_time,
            'save_path': self.save_path,
            'save_path_url': self.save_path_url,
        }
