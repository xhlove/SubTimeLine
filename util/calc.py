'''
@作者: weimo
@创建日期: 2020-05-13 11:17:35
@上次编辑时间: 2020-05-13 11:17:53
@一个人的命运啊,当然要靠自我奋斗,但是...
'''

import numpy as np

def get_white_ratio(img: np.ndarray):
    # 统计白色（255）占比
    counts = dict(zip(*np.unique(img, return_counts=True)))
    if counts.get(255) is None:
        return 0.0
    return float(counts[255] / img.size)