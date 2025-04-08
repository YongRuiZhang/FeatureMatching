"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/17 09:43
Project    : FeatureMatchingBackend
FilePath   : apis/User.py
Description: 用户相关 api
"""
from datetime import datetime
from urllib.parse import unquote

import pytz
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, \
    get_jwt_header
from sqlalchemy import func

from models import User, Detection, Matching, Mosaic,db
from utils.Res import res
from utils.role_required import role_required

user_api = Blueprint('user', __name__, url_prefix='/user')


@user_api.post('/register')
def register():
    try:
        username = request.json.get('username')
        password = request.json.get('password')
        if User.query.filter_by(username=username).first():
            return res(300, '注册失败', data='用户名已存在！')

        user = User(username=username, password=password)
        user.generate_id()
        user.set_register_data()

        db.session.add(user)
        db.session.commit()
        return res(200, '注册成功')
    except Exception as e:
        return res(500, '注册失败', data=str(e))


@user_api.post('/login')
def login():
    try:
        username = unquote(request.form.get('username'))
        password = request.form.get('password')
        if User.query.filter_by(username=username, password=password).first():
            user = User.query.filter_by(username=username, password=password).first()

            # 根据用户名生成 access token 和 refresh token
            payload = {
                'gender': user.gender,
                'role': user.role,
            }
            access_token = create_access_token(identity=username, additional_headers=payload)
            refresh_token = create_refresh_token(identity=username, additional_headers=payload)
            return res(200, '登陆成功', data={
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': user.to_json()
            })
        if User.query.filter_by(username=username).first():
            return res(300, '登陆失败', data='密码或用户名错误!')
        else:
            return res(300, msg='登陆失败', data='无当前用户信息！')
    except Exception as e:
        return res(500, '登陆失败', data=str(e))


@user_api.post('/')
@jwt_required()
@role_required('admin')
def add_user():
    try:
        uid = request.json.get('id')
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')
        birthday = request.json.get('birthday')
        gender = request.json.get('gender')
        role = request.json.get('role')

        if username is None or password is None or role is None or gender is None:
            return res(300, '新增失败', '用户信息不完善')

        user = User(username=username, password=password, gender=gender, role=role)
        user.generate_id()
        user.set_register_data()
        if email is not None:
            if len(email.split('@')) == 2 and email.split('@')[0] != '':
                user.email = email
        if birthday is not None and len(birthday) > 0:
            date = datetime.fromisoformat(birthday[0].replace('Z', '+00:00'))
            newBirthday = date.astimezone(pytz.timezone('Asia/Shanghai')).date()
            user.birthday = newBirthday

        db.session.add(user)
        db.session.commit()
        return res(msg='添加成功')
    except Exception as e:
        return res(500, '添加失败', data=str(e))


# 使用 refresh token 获取新的 access_token
@user_api.post("/refresh")
@jwt_required(refresh=True)  # 使用刷新令牌进行验证
def refresh():
    current_user = get_jwt_identity()
    header = get_jwt_header()
    payload = {
        'gender': header['gender'],
        'role': header['role'],
    }
    access_token = create_access_token(identity=current_user, additional_headers=payload)
    return res(msg='获取成功', data={'access_token': access_token})


@user_api.delete('/')
@jwt_required()
def delete():
    try:
        uid = request.json.get('uid')
        username = request.json.get('username')
        user = User.query.filter_by(username=username).first()
        db.session.delete(user)
        db.session.commit()
        return res(msg='注销成功', data='成功注销用户名为 ' + username + ' 的用户')
    except Exception as e:
        return res(500, '注销失败', data=str(e))


@user_api.delete('/some')
@jwt_required()
@role_required('admin')
def delete_some():
    try:
        deleteIds = request.json.get('deleteIds')
        for id in deleteIds:
            user = User.query.filter_by(id=id).first()
            db.session.delete(user)
            db.session.commit()
        return res(code=200, msg='批量删除成功')
    except Exception as e:
        return res(code='500', msg='批量删除失败', data=str(e))


@user_api.put('/')
@jwt_required()
def modify():
    try:
        uid = request.json.get('id')
        username = request.json.get('username')
        password = request.json.get('password')
        email = request.json.get('email')
        birthday = request.json.get('birthday')
        gender = request.json.get('gender')

        user = User.query.filter_by(username=username).first()

        content = []
        if password is not None and password != '':
            user.password = password
            content.append("密码")
        if email is not None:
            if len(email.split('@')) == 2 and email != user.email:
                user.email = email
                content.append("邮箱")
        if len(birthday) >= 1 and birthday[0] != '':
            date = datetime.fromisoformat(birthday[0].replace('Z', '+00:00'))
            newBirthday = date.astimezone(pytz.timezone('Asia/Shanghai')).date()
            if user.birthday is None or newBirthday.year != user.birthday.year or newBirthday.month != user.birthday.month or newBirthday.day != user.birthday.day:
                user.birthday = newBirthday
                content.append("生日")
        if gender is not None and gender != '' and gender != user.gender:
            user.gender = gender
            content.append("性别")

        db.session.add(user)
        db.session.commit()
        return res(msg='修改成功', data={'content': content})
    except Exception as e:
        return res(500, '修改失败', data=str(e))


@user_api.put('/role')
@jwt_required()
@role_required('admin')
def update_role():
    try:
        uid = request.json.get('id')
        username = request.json.get('username')
        gender = request.json.get('gender')
        role = request.json.get('role')

        user = User.query.filter_by(id=uid).first()

        content = []
        if gender is not None and gender != '' and gender != user.gender:
            user.gender = gender
            content.append("性别")
        if role is not None and role != '' and role != user.role:
            user.role = role
            content.append('身份')

        db.session.add(user)
        db.session.commit()
        return res(msg='修改成功', data={'content': content})
    except Exception as e:
        return res(500, '修改失败', data=str(e))


@user_api.get('/')
def get_user_all():
    try:
        Users = User.query.all()
        if Users is None:
            return res(300, '查询失败', '没有这个用户的信息')
        else:
            resList = []
            for user in Users:
                resList.append(user.to_json())
            return res(200, '批量查询成功', data=resList)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@user_api.get('/<string:username>')
@jwt_required()
def get_user(username):
    try:
        user = User.query.filter_by(username=username).first()
        if user is None:
            return res(300, '查询失败', '没有这个用户的信息')
        else:
            if user.password == '123456':
                info = user.to_json()
                info['warning'] = True
            else:
                info = user.to_json()
                info['warning'] = False
            return res(200, '查询成功', data=info)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@user_api.get('/<int:pageSize>/<int:page>')
@jwt_required()
@role_required('admin')
def get_users(pageSize, page):
    try:
        offset = pageSize * (page - 1)
        Users = User.query.order_by(User.register_date.desc()).offset(offset).limit(pageSize).all()
        if Users is None:
            return res(300, '查询失败', '没有用户信息')
        else:
            resList = []
            for user in Users:
                resList.append(user.to_json())
            return res(200, '查询成功', data=resList)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@user_api.get('/total')
@jwt_required()
@role_required('admin')
def get_users_total():
    try:
        users_num = User.query.order_by(User.register_date).count()
        if users_num is None:
            return res(300, '查询失败', '没有用户信息')
        else:
            return res(200, '查询成功', data=users_num)
    except Exception as e:
        return res(500, '查询失败', data=str(e))


@user_api.get('/charts/<string:user_id>')
@jwt_required()
def get_charts(user_id):
    try:
        print(user_id)
        result_detection = db.session.query(
            Detection.algorithm,
            func.count(Detection.algorithm).label('count')
        ).join(User).filter(User.id == user_id).group_by(Detection.algorithm).all()

        data_detection = [
            {
                "name": item.algorithm,
                "value": item.count
            }
            for item in result_detection
        ]
        result_matching = (db.session.query(
            Matching.algorithm,
            func.count(Matching.algorithm).label('count')
        ).join(User).filter(User.id == user_id)
                           .group_by(Matching.algorithm).all())

        data_matching = [
            {
                "name": item.algorithm,
                "value": item.count
            }
            for item in result_matching
        ]
        result_mosaic = db.session.query(
            Mosaic.algorithm,
            func.count(Mosaic.algorithm).label('count')
        ).join(User).filter(User.id == user_id).group_by(Mosaic.algorithm).all()

        data_mosaic = [
            {
                "name": item.algorithm,
                "value": item.count
            }
            for item in result_mosaic
        ]

        detection_count = Detection.query.join(User).filter(User.id == user_id).count()
        matching_count = Matching.query.join(User).filter(User.id == user_id).count()
        mosaic_count = Mosaic.query.join(User).filter(User.id == user_id).count()

        data_pie = [
            {
                "name": '特征检测',
                "value": detection_count
            },
            {
                "name": '特征匹配',
                "value": matching_count
            },
            {
                "name": '图像匹配',
                "value": mosaic_count
            }
        ]

        return res(200, '查询成功', data={
                'data_detection': data_detection,
                'data_matching': data_matching,
                'data_mosaic': data_mosaic,
                'data_pie': data_pie,
            })
    except Exception as e:
        res(500, '查询失败', data=str(e))
