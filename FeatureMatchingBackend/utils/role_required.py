"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/18 19:44
Project    : FeatureMatchingBackend
FilePath   : utils/role_required.py
Description:
"""

from functools import wraps

import jwt
from flask import request
from flask_jwt_extended import get_jwt_header

from utils.Res import res


def role_required(role):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get("Authorization")
            if not token:
                return res(303, '未登陆')

            try:
                header = get_jwt_header()
                truth_role = header["role"]
            except jwt.ExpiredSignatureError:
                return res(301, 'token已经过期')
            except jwt.InvalidTokenError:
                return res(302,  "请重新登陆")

            # 检查用户角色是否符合要求
            if truth_role != role:
                return res(300, msg='权限不匹配', data=f'需要 {role} 权限')

            return f(*args, **kwargs)

        return decorated

    return wrapper
