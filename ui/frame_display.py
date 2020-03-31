'''
@作者: weimo
@创建日期: 2020-03-31 22:19:17
@上次编辑时间: 2020-03-31 23:34:40
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
import cv2

from PyQt5 import QtWidgets, QtCore, QtGui

class FrameDisplayArea(QtWidgets.QLabel):
    
    def __init__(self, w, cbox: tuple, *args, **kwargs):
        super(FrameDisplayArea, self).__init__(w, *args, **kwargs)
        self.resize_box = None
        self.rect = cbox
        self.setObjectName("frame_display_area")
        self.setGeometry(*self.rect)
        self.setStyleSheet('#frame_display_area {background: #e0f0e9;}')
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(200)#200ms刷新一次

    def paintEvent(self, event):
        super(FrameDisplayArea, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        # painter.setRenderHint(QtGui.QPainter.Antialiasing)
        painter.setPen(QtGui.QPen(QtCore.Qt.red, 3))
        painter.save()
        # painter.setBrush(QtCore.Qt.red)
        painter.drawRect(*self.rect)
        painter.restore()
        painter.end()

    def set_new_rect(self, rect: tuple):
        self.rect = rect

    def show_select_frame(self, _frame, _area):
        _frame_width, _frame_height = _area
        # frame_height, frame_width, channels = frame.shape
        # if frame_width / frame_height > self.width() / self.height():
        #     _frame_width = self.width()
        #     _frame_height = int(frame_height * self.width() / frame_width)
        # else:
        #     _frame_height = self.height()
        #     _frame_width = int(frame_width * self.height() / frame_height)
        # print(f"{frame_width}x{frame_height} -> {_frame_width}x{_frame_height}")
        # _frame = cv2.resize(frame, (_frame_width, _frame_height))
        _frame = QtGui.QImage(_frame, _frame_width, _frame_height, QtGui.QImage.Format_RGB888).rgbSwapped()
        self.setPixmap(QtGui.QPixmap(_frame))
        # img = only_subtitle(frame[y:y+h, x:x+w], inrange_params=inrange_params, just_return=True)