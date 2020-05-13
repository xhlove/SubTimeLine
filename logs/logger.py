'''
@作者: weimo
@创建日期: 2020-05-12 14:17:52
@上次编辑时间: 2020-05-13 19:27:12
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
from pathlib import Path

import logging

# def get_logger(filename: Path):
#     # 这种不适用于同一个脚本中输出两个日志文件
#     logging.basicConfig(
#         handlers=[
#             logging.FileHandler(filename=str(filename.absolute()), encoding='utf-8'),
#             logging.StreamHandler()
#         ],
#         level=logging.INFO,
#         format="%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s",
#         datefmt="[%Y-%m_%d %H:%M:%S]"
#     )
#     logger = logging.getLogger(filename.stem)    
#     return logger

def get_logger(filename: Path, show: bool = True):
    formatter = logging.Formatter("%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s", datefmt="[%Y-%m_%d %H:%M:%S]")
    fileHandler = logging.FileHandler(filename=str(filename.absolute()), encoding="utf-8")      
    fileHandler.setFormatter(formatter)
    logger = logging.getLogger(filename.stem)
    logger.addHandler(fileHandler)
    if show:
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        logger.addHandler(streamHandler)
    logger.setLevel(logging.INFO)
    return logger