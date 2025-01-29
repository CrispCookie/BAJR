import os
import sys
from PIL import Image
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


def check_image_size(image_path):
    try:
        # 打开图片
        with Image.open(image_path) as img:
            # 获取图片的宽和高
            width, height = img.size

            # 判断是否为 1920x1080
            if width == 1920 and height == 1080:
                print("图片尺寸是 1920x1080")
                return True
            else:
                print(f"图片尺寸是 {width}x{height}，不符合 1920x1080")
                return False
    except Exception as e:
        print(f"无法打开图片: {e}")
        return False