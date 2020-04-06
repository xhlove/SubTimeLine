'''
@作者: weimo
@创建日期: 2020-04-06 13:21:25
@上次编辑时间: 2020-04-06 17:44:28
@一个人的命运啊,当然要靠自我奋斗,但是...
'''
from pathlib import Path
import json

DEFAULT_PARAMS = [0, 180, 0, 16, 128, 255]

def load_config(video_name: str = ""):
    config_path = Path("config.json").absolute()
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"read config from {str(config_path)} failed.")
        config = {"default":DEFAULT_PARAMS}
        config_path.write_text(json.dumps(config, ensure_ascii=False, indent=4), encoding="utf-8")
    if config.get(video_name):
        return config[video_name]
    return config, config_path

def save_custom_inrange_params(params: list, video_name: str):
    config, config_path = load_config()
    config.update({video_name:params})
    config_path.write_text(json.dumps(config, ensure_ascii=False, indent=4), encoding="utf-8")