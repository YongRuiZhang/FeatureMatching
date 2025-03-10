"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/10 11:22
Project    : FeatureMatchingBackend
FilePath   : utils/Res.py
Description: 返回结果方法
"""
from flask import jsonify


def res(code=200, msg='', data=None):
    """
    自定义返回结果的封装函数
    :param code: 状态码，默认为 200
    :param msg: 提示信息，默认为空字符串
    :param data: 返回数据，默认为 None
    :return: Response 对象
    """
    response_data = {
        'code': code,
        'msg': msg,
        'data': data
    }
    return jsonify(response_data)