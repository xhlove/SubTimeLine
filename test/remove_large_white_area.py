'''
@作者: weimo
@创建日期: 2020-05-11 18:56:57
@上次编辑时间: 2020-05-11 18:57:34
@一个人的命运啊,当然要靠自我奋斗,但是...
'''

import cv2
import numpy as np

def nothing(x):
    pass

def test_remove_large_white_area(img: np.ndarray, _erode: int = 10, _dilate: int = 10):
    cv2.imshow("img ori", img)
    cv2.namedWindow("erode and dilate", cv2.WINDOW_NORMAL)
    cv2.createTrackbar("erode", "erode and dilate", 1, 20, nothing)
    cv2.createTrackbar("dilate", "erode and dilate", 1, 20, nothing)
    cv2.setTrackbarPos("erode", "erode and dilate", 1)
    cv2.setTrackbarPos("dilate", "erode and dilate", 1)
    while True:
        _erode = cv2.getTrackbarPos("erode", "erode and dilate")
        _dilate = cv2.getTrackbarPos("dilate", "erode and dilate")
        _img = cv2.erode(img, cv2.getStructuringElement(cv2.MORPH_RECT, (_erode, _erode)))
        cv2.imshow("erode", _img)
        _img = cv2.dilate(_img, cv2.getStructuringElement(cv2.MORPH_RECT, (_dilate, _dilate)))
        cv2.imshow("dilate", _img)
        cv2.imshow("remove_large_white_area", img & cv2.bitwise_not(_img))
        if cv2.waitKey(1) == 27:
            break