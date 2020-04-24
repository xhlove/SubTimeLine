'''
@作者: weimo
@创建日期: 2020-04-24 18:07:03
@上次编辑时间: 2020-04-24 18:17:36
@一个人的命运啊,当然要靠自我奋斗,但是...
'''

from PyQt5 import QtCore

def DropEnable(CustomWidget):
    class CustomFilter(QtCore.QObject):
        def eventFilter(self, source, event):
            if source == CustomWidget:
                if event.type() in [QtCore.QEvent.DragEnter, QtCore.QEvent.DragMove]:
                    if event.mimeData().hasUrls():
                        event.acceptProposedAction()
                        return True
                    else:
                        event.ignore()
                        return False
                if event.type() == QtCore.QEvent.Drop:
                    paths = [url.toLocalFile() for url in event.mimeData().urls()]
                    source.setText(paths[0])
                    return True
            return False
    if hasattr(CustomWidget, "setAcceptDrops"):
        CustomWidget.setAcceptDrops(True)
    CustomWidget.installEventFilter(CustomFilter(CustomWidget))