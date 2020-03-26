'''
@作者: weimo
@创建日期: 2020-03-19 21:51:13
@上次编辑时间: 2020-03-26 15:24:30
@一个人的命运啊,当然要靠自我奋斗,但是...
'''

# 寻找字幕
# 通过
from pathlib import Path
from collections import OrderedDict

import cv2
import sys
import time
import numpy as np

MIN_SPACE = 300
MAX_HEIGHT = 60

def filter_box(bboxes: np.ndarray, img: np.ndarray, half_width: float):
    if bboxes.__len__() == 0:
        return bboxes, (0, 0, 0, 0), 0
    # 过滤处理一些box
    xs, ys, ws, hs, _xs, _wh = [], [], [], [], [], []
    _ = [(xs.append(x), ys.append(y), ws.append(x + w), hs.append(y + h), _xs.append([x, x + w]), _wh.append(w / h)) for x, y, w, h in bboxes]
    # if bboxes.__len__() == 1:
    #     max_space = 0 # 在前面处理不会把一些box漏掉 虽然这些box可能比较小
    # else:
    #     max_space = max([_xs[i][0] - _xs[i - 1][1] for i in range(1, _xs.__len__())])
    # 对称性判断 有的字幕不一定对称 暂时不加这个
    data_distances = [(((x + w) / 2) - half_width) / half_width for x, w in zip(xs, ws)]
    if data_distances.__len__() > 2:
        # 全部在一边 也认为是没有字幕的
        _data_distances = np.array(data_distances, dtype="float64")
        zero_reduce = _data_distances[_data_distances < 0].shape[0]
        zero_plus = _data_distances[_data_distances > 0].shape[0]
        if zero_plus == 0 or zero_reduce == 0:
            return (), (0, 0, 0, 0), 0
    # 很近的时候就不用加入了
    data_distances = [abs(_) for _ in data_distances if _ > 0.1]
    if data_distances.__len__() > 1:
        max_distance = np.median(data_distances) * 1.5
        # print(f"data_distances -> {data_distances} max_distance -> {max_distance}")
        remove_indices = [index for index, distance in enumerate(data_distances) if distance > max_distance or _wh[index] > 4]
        bboxes = [box for index, box in enumerate(bboxes) if index not in remove_indices]
    if bboxes.__len__() == 0:
        return bboxes, (0, 0, 0, 0), 0
    if bboxes.__len__() == 1:
        max_space = 0
    if bboxes.__len__() > 1:
        # 只有大于1个box这样做才有意义
        xs, ys, ws, hs, _xs = [], [], [], [], []
        _ = [(xs.append(x), ys.append(y), ws.append(x + w), hs.append(y + h), _xs.append([x, x + w])) for x, y, w, h in bboxes]
        _xs = sorted(_xs, key=lambda x: x[0])
        max_space = max([_xs[i][0] - _xs[i - 1][1] for i in range(1, _xs.__len__())])
    return bboxes, (xs, ys, ws, hs), max_space

def get_mser(img: np.ndarray, frame_index: int, half_width: float, min_area=300, isbase: bool = False):
    box_area = 0
    mser = cv2.MSER_create(_min_area=min_area)
    img = cv2.dilate(img, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    regions, bboxes = mser.detectRegions(img)
    # if frame_index == 9144:
    #     img_bak = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    #     for x, y, w, h in bboxes:
    #         cv2.rectangle(img_bak, (x, y), (x + w, y + h), (255, 255, 0), 2)
    #     cv2.imshow(f"{frame_index}_img_mser_color", img_bak)
    #     cv2.waitKey(0)
    if bboxes.__len__() == 0:
        print(f"{frame_index} box is zero before filter box")
        return "no subtitle", box_area
    bboxes, (xs, ys, ws, hs), max_space = filter_box(bboxes, img.copy(), half_width)
    if bboxes.__len__() == 0:
        print(f"{frame_index} box is zero after filter box")
        return "no subtitle", box_area
    elif bboxes.__len__() == 1:
        if min(xs) < half_width and max(ws) > half_width:
            pass
        else:
            print(f"{frame_index} bboxes 不居中")
            return "no subtitle", box_area
    elif bboxes.__len__() > 1 and max_space > MIN_SPACE:
        print(f"{frame_index} 间隔太远 不符合字幕的特征 {max_space} {xs} {ws}")
        return "no subtitle", box_area
    # 高度占比过低 不符合字幕特征
    if (max(hs) - min(ys)) / MAX_HEIGHT < 0.2:
        print(f"{frame_index} 高度占比过低 不符合字幕特征")
        return "no subtitle", box_area
    box_area = (max(ws) - min(xs)) * (max(hs) - min(ys))
    if isbase and min(xs) - 5 > 0 and min(ys) - 5 > 0:
        x, y, w, h = min(xs) - 5, min(ys) - 5, max(ws) + 5, max(hs) + 5
    else:
        x, y, w, h = min(xs), min(ys), max(ws), max(hs)
    # img_bak = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    # for _x, _y, _w, _h in bboxes:
    #     cv2.rectangle(img_bak, (_x, _y), (_x + _w, _y + _h), (255, 255, 0), 2)
    # cv2.rectangle(img_bak, (x, y), (w, h), (0, 255, 255), 2)
    # cv2.imshow(f"{frame_index}_img_mser_color", img_bak)
    # cv2.waitKey(0)
    # 注意这里返回的w和h已经是实际坐标了
    return (x, y, w, h), box_area

def nothing(x):
    pass

def remove_large_white_area(img: np.ndarray, _erode: int = 10, _dilate: int = 10):
    _img = cv2.erode(img, cv2.getStructuringElement(cv2.MORPH_RECT, (_erode, _erode)))
    _img = cv2.dilate(_img, cv2.getStructuringElement(cv2.MORPH_RECT, (_dilate, _dilate)))
    return img & cv2.bitwise_not(_img)

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

def check_subtitle(frame: np.ndarray, _inrange_params: tuple, frame_index: int, isbase: bool = False):
    # 指定参数做inRange
    hmin, hmax, smin, smax, vmin, vmax = _inrange_params
    img_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    img_inrange = cv2.inRange(img_hsv, np.array([hmin, smin, vmin]), np.array([hmax, smax, vmax]))
    img_inrange = remove_large_white_area(img_inrange)
    # 转灰度图并提取边缘，最后取反
    img_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    img_gray_gaus_canny = cv2.Canny(img_gray, 90, 240)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    img_close = cv2.bitwise_not(cv2.morphologyEx(img_gray_gaus_canny, cv2.MORPH_CLOSE, kernel))
    # 对前面的结果与运算并轻微腐蚀
    img_no_border = cv2.dilate(img_inrange & img_close, cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1)))
    # test_remove_large_white_area(img_no_border)
    # 通过MSER定位字幕
    # if frame_index == 8808:
    #     cv2.imshow("img_hsv", img_hsv)
    #     cv2.imshow("img_inrange", img_inrange)
    #     cv2.imshow("img_gray", img_gray)
    #     cv2.imshow("img_close", img_close)
    #     cv2.imshow("img_no_border", img_no_border)
        # cv2.waitKey(0)
    height, width, channels = frame.shape # 注意这里的frame是彩色的
    box, box_area = get_mser(img_no_border, frame_index, float(width / 2), isbase=isbase)
    return box, box_area, img_no_border

def log_calc_infos(text: str):
    log_path = Path("infos.log").absolute()
    with open(log_path.__str__(), "a+", encoding="utf-8") as f:
        f.write(text + "\n")

class SubStorage(object):
    def __init__(self):
        self.base_frame = None
        self.offset_base = None
        self.offset_start = None
        self.offset_end = None
        self.base_frame_area = None
        self.base_frame_white_counts = None
        # 存当前帧和模板帧的匹配程度
        self.stackstorage = OrderedDict()

    def sort_stack(self):
        keys = sorted(self.stackstorage.keys(), reverse=False)
        self.stackstorage = OrderedDict((key, self.stackstorage[key]) for key in keys)

class Status:
    direction = None
    offset = None
    frame = None
    has_subtitle = None
    start = None
    end = None

class Worker(object):
    def __init__(self, video_path: Path, inrange_params: list, cbox: tuple, offset: int = 0, step: int = 12):
        self.video_path = video_path.absolute()
        self.inrange_params = inrange_params
        self.cbox = cbox
        self.offset = offset
        self.step = step
        self.check()
    
    def check(self):
        self.vc = cv2.VideoCapture(str(self.video_path))
        if self.vc.isOpened() is False:
            sys.exit(f"Can not open {self.video_path.name} !")
        self.total_frames = self.vc.get(cv2.CAP_PROP_FRAME_COUNT)

    def get_inrange_params(self, offset_key: str):
        # 针对单个视频不同时间区域的字幕 提取的设定不一样 注意这里使用的是帧数
        offset_range = (int(_) for _ in offset_key.split(":"))
        hmin, hmax, smin, smax, vmin, vmax = self.inrange_params[offset_key]
        return offset_range, (hmin, hmax, smin, smax, vmin, vmax)

    def get_diff(self, frame: np.ndarray, base_frame: np.ndarray, base_frame_white_counts):
        _base_frame = frame & base_frame
        diff = dict(zip(*np.unique(_base_frame, return_counts=True)))
        # base = dict(zip(*np.unique(base_frame, return_counts=True)))
        # if base.get(255) is None:
        #     sys.exit(f"base_frame没有字幕")
        if diff.get(255) is None:
            return 0.0, _base_frame
        else:
            return float(diff[255] / base_frame_white_counts * 100), _base_frame

    def base_frame_counts(self, base_frame: np.ndarray):
        base_counts = dict(zip(*np.unique(base_frame, return_counts=True)))
        if base_counts.get(255) is None:
            return 0
        return base_counts[255]

    def find_start_frame(self, offset: int, offset_key: str):
        offset_init = offset
        ts = time.time()
        # 寻找字幕起始帧
        cut_x, cut_y, cut_w, cut_h = self.cbox
        (offset_lowwer, offset_upper), inrange_params = self.get_inrange_params(offset_key)
        if offset < offset_lowwer or offset > offset_upper:
            sys.exit(f"{offset} is out of {offset_lowwer} <-> {offset_upper} !")
        sst = SubStorage()
        base_frame = None
        #<----先找到有字幕的帧---->
        while True:
            self.vc.set(cv2.CAP_PROP_POS_FRAMES, offset)
            retval, frame = self.vc.read()
            if retval is False:
                sys.exit(f"retval is False at {offset} ! exit...")
            cv2.imwrite(f"frames/1.jpg", frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w])
            boxes, box_area, frame = check_subtitle(frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w], inrange_params, offset, isbase=True)
            # cv2.imwrite(f"frames/2.jpg", frame)
            if box_area == 0:
                sub_ratio = 0
            else:
                sub_ratio = self.base_frame_counts(frame) / box_area
            if boxes == "no subtitle" or sub_ratio < 0.2:
                offset += self.step
            else:
                x, y, w, h = boxes
                cut_x = cut_x + x
                cut_y = cut_y + y
                cut_w = w - x
                cut_h = h - y
                base_frame = frame[y:h, x:w]
                # cv2.imwrite(f"frames/3.jpg", base_frame)
                sst.base_frame = base_frame
                sst.offset_base = offset
                sst.base_frame_area = box_area
                sst.base_frame_white_counts = self.base_frame_counts(base_frame)
                sst.stackstorage.update({offset:100.0})
                base_frame_offset = offset
                print(f"定位{offset}帧 开始寻找")
                break
        #<-------->
        flag = "start"
        last_status = Status()
        similarity_threshold = 65
        if flag == "start":
            last_status.end = offset
            last_status.start = offset - self.step
            offset = offset - self.step
        while True:
            #<----read frame and get mser boxes---->
            self.vc.set(cv2.CAP_PROP_POS_FRAMES, offset)
            retval, frame = self.vc.read()
            _frame = frame
            if retval is False:
                sys.exit(f"retval is False at {offset} ! exit...")
            boxes, box_area, frame = check_subtitle(frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w], inrange_params, offset)
            similarity, _base_frame = self.get_diff(frame, sst.base_frame, sst.base_frame_white_counts)
            print(f"--> {offset} {similarity:.2f}")
            sst.stackstorage.update({offset:similarity})
            sst.sort_stack()
            offset_index_in_stack = list(sst.stackstorage.keys())[list(sst.stackstorage.keys()).index(offset)]
            left_key = offset_index_in_stack - 1
            right_key = offset_index_in_stack + 1
            #<------进行判断 寻找下一个位置或得到最终结果------>
            if similarity >= 97:
                # 修正base_frame 并重新计数
                sst.base_frame_white_counts = self.base_frame_counts(_base_frame)
                sst.base_frame = _base_frame
            #<----增加一个面积的辅助判断---->
            # _similarity_bak = box_area / sst.base_frame_area
            if similarity >= similarity_threshold:
                if boxes == "no subtitle":
                    print(f"{offset} {sst.offset_base} 警告！匹配判断与直接判断冲突")
                # 当前帧和base_frame同一字幕 而左侧不是同一字幕 那说明这里是起始帧
                stack_flag = False
                if sst.stackstorage.get(left_key) and sst.stackstorage[left_key] < similarity_threshold:
                    sst.offset_start = offset
                    print(f"{offset}是{sst.offset_base}的起始帧 ×√√")
                    cv2.imwrite(f"frames/{sst.offset_start}_start.jpg", sst.base_frame)
                    break
                else:
                    for checked_offset, checked_similarity in sst.stackstorage.items().__reversed__():
                        if checked_similarity < similarity_threshold:
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
                if sst.stackstorage.get(right_key) and sst.stackstorage[right_key] >= similarity_threshold:
                    sst.offset_start = right_key
                    print(f"{right_key}是{sst.offset_base}的起始帧 ××√")
                    # cv2.imwrite(f"frames/{sst.offset_start}_start_{offset}.jpg", frame)
                    cv2.imwrite(f"frames/{sst.offset_start}_start.jpg", sst.base_frame)
                    break
                else:
                    # 此时offset在字幕区的左侧 寻找一个右侧上限 然后二分 这样能避免重复判断
                    for checked_offset, checked_similarity in sst.stackstorage.items():
                        if checked_similarity >= similarity_threshold:
                            offset = (offset + checked_offset) // 2
                            stack_flag = True
                            break
        print(f"耗时统计 -> {abs(sst.offset_base - offset_init)}帧 {time.time() - ts:.2f}s")
        # cv2.waitKey(0)
            # #下面的方案已废弃
            # #<----检查是不是边界---->
            # if boxes == "no subtitle":
            #     if last_status.end - offset == 1:
            #         start_frame = last_status.frame
            #         cv2.imwrite(f"frames/{last_status.offset}_start.jpg", base_frame)
            #         break
            #     else:
            #         last_status.start = offset
            #         offset = (offset + last_status.end) // 2
            # else:
            #     print(f"{offset} has subtitle {similarity}")
            #     if similarity > 50:
            #         last_status.end = offset
            #         offset = offset - self.step
            #         # offset = (last_status.start + offset) // 2
            #     else:
            #         if last_status.end - offset == 1:
            #             # 记录时间起点
            #             start_frame = last_status.frame
            #             # 这样写是以字幕第一帧保存的 可能保存base_frame会好些
            #             cv2.imwrite(f"frames/{last_status.offset}_start.jpg", base_frame)
            #             print(f"break after {offset} and last offset is {last_status.offset}")
            #             break
            #         else:
            #             # cv2.imwrite(f"frames/{offset}_error.jpg", frame)
            #             # cv2.imwrite(f"frames/{offset}_error_color.jpg", _frame)
            #             # print(f"查找字幕首帧失败 第{offset}帧和模板{base_frame_offset}不匹配")
            #             last_status.start = offset
            #             offset = (offset + last_status.end) // 2
                        # break

            #<----set last status in the end---->
            # if boxes == "no subtitle":
            #     last_status.has_subtitle = False
            # else:
            #     last_status.has_subtitle = True
            # last_status.frame = frame
            # last_status.offset = offset_bak

if __name__ == "__main__":
    # work()
    video_path = Path(r"demo.mp4")
    inrange_params = {
        "0:25300": [0, 190, 0, 30, 180, 255],
        "2530:30038": [0, 190, 0, 50, 220, 244],
    }
    cbox = [0, 960, 1920, 60] # x y w h 
    worker = Worker(video_path, inrange_params, cbox)
    # worker.find_start_frame(9391, "0:2530")
    worker.find_start_frame(25286, "2530:30038")