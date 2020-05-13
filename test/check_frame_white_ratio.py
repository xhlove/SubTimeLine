'''
@作者: weimo
@创建日期: 2020-05-12 14:33:11
@上次编辑时间: 2020-05-13 19:48:57
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
import os
import sys
sys.path.append(os.getcwd())

import cv2

from pathlib import Path

from util.calc import get_white_ratio
from util.act import find_subtitle_box

if __name__ == "__main__":
    scale = True
    scale_height = 360
    offset = 3020
    cbox = [0, 960, 1920, 60]
    inrange_params = [0, 180, 0, 15, 180, 244]
    video_path = Path(r"tests\videos\demo.mp4")
    
    offset = 96
    cbox = [0, 610, 1280, 60]
    inrange_params = [0, 180, 0, 28, 210, 255]
    video_path = Path(r"tests\videos\下辈子我再好好过.Raise.de.wa.Chanto.Shimasu.Ep01.Chi_Jap.WEBrip.1280X720-ZhuixinFan.mp4")

    vc = cv2.VideoCapture(str(video_path))
    vc.set(cv2.CAP_PROP_POS_FRAMES, offset)
    if scale:
        scale_ratio = scale_height / vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
        vw = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH) * scale_ratio)
        vh = scale_height
    else:
        scale_ratio = 1.0
        vw = vc.get(cv2.CAP_PROP_FRAME_WIDTH)
        vh = vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
    cbox = [int(_ * scale_ratio) for _ in cbox]
    cut_x, cut_y, cut_w, cut_h = cbox
    print(cbox, "缩放后剪裁区域", scale_height, scale_ratio, f"{vw}x{vh}")
    retval, frame = vc.read()
    cv2.imshow(f"frame origin {scale_ratio}",frame)
    if scale:
        frame = cv2.resize(frame, (vw, vh))
    cv2.imshow(f"frame after scale_ratio {scale_ratio}", frame)
    cv2.imshow(f"frame cut", frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w])
    boxes, frame_subtitle = find_subtitle_box(frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w], inrange_params, offset, isbase=True)
    print(boxes)
    if type(boxes) == tuple:
        x, y, w, h = boxes
        cv2.imshow(f"frame_subtitle_{boxes}", frame_subtitle[y:h, x:w])
        ratio = get_white_ratio(frame_subtitle[y:h, x:w])
        print(ratio)
    cv2.waitKey(0)