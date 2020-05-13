'''
@作者: weimo
@创建日期: 2020-03-19 21:51:13
@上次编辑时间: 2020-05-13 14:32:26
@一个人的命运啊,当然要靠自我奋斗,但是...
'''

# 寻找字幕
# 通过
from pathlib import Path

import cv2
import sys
import time
import numpy as np
from sklearn import metrics as mr
from datetime import datetime

from PyQt5 import QtCore

from util.writeass import write_ass_line
from util.sst import SubStorage
from util.act import find_subtitle_box
from logs.logger import get_logger

logger = get_logger(Path(r"logs\subtimeline.log"))

class FWorker(QtCore.QThread):
    progress_frame = QtCore.pyqtSignal(int)
    def __init__(self, video_path: Path, inrange_params: list, cbox: tuple, offset: int = 0, step: int = 54):
        super(FWorker, self).__init__()
        self.video_path = video_path.absolute()
        self.inrange_params = inrange_params
        self.inrange_params_list = []
        self.cbox = [int(_ / 2) for _ in cbox]
        self.offset = offset
        self.step = step
        self.check()
        self.load_configs()
        self.start_params = []

    def run(self):
        # 
        offset, offset_key = self.start_params
        self.work_start(offset, offset_key)

    def load_configs(self):
        self.similarity_threshold = 60

    def calc_frame_time(self, frame_index: int):
        return datetime.utcfromtimestamp(frame_index / self.video_fps).strftime('%H:%M:%S.%f')[1:-4]
    
    def check(self):
        self.vc = cv2.VideoCapture(str(self.video_path))
        if self.vc.isOpened() is False:
            sys.exit(f"Can not open {self.video_path.name} !")
        self.video_frames = self.vc.get(cv2.CAP_PROP_FRAME_COUNT)
        self.video_fps = self.vc.get(cv2.CAP_PROP_FPS)
        # self.vc.set(cv2.CAP_PROP_FRAME_WIDTH, 720)
        # self.vc.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)

    def get_inrange_params(self, offset_key: str):
        # 针对单个视频不同时间区域的字幕 提取的设定不一样 注意这里使用的是帧数
        offset_range = (int(_) for _ in offset_key.split(":"))
        hmin, hmax, smin, smax, vmin, vmax = self.inrange_params[offset_key]
        return offset_range, (hmin, hmax, smin, smax, vmin, vmax)

    def work_start(self, offset: int, offset_key: str):
        offset_init = offset
        ts = time.time()
        # 寻找字幕起始帧
        cut_x, cut_y, cut_w, cut_h = self.cbox
        (offset_lowwer, offset_upper), inrange_params = self.get_inrange_params(offset_key)
        if offset < offset_lowwer or offset > offset_upper:
            sys.exit(f"{offset} is out of {offset_lowwer} <-> {offset_upper} !")
        sst = SubStorage()
        base_frame = None
        offset_end = None
        #<----先找到有字幕的帧---->
        seek_flag = False
        while True:
            if offset > self.video_frames:
                break
            self.vc.set(cv2.CAP_PROP_POS_FRAMES, offset)
            retval, frame = self.vc.read()
            if retval is False:
                sys.exit(f"retval is False at {offset} ! exit...")
            frame = cv2.resize(frame, (640, 360))
            boxes, frame = find_subtitle_box(frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w], inrange_params, offset, isbase=True)
            if boxes == "no subtitle":
                offset += self.step
            else:
                x, y, w, h = boxes
                cut_x = cut_x + x
                cut_y = cut_y + y
                cut_w = w - x
                cut_h = h - y
                cut_area = [cut_x, cut_y, cut_w, cut_h]
                base_frame = frame[y:h, x:w]
                sst.base_frame = base_frame
                sst.offset_base = offset
                sst.stackstorage.update({offset:100.0})
                print(f"定位{offset}帧 开始寻找")
                self.progress_frame.emit(offset)
                seek_flag = True
            if seek_flag:
                # print(offset_end, offset, offset_end is not None and offset_end - offset == 1)
                if offset_end is not None and offset_end - offset == 1:
                    print("前后字幕相邻~~~~~~~~~~~~~~~~~~")
                    offset_start = offset
                else:
                    offset_start = self.seek_start(offset, cut_area, sst, ts, inrange_params)
                offset_end = self.seek_end(offset, cut_area, sst, ts, inrange_params)
                if offset_end - offset_start >= 8:
                    # 间隔太近的不可以认为是一句话
                    pic_save_path = Path(f"subpics/{offset}.jpg")
                    cv2.imwrite(str(pic_save_path), base_frame)
                    write_ass_line(f"Dialogue: 0,{self.calc_frame_time(offset_start)},{self.calc_frame_time(offset_end)},微软雅黑,,0,0,0,,{offset_start}-{offset_end}")
                offset = offset_end + 1
                sst = SubStorage()
                seek_flag = False
                cut_x, cut_y, cut_w, cut_h = self.cbox
        print(f"耗时{time.time() - ts:.2f}s")

    def seek_end(self, offset: int, cut_area: list, sst: SubStorage, ts: float, inrange_params: list):
        cut_x, cut_y, cut_w, cut_h = cut_area
        offset = offset + self.step
        find_offset_end = False
        while True:
            if offset > self.video_frames:
                break
            self.vc.set(cv2.CAP_PROP_POS_FRAMES, offset)
            retval, frame = self.vc.read()
            _frame = frame
            if retval is False:
                sys.exit(f"retval is False at {offset} ! exit...")
            frame = cv2.resize(frame, (640, 360))
            boxes, frame = find_subtitle_box(frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w], inrange_params, offset)
            _sm_frame = frame & sst.base_frame
            sh, sw = _sm_frame.shape
            sh = int(sh / 2)
            similarity = mr.normalized_mutual_info_score(_sm_frame[sh-1:sh+1, :].reshape(-1), sst.base_frame[sh-1:sh+1, :].reshape(-1)) * 100
            
            sst.stackstorage.update({offset:similarity})
            sst.sort_stack()
            offset_index_in_stack = list(sst.stackstorage.keys())[list(sst.stackstorage.keys()).index(offset)]
            left_key = offset_index_in_stack - 1
            right_key = offset_index_in_stack + 1
            logger.info(f"seek_end --> {offset} {similarity:.2f},left_key {left_key} right_key {right_key}")
            if similarity >= 85:
                sst.base_frame = _sm_frame
            if similarity >= self.similarity_threshold:
                if boxes == "no subtitle":
                    print(f"{offset} {sst.offset_base} 警告！匹配判断与直接判断冲突")
                stack_flag = False # sst.stackstorage.get(right_key) 当similarity为0.0这里布尔值是False 后面优化一下 目前将0.0设定到0.01
                if sst.stackstorage.get(right_key) is not None and sst.stackstorage[right_key] < self.similarity_threshold:
                    sst.offset_end = offset
                    print(f"{offset}是{sst.offset_base}的末尾帧 √√×")
                    find_offset_end = True
                    break
                else:
                    for checked_offset, checked_similarity in sst.stackstorage.items():
                        if checked_offset < sst.offset_base:
                            continue
                        if checked_similarity < self.similarity_threshold:
                            offset = (offset + checked_offset) // 2
                            stack_flag = True
                            break
                if stack_flag is False:
                    offset = offset + self.step
            else:
                stack_flag = False
                if sst.stackstorage.get(left_key) is not None and sst.stackstorage[left_key] >= self.similarity_threshold:
                    sst.offset_end = left_key
                    print(f"{left_key}是{sst.offset_base}的末尾帧 √××")
                    find_offset_end = True
                    break
                else:
                    for checked_offset, checked_similarity in sst.stackstorage.items().__reversed__():
                        if checked_similarity >= self.similarity_threshold:
                            offset = (checked_offset + offset) // 2
                            stack_flag = True
                            break
        if find_offset_end:
            return sst.offset_end
        else:
            sys.exit("find_offset_end 失败")

    def seek_start(self, offset: int, cut_area: list, sst: SubStorage, ts: float, inrange_params: list):
        cut_x, cut_y, cut_w, cut_h = cut_area
        offset = offset - self.step
        find_offset_start = False
        while True:
            if offset > self.video_frames:
                break
            #<----read frame and get mser boxes---->
            self.vc.set(cv2.CAP_PROP_POS_FRAMES, offset)
            retval, frame = self.vc.read()
            _frame = frame
            if retval is False:
                sys.exit(f"retval is False at {offset} ! exit...")
            frame = cv2.resize(frame, (640, 360))
            boxes, frame = find_subtitle_box(frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w], inrange_params, offset)
            _sm_frame = frame & sst.base_frame
            sh, sw = _sm_frame.shape
            sh = int(sh / 2)
            similarity = mr.normalized_mutual_info_score(_sm_frame[sh-1:sh+1, :].reshape(-1), sst.base_frame[sh-1:sh+1, :].reshape(-1)) * 100
            logger.info(f"seek_start --> {offset} {similarity:.2f}")
            sst.stackstorage.update({offset:similarity})
            sst.sort_stack()
            offset_index_in_stack = list(sst.stackstorage.keys())[list(sst.stackstorage.keys()).index(offset)]
            left_key = offset_index_in_stack - 1
            right_key = offset_index_in_stack + 1
            #<------进行判断 寻找下一个位置或得到最终结果------>
            if similarity >= 85:
                # 修正base_frame
                sst.base_frame = _sm_frame
            #<----增加一个面积的辅助判断---->
            if similarity >= self.similarity_threshold:
                if boxes == "no subtitle":
                    print(f"{offset} {sst.offset_base} 警告！匹配判断与直接判断冲突")
                # 当前帧和base_frame同一字幕 而左侧不是同一字幕 那说明这里是起始帧
                stack_flag = False
                if sst.stackstorage.get(left_key) is not None and sst.stackstorage[left_key] < self.similarity_threshold:
                    sst.offset_start = offset
                    print(f"{offset}是{sst.offset_base}的起始帧 ×√√")
                    find_offset_start = True
                    break
                else:
                    for checked_offset, checked_similarity in sst.stackstorage.items().__reversed__():
                        if checked_similarity < self.similarity_threshold:
                            offset = (checked_offset + offset) // 2
                            stack_flag = True
                            break
                if stack_flag is False:
                    # 认为是同一字幕 需要继续向左搜索
                    offset = offset - self.step
            else:
                # 不是同一字幕 或者没有字幕
                # 先检查之前已经有的结果中 有没有相邻的 
                # 如果有相邻的且匹配程度符合要求 那么就可以认为当前帧是边界 相邻帧是base_frame的起始帧
                stack_flag = False
                if sst.stackstorage.get(right_key) is not None and sst.stackstorage[right_key] >= self.similarity_threshold:
                    sst.offset_start = right_key
                    print(f"{right_key}是{sst.offset_base}的起始帧 ××√")
                    find_offset_start = True
                    break
                else:
                    # 此时offset在字幕区的左侧 寻找一个右侧上限 然后二分 这样能避免重复判断
                    for checked_offset, checked_similarity in sst.stackstorage.items():
                        if checked_similarity >= self.similarity_threshold:
                            offset = (offset + checked_offset) // 2
                            stack_flag = True
                            break
        if find_offset_start:
            return sst.offset_start
        else:
            sys.exit("find_offset_start 失败")
        # print(f"耗时统计 -> {abs(sst.offset_base - offset_init)}帧 {time.time() - ts:.2f}s")
        # cv2.waitKey(0)

def get_params(video_path: Path, offset: int, cbox: list, inrange_params: list = None):
    from util.inrange import only_subtitle, get_canny
    vc = cv2.VideoCapture(str(video_path))
    if vc.isOpened() is False:
        sys.exit(f"Can not open {video_path.name} !")
    vc.set(cv2.CAP_PROP_POS_FRAMES, offset)
    retval, frame = vc.read()
    x, y, w, h = cbox
    # img = get_canny(frame[y:y+h, x:x+w])
    img = only_subtitle(frame[y:y+h, x:x+w], inrange_params=inrange_params, just_return=False)

if __name__ == "__main__":
    # work()
    video_path = Path(r"tests\videos\demo.mp4")
    # get_params(video_path, 15337, [0, 960, 1920, 60], inrange_params=[0, 190, 0, 50, 220, 244])
    # get_params(video_path, 6345, [0, 960, 1920, 60], inrange_params=[0, 180, 0, 15, 180, 244])
    inrange_params = {
        "0:25300": [0, 190, 0, 30, 180, 255],
        # "2530:30038": [0, 190, 0, 50, 220, 244],
        "2530:30038": [0, 180, 0, 15, 180, 244],
    }
    cbox = [0, 960, 1920, 60] # x y w h 
    worker = FWorker(video_path, inrange_params, cbox)
    # worker.work_start(9391, "0:2530")
    worker.work_start(2531, "2530:30038")