'''
@作者: weimo
@创建日期: 2020-05-11 19:32:47
@上次编辑时间: 2020-05-11 19:34:03
@一个人的命运啊,当然要靠自我奋斗,但是...
'''

from pathlib import Path

def write_ass_line(text: str):
    log_path = Path(r"test\out.ass").absolute()
    with open(log_path.__str__(), "a+", encoding="utf-8") as f:
        f.write(text + "\n")