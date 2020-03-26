'''
@作者: weimo
@创建日期: 2020-03-26 19:20:50
@上次编辑时间: 2020-03-26 19:21:05
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
from collections import OrderedDict

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