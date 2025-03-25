# %BANNER_BEGIN%
# ---------------------------------------------------------------------
# %COPYRIGHT_BEGIN%
#
#  Magic Leap, Inc. ("COMPANY") CONFIDENTIAL
#
#  Unpublished Copyright (c) 2020
#  Magic Leap, Inc., All Rights Reserved.
#
# NOTICE:  All information contained herein is, and remains the property
# of COMPANY. The intellectual and technical concepts contained herein
# are proprietary to COMPANY and may be covered by U.S. and Foreign
# Patents, patents in process, and are protected by trade secret or
# copyright law.  Dissemination of this information or reproduction of
# this material is strictly forbidden unless prior written permission is
# obtained from COMPANY.  Access to the source code contained herein is
# hereby forbidden to anyone except current COMPANY employees, managers
# or contractors who have executed Confidentiality and Non-disclosure
# agreements explicitly covering such access.
#
# The copyright notice above does not evidence any actual or intended
# publication or disclosure  of  this source code, which includes
# information that is confidential and/or proprietary, and is a trade
# secret, of  COMPANY.   ANY REPRODUCTION, MODIFICATION, DISTRIBUTION,
# PUBLIC  PERFORMANCE, OR PUBLIC DISPLAY OF OR THROUGH USE  OF THIS
# SOURCE CODE  WITHOUT THE EXPRESS WRITTEN CONSENT OF COMPANY IS
# STRICTLY PROHIBITED, AND IN VIOLATION OF APPLICABLE LAWS AND
# INTERNATIONAL TREATIES.  THE RECEIPT OR POSSESSION OF  THIS SOURCE
# CODE AND/OR RELATED INFORMATION DOES NOT CONVEY OR IMPLY ANY RIGHTS
# TO REPRODUCE, DISCLOSE OR DISTRIBUTE ITS CONTENTS, OR TO MANUFACTURE,
# USE, OR SELL ANYTHING THAT IT  MAY DESCRIBE, IN WHOLE OR IN PART.
#
# %COPYRIGHT_END%
# ----------------------------------------------------------------------
# %AUTHORS_BEGIN%
#
#  Originating Authors: Paul-Edouard Sarlin
#                       Daniel DeTone
#                       Tomasz Malisiewicz
#
# %AUTHORS_END%
# --------------------------------------------------------------------*/
# %BANNER_END%

# 基于 Magic Leap 的代码修改

from pathlib import Path
import time
from collections import OrderedDict
from threading import Thread
import numpy as np
import cv2
import torch
import matplotlib

matplotlib.use('Agg')


class AverageTimer:
    """ 用于管理代码处理时间的类 """

    def __init__(self, smoothing=0.3, newline=False):
        self.smoothing = smoothing
        self.newline = newline
        self.times = OrderedDict()
        self.will_print = OrderedDict()  # 将会输出的时间名
        self.reset()

    def reset(self):
        now = time.time()
        self.start = now  # 开始时刻
        self.last_time = now  # 最后一次时刻
        for name in self.will_print:
            self.will_print[name] = False

    def update(self, name='default'):
        now = time.time()
        dt = now - self.last_time  # 时刻间隔
        if name in self.times:
            dt = self.smoothing * dt + (1 - self.smoothing) * self.times[name]
        self.times[name] = dt
        self.will_print[name] = True
        self.last_time = now

    def print(self, text='Timer', small_text=None):
        if small_text is None:
            small_text = []
        total = 0.  # 总时长
        print('[{}]'.format(text), end=' ')
        for key in self.times:
            val = self.times[key]
            if self.will_print[key]:
                print('%s=%.3f' % (key, val), end=' ')
                small_text.append('%s=%.3f sec' % (key, val))
                total += val
        print('total=%.3f sec {%.1f FPS}' % (total, 1. / total), end=' ')
        if self.newline:
            print(flush=True)
        else:
            print(end='\r', flush=True)
        self.reset()
        small_text.append('total=%.3f sec {%.1f FPS}' % (total, 1. / total))
        return small_text


class VideoStreamer:
    """
   处理输入流的类.
        支撑四种输入类型:
        1.) USB
        2.) IP 摄像机
        3.) 目录
        4.) 视频
    """

    def __init__(self, basedir, resize, skip, image_glob, max_length=1000000):
        self._ip_grabbed = False
        self._ip_running = False
        self._ip_camera = False  # 是否 使用 IP 摄像机
        self._ip_image = None
        self._ip_index = 0
        self.cap = []  # 摄像机
        self.camera = True  # 是否 使用摄像机
        self.video_file = False  # 是否是 视频文件
        self.listing = []  # 图像路径列表
        self.resize = resize  # resize的尺寸 [weight, height]
        self.interp = cv2.INTER_AREA
        self.i = 0  # 第 i 张图像
        self.skip = int(skip)  # 跳过图片数量，1表示不跳过
        self.max_length = max_length  # 最多的图像数量
        self.scales = (1., 1.)  # resize 缩放尺度
        if isinstance(basedir, int) or basedir.isdigit():
            print('==> 处理 USB 输入源: {}'.format(basedir))
            self.cap = cv2.VideoCapture(int(basedir))
            self.listing = range(0, self.max_length)
        elif basedir.startswith(('http', 'rtsp')):
            print('==> 处理 IP 摄像机输入源: {}'.format(basedir))
            self.cap = cv2.VideoCapture(basedir)
            self.start_ip_camera_thread()
            self._ip_camera = True
            self.listing = range(0, self.max_length)
        elif Path(basedir).is_dir():
            print('==> 处理 目录 输入源: {}'.format(basedir))
            self.listing = list(Path(basedir).glob(image_glob[0]))
            for j in range(1, len(image_glob)):
                image_path = list(Path(basedir).glob(image_glob[j]))
                self.listing = self.listing + image_path
            self.listing.sort()
            self.listing = self.listing[::self.skip]
            self.max_length = np.min([self.max_length, len(self.listing)])
            if self.max_length == 0:
                raise IOError('没有发现图片 (可能 \'image_glob\' 设置错误 ?)')
            self.listing = self.listing[:self.max_length]
            self.camera = False
        elif Path(basedir).exists():
            print('==> 处理 视频 输入源: {}'.format(basedir))
            self.cap = cv2.VideoCapture(basedir)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            num_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            print(num_frames)
            self.listing = range(0, num_frames)
            print(self.listing, self.skip)
            self.listing = self.listing[::self.skip]
            print(self.listing)
            self.video_file = True
            self.max_length = np.min([self.max_length, len(self.listing)])
            self.listing = self.listing[:self.max_length]

        else:
            raise ValueError('VideoStreamer 输入源 \"{}\" 识别失败.'.format(basedir))
        if self.camera and not self.cap.isOpened():
            raise IOError('打开摄像头失败')

    def load_image(self, impath):
        """  加载图片，转为灰度图并resize """
        grayim = cv2.imread(impath, 0)
        if grayim is None:
            raise Exception('读取图片 %s 失败' % impath)
        w, h = grayim.shape[1], grayim.shape[0]
        w_new, h_new = process_resize(w, h, self.resize)
        self.scales = (float(w) / float(w_new), float(h) / float(h_new))
        grayim = cv2.resize(
            grayim, (w_new, h_new), interpolation=self.interp)
        return grayim

    def next_frame(self):
        """ 加载下一帧 """
        if self.i == self.max_length:
            return (None, False)
        if self.camera:  # 除了目录都是调用这个方法
            if self._ip_camera:
                # Wait for first image, making sure we haven't exited
                while self._ip_grabbed is False and self._ip_exited is False:
                    time.sleep(.001)

                ret, image = self._ip_grabbed, self._ip_image.copy()
                if ret is False:
                    self._ip_running = False
            else:
                ret, image = self.cap.read()
            if ret is False:
                print('VideoStreamer: 不能从摄像机获得帧')
                return (None, False)
            w, h = image.shape[1], image.shape[0]
            if self.video_file:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.listing[self.i])

            w_new, h_new = process_resize(w, h, self.resize)
            self.scales = (float(w) / float(w_new), float(h) / float(h_new))
            image = cv2.resize(image, (w_new, h_new),
                               interpolation=self.interp)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            image_file = str(self.listing[self.i])
            image = self.load_image(image_file)
        self.i = self.i + 1
        return (image, True)

    def start_ip_camera_thread(self):
        self._ip_thread = Thread(target=self.update_ip_camera, args=())
        self._ip_running = True
        self._ip_thread.start()
        self._ip_exited = False
        return self

    def update_ip_camera(self):
        while self._ip_running:
            ret, img = self.cap.read()
            if ret is False:
                self._ip_running = False
                self._ip_exited = True
                self._ip_grabbed = False
                return

            self._ip_image = img
            self._ip_grabbed = ret
            self._ip_index += 1

    def cleanup(self):
        self._ip_running = False


# --- PREPROCESSING ---

def process_resize(w, h, resize):
    assert (len(resize) > 0 and len(resize) <= 2)
    if len(resize) == 1 and resize[0] > -1:
        scale = resize[0] / max(h, w)
        w_new, h_new = int(round(w * scale)), int(round(h * scale))
    elif len(resize) == 1 and resize[0] == -1:
        w_new, h_new = w, h
    else:  # len(resize) == 2:
        w_new, h_new = resize[0], resize[1]

    # Issue warning if resolution is too small or too large.
    if max(w_new, h_new) < 160:
        print('Warning: input resolution is very small, results may vary')
    elif max(w_new, h_new) > 2000:
        print('Warning: input resolution is very large, results may vary')

    return w_new, h_new


def frame2tensor(frame, device, half=False):
    if half:
        return torch.from_numpy(frame / 255.).float()[None, None].half().to(device)
    return torch.from_numpy(frame / 255.).float()[None, None].to(device)


def read_image(path, device, resize, rotation, resize_float):
    image = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return None, None, None
    w, h = image.shape[1], image.shape[0]
    w_new, h_new = process_resize(w, h, resize)
    scales = (float(w) / float(w_new), float(h) / float(h_new))

    if resize_float:
        image = cv2.resize(image.astype('float32'), (w_new, h_new))
    else:
        image = cv2.resize(image, (w_new, h_new)).astype('float32')

    if rotation != 0:
        image = np.rot90(image, k=rotation)
        if rotation % 2:
            scales = scales[::-1]

    inp = frame2tensor(image, device)
    return image, inp, scales


# --- GEOMETRY ---


def estimate_pose(kpts0, kpts1, K0, K1, thresh, conf=0.99999):
    """ 位姿估计 """

    # 匹配对大于等于 5
    if len(kpts0) < 5:
        return None, ''
    print(2.1)

    # 焦距归一化：求 a_x, a_y, b_x, b_y（两个相机x，y方向上的焦距）
    f_mean = np.mean([K0[0, 0], K1[1, 1], K0[0, 0], K1[1, 1]])
    # 将 像素误差 转换为与 相机内参无关 的 几何误差
    norm_thresh = thresh / f_mean
    print(2.2)

    # 将 像素平面 的坐标点转换到 摄像机坐标系
    kpts0 = (kpts0 - K0[[0, 1], [2, 2]][None]) / K0[[0, 1], [0, 1]][None]  # (x0, y0) = ((x0'-c0_x)/a0, (y0'-c0_y)/b0)
    kpts1 = (kpts1 - K1[[0, 1], [2, 2]][None]) / K1[[0, 1], [0, 1]][None]  # (x1, y1) = ((x1'-c1_x)/a1, (y1'-c1_y)/b1)
    print(2.3)

    # 求本质矩阵，E 为本质矩阵，mask为0，1矩阵（0表示异常值（外点），1表示内点）
    E, mask = cv2.findEssentialMat(
        kpts0, kpts1, np.eye(3), threshold=norm_thresh, prob=conf,
        method=cv2.RANSAC)

    assert E is not None

    best_num_inliers = 0
    ret = None
    # 可能会求得多组本质矩阵
    for _E in np.split(E, len(E) / 3):
        n, R, t, _ = cv2.recoverPose(_E, kpts0, kpts1, np.eye(3), 1e9, mask=mask)  # n: 内点数  ; R:(3,3); t:(3,1);  _:mask
        if best_num_inliers == 0:
            ret = (R, t[:, 0], mask.ravel() > 0)
        # 根据内点数，获得最佳的恢复结果（旋转和平移矩阵）
        if n > best_num_inliers:
            best_num_inliers = n
            ret = (R, t[:, 0], mask.ravel() > 0)  # mask.ravel() 表示按行展开为一维
    return ret, E


def rotate_intrinsics(K, image_shape, rot):
    """ 根据摄像机旋转方向旋转内参矩阵，其中image_shape作为参数提供h, w """
    assert rot <= 3
    h, w = image_shape[:2][::-1 if (rot % 2) else 1]
    fx, fy, cx, cy = K[0, 0], K[1, 1], K[0, 2], K[1, 2]
    rot = rot % 4
    if rot == 1:
        return np.array([[fy, 0., cy],
                         [0., fx, w - 1 - cx],
                         [0., 0., 1.]], dtype=K.dtype)
    elif rot == 2:
        return np.array([[fx, 0., w - 1 - cx],
                         [0., fy, h - 1 - cy],
                         [0., 0., 1.]], dtype=K.dtype)
    else:  # if rot == 3:
        return np.array([[fy, 0., h - 1 - cy],
                         [0., fx, cx],
                         [0., 0., 1.]], dtype=K.dtype)


def rotate_pose_inplane(i_T_w, rot):
    """ 旋转外参矩阵  """
    rotation_matrices = [
        np.array([[np.cos(r), -np.sin(r), 0., 0.],
                  [np.sin(r), np.cos(r), 0., 0.],
                  [0., 0., 1., 0.],
                  [0., 0., 0., 1.]], dtype=np.float32)
        for r in [np.deg2rad(d) for d in (0, 270, 180, 90)]
    ]
    return np.dot(rotation_matrices[rot], i_T_w)


def scale_intrinsics(K, scales):
    """ 根据原图像resize的尺度，缩放内参矩阵 """
    scales = np.diag([1. / scales[0], 1. / scales[1], 1.])
    return np.dot(scales, K)


def to_homogeneous(points):
    """ 将点的坐标转换为齐次坐标（添加一个纬度，值为1） """
    return np.concatenate([points, np.ones_like(points[:, :1])], axis=-1)


def compute_epipolar_error(kpts0, kpts1, T_0to1, K0, K1):
    """
    根据辛普森距离 求 极线误差
        kpts0: (n, 3)
        kpts1: (n, 2)
        T_0to1: (4, 4)
        K0: (3,3)
        K1: (3,3)
    """
    # 将像素平面的坐标点转换到摄像机坐标系
    kpts0 = (kpts0 - K0[[0, 1], [2, 2]][None]) / K0[[0, 1], [0, 1]][None]  # (x0, y0) = ((x0'-c0_x)/a0, (y0'-c0_y)/b0)
    kpts1 = (kpts1 - K1[[0, 1], [2, 2]][None]) / K1[[0, 1], [0, 1]][None]  # (x1, y1) = ((x1'-c1_x)/a1, (y1'-c1_y)/b1)
    # 将摄像机坐标系的坐标点转换为齐次坐标
    # (n, 3)
    kpts0 = to_homogeneous(kpts0)  # (x0, y0) -> (x0, y0, 1)
    kpts1 = to_homogeneous(kpts1)  # (x1, y1) -> (x1, y1, 1)

    # 获取 gt 平移参数tx, ty, tz
    t0, t1, t2 = T_0to1[:3, 3]
    # 构建[T]\times
    t_skew = np.array([
        [0, -t2, t1],
        [t2, 0, -t0],
        [-t1, t0, 0]
    ])
    # 求本质矩阵：E = [T]\times R (3,3)
    E = t_skew @ T_0to1[:3, :3]

    # p0 = kpts0^T, p1 = kpts1^T
    Ep0 = kpts0 @ E.T  # kpts0 @ E.T = (E @ p0)^T  : (n, 3) @ (3, 3) = (n, 3)
    p1Ep0 = np.sum(kpts1 * Ep0, -1)  # p1^T @ (E @ p0)^T  : (n,3) * (n,3) 按列相加 = (n, )
    Etp1 = kpts1 @ E  # p1^T @ E : (n, 3) @ (3, 3) = (n, 3)
    # 辛普森距离
    d = p1Ep0 ** 2 * (1.0 / (Ep0[:, 0] ** 2 + Ep0[:, 1] ** 2)
                      + 1.0 / (Etp1[:, 0] ** 2 + Etp1[:, 1] ** 2))
    return d  # (n,)


def angle_error_mat(R1, R2):
    """ 求 矩阵 的 角度 误差 \arccos(\frac{tr(R1^T R2) - 1}{2}) """
    cos = (np.trace(np.dot(R1.T, R2)) - 1) / 2
    cos = np.clip(cos, -1., 1.)  # 将 cos 的值限制在 [-1, 1] 范围内（小于 -1 取值为 -1， 大于 1 取值为 1）
    return np.rad2deg(np.abs(np.arccos(cos)))  # 弧度制 转为 角度制


def angle_error_vec(v1, v2):
    """
    求 向量 的 角度 误差：
        \arccos(\frac{v1 v2}{\Vert v1 \Vert \Vert v2 \Vert})
     """
    n = np.linalg.norm(v1) * np.linalg.norm(v2)  # v1 和 v2 的二范式相乘
    return np.rad2deg(np.arccos(np.clip(np.dot(v1, v2) / n, -1.0, 1.0)))  # 弧度制 转为 角度制


def compute_pose_error(T_0to1, R, t):
    R_gt = T_0to1[:3, :3]
    t_gt = T_0to1[:3, 3]
    error_t = angle_error_vec(t, t_gt)  # 求平移角度误差
    error_t = np.minimum(error_t, 180 - error_t)  # 处理方向模糊性，即限制在 0 - 180度范围内
    error_R = angle_error_mat(R, R_gt)  # 求旋转角度误差
    return error_t, error_R


def pose_auc(errors, thresholds):
    # 按 errors 排序
    sort_idx = np.argsort(errors)
    errors = np.array(errors.copy())[sort_idx]

    # 计算召回率
    recall = (np.arange(len(errors)) + 1) / len(errors)

    # 添加起点
    errors = np.r_[0., errors]
    recall = np.r_[0., recall]

    aucs = []
    for t in thresholds:
        # 找到最后一个误差 <= t 的位置
        last_index = np.searchsorted(errors, t)
        # 构造曲线段
        r = np.r_[recall[:last_index], recall[last_index - 1]]
        e = np.r_[errors[:last_index], t]
        # 梯形法积分计算AUC
        aucs.append(np.trapezoid(r, x=e) / t)
    return aucs


# --- VISUALIZATION ---
def make_matching_plot_fast(image0, image1, mkpts0,
                            mkpts1, color, text, kpts0=None, kpts1=None, path=None,
                            show_keypoints=False, margin=10,
                            opencv_display=False, opencv_title='',
                            small_text=[]):
    if kpts0 is None:
        kpts0 = []
    if kpts1 is None:
        kpts1 = []
    H0, W0 = image0.shape
    H1, W1 = image1.shape
    H, W = max(H0, H1), W0 + W1 + margin

    out = 255 * np.ones((H, W), np.uint8)
    out[:H0, :W0] = image0
    out[:H1, W0 + margin:] = image1
    out = np.stack([out] * 3, -1)

    if show_keypoints:
        kpts0, kpts1 = np.round(kpts0).astype(int), np.round(kpts1).astype(int)
        white = (255, 255, 255)
        black = (0, 0, 0)
        for x, y in kpts0:
            cv2.circle(out, (x, y), 2, black, -1, lineType=cv2.LINE_AA)
            cv2.circle(out, (x, y), 1, white, -1, lineType=cv2.LINE_AA)
        for x, y in kpts1:
            cv2.circle(out, (x + margin + W0, y), 2, black, -1,
                       lineType=cv2.LINE_AA)
            cv2.circle(out, (x + margin + W0, y), 1, white, -1,
                       lineType=cv2.LINE_AA)

    mkpts0, mkpts1 = np.round(mkpts0).astype(int), np.round(mkpts1).astype(int)

    color = (np.array(color[:, :3]) * 255).astype(int)[:, ::-1]
    for (x0, y0), (x1, y1), c in zip(mkpts0, mkpts1, color):
        c = c.tolist()
        cv2.line(out, (x0, y0), (x1 + margin + W0, y1),
                 color=c, thickness=1, lineType=cv2.LINE_AA)
        # display line end-points as circles
        cv2.circle(out, (x0, y0), 2, c, -1, lineType=cv2.LINE_AA)
        cv2.circle(out, (x1 + margin + W0, y1), 2, c, -1,
                   lineType=cv2.LINE_AA)

    # Scale factor for consistent visualization across scales.
    sc = min(H / 640., 2.0)

    # Big text.
    Ht = int(30 * sc)  # text height
    txt_color_fg = (255, 255, 255)
    txt_color_bg = (0, 0, 0)
    for i, t in enumerate(text):
        cv2.putText(out, t, (int(8 * sc), Ht * (i + 1)), cv2.FONT_HERSHEY_DUPLEX,
                    1.0 * sc, txt_color_bg, 2, cv2.LINE_AA)
        cv2.putText(out, t, (int(8 * sc), Ht * (i + 1)), cv2.FONT_HERSHEY_DUPLEX,
                    1.0 * sc, txt_color_fg, 1, cv2.LINE_AA)

    # Small text.
    Ht = int(18 * sc)  # text height
    for i, t in enumerate(reversed(small_text)):
        cv2.putText(out, t, (int(8 * sc), int(H - Ht * (i + .6))), cv2.FONT_HERSHEY_DUPLEX,
                    0.5 * sc, txt_color_bg, 2, cv2.LINE_AA)
        cv2.putText(out, t, (int(8 * sc), int(H - Ht * (i + .6))), cv2.FONT_HERSHEY_DUPLEX,
                    0.5 * sc, txt_color_fg, 1, cv2.LINE_AA)

    if path is not None:
        cv2.imwrite(str(path), out)

    if opencv_display:
        cv2.imshow(opencv_title, out)
        cv2.waitKey(1)

    return out


def error_colormap(x):
    return np.clip(
        np.stack([2 - x * 2, x * 2, np.zeros_like(x), np.ones_like(x)], -1), 0, 1)
