'''
@作者: weimo
@创建日期: 2020-05-11 18:55:08
@上次编辑时间: 2020-05-12 16:45:56
@一个人的命运啊,当然要靠自我奋斗,但是...
'''

import cv2
import numpy as np

from util.mser import get_mser
from util.inrange import convert_img_hsv_with_inrange

def remove_large_white_area(img: np.ndarray, _erode: int = 10, _dilate: int = 10):
    # 先腐蚀后膨胀 可以去掉一些较小的白色部分
    _img = cv2.erode(img, cv2.getStructuringElement(cv2.MORPH_RECT, (_erode, _erode)))
    _img = cv2.dilate(_img, cv2.getStructuringElement(cv2.MORPH_RECT, (_dilate, _dilate)))
    return img & cv2.bitwise_not(_img)

def pre_get_mser(frame: np.ndarray, inrange_params: tuple, gaus: int = 0):
    # 在做MSER前预处理图像 (提取边缘 -> 闭运算 -> 取反) & (高斯模糊 -> 转hsv做inrange)
    # 以此尽可能保留字幕区域 去除干扰

    # 提取边缘 -> 闭运算 -> 取反
    frame_canny = cv2.Canny(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), 90, 240)
    frame_canny_close = cv2.morphologyEx(frame_canny, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))
    frame_close = cv2.bitwise_not(frame_canny_close)
    
    # 高斯模糊（可选） -> 转hsv做inrange
    if gaus > 0:
        frame = cv2.GaussianBlur(frame, (gaus, gaus), 0)
    frame_inrange = convert_img_hsv_with_inrange(frame, inrange_params)
    frame_inrange_without_white = remove_large_white_area(frame_inrange, 10, 10)
    
    # 相与去干扰 膨胀字幕部分
    frame_subtitle = cv2.dilate(frame_inrange_without_white & frame_close, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))
    # 通过MSER定位字幕
    # if frame_index == 3489:
    #     cv2.imshow("img_hsv", img_hsv)
    #     cv2.imshow("img_inrange", img_inrange)
    #     cv2.imshow("img_gray", img_gray)
    #     cv2.imshow("img_close", img_close)
    #     cv2.imshow("img_no_border", img_no_border)
        # cv2.waitKey(0)
    
    return frame_subtitle

def find_subtitle_box(frame: np.ndarray, params: tuple, frame_index: int, isbase: bool = False):
    frame_subtitle = pre_get_mser(frame, params)
    # cv2.imshow("frame_subtitle_pre_get_mser", frame_subtitle)
    # cv2.waitKey(0)
    box, box_area = get_mser(frame_subtitle, frame_index, frame.shape, isbase=isbase)
    return box, box_area, frame_subtitle

def get_white_ratio(img: np.ndarray):
    # 统计白色（255）占比
    counts = dict(zip(*np.unique(img, return_counts=True)))
    if counts.get(255) is None:
        return 0.0
    return float(counts[255] / img.size)