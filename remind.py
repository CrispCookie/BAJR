import time

import winsound
from plyer import notification
import ctypes

from time import sleep

def plyer_remind(sound_file):

    notification.notify(
        title='你的竞技场排名发生变动！',
        message='该上号开根了',
        app_name = "超级根批恶霸",
        timeout=3,  # 通知显示的时间（秒）
        ticker = "你的竞技场排名发生变动",
    )

    time.sleep(1.4)

    winsound.PlaySound(sound_file, winsound.SND_FILENAME)




def ctypes_remind(message, sound_file):
    # 播放指定音频
    winsound.PlaySound(sound_file, winsound.SND_FILENAME)

    # 显示Windows弹出窗口
    msg_box = ctypes.windll.user32.MessageBoxW(0, message, "超级根批恶霸", 0x40 | 0x1)

    # 获取弹窗的窗口句柄
    hwnd = ctypes.windll.user32.GetForegroundWindow()

    # 调用 SetWindowPos 将弹窗窗口置顶
    ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0, 0x03)



#ctypes_remind("你的竞技场排名发生变动！", "D:\\Code\\PyCharm\\BJAR\img\\01.wav");


#plyer_remind("D:\\Code\\PyCharm\\BJAR\\img\\01.wav")
