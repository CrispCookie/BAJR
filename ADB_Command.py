import subprocess
import threading
import time

import OCR
import Util



import cv2
import configparser
import numpy as np

from PIL import Image
import os

import main


# 两个命令合并
def combine_adb_commands(cd_command, adb_command):
    combined = f"{cd_command}&{adb_command}"
    return combined


# adb root
def adb_root(cd_adbpath):
    adb_command01 = f"adb root"
    adb_command01 = combine_adb_commands(cd_adbpath, adb_command01)
    print(f"【执行-ROOT】{adb_command01}")
    return subprocess.run(adb_command01, shell=True, capture_output=True, text=True,encoding='utf-8')


# adb connect
def adb_connect(cd_adbpath,port):
    adb_command01 = f"adb connect 127.0.0.1:{port}"
    adb_command01 = combine_adb_commands(cd_adbpath, adb_command01)
    print(f"【执行-ADB连接】{adb_command01}")
    return subprocess.run(adb_command01, shell=True, capture_output=True, text=True,encoding='utf-8')


#adb 鼠标点击
def adb_click(cd_adbpath,x,y):
    adb_command01 = f"adb shell input tap {x} {y}"
    adb_command01 = combine_adb_commands(cd_adbpath, adb_command01)
    print(f"【执行-ADB屏幕点击】{adb_command01}")
    return subprocess.run(adb_command01, shell=True, capture_output=True, text=True,encoding='utf-8')




# adb截图并导出
def adb_screencap(cd_adbpath, img_src):
    adb_command01 = f"adb shell screencap /sdcard/screen.png"
    adb_command01 = combine_adb_commands(cd_adbpath, adb_command01)
    print(f"【执行-ADB截图命令】{adb_command01}")
    result = subprocess.run(adb_command01, shell=True, capture_output=True, text=True,encoding="utf-8")
    print(f"【结果-ADB截图命令】{result.stdout}")
    print(f"【报错-ADB截图命令】{result.stderr}")
    adb_command02 = combine_adb_commands(cd_adbpath, "adb pull /sdcard/screen.png " + img_src)
    print(f"【执行-截图导出至PC】{adb_command02}")
    result = subprocess.run(adb_command02, shell=True, capture_output=True, text=True,encoding='utf-8')
    print(f"【结果-截图导出至PC】{result.stdout}")
    if("failed to stat remote" in result.stdout):
        return False
    return True


# Pillow 库剪切图片
def crop_and_save_image(input_dir, input_image_name, x1, y1, x2, y2, output_dir, new_image_name):
    # 构造输入图片的路径
    input_image_path = input_dir + "/" + input_image_name
    # 打开图片
    try:
        img = Image.open(input_image_path)
    except FileNotFoundError:
        print(f"【错误】: 文件 {input_image_name} 在文件夹 {input_dir}中未找到.")
        return

    # 确保给定的坐标在图片尺寸范围内
    img_width, img_height = img.size
    if not (0 <= x1 < img_width and 0 <= y1 < img_height and 0 <= x2 < img_width and 0 <= y2 < img_height):
        print("【错误】参数范围越界")
        return

    # 截取图片
    cropped_img = img.crop((x1, y1, x2, y2))

    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)

    # 构造保存图片的路径
    output_image_path = output_dir + "/" + new_image_name

    # 保存新图片
    cropped_img.save(output_image_path)
    print(f"【结果】截取图片保存到 {output_image_path}")


# 对比图片
def compare_images(img1, img2):
    """ 比较两张图片是否一致 """
    # 转换为灰度图像
    img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    if img1_gray.shape != img2_gray.shape:
        img2_gray = cv2.resize(img2_gray, (img1_gray.shape[1], img1_gray.shape[0]))

    # 计算两张图像的绝对差异
    diff = cv2.absdiff(img1_gray, img2_gray)

    # 如果差异为0，则认为图像相同
    return np.count_nonzero(diff) == 0


# 从config.ini中读取adb的路径
def get_adb_path():

    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(ini_path)
    # 获取当前的 adb_path 值
    adb_path = config.get('settings', 'adb_path')
    print(f'【当前ADB路径】 {adb_path}')
    return adb_path


# 写入adb的路径到config.ini
def set_adb_path(new_adb_path):
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read(ini_path)
    # 修改 adb_path 的值
    config.set('settings', 'adb_path', new_adb_path)
    # 将修改保存回配置文件
    with open(ini_path, 'w') as configfile:
        config.write(configfile)

    print(f'【新的ADB路径】: {new_adb_path}')


# 从config.ini中读取adb的路径
def get_adb_port():
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(ini_path)
    # 获取当前的 adb_path 值
    adb_path = config.get('settings', 'adb_port')
    print(f'【当前ADB路径】 {adb_path}')
    return adb_path


# 写入adb的端口到config.ini
def set_adb_port(new_adb_port):
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read(ini_path)
    # 修改 adb_path 的值
    config.set('settings', 'adb_port', new_adb_port)
    # 将修改保存回配置文件
    with open(ini_path, 'w') as configfile:
        config.write(configfile)

    print(f'【新的ADB端口】: {new_adb_port}')

# 写入email到config.ini
def set_email(new_email):
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read(ini_path)
    # 修改 adb_path 的值
    config.set('settings', 'email', new_email)
    # 将修改保存回配置文件
    with open(ini_path, 'w') as configfile:
        config.write(configfile)

    print(f'【新的email】: {new_email}')


# 从config.ini中读取adb的路径
def get_email():
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(ini_path)
    # 获取当前的 adb_path 值
    adb_path = config.get('settings', 'email')
    print(f'【当前email】 {adb_path}')
    return adb_path



def get_rank_coordinate():
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(ini_path)
    # 获取当前的坐标
    x = config.get('settings', 'my_rank_range_x')
    y = config.get('settings', 'my_rank_range_y')
    w = config.get('settings', 'my_rank_range_w')
    h = config.get('settings', 'my_rank_range_h')
    print(f"【本人排名-截图坐标】x轴:{x}  y轴:{y}  宽:{w} 高:{h}")
    return int(x), int(y), int(w), int(h)


def set_rank_coordinate(x, y, w, h):
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read(ini_path)
    # 修改 adb_path 的值
    config.set('settings', 'my_rank_range_x', x)
    config.set('settings', 'my_rank_range_y', y)
    config.set('settings', 'my_rank_range_w', w)
    config.set('settings', 'my_rank_range_h', h)

    with open(ini_path, 'w') as configfile:
        config.write(configfile)
    print(f"【更新-本人排名-截图坐标】x轴:{x}  y轴:{y}  宽:{w} 高:{h}")


# 从config.ini中读取是否弹窗提醒
def get_popup_reminders():
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(ini_path)
    # 设置布尔值字段
    flag = True
    # 获取当前的 get_popup_reminders 值
    get_popup_reminders = config.get('settings', 'popup_reminders')
    flag = get_popup_reminders.lower() == 'true'
    print(f'【开启弹窗提醒FLAG】 {flag}')
    return flag


# 设置弹窗提醒flag
def set_popup_reminders(flag):
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read(ini_path)
    # 修改 adb_path 的值
    config.set('settings', 'popup_reminders', 'true' if flag else 'false')
    # 将修改保存回配置文件
    with open(ini_path, 'w') as configfile:
        config.write(configfile)

    print(f'【更新-开启弹窗提醒FLAG】: {flag}')


# 从config.ini中读取是否声音提醒
def get_sound_reminders():
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    # 读取配置文件
    config.read(ini_path)
    # 设置布尔值字段
    flag = True
    # 获取当前的 get_popup_reminders 值
    get_popup_reminders = config.get('settings', 'sound_reminders')
    flag = get_popup_reminders.lower() == 'true'
    print(f'【开启声音提醒FLAG】 {flag}')
    return flag


# 写入声音提醒flag
def set_sound_reminders(flag):
    ini_path = Util.get_path("config\\config.ini")
    # 创建配置解析器
    config = configparser.ConfigParser()
    config.read(ini_path)
    # 修改 adb_path 的值
    config.set('settings', 'sound_reminders', 'true' if flag else 'false')
    # 将修改保存回配置文件
    with open(ini_path, 'w') as configfile:
        config.write(configfile)

    print(f'【更新-开启声音提醒FLAG】: {flag}')





# 截取图像指定区域
def capture_region(img, x, y, w, h):
    """ 截取图像指定区域 """
    return img[y:y + h, x:x + w]



def capture_xy(img, x1, y1, x2, y2):
    """ 截取图像指定区域 """
    return img[y1:y2,x1:x2]


def crop_image(image_path, x1, y1, x2, y2, result_path):
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        print("无法读取图片，请检查路径是否正确")
        return
    # 使用切片裁剪图片
    cropped_img = img[y1:y2, x1:x2]
    # 保存裁剪后的图片到 result_path
    cv2.imwrite(result_path, cropped_img)
