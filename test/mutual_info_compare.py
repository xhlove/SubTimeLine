'''
@作者: weimo
@创建日期: 2020-05-11 20:38:40
@上次编辑时间: 2020-05-12 17:51:48
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
# 测试互信息计算字幕图像相似度亲情况

import os
import sys
sys.path.append(os.getcwd())

import cv2
import numpy as np
from sklearn import metrics as mr

from pathlib import Path

from util.act import find_subtitle_box

class MuTualInfoCompare(object):
    def __init__(self, video_path: Path, cbox: list, inrange_params: list):
        self.cbox = cbox
        self.inrange_params = inrange_params
        self.vc = cv2.VideoCapture(str(video_path))
        self.video_width, self.video_height = self.vc.get(cv2.CAP_PROP_FRAME_WIDTH), self.vc.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_subtitle(self, offset: int):
        cut_x, cut_y, cut_w, cut_h = self.cbox
        self.vc.set(cv2.CAP_PROP_POS_FRAMES, offset)
        retval, frame = self.vc.read()
        boxes, box_area, frame = find_subtitle_box(frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w], self.inrange_params, offset, isbase=False)
        print(boxes)
        return frame, boxes#[12:59, 418-20:863+20]

    def check(self, frame_indexs: list):
        frame1, (x1, y1, w1, h1) = self.get_subtitle(frame_indexs[0])
        frame1 = frame1[y1:h1, x1:w1]
        frame2, (x2, y2, w2, h2) = self.get_subtitle(frame_indexs[1])
        frame2 = frame2[y1:h1, x1:w1]
        mutual_infor = mr.normalized_mutual_info_score(frame1.reshape(-1), frame2.reshape(-1))
        print(mutual_infor)
        mutual_infor = mr.adjusted_mutual_info_score(np.reshape(frame1, -1), np.reshape(frame2, -1))
        print(mutual_infor)
        mutual_infor = mr.mutual_info_score(np.reshape(frame1, -1), np.reshape(frame2, -1))
        print(mutual_infor)
        cv2.imshow(f"frames_{frame_indexs}", np.vstack((frame1, frame2)))
        

if __name__ == "__main__":
    cbox = [0, 960, 1920, 60]
    inrange_params = [0, 180, 0, 15, 180, 244]
    video_path = Path(r"tests\videos\demo.mp4")

    cbox = [0, 610, 1280, 60]
    inrange_params = [0, 180, 0, 28, 210, 255]
    video_path = Path(r"tests\videos\下辈子我再好好过.Raise.de.wa.Chanto.Shimasu.Ep01.Chi_Jap.WEBrip.1280X720-ZhuixinFan.mp4")

    MTIC = MuTualInfoCompare(video_path, cbox, inrange_params)
    # MTIC.check([3903, 3989])
    # MTIC.check([32182, 32208])
    # MTIC.check([42062, 42068])
    MTIC.check([33020, 33021])
    cv2.waitKey(0)