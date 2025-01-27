import os
import sys

#打包前后的路径处理
def get_path(relative_path):
    # if getattr(sys, 'frozen', False):
    #     base_path = sys._MEIPASS  # pyinstaller打包后的路径
    #     print(base_path)
    # else:
    base_path = os.path.abspath(".")  # 当前工作目录的路径
    print(base_path)
    return os.path.normpath(os.path.join(base_path, relative_path))  # 返回实际路径


def get_work_path():
    # if getattr(sys, 'frozen', False):
    #     base_path = sys._MEIPASS  # pyinstaller打包后的路径
    #     print(base_path)
    # else:
    base_path = os.path.abspath(".")  # 当前工作目录的路径
    print(base_path)
    return base_path
