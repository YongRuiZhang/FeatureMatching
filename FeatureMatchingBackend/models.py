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
