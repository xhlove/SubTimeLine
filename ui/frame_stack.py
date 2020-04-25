'''
@作者: weimo
@创建日期: 2020-04-02 00:03:36
@上次编辑时间: 2020-04-26 00:21:47
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
import cv2
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore

from util.get_params import only_subtitle

class FrameStack(QtWidgets.QLabel):

    def __init__(self, cbox: tuple, *args, **kwargs):
        super(FrameStack, self).__init__(*args, **kwargs)
        self.frame = None
        self.cbox = cbox
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

    @QtCore.pyqtSlot(list)
    def do_inrange(self, params: list):
        frame = only_subtitle(self.frame, inrange_params=params, just_return=True)
        frame_height, frame_width = frame.shape # 这里是二值化后的
        _frame = QtGui.QImage(frame, frame_width, frame_height, QtGui.QImage.Format_Indexed8)
        # self.resize(frame_width, frame_height)
        # cv2.imshow("demo", frame)
        self.setPixmap(QtGui.QPixmap(_frame))

    @QtCore.pyqtSlot(list)
    def do_inrange_in_subtitle_area(self, frame, params: list):
        cut_x, cut_y, cut_w, cut_h = self.cbox
        _hsv = cv2.cvtColor(frame[cut_y:cut_y+cut_h, cut_x:cut_x+cut_w], cv2.COLOR_BGR2HSV)
        hmin, hmax, smin, smax, vmin, vmax = params
        lower_blue = np.array([hmin, smin, vmin])
        upper_blue = np.array([hmax, smax, vmax])
        hsv = cv2.inRange(_hsv, lower_blue, upper_blue)
        hsv = cv2.cvtColor(hsv, cv2.COLOR_GRAY2RGB)
        frame[cut_y:cut_y+hsv.shape[0], cut_x:cut_x+hsv.shape[1]] = hsv
        return frame