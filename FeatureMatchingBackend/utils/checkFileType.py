"""
-*-  coding: utf-8  -*-
Author     : YongRuiZhang
Date       : 2025/2/10 11:17
Project    : FeatureMatchingBackend
FilePath   : utils/checkFileType.py
Description: 检查文件类型
"""
ALLOWED_PIC_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_pic_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_PIC_EXTENSIONS
