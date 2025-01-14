import tkinter as tk
from tkinter import scrolledtext, messagebox, Toplevel

import cv2
from PIL import Image, ImageTk
import threading
import time
import os
import ADB_Command


class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("超级根批恶霸")
        self.is_running = False
        self.loop_thread = None

        self.adb_path = ADB_Command.get_adb_path()
        self.adb_port = ADB_Command.get_adb_port()

        # 左侧布局
        left_frame = tk.Frame(root)
        left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        # 文本框
        self.text_entry = tk.Entry(left_frame,width=30)
        self.text_entry.insert(0, "当前竞技场排名")  # 默认文本
        self.text_entry.pack(pady=5)

        # 图片框
        self.image_label = tk.Label(left_frame, width=280, height=161, bg="white")
        self.image_label.pack(pady=5)
        self.load_image()

        # 按钮：关于和配置（同一行）
        button_frame = tk.Frame(left_frame)
        button_frame.pack(pady=5)

        self.about_button = tk.Button(button_frame,width=14, text="关于", command=self.show_about)
        self.about_button.pack(side=tk.LEFT, padx=5)

        self.config_button = tk.Button(button_frame,width=14, text="配置", command=self.show_config)
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
            img_path = os.path.join(os.getcwd(), "img", "GP.png")  # 图片路径
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
            self.is_running = True
            self.start_pause_button.config(text="暂停")
            self.log_text.insert(tk.END, "循环开始...\n")
            self.loop_thread = threading.Thread(target=self.loop_function, daemon=True)
            self.loop_thread.start()
            #结束
        else:
            self.is_running = False
            self.start_pause_button.config(text="开始")

            self.log_text.insert(tk.END, "循环暂停...\n")

    def loop_function(self):
        """循环执行的任务"""
        ADB_Command.adb_connect(self.adb_port)
        ADB_Command.adb_root(self.adb_path)
        current_file_directory = os.path.dirname(os.path.abspath(__file__))
        img_dir = os.path.join(current_file_directory, "img")
        adb_dir = self.adb_path
        cd_adbpath = "cd " + adb_dir
        img_name = "screenshot10.png"
        img_src_path = img_dir + "\\" + img_name
        crop_img_src_path = img_dir + "\\child_screenshot.png"
        print("【配置参数】")
        print("【当前工作目录】" + current_file_directory)
        print("【shell目录】" + adb_dir)
        print("【img目录】" + img_dir)
        print("【截图文件路径】" + img_src_path)
        print("【截图的截图路径】" + crop_img_src_path)
        ADB_Command.adb_root(cd_adbpath)
        ADB_Command.adb_screencap(cd_adbpath, img_src_path)
        x, y, w, h = ADB_Command.get_rank_coordinate()
        original_img = cv2.imread(img_src_path)
        # 第一次截取并保存为 child_screenshot.png
        child_screenshot = ADB_Command.capture_region(original_img, x, y, w, h)
        cv2.imwrite(crop_img_src_path, child_screenshot)

        img = Image.open(crop_img_src_path)
        img = img.resize((279, 160))  # 调整图片大小
        self.img = ImageTk.PhotoImage(img)
        self.image_label.config(image=self.img)
        count = 0
        self.log_text.insert(tk.END, f"【 {time.strftime('%H:%M:%S')}】开始监听！\n")
        while self.is_running:
            time.sleep(30)  # 每 30 秒执行一次循环
            count = count + 1
            print(f"【第{count}次循环】开始")
            self.log_text.insert(tk.END, f"【 {time.strftime('%H:%M:%S')}】第{count}次监听\n")
            # 每次循环重新加载最新的图像
            ADB_Command.adb_screencap(cd_adbpath, img_src_path)
            img = cv2.imread(img_src_path)

            # 截取当前图像的指定区域
            current_screenshot = ADB_Command.capture_region(img, x, y, w, h)
            # 读取之前保存的 child_screenshot.png
            prev_screenshot = cv2.imread(crop_img_src_path)

            # 比较当前截图与之前的截图是否一致
            if ADB_Command.compare_images(current_screenshot, prev_screenshot):
                print(f"【第{count}次循环】排名未变动")
                self.log_text.insert(tk.END, f"【 {time.strftime('%H:%M:%S')}】排名未变动\n")
            else:
                self.log_text.insert(tk.END, f"【 {time.strftime('%H:%M:%S')}】排名发生变动\n")
                # 更新 child_screenshot.png 为新的截图
                cv2.imwrite(crop_img_src_path, current_screenshot)

                img = Image.open(crop_img_src_path)
                img = img.resize((279, 160))  # 调整图片大小
                self.img = ImageTk.PhotoImage(img)
                self.image_label.config(image=self.img)
            self.log_text.see(tk.END)  # 自动滚动到最后


    def show_about(self):
        """显示关于窗口"""
        about_window = Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("300x150")
        about_window.resizable(False, False)

        # 在子窗口中显示作者信息
        tk.Label(about_window, text="作者：你的名字", font=("Arial", 12)).pack(pady=10)
        tk.Label(about_window, text="版本：1.0", font=("Arial", 12)).pack(pady=10)
        tk.Label(about_window, text="感谢使用！", font=("Arial", 12)).pack(pady=10)

        # 关闭按钮
        tk.Button(about_window, text="关闭", command=about_window.destroy).pack(pady=10)

    def show_config(self):
        """显示配置窗口"""
        config_window = Toplevel(self.root)
        config_window.title("配置")
        config_window.geometry("400x250")
        config_window.resizable(False, False)

        # 居中显示子窗口
        self.center_window(config_window)

        # 标签
        tk.Label(config_window, text="MuMu模拟器adb.exe所处的目录路径：", font=("Arial", 12)).pack(pady=10)

        # 输入框
        adb_path_input_field = tk.Entry(config_window, width=40)
        adb_path_input_field.pack(pady=5)

        # 标签
        tk.Label(config_window, text="MuMu模拟器adb调试端口：", font=("Arial", 12)).pack(pady=10)
        # 输入框
        adb_port_input_field = tk.Entry(config_window, width=40)
        adb_port_input_field.pack(pady=5)


        # 调用 get_adb_path 函数获取配置值，并预填入输入框
        adb_path_input_field.insert(0, self.adb_path)
        adb_port_input_field.insert(0, self.adb_port)

        # 按钮：提交和取消
        button_frame = tk.Frame(config_window)
        button_frame.pack(pady=20)



        def submit_action():
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


if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)
    root.mainloop()
