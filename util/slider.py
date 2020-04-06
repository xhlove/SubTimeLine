'''
@作者: weimo
@创建日期: 2020-04-06 13:51:15
@上次编辑时间: 2020-04-06 14:44:52
@一个人的命运啊,当然要靠自我奋斗,但是...
'''

from PyQt5 import QtCore
from ui.gui import PaintQSlider

class 自定义slider(PaintQSlider):

    def __init__(self, slidername: str, sliderbox: tuple, *args, **kwargs):
        super(自定义slider, self).__init__(*args, **kwargs)
        self.setObjectName(slidername)
        self.setGeometry(QtCore.QRect(*sliderbox))