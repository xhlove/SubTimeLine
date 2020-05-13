'''
@作者: weimo
@创建日期: 2020-03-31 13:20:26
@上次编辑时间: 2020-05-13 14:10:24
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
import os
import sys
import cv2
import numpy as np

from datetime import datetime
from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QPainter, QColor, QPen
from ui.gui import PaintQSlider
from ui.frame_display import FrameDisplayArea
from ui.frame_stack import FrameStack
from ui.dropfile import DropEnable
from util.inrange import convert_img_hsv_with_inrange
from util.transfer import load_config as load_inrange_config, save_custom_inrange_params

from subtimeline import FWorker

ALLOW_VIDEO_SUFFIXS = ["mkv", "mp4", "flv", "ts"]

def frame_index_to_time(frame_index: int, fps: float):
    return datetime.utcfromtimestamp(frame_index / fps).strftime('%H:%M:%S')

def 获取默认窗口大小():
    desktop = QtWidgets.QApplication.desktop()
    print(desktop.width(), desktop.height())
    return desktop.width() // 1.8, desktop.height() // 2.2

class GUI(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(GUI, self).__init__(*args, **kwargs)
        self.window_width, self.window_height = 获取默认窗口大小()
        self.setObjectName("MainWindow")
        self.resize(self.window_width, self.window_height)
        # self.centralwidget = QtWidgets.QWidget(self)
        # self.centralwidget.setObjectName("centralwidget")
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.vc = None
        self.iconfig = {}
        self.video_fps = None
        self.video_path = Path()
        self.has_frame_stack = False
        self.max_frame_to_stack = 5
        self.select_frame_is_locked = False
        self.sliderslabel = {}
        self.设置图标和窗口标题等()
        self.设置图片显示区域()
        self.绘制slider()
        self.设置视频输入路径输入框()

    def 设置图标和窗口标题等(self):
        self.setWindowTitle("SubTimeLine Control Panel v1.0")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(r"ui\subtimeline.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setStyleSheet('#MainWindow {background: #eedeb0;}')

    def 设定slider(self, slidername: str, initargs: dict, sliderbox: tuple, sliderlabelbox: tuple, customtext: str = None):
        slider = PaintQSlider(QtCore.Qt.Horizontal, self, **initargs)
        slider.setObjectName(slidername)
        # slider.setGeometry(QtCore.QRect(*sliderbox))
        # self.layout().addWidget(slider)
        setattr(self, slidername, slider)
        slider = self.findChild((PaintQSlider,), slidername)
        slider.setGeometry(QtCore.QRect(*sliderbox))
        self.sliderslabel[slider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[slider.objectName()].setGeometry(*sliderlabelbox)
        self.sliderslabel[slider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        if customtext is None:
            self.sliderslabel[slider.objectName()].setText(f"{slider.objectName()[:4]}->{slider.value()}")
        else:
            self.sliderslabel[slider.objectName()].setText(customtext)
        slider.value_update.connect(self.update_slider_label)

    def 绘制slider(self):
        
        sliderinitargs = {
            "timeslider": {"minimum": 0, "maximum": 0, "minimumWidth": 0, "minimumHeight": 30},
            "hminslider": {"minimum": 0, "maximum": 360, "minimumWidth": 360, "minimumHeight": 75},
            "hmaxslider": {"minimum": 0, "maximum": 360, "minimumWidth": 360, "minimumHeight": 75},
            "sminslider": {"minimum": 0, "maximum": 255, "minimumWidth": 360, "minimumHeight": 75},
            "smaxslider": {"minimum": 0, "maximum": 255, "minimumWidth": 360, "minimumHeight": 75},
            "vminslider": {"minimum": 0, "maximum": 255, "minimumWidth": 360, "minimumHeight": 75},
            "vmaxslider": {"minimum": 0, "maximum": 255, "minimumWidth": 360, "minimumHeight": 75},
            "cutxslider": {"minimum": 0, "maximum": 1920, "minimumWidth": 360, "minimumHeight": 75},
            "cutyslider": {"minimum": 0, "maximum": 1080, "minimumWidth": 360, "minimumHeight": 75},
            "cutwslider": {"minimum": 0, "maximum": 1920, "minimumWidth": 360, "minimumHeight": 75},
            "cuthslider": {"minimum": 0, "maximum": 1080, "minimumWidth": 360, "minimumHeight": 75},
        }
        x, y, w, h = self.frame_display_area.geometry().getRect()        
        self.设定slider("timeslider", sliderinitargs["timeslider"], (x, y + h, w - 160, 30), (x + w - 160, y + h, 160, 30), customtext="time->00:00:00")
        self.timeslider.custom_name = "time"
        self.timeslider.drawtext = False
        self.timeslider.show_frame_real_time = True
        self.timeslider.show_frame.connect(self.select_frame)
        start_x = self.window_width - 500
        start_y = 25
        self.设定slider("hminslider", sliderinitargs["hminslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))
        start_y += 50
        self.设定slider("hmaxslider", sliderinitargs["hmaxslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))
        start_y += 50
        self.设定slider("sminslider", sliderinitargs["sminslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))
        start_y += 50
        self.设定slider("smaxslider", sliderinitargs["smaxslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))
        start_y += 50
        self.设定slider("vminslider", sliderinitargs["vminslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))
        start_y += 50
        self.设定slider("vmaxslider", sliderinitargs["vmaxslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))
        start_y += 50
        self.设定slider("cutxslider", sliderinitargs["cutxslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))
        start_y += 50
        self.设定slider("cutyslider", sliderinitargs["cutyslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))
        start_y += 50
        sliderinitargs["cutwslider"]["maximum"] = self.cutxslider.maximum()
        self.设定slider("cutwslider", sliderinitargs["cutwslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))
        start_y += 50
        sliderinitargs["cutwslider"]["maximum"] = self.cutyslider.maximum()
        self.设定slider("cuthslider", sliderinitargs["cuthslider"], (start_x, start_y, 360, 75), (start_x + 365, start_y, 130, 75))

    def 设置图片显示区域(self):
        x = 40
        y = 25
        w = self.window_width - 500 - x * 2
        h = w * 9 / 16
        self.frame_display_area = FrameDisplayArea(self, (x, y, w, h))

    def 设置加载视频按钮等(self, box_area: list):
        box_x, box_y, box_w, box_h = box_area
        self.load_video_button = QtWidgets.QPushButton(self)
        self.load_video_button.setGeometry(QtCore.QRect(box_x, box_y, box_w, box_h))
        self.load_video_button.setObjectName("load_video_button")
        self.load_video_button.setText("加载视频")
        self.load_video_button.clicked.connect(self.load_video)
        self.save_inrange_params_button = QtWidgets.QPushButton(self)
        self.save_inrange_params_button.setGeometry(QtCore.QRect(box_x, box_y - 10 - box_h, box_w, box_h))
        self.save_inrange_params_button.setObjectName("save_inrange_params_button")
        self.save_inrange_params_button.setText("保存参数")
        self.save_inrange_params_button.clicked.connect(self.save_inrange_params)
        self.worker_button = QtWidgets.QPushButton(self)
        self.worker_button.setGeometry(QtCore.QRect(box_x - box_w - 10, box_y - 10 - box_h, box_w, box_h))
        self.worker_button.setObjectName("worker_button")
        self.worker_button.setText("开始提取")
        self.worker_button.clicked.connect(self.do_work)
        self.select_frame_button = QtWidgets.QPushButton(self)
        self.select_frame_button.setGeometry(QtCore.QRect(box_x + box_w + 10, box_y, box_w, box_h))
        self.select_frame_button.setObjectName("select_frame_button")
        self.select_frame_button.setText("选定当前帧")
        self.select_frame_button.clicked.connect(self.select_frame)
        self.find_inrange_params_button = QtWidgets.QPushButton(self)
        self.find_inrange_params_button.setGeometry(QtCore.QRect(box_x + box_w + 10, box_y - 10 - box_h, box_w, box_h))
        self.find_inrange_params_button.setObjectName("find_inrange_params_button")
        self.find_inrange_params_button.setText("二值化调整")
        self.find_inrange_params_button.clicked.connect(self.lock_and_connect)
        # 加载配置
        self.iconfig, config_path = load_inrange_config()

    def save_inrange_params(self):
        if self.video_path.is_dir():
            self.show_debug_info("还没有加载视频~")
            return
        if self.video_path.suffix[1:] not in ALLOW_VIDEO_SUFFIXS:
            self.show_debug_info(f"{self.video_path.name} 后缀非法！")
            return
        params = [
            self.hminslider.value(),
            self.hmaxslider.value(),
            self.sminslider.value(),
            self.smaxslider.value(),
            self.vminslider.value(),
            self.vmaxslider.value()
        ]
        save_custom_inrange_params(params, str(self.video_path.name))
        return params
    
    def lock_and_connect(self):
        if self.select_frame_is_locked is True:
            self.show_debug_info(f"选定当前帧已经被锁定过了")
            return
        self.select_frame_is_locked = True
        self.setslidersvalue()
        # 首次点击按钮时就执行二值化操作
        self.find_inrange_params()

    @QtCore.pyqtSlot(int)
    def goto_subtitle_frame(self, frame_index: int):
        self.timeslider.setValue(frame_index)
        # self.select_frame(show_sub_inrange=True)

    def do_work(self):
        inrange_params = self.save_inrange_params()
        self.worker = FWorker(self.video_path, {f"0:{self.timeslider.maximum()}": inrange_params}, self.frame_stack.cbox)
        self.worker.inrange_params_list = inrange_params
        self.worker.progress_frame.connect(self.goto_subtitle_frame)
        self.timeslider.show_frame.disconnect(self.select_frame)
        self.worker.start_params = [0, f"0:{self.timeslider.maximum()}"]
        self.worker.start()

    def setslidersvalue(self, video_name="", connect=True):
        if self.iconfig.get(video_name) is None:
            video_name = "default"
        for name, value in zip(["hmin", "hmax", "smin", "smax", "vmin", "vmax"], self.iconfig[video_name]):
            slider = self.findChild((PaintQSlider,), name + "slider")
            slider.setValue(value)
            if connect:
                slider.valueChanged.connect(self.find_inrange_params)

    def 设置视频输入路径输入框(self):
        box_x = 40
        box_y = self.window_height - 50
        box_w = self.window_width - box_x * 2 - 200
        box_h = 40
        self.video_path_input_box = QtWidgets.QLineEdit(self)
        self.video_path_input_box.setGeometry(QtCore.QRect(box_x, box_y, box_w, box_h))
        self.video_path_input_box.setObjectName("video_path_input_box")
        DropEnable(self.video_path_input_box)
        box_area = [box_x + box_w + 10, box_y, 100, box_h]
        self.设置加载视频按钮等(box_area)

    def load_video(self):
        video_path = Path(self.video_path_input_box.text())
        if video_path.exists() and video_path.suffix[1:] in ALLOW_VIDEO_SUFFIXS:
            pass
        else:
            self.show_debug_info("非法后缀或视频不存在")
            return
        vc = cv2.VideoCapture(str(video_path))
        if vc.isOpened() is False:
            self.show_debug_info(f"无法打开 {video_path.name} !")
            return
        else:
            self.video_path = video_path
            if self.iconfig.get(str(self.video_path.name)):
                self.setslidersvalue(connect=False)
            self.video_fps = vc.get(cv2.CAP_PROP_FPS)
            total_frames = vc.get(cv2.CAP_PROP_FRAME_COUNT)
            self.show_debug_info(f"{self.video_path.name} 加载成功 共计{total_frames}帧")
            self.timeslider.setMaximum(total_frames)
            #<---计算缩放前后大小 方便后续转换要剪切的区域--->
            video_width, video_height = vc.get(cv2.CAP_PROP_FRAME_WIDTH), vc.get(cv2.CAP_PROP_FRAME_HEIGHT)
            if video_width / video_height > self.frame_display_area.width() / self.frame_display_area.height():
                _frame_width = self.frame_display_area.width()
                _frame_height = int(video_height * self.frame_display_area.width() / video_width)
            else:
                _frame_height = self.frame_display_area.height()
                _frame_width = int(video_width * self.frame_display_area.height() / video_height)
            self.frame_display_area.resize_box = ((video_width, video_height), (_frame_width, _frame_height))            
            # self.cutxslider.setMaximum(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
            # self.cutyslider.setMaximum(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
            self.cutxslider.setMaximum(self.frame_display_area.width())
            self.cutyslider.setMaximum(self.frame_display_area.height())
            self.cutwslider.setMaximum(self.cutxslider.maximum())
            self.cuthslider.setMaximum(self.cutyslider.maximum())
            # 设置一个默认范围
            self.cutxslider.setValue(0)
            self.cutyslider.setValue(self.frame_display_area.height() * 0.8)
            self.cutwslider.setValue(self.cutxslider.maximum())
            self.cuthslider.setValue(self.cutyslider.maximum() * 0.15)
            self.vc = vc
        # vc.set(cv2.CAP_PROP_POS_FRAMES, 6668)
        # retval, frame = vc.read()
        # cv2.imshow("frame", frame)
        # cv2.waitKey(0)

    def select_frame(self, *args, **kwargs):
        if self.vc is None:
            self.show_debug_info(f"没有加载视频")
            return
        frame_index = self.timeslider.value()
        self.vc.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        retval, frame = self.vc.read()
        if kwargs.get("show_sub_inrange") is True:
            frame = self.frame_stack.do_inrange_in_subtitle_area(frame, self.worker.inrange_params_list)
        _frame = cv2.resize(frame, self.frame_display_area.resize_box[1])
        self.frame_display_area.show_select_frame(_frame, self.frame_display_area.resize_box[1])
        if self.max_frame_to_stack <= 0:
            self.show_debug_info(f"已达到上限")
            return
        if self.select_frame_is_locked:
            self.show_debug_info(f"禁止新增选定帧")
            return
        if args.__len__() == 1 and args[0] is False:
            self.has_frame_stack = True
            self.cut_frame_to_concat(frame)

    def cut_frame_to_concat(self, frame: np.ndarray):
        if self.max_frame_to_stack == 5:
            # 第一次 则生成一个部件
            (video_width, video_height), (_frame_width, _frame_height) = self.frame_display_area.resize_box
            x = int(self.cutxslider.value() * video_width / _frame_width)
            y = int(self.cutyslider.value() * video_height / _frame_height)
            w = int(self.cutwslider.value() * video_width / _frame_width)
            h = int(self.cuthslider.value() * video_height / _frame_height)
            cbox = x, y, w, h
            # cbox = self.cutxslider.value(), self.cutyslider.value(), self.cutwslider.value(), self.cuthslider.value()
            self.frame_stack = FrameStack(cbox)
            self.frame_stack.show_with_first_frame(frame)
        else:
            self.frame_stack.append(frame)
        self.max_frame_to_stack -= 1

    def find_inrange_params(self):
        if self.has_frame_stack is False:
            return
        params = [
            self.hminslider.value(),
            self.hmaxslider.value(),
            self.sminslider.value(),
            self.smaxslider.value(),
            self.vminslider.value(),
            self.vmaxslider.value()
        ]
        self.frame_stack.do_inrange(params)

    @QtCore.pyqtSlot(str)
    def show_debug_info(self, text):
        print(f"debug -> {text}")

    @QtCore.pyqtSlot(int, str, str)
    def update_slider_label(self, value: int, name: str, custom_name: str):
        if custom_name:
            if custom_name == "time":
                if self.video_fps is None:
                    value = "00:00:00"
                else:
                    # 帧数转时间
                    value = frame_index_to_time(value, self.video_fps)
            self.sliderslabel[name].setText(f"{custom_name}->{value}")
        else:
            self.sliderslabel[name].setText(f"{name[:4]}->{value}")
        if name in ["cutxslider", "cutyslider", "cutwslider", "cuthslider"]:
            x, y, w, h = self.frame_display_area.geometry().getRect()
            rect = self.cutxslider.value(), self.cutyslider.value(), self.cutwslider.value(), self.cuthslider.value()
            self.frame_display_area.set_new_rect(rect)

def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()