'''
@作者: weimo
@创建日期: 2020-03-26 19:17:52
@上次编辑时间: 2020-03-29 10:19:46
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
import cv2
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

def get_mser(img: np.ndarray, frame_index: int, shape: tuple, min_area=300, isbase: bool = False):
    height, width, channels = shape # 注意这里的frame是彩色的
    half_width = width / 2
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
    if isbase and min(xs) - 5 > 0 and min(ys) - 5 > 0 and max(ws) + 5 < width and max(hs) + 5 < height:
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