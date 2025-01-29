import os
import unittest

import cv2

import ADB_Command
import OCR
import Util
from ADB_Command import capture_xy


def getInfo():

    img_dir = Util.get_path("img")
    img_name = "screenshot10.png"
    img_src_path = img_dir + "\\" + img_name
    info_img_src_path = os.path.join(img_dir, "info.png")
    ADB_Command.crop_image(img_src_path,1039,324,1305,381,info_img_src_path)
    T, C = OCR.getTextByOCR(info_img_src_path)  # 获取识别文字与置信度
    print(f"文字：{T}，置信度：{C}")


getInfo()

