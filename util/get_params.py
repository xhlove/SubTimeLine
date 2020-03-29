'''
@作者: weimo
@创建日期: 2020-03-29 09:51:05
@上次编辑时间: 2020-03-29 10:07:37
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
from pathlib import Path

import cv2
import sys
import numpy as np

def nothing(x):
    pass

def only_subtitle(img: np.ndarray, inrange_params: list = None, just_return: bool = False):
    _hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    if inrange_params is None:
        # hmin, hmax, smin, smax, vmin, vmax = (0, 190, 0, 50, 180, 255) # OP字幕
        hmin, hmax, smin, smax, vmin, vmax = (0, 190, 0, 50, 220, 244) # 正文字幕
    else:
        hmin, hmax, smin, smax, vmin, vmax = inrange_params
    if just_return:
        lower_blue = np.array([hmin, smin, vmin])
        upper_blue = np.array([hmax, smax, vmax])
        hsv = cv2.inRange(_hsv, lower_blue, upper_blue)
        return hsv
    cv2.imshow("ori", img)
    # cv2.waitKey(0)
    cv2.namedWindow("inrange test", cv2.WINDOW_NORMAL)
    cv2.createTrackbar("hmin", "inrange test", 0, 360, nothing)
    cv2.createTrackbar("hmax", "inrange test", 0, 360, nothing)
    cv2.createTrackbar("smin", "inrange test", 0, 255, nothing)
    cv2.createTrackbar("smax", "inrange test", 0, 255, nothing)
    cv2.createTrackbar("vmin", "inrange test", 0, 255, nothing)
    cv2.createTrackbar("vmax", "inrange test", 0, 255, nothing)
    cv2.setTrackbarPos("hmin", "inrange test", hmin)
    cv2.setTrackbarPos("hmax", "inrange test", hmax)
    cv2.setTrackbarPos("smin", "inrange test", smin)
    cv2.setTrackbarPos("smax", "inrange test", smax)
    cv2.setTrackbarPos("vmin", "inrange test", vmin)
    cv2.setTrackbarPos("vmax", "inrange test", vmax)

    while True:
        hmin = cv2.getTrackbarPos("hmin", "inrange test")
        hmax = cv2.getTrackbarPos("hmax", "inrange test")
        smin = cv2.getTrackbarPos("smin", "inrange test")
        smax = cv2.getTrackbarPos("smax", "inrange test")
        vmin = cv2.getTrackbarPos("vmin", "inrange test")
        vmax = cv2.getTrackbarPos("vmax", "inrange test")
        lower_blue = np.array([hmin, smin, vmin])
        upper_blue = np.array([hmax, smax, vmax])
        hsv = cv2.inRange(_hsv, lower_blue, upper_blue)
        cv2.imshow("hsv", hsv)
        if cv2.waitKey(1) == 27:
            break