"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/12 21:07
Project    : FeatureMatchingBackend
FilePath   : /config.py
Description: Flask 的配置类
"""
from datetime import timedelta

DB_HOSTNAME = '127.0.0.1'
DB_PORT = 3306
DB_USERNAME = 'root'
DB_PASSWORD = 'zyr12345'
DB_DATABASE = 'FeatureMatching'


class Config:
    DEBUG = True
    HOST = '127.0.0.1'
    PORT = 5000
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}:{DB_PORT}/{DB_DATABASE}?charset=utf8mb4'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = 'zyr1234567890'  # JWT的密钥
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=240)  # 设置JWT的默认过期时间为240分钟
