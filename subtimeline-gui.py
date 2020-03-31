'''
@作者: weimo
@创建日期: 2020-03-31 13:20:26
@上次编辑时间: 2020-04-01 00:05:58
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
import os
import sys
import cv2
import numpy as np

from pathlib import Path
from PyQt5 import QtCore, QtGui, QtWidgets
from ui.gui import PaintQSlider
from ui.frame_display import FrameDisplayArea
from util.get_params import only_subtitle

ALLOW_VIDEO_SUFFIXS = ["mkv", "mp4", "flv", "ts"]

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
        self.max_frame_to_stack = 5
        self.sliderslabel = {}
        self.设置图标和窗口标题等()
        self.设置图片显示区域()
        self.绘制slider()
        self.设置视频输入路径输入框()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.DragEnter:
            event.accept()
        if event.type() == QtCore.QEvent.Drop:
            md = event.mimeData()
            if md.hasUrls():
                text = md.urls()[0].toLocalFile()
                source.setText(text)
                # if os.path.exists(text) and source.objectName() == "video_path_input_box":
                #     name = os.path.splitext(os.path.split(text)[-1])[0]
                #     self.video_path_input_box.setText(name)
                return True
        return super(GUI, self).eventFilter(source, event)

    def 设置图标和窗口标题等(self):
        self.setWindowTitle("SubTimeLine Control Panel v1.0")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(r"ui\subtimeline.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.setIconSize(QtCore.QSize(32, 32))
        self.setStyleSheet('#MainWindow {background: #eedeb0;}')

    def 绘制slider(self):
        start_x = self.window_width - 500
        start_y = 25
        self.hminslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=1, maximum=360, minimumWidth=360, minimumHeight=75)
        self.hminslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.hminslider.setObjectName("hminslider")
        self.sliderslabel[self.hminslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.hminslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.hminslider.objectName()].setText(f"{self.hminslider.objectName()[:4]}->{self.hminslider.value()}")
        self.sliderslabel[self.hminslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.hminslider.value_update.connect(self.update_slider_label)
        start_y += 50
        self.hmaxslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=1, maximum=360, minimumWidth=360, minimumHeight=75)
        self.hmaxslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.hmaxslider.setObjectName("hmaxslider")
        self.sliderslabel[self.hmaxslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.hmaxslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.hmaxslider.objectName()].setText(f"{self.hmaxslider.objectName()[:4]}->{self.hmaxslider.value()}")
        self.sliderslabel[self.hmaxslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.hmaxslider.value_update.connect(self.update_slider_label)
        start_y += 50
        self.sminslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=1, maximum=255, minimumWidth=360, minimumHeight=75)
        self.sminslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.sminslider.setObjectName("sminslider")
        self.sliderslabel[self.sminslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.sminslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.sminslider.objectName()].setText(f"{self.sminslider.objectName()[:4]}->{self.sminslider.value()}")
        self.sliderslabel[self.sminslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.sminslider.value_update.connect(self.update_slider_label)
        start_y += 50
        self.smaxslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=1, maximum=255, minimumWidth=360, minimumHeight=75)
        self.smaxslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.smaxslider.setObjectName("smaxslider")
        self.sliderslabel[self.smaxslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.smaxslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.smaxslider.objectName()].setText(f"{self.smaxslider.objectName()[:4]}->{self.smaxslider.value()}")
        self.sliderslabel[self.smaxslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.smaxslider.value_update.connect(self.update_slider_label)
        start_y += 50
        self.vminslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=1, maximum=255, minimumWidth=360, minimumHeight=75)
        self.vminslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.vminslider.setObjectName("vminslider")
        self.sliderslabel[self.vminslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.vminslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.vminslider.objectName()].setText(f"{self.vminslider.objectName()[:4]}->{self.vminslider.value()}")
        self.sliderslabel[self.vminslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.vminslider.value_update.connect(self.update_slider_label)
        start_y += 50
        self.vmaxslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=1, maximum=255, minimumWidth=360, minimumHeight=75)
        self.vmaxslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.vmaxslider.setObjectName("vmaxslider")
        self.sliderslabel[self.vmaxslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.vmaxslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.vmaxslider.objectName()].setText(f"{self.vmaxslider.objectName()[:4]}->{self.vmaxslider.value()}")
        self.sliderslabel[self.vmaxslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.vmaxslider.value_update.connect(self.update_slider_label)
        start_y += 50
        self.videoframeslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=0, maximum=0, minimumWidth=360, minimumHeight=75)
        self.videoframeslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.videoframeslider.setObjectName("videoframeslider")
        self.sliderslabel[self.videoframeslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.videoframeslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.videoframeslider.objectName()].setText(f"frames->{self.videoframeslider.value()}")
        self.sliderslabel[self.videoframeslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.videoframeslider.custom_name = "frames"
        self.videoframeslider.value_update.connect(self.update_slider_label)
        self.videoframeslider.show_frame.connect(self.select_frame)
        start_y += 50
        self.cutxslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=0, maximum=1920, minimumWidth=360, minimumHeight=75)
        self.cutxslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.cutxslider.setObjectName("cutxslider")
        self.sliderslabel[self.cutxslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.cutxslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.cutxslider.objectName()].setText(f"{self.cutxslider.objectName()[:4]}->{self.cutxslider.value()}")
        self.sliderslabel[self.cutxslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.cutxslider.value_update.connect(self.update_slider_label)
        start_y += 50
        self.cutyslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=0, maximum=1280, minimumWidth=360, minimumHeight=75)
        self.cutyslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.cutyslider.setObjectName("cutyslider")
        self.sliderslabel[self.cutyslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.cutyslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.cutyslider.objectName()].setText(f"{self.cutyslider.objectName()[:4]}->{self.cutyslider.value()}")
        self.sliderslabel[self.cutyslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.cutyslider.value_update.connect(self.update_slider_label)
        start_y += 50
        self.cutwslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=0, maximum=self.cutxslider.maximum(), minimumWidth=360, minimumHeight=75)
        self.cutwslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.cutwslider.setObjectName("cutwslider")
        self.sliderslabel[self.cutwslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.cutwslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.cutwslider.objectName()].setText(f"{self.cutwslider.objectName()[:4]}->{self.cutwslider.value()}")
        self.sliderslabel[self.cutwslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.cutwslider.value_update.connect(self.update_slider_label)
        start_y += 50
        self.cuthslider = PaintQSlider(QtCore.Qt.Horizontal, self, minimum=0, maximum=self.cutyslider.maximum(), minimumWidth=360, minimumHeight=75)
        self.cuthslider.setGeometry(QtCore.QRect(start_x, start_y, 360, 75))
        self.cuthslider.setObjectName("cuthslider")
        self.sliderslabel[self.cuthslider.objectName()] = QtWidgets.QLabel(self)
        self.sliderslabel[self.cuthslider.objectName()].setGeometry(start_x + 365, start_y, 130, 75)
        self.sliderslabel[self.cuthslider.objectName()].setText(f"{self.cuthslider.objectName()[:4]}->{self.cuthslider.value()}")
        self.sliderslabel[self.cuthslider.objectName()].setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignVCenter)
        self.cuthslider.value_update.connect(self.update_slider_label)

    def 设置图片显示区域(self):
        x = 40
        y = 25
        w = self.window_width - 500 - x * 2
        h = w * 9 / 16
        self.frame_display_area = FrameDisplayArea(self, (x, y, w, h))

    def 设置加载视频按钮(self, box_area: list):
        box_x, box_y, box_w, box_h = box_area
        self.load_video_button = QtWidgets.QPushButton(self)
        self.load_video_button.setGeometry(QtCore.QRect(box_x, box_y, box_w, box_h))
        self.load_video_button.setObjectName("load_video_button")
        self.load_video_button.setText("加载视频")
        self.load_video_button.clicked.connect(self.load_video)
        self.select_frame_button = QtWidgets.QPushButton(self)
        self.select_frame_button.setGeometry(QtCore.QRect(box_x + box_w + 10, box_y, box_w, box_h))
        self.select_frame_button.setObjectName("select_frame_button")
        self.select_frame_button.setText("选定当前帧")
        self.select_frame_button.clicked.connect(self.select_frame)

    def 设置视频输入路径输入框(self):
        box_x = 40
        box_y = self.window_height - 50
        box_w = self.window_width - box_x * 2 - 200
        box_h = 40
        self.video_path_input_box = QtWidgets.QLineEdit(self)
        self.video_path_input_box.setGeometry(QtCore.QRect(box_x, box_y, box_w, box_h))
        self.video_path_input_box.setObjectName("video_path_input_box")
        self.video_path_input_box.setAcceptDrops(True)
        self.video_path_input_box.installEventFilter(self)
        box_area = [box_x + box_w + 10, box_y, 100, box_h]
        self.设置加载视频按钮(box_area)

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
            self.show_debug_info(f"{video_path.name} 加载成功 共计{vc.get(cv2.CAP_PROP_FRAME_COUNT)}帧")
            self.videoframeslider.setMaximum(vc.get(cv2.CAP_PROP_FRAME_COUNT))
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
            self.vc = vc
        # vc.set(cv2.CAP_PROP_POS_FRAMES, 6668)
        # retval, frame = vc.read()
        # cv2.imshow("frame", frame)
        # cv2.waitKey(0)

    def select_frame(self, *args):
        if self.vc is None:
            self.show_debug_info(f"没有加载视频")
            return
        frame_index = self.videoframeslider.value()
        self.vc.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        retval, frame = self.vc.read()
        _frame = cv2.resize(frame, self.frame_display_area.resize_box[1])
        self.frame_display_area.show_select_frame(_frame, self.frame_display_area.resize_box[1])
        if args.__len__() == 1 and args[0] is False:
            self.cut_frame_to_concat(frame)

    def cut_frame_to_concat(self, frame: np.ndarray):
        if self.max_frame_to_stack <= 0:
            self.show_debug_info(f"已达到上限")
            return
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

    @QtCore.pyqtSlot(str)
    def show_debug_info(self, text):
        print(f"debug -> {text}")

    @QtCore.pyqtSlot(int, str, str)
    def update_slider_label(self, value: int, name: str, custom_name: str):
        if custom_name:
            self.sliderslabel[name].setText(f"{custom_name}->{value}")
        else:
            self.sliderslabel[name].setText(f"{name[:4]}->{value}")
        if name in ["cutxslider", "cutyslider", "cutwslider", "cuthslider"]:
            x, y, w, h = self.frame_display_area.geometry().getRect()
            rect = self.cutxslider.value(), self.cutyslider.value(), self.cutwslider.value(), self.cuthslider.value()
            self.frame_display_area.set_new_rect(rect)

class FrameStack(QtWidgets.QLabel):

    def __init__(self, cbox: tuple, *args, **kwargs):
        super(FrameStack, self).__init__(*args, **kwargs)
        self.frame = None
        self.cut_x, self.cut_y, self.cut_w, self.cut_h = cbox
        self.设置图标和窗口标题等()

    def append(self, frame: np.ndarray):
        frame = frame[self.cut_y:self.cut_y+self.cut_h, self.cut_x:self.cut_x+self.cut_w]
        self.frame = np.vstack((self.frame, frame))
        frame_height, frame_width, channels = self.frame.shape
        _frame = QtGui.QImage(self.frame, frame_width, frame_height, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.resize(frame_width, frame_height)
        self.setPixmap(QtGui.QPixmap(_frame))

    def show_with_first_frame(self, frame: np.ndarray):
        frame = frame[self.cut_y:self.cut_y+self.cut_h, self.cut_x:self.cut_x+self.cut_w]
        self.frame = frame
        frame_height, frame_width, channels = self.frame.shape
        _frame = QtGui.QImage(frame, frame_width, frame_height, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.setGeometry(0, 0, frame_width, frame_height)
        self.setPixmap(QtGui.QPixmap(_frame))
        self.show()

    def 设置图标和窗口标题等(self):
        self.setWindowTitle("SubTimeLine FrameStack")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(r"ui\subtimeline.ico"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        # self.setIconSize(QtCore.QSize(32, 32))
        self.setStyleSheet('#MainWindow {background: #eedeb0;}')

def main():
    app = QtWidgets.QApplication(sys.argv)
    gui = GUI()
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()