"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/11 21:23
Project    : FeatureMatchingBackend
FilePath   : apis/test.py
Description: 测试 restful
"""
from flask import Blueprint, request
from utils.Res import res

test_api = Blueprint('test_api', __name__)


@test_api.get('/name')
def getnameall():
    return res(msg='请求成功', data={'name': 'zyr', 'age': 20})


@test_api.get('/name/<string:name>/<int:age>')
def getnamesomeone(name, age):
    return res(msg='请求成功', data={'name': name, 'age': age})


@test_api.post('/name')
def postname1():
    name = request.json.get('name')
    age = request.json.get('age')
    return res(msg='请求成功', data={'name': name, 'age': age})


@test_api.put('/name')
def putname():
    name = request.json.get('name')
    age = request.json.get('age')
    return res(msg='请求成功', data={'name': name, 'age': age})


@test_api.delete('/name')
def deletename():
    name = request.json.get('name')
    age = request.json.get('age')
    return res(msg='请求成功', data={'name': name, 'age': age})
