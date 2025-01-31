import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel

import cv2
import winsound
from PIL import Image, ImageTk
import threading
import time
import os
import ADB_Command
import BAJR_Request
import Util
import remind
import OCR


class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("超级根批恶霸 ver1.8 -邮件推送")
        self.is_running = False
        self.stop_thread = threading.Event()

        self.adb_path = ADB_Command.get_adb_path()
        self.adb_port = ADB_Command.get_adb_port()
        self.email = ADB_Command.get_email()

        # 左侧布局
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # 文本框
        self.text_entry = tk.Entry(left_frame, width=30)
        self.text_entry.insert(0, "当前竞技场排名")  # 默认文本
        self.text_entry.pack(pady=5)

        # 图片框
        self.image_label = tk.Label(left_frame, width=280, height=161, bg="white")
        self.image_label.pack(pady=5)
        self.load_image()

        # 按钮：关于和配置（同一行）
        button_frame = tk.Frame(left_frame)
        button_frame.pack(pady=5)

        self.about_button = tk.Button(button_frame, width=14, text="关于", command=self.show_about)
        self.about_button.pack(side=tk.LEFT, padx=5)

        self.config_button = tk.Button(button_frame, width=14, text="配置", command=self.show_config)
        self.config_button.pack(side=tk.LEFT, padx=5)

        # 按钮：开始/暂停
        self.start_pause_button = tk.Button(left_frame, width=30, text="开始", command=self.toggle_start_pause)
        self.start_pause_button.pack(pady=5)

        # 右侧日志框
        right_frame = tk.Frame(root)
        right_frame.pack(side=tk.RIGHT, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(right_frame, width=50, height=20, wrap=tk.WORD)
        self.log_text.pack()

    def load_image(self):
        """加载并显示图片"""
        try:
            img_path = os.path.join(Util.get_work_path(), "img", "GP.png")  # 图片路径
            img = Image.open(img_path)
            img = img.resize((279, 160))  # 调整图片大小
            self.img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.img)
        except FileNotFoundError:
            self.log_text.insert(tk.END, "未找到图片: img/GP.png\n")
        except Exception as e:
            self.log_text.insert(tk.END, f"加载图片时发生错误: {e}\n")

    def toggle_start_pause(self):
        """开始或暂停循环"""
        # 开始
        if not self.is_running:
            self.log_text.delete("1.0", "end")
            if self.adb_port == "":
                self.log_text.insert(tk.END, "请先配置adb调试端口(从MuMu模拟器问题诊断处查找或直接百度)\n")
                return
            if self.adb_path == "":
                self.log_text.insert(tk.END, "请先配置MuMu模拟器的adb.exe所处目录路径\n")
                return

            self.is_running = True
            self.start_pause_button.config(text="暂停")
            self.stop_thread.clear()  # 清除停止事件
            self.log_text.insert(tk.END, "【监听开始】\n")
            self.loop_thread = threading.Thread(target=self.loop_function, daemon=True)
            self.loop_thread.start()
            # 结束
        else:
            self.is_running = False
            self.start_pause_button.config(text="开始")
            self.stop_thread.set()  # 设置停止事件，通知线程终止
            self.log_text.insert(tk.END, "【监听结束】用户终止\n")

    def loop_function(self):
        """循环执行的任务"""

        adb_dir = self.adb_path
        drive, _ = os.path.splitdrive(adb_dir)
        cd_adbpath = drive + "&cd " + adb_dir

        try:
            result = ADB_Command.adb_connect(cd_adbpath, self.adb_port)
            print("【ADB连接结果】" + result.stdout)
            if not ("already connected" in result.stdout) and not ("connected to" in result.stdout):
                # 暂停循环
                self.is_running = False
                self.start_pause_button.config(text="开始")
                self.stop_thread.set()  # 设置停止事件，通知线程终止
                self.log_text.insert(tk.END, "【监听结束】ADB连接错误，请查看配置参数是否正确\n")
                return
        except TypeError:
            # 暂停循环
            self.is_running = False
            self.start_pause_button.config(text="开始")
            self.stop_thread.set()  # 设置停止事件，通知线程终止
            self.log_text.insert(tk.END, "【监听结束】此端口下的模拟器未打开\n")
            return


        current_file_directory = Util.get_work_path()
        img_dir = Util.get_path("img")
        img_name = "screenshot10.png"
        img_src_path = img_dir + "\\" + img_name
        crop_img_src_path = img_dir + "\\child_screenshot.png"
        print("【配置参数】")
        print("【当前工作目录】" + current_file_directory)
        print("【shell目录】" + adb_dir)
        print("【img目录】" + img_dir)
        print("【截图文件路径】" + img_src_path)
        print("【截图的截图路径】" + crop_img_src_path)

        if not ADB_Command.adb_screencap(cd_adbpath, img_src_path):
            # 如果因为没有权限而截屏失败
            self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】缺少ROOT权限,请在模拟器中进行确认\n")
            ADB_Command.adb_root(cd_adbpath)
            ADB_Command.adb_screencap(cd_adbpath, img_src_path)

        if not Util.check_image_size(img_src_path):
            # 暂停循环
            self.is_running = False
            self.start_pause_button.config(text="开始")
            self.stop_thread.set()  # 设置停止事件，通知线程终止
            self.log_text.insert(tk.END, "【监听结束】屏幕分辨率不为1920*1080\n")
            return
        self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】屏幕分辨率满足1920*1080\n")

        x, y, w, h = ADB_Command.get_rank_coordinate()
        img00 = cv2.imread(img_src_path)
        # 第一次截取并保存为 child_screenshot.png
        child_screenshot = ADB_Command.capture_region(img00, x, y, w, h)
        cv2.imwrite(crop_img_src_path, child_screenshot)
        img = Image.open(crop_img_src_path)
        img = img.resize((279, 160))  # 调整图片大小
        self.img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.img)



        height, width, channels = cv2.imread(img_src_path).shape  # 获取截图长宽高
        if not width == 1920 or not height == 1080:
            print("【模拟器分别率不为1920*1080】")
            # 暂停循环
            self.is_running = False
            self.start_pause_button.config(text="开始")
            self.stop_thread.set()  # 设置停止事件，通知线程终止
            self.log_text.insert(tk.END, "模拟器分别率不为1920*1080\n")
            return

        # OCR读取当前竞技场排名并填入文本框中
        self.log_text.insert(tk.END,
                             f"【{time.strftime('%H:%M:%S')}】OCR开启，初次使用时需搭梯子下载模型(需加载一段时间)\n")
        now_rank, rank_T = OCR.getTextByOCR(crop_img_src_path)
        self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】初始排名: {now_rank}\n")
        print("【排名文本框】" + self.text_entry.get())
        entry_info = "当前竞技场排名-" + now_rank
        self.text_entry.delete(0, tk.END)  # 清空排名文本框
        self.text_entry.insert(0, entry_info)

        self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】开始监听！\n")
        count = 0
        # ---------------------------------------监听循环---------------------------------------------------------------------------------------
        while not self.stop_thread.is_set():
            ADB_Command.adb_screencap(cd_adbpath, img_src_path)  # 截图

            if check_in_JJC():
                if check_have_message():
                    print("【识别到通知弹窗】")
                    Info = check_message()
                    if ("網路存取不順暢" == Info):
                        link_count = 1
                        self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】检测到弹窗：網絡存取不順暢\n")
                        while True:
                            ADB_Command.adb_screencap(cd_adbpath, img_src_path)  # 截图
                            link_info = check_message()
                            print(f"【消息弹窗-网络存取不顺畅】{link_info}")
                            if "網路存取不順暢" in link_info:
                                print(f"【尝试重新连接】第{link_count}次")
                                self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】尝试重新连接-第{link_count}次\n")
                                ADB_Command.adb_click(cd_adbpath, 1114,752)  # 点击重新连接
                                time.sleep(5)  # 延时5S
                                link_count = link_count + 1
                            else:
                                if (not check_have_message()) and check_in_JJC():
                                    print(f"重新连接成功")
                                    self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】重新连接成功\n")
                                    break
                                else:
                                    print(f"监听软件错误操作致使游戏重启")
                                    self.stop_run("监听软件错误操作致使游戏重启")
                                    return
                            if link_count == 4:
                                # 暂停循环
                                print("【监听结束】三次重连均失败\n")
                                self.stop_run("三次重连均失败")
                                return

            else:
                print("【当前页面并不处于竞技场】")
                self.stop_run("当前页面并不处于竞技场")
                return

            print("【当前页面处于竞技场】")
            print(f"【第{count}次循环】开始")

            ADB_Command.adb_screencap(cd_adbpath, img_src_path)  # 截图
            if not count == 0:  # 点击逻辑
                if not check_have_message():
                    self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】第{count}次监听\n")
                    print(f"【第{count}次循环】点击刷新按钮")
                    ADB_Command.adb_click(cd_adbpath, 1734, 219)  # 点击刷新按钮
                    time.sleep(1)
                else:
                    self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】检测到通知框-跳过点击刷新事件-{now_rank}\n")
                    continue
            # 截图：排名
            ADB_Command.adb_screencap(cd_adbpath, img_src_path)  # 截图
            original_img = cv2.imread(img_src_path)
            child_screenshot01 = ADB_Command.capture_region(original_img, x, y, w, h)
            cv2.imwrite(crop_img_src_path, child_screenshot01)
            img = Image.open(crop_img_src_path)
            img = img.resize((279, 160))  # 调整图片大小
            self.img = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.img)

            # 比较当前截图与之前的截图是否一致
            if not count == 0:
                now_rank, rank_T = OCR.getTextByOCR(crop_img_src_path)
                pre_rank = self.text_entry.get().split('-')[1];
                entry_info = "当前竞技场排名-" + now_rank
                self.text_entry.delete(0, tk.END)  # 清空排名文本框
                self.text_entry.insert(0, entry_info)

                if now_rank == pre_rank:
                    print(f"【第{count}次循环】排名未变动")
                    self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】排名未变动-{now_rank}\n")
                else:
                    if  "第" in now_rank and "名" in now_rank:

                        wav_name = "01.wav"
                        wav_src_path = img_dir + "\\" + wav_name
                        # 更新 child_screenshot.png 为新的截图
                        cv2.imwrite(crop_img_src_path, child_screenshot01)
                        img = Image.open(crop_img_src_path)
                        img01 = img.resize((279, 160))  # 调整图片大小
                        self.img = ImageTk.PhotoImage(img01)
                        self.image_label.config(image=self.img)
                        self.log_text.insert(tk.END,f"【{time.strftime('%H:%M:%S')}】排名发生变动{pre_rank}->{now_rank}\n")

                        winsound.PlaySound(wav_src_path, winsound.SND_FILENAME)     #播放爱丽丝语音
                        message_box_text = "排名发生变动！\n"+pre_rank+" -> "+now_rank
                        show_message(message_box_text)

                        # 点击战报
                        ADB_Command.adb_click(cd_adbpath, 207, 885)
                        time.sleep(2)
                        ADB_Command.adb_screencap(cd_adbpath, img_src_path)  # 截图
                        attacker_img_src_path = os.path.join(img_dir, "attacker.png")

                        #退出战报
                        ADB_Command.crop_image(img_src_path,1039,324,1305,381,attacker_img_src_path)

                        T, C = OCR.getTextByOCR(attacker_img_src_path)  # 获取识别文字与置信度
                        print(f"【竞技场排名变动】进攻者:{T}")
                        self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】进攻者:{T}\n")
                        try:
                            result =  BAJR_Request.send_email(self.email,T,pre_rank,now_rank)
                            if "邮件发送成功" in result:
                                self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】发送邮件通知{self.email}\n")
                            else:
                                self.log_text.insert(tk.END, f"【{time.strftime('%H:%M:%S')}】{self.email}此邮箱地址不处于白名单内\n")
                        except:
                            print(f"【邮件发送未成功】:{T}")

                        entry_info = "当前竞技场排名-" + now_rank
                        self.text_entry.delete(0, tk.END)  # 清空排名文本框
                        self.text_entry.insert(0, entry_info)
                        ADB_Command.adb_click(cd_adbpath, 1734, 219)  # 点击刷新按钮
                    else:
                        self.stop_run("当前不处于竞技场页面")
                        return
            count = count + 1
            self.log_text.see(tk.END)  # 自动滚动到最后
            time.sleep(5)  # 每 10 秒执行一次循环

    def show_about(self):
        """显示关于窗口"""
        about_window = Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("400x300")
        about_window.resizable(False, False)
        self.center_window(about_window)

        # 在子窗口中显示作者信息
        tk.Label(about_window, text="此软件是以MuMu模拟器的adb截图命令\n"
                                    "与OCR文字识别为基础实现的，使用需要\n"
                                    "用户的模拟器分辨率满足1920*1080并\n"
                                    "配置Mumu模拟器adb.exe所在路径与端口\n"
                                    "号(默认为16384)。 欢迎提出合理的需求", font=("Arial", 12)).pack(pady=10)
        tk.Label(about_window, text="作者: B站@Roxy7650", font=("Arial", 12)).pack(pady=10)
        tk.Label(about_window, text="Q群超级根批恶霸: 248348154", font=("Arial", 12)).pack(pady=10)

    # 配置
    def show_config(self):
        """显示配置窗口"""
        config_window = Toplevel(self.root)
        config_window.title("配置")
        config_window.geometry("400x320")
        config_window.resizable(False, False)

        # 居中显示子窗口
        self.center_window(config_window)

        # 标签
        tk.Label(config_window, text="模拟器adb.exe所处的目录路径：", font=("Arial", 12)).pack(pady=10)

        # 输入框
        adb_path_input_field = tk.Entry(config_window, width=40)
        adb_path_input_field.pack(pady=5)

        # 标签
        tk.Label(config_window, text="模拟器adb调试端口：", font=("Arial", 12)).pack(pady=10)
        # 输入框
        adb_port_input_field = tk.Entry(config_window, width=40)
        adb_port_input_field.pack(pady=5)

        # 标签
        tk.Label(config_window, text="通知用QQ邮箱：", font=("Arial", 12)).pack(pady=10)
        email_input_field = tk.Entry(config_window, width=40)
        email_input_field.pack(pady=5)

        # 调用 get_adb_path 函数获取配置值，并预填入输入框
        adb_path_input_field.insert(0, self.adb_path)
        adb_port_input_field.insert(0, self.adb_port)
        email_input_field.insert(0,self.email)

        # 按钮：提交和取消
        button_frame = tk.Frame(config_window)
        button_frame.pack(pady=20)

        def submit_action():
            self.log_text.delete("1.0", "end")

            value01 = adb_path_input_field.get()
            self.log_text.insert(tk.END, f"【配置adb路径】 {value01}\n")
            self.log_text.see(tk.END)  # 滚动到日志框底部
            ADB_Command.set_adb_path(value01)
            self.adb_path = ADB_Command.get_adb_path()

            value02 = adb_port_input_field.get()
            self.log_text.insert(tk.END, f"【配置adb端口】 {value02}\n")
            self.log_text.see(tk.END)  # 滚动到日志框底部
            ADB_Command.set_adb_port(value02)
            self.adb_port = ADB_Command.get_adb_port()

            value03 = email_input_field.get()
            self.log_text.insert(tk.END, f"【配置通知邮箱】 {value03}\n")
            self.log_text.see(tk.END)  # 滚动到日志框底部
            ADB_Command.set_email(value03)
            self.email = ADB_Command.get_email()

            config_window.destroy()

        def cancel_action():
            config_window.destroy()

        tk.Button(button_frame, text="提交", command=submit_action).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="取消", command=cancel_action).pack(side=tk.LEFT, padx=5)

    def center_window(self, window):
        """将窗口居中显示"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f"{width}x{height}+{x}+{y}")

    def stop_run(self,Text):
        self.is_running = False
        self.start_pause_button.config(text="开始")
        self.stop_thread.set()  # 设置停止事件，通知线程终止
        self.log_text.insert(tk.END, f"【监听结束】{Text}\n")


def show_message(message):
    # 在主线程中调用显示消息框
    def display_message():
        # 创建一个新的顶级窗口作为消息框
        msg_box = tk.Toplevel(root)
        msg_box.title("超级根批恶霸")

        # 设置消息内容
        message_label = tk.Label(msg_box, text=message)
        message_label.pack(padx=50, pady=20)

        # 创建确认按钮，并绑定关闭函数
        def close_message_box():
            msg_box.destroy()  # 关闭消息框

        ok_button = tk.Button(msg_box, text="确认", command=close_message_box)
        ok_button.pack(pady=10)

        # 设置自定义的宽度和高度
        msg_box_width = 300
        msg_box_height = 140
        msg_box.geometry(f"{msg_box_width}x{msg_box_height}")  # 设置消息框的大小
        msg_box.attributes('-topmost', True)
        # 获取屏幕宽度和高度
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # 获取消息框的宽度和高度
        msg_box_width = msg_box.winfo_reqwidth()
        msg_box_height = msg_box.winfo_reqheight()

        # 计算消息框居中位置
        position_top = (screen_height - msg_box_height) // 2
        position_left = (screen_width - msg_box_width) // 2

        # 设置消息框的位置
        msg_box.geometry(f"+{position_left}+{position_top}")

        # 启动消息框的事件循环
        msg_box.mainloop()

    # 使用 after() 方法在主线程中调度显示消息框
    root.after(0, display_message)


#检查页面是否在JJC
def check_in_JJC():
    img_dir = Util.get_path("img")
    img_name = "screenshot10.png"
    img_src_path = img_dir + "\\" + img_name
    original_img = cv2.imread(img_src_path)
    flag_img_src_path = os.path.join(img_dir, "flag.png")
    child_screenshot02 = ADB_Command.capture_region(original_img, 156, 11, 172, 52)
    cv2.imwrite(flag_img_src_path, child_screenshot02)  # 截取标志位
    T, C = OCR.getTextByOCR(flag_img_src_path)  # 获取识别文字与置信度
    print(f"【识别界面】{T}")
    if (not T == "戰術大賽"):
        return False
    else:
        return True

def check_have_message():
    img_dir = Util.get_path("img")
    img_name = "screenshot10.png"
    img_src_path = img_dir + "\\" + img_name
    info_flag_img_src_path = os.path.join(img_dir, "info_flag.png")
    ADB_Command.crop_image(img_src_path, 751, 208, 1244, 262, info_flag_img_src_path)
    T, C = OCR.getTextByOCR(info_flag_img_src_path)  # 获取识别文字与置信度
    print(f"【识别有无通知框】{T}")
    if T == "通知":
        return True
    else:
        return False


def check_message():
    img_dir = Util.get_path("img")
    img_name = "screenshot10.png"
    img_src_path = img_dir + "\\" + img_name
    info_img_src_path = os.path.join(img_dir, "info.png")
    ADB_Command.crop_image(img_src_path, 571, 374, 1294, 608, info_img_src_path)
    Info, _ = OCR.getTextByOCR(info_img_src_path)
    print(f"【识别消息框内文字】{Info}")
    return Info



if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    icon_path = Util.get_work_path() + "\\img\\BJAR.ico"
    root.iconbitmap(icon_path)
    root.mainloop()

