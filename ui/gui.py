'''
@作者: weimo
@创建日期: 2020-03-31 13:20:09
@上次编辑时间: 2020-04-06 20:06:31
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
from PyQt5.QtCore import Qt, QRect, QPointF, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QPen
from PyQt5.QtWidgets import QSlider, QProxyStyle, QStyle, QStyleOptionSlider, QLabel


class SliderStyle(QProxyStyle):

    def subControlRect(self, control, option, subControl, widget=None):
        rect = super(SliderStyle, self).subControlRect(
            control, option, subControl, widget)
        if subControl == QStyle.SC_SliderHandle:
            if option.orientation == Qt.Horizontal:
                # 高度1/3
                radius = int(widget.height() / 3)
                offset = int(radius / 3)
                if option.state & QStyle.State_MouseOver:
                    x = min(rect.x() - offset, widget.width() - radius)
                    x = x if x >= 0 else 0
                else:
                    radius = offset
                    x = min(rect.x(), widget.width() - radius)
                rect = QRect(x, int((rect.height() - radius) / 2),
                             radius, radius)
            else:
                # 宽度1/3
                radius = int(widget.width() / 3)
                offset = int(radius / 3)
                if option.state & QStyle.State_MouseOver:
                    y = min(rect.y() - offset, widget.height() - radius)
                    y = y if y >= 0 else 0
                else:
                    radius = offset
                    y = min(rect.y(), widget.height() - radius)
                rect = QRect(int((rect.width() - radius) / 2),
                             y, radius, radius)
            return rect
        return rect


class PaintQSlider(QSlider):
    show_frame = pyqtSignal()
    value_update = pyqtSignal(int, str, str)
    def __init__(self, *args, **kwargs):
        super(PaintQSlider, self).__init__(*args, **kwargs)
        self.custom_name = ""
        self.drawtext = True
        self.show_frame_real_time = False
        # 设置代理样式,主要用于计算和解决鼠标点击区域
        self.setStyle(SliderStyle())

    def mousePressEvent(self, event):
        # 获取上面的拉动块位置
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        rect = self.style().subControlRect(QStyle.CC_Slider, option, QStyle.SC_SliderHandle, self)
        if rect.contains(event.pos()):
            # 如果鼠标点击的位置在滑块上则交给Qt自行处理
            super(PaintQSlider, self).mousePressEvent(event)
            return
        if self.orientation() == Qt.Horizontal:
            # 横向，要考虑invertedAppearance是否反向显示的问题
            self.setValue(self.style().sliderValueFromPosition(self.minimum(), self.maximum(), event.x() if not self.invertedAppearance() else (self.width() - event.x()), self.width()))
        else:
            # 纵向
            self.setValue(self.style().sliderValueFromPosition(self.minimum(), self.maximum(), (self.height() - event.y()) if not self.invertedAppearance() else event.y(), self.height()))

    def paintEvent(self, _):
        option = QStyleOptionSlider()
        self.initStyleOption(option)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 中间圆圈的位置
        rect = self.style().subControlRect(QStyle.CC_Slider, option, QStyle.SC_SliderHandle, self)

        # 画中间白色线条
        painter.setPen(QPen(Qt.white, 3))
        # painter.setBrush(Qt.red)
        if self.orientation() == Qt.Horizontal:
            y = self.height() / 2
            painter.drawLine(QPointF(0, y), QPointF(self.width(), y))
        else:
            x = self.width() / 2
            painter.drawLine(QPointF(x, 0), QPointF(x, self.height()))
        # 画圆
        painter.setPen(Qt.NoPen)
        if option.state & QStyle.State_MouseOver:  # 双重圆
            # 半透明大圆
            r = rect.height() / 2
            painter.setBrush(QColor(255, 255, 255, 100))
            painter.drawRoundedRect(rect, r, r)
            # 实心小圆(上下左右偏移4)
            rect = rect.adjusted(4, 4, -4, -4)
            r = rect.height() / 2
            painter.setBrush(QColor(255, 255, 255, 255))
            painter.drawRoundedRect(rect, r, r)
            if self.drawtext:
                # 绘制文字
                painter.setPen(QPen(Qt.red, 3))
                width_should_sub = self.get_value_length()
                if self.orientation() == Qt.Horizontal:  # 在上方绘制文字
                    x, y = rect.x() - width_should_sub // 2, rect.y() - rect.height() - 4
                else:  # 在左侧绘制文字
                    x, y = rect.x() - rect.width() - 4, rect.y()
                painter.drawText(x, y, rect.width() + width_should_sub, rect.height(), Qt.AlignCenter, str(self.value()))
        else:  # 实心圆
            r = rect.height() / 2
            painter.setBrush(Qt.white)
            painter.drawRoundedRect(rect, r, r)
        self.value_update.emit(self.value(), self.objectName(), self.custom_name)
        if self.show_frame_real_time:
            # 实时更新图像
            self.show_frame.emit()

    def get_value_length(self):
        label = QLabel()
        label.setText(str(self.value()))
        width = label.fontMetrics().boundingRect(label.text()).width()
        return width