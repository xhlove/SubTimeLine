'''
@作者: weimo
@创建日期: 2020-03-29 09:51:05
@上次编辑时间: 2020-04-02 00:50:27
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
from pathlib import Path

import cv2
import sys
import numpy as np

def nothing(x):
    pass

def only_subtitle(img: np.ndarray, inrange_params: list = None, just_return: bool = False):
    _hsv1 = cv2.cvtColor(cv2.GaussianBlur(img, (5, 5), 0), cv2.COLOR_BGR2HSV)
    _hsv2 = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    _hsv = _hsv2
    # _hsv = np.vstack((_hsv1, _hsv2))

    hmin, hmax, smin, smax, vmin, vmax = [0, 180, 0, 180, 88, 218]
    lower_mask = np.array([hmin, smin, vmin])
    upper_mask = np.array([hmax, smax, vmax])
    _mask = cv2.bitwise_not(cv2.inRange(_hsv, lower_mask, upper_mask))

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
    cv2.imshow("ori", _hsv)
    # get_canny(_hsv_)
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
        hsv = np.vstack((hsv, hsv & _mask))
        cv2.imshow("hsv", hsv)
        if cv2.waitKey(1) == 27:
            break

def get_canny(img: np.ndarray):
    cv2.imshow("get_canny input img", img)
    cv2.namedWindow("get_canny test", cv2.WINDOW_NORMAL)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    v = np.median(img_gray)
    sigma = 0.33
    lower_thresh = int(max(0, (1.0 - sigma) * v))
    upper_thresh = int(min(255, (1.0 + sigma) * v))
    cv2.imshow("img_gray", img_gray)
    cv2.createTrackbar("threshold1", "get_canny test", 0, 255, nothing)
    cv2.createTrackbar("threshold2", "get_canny test", 0, 255, nothing)
    cv2.setTrackbarPos("threshold1", "get_canny test", lower_thresh)
    cv2.setTrackbarPos("threshold2", "get_canny test", upper_thresh)
    while True:
        threshold1 = cv2.getTrackbarPos("threshold1", "get_canny test")
        threshold2 = cv2.getTrackbarPos("threshold2", "get_canny test")
        img_canny = cv2.Canny(img_gray, threshold1, threshold2)
        cv2.imshow("img_canny", img_canny)
        if cv2.waitKey(1) == 27:
            break