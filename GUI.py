import tkinter as tk
from tkinter import scrolledtext
import threading
import time


class App:

    #__init__(self, root) 是 Python 中类的构造函数。当你创建类的一个实例时，__init__ 方法会自动被调用
    #self 表示当前类的实例，它是所有类方法的第一个参数，表示该方法作用于哪个对象实例。
    #root 是传入的参数，通常是 tk.Tk() 创建的主窗口对象。root 是用来表示 GUI 程序的根窗口
    def __init__(self, root):

        #这一行将传入的 root 参数（即主窗口对象）保存到实例变量 self.root 中。通过 self.root，你可以在类的其他方法中引用这个窗口对象
        self.root = root

        #设置主窗口的标题栏为 "开始/暂停 循环打印"，这会在程序界面上显示
        self.root.title("开始/暂停 循环打印")


        self.is_running = False #一个布尔值，表示是否正在运行循环，初始化时为 False
        self.is_paused = False  #一个布尔值，表示循环是否被暂停，初始化时为 False
        self.counter = 0        #一个计数器，用来跟踪循环打印的次数。初始化时为 0

        # 创建文本框

        #这一行创建了一个可滚动的文本框 text_box，并将其放置在 root 窗口中。
        #scrolledtext.ScrolledText 是 tkinter 中一个带滚动条的文本框组件。
        #width=40：文本框宽度为 40 个字符。
        #height=10：文本框高度为 10 行。
        #wrap=tk.WORD：设置文本自动换行的方式，tk.WORD 意味着按单词进行换行，而不是按字符换行
        self.text_box = scrolledtext.ScrolledText(self.root, width=40, height=10, wrap=tk.WORD)

        #self.text_box.pack() 会将 text_box 组件加入到界面中并显示。
        #padx=10, pady=10 用于设置组件与周围元素的内边距，确保文本框不会紧贴窗口边缘
        self.text_box.pack(padx=10, pady=10)

        # 创建开始按钮
        #创建了一个 Button 按钮组件，文本为 "开始"，并绑定一个事件处理函数 self.toggle，即当点击此按钮时，会调用 self.toggle 方法。
        #self.toggle 是一个方法，它的作用是在点击“开始”按钮时启动或停止循环
        self.start_button = tk.Button(self.root, text="开始", command=self.toggle)
        self.start_button.pack(padx=10, pady=5)

        # 创建暂停按钮
        #创建了第二个按钮，文本为 "暂停"，并绑定一个事件处理函数 self.pause，即当点击此按钮时，会调用 self.pause 方法。
        #self.pause 方法用于切换循环的暂停状态
        self.pause_button = tk.Button(self.root, text="暂停", command=self.pause)
        self.pause_button.pack(padx=10, pady=5)


    #这段代码是 App 类中的一个方法 toggle，它用于【控制循环的启动和停止】。具体来说，它会根据当前循环的状态（是否正在运行）来决定是开始循环还是停止循环，并且修改界面按钮的文本
    def toggle(self):
        #表示如果当前循环没有在运行
        if not self.is_running:
            self.is_running = True  #设置布尔值【正在运行】为【true】
            self.is_paused = False  #设置布尔值【已停止】为【false】

            #通过self.start_button.config(text="停止")修改“开始”按钮的文本，变为"停止"。
            # 这意味着当点击按钮后，按钮的文本会变成“停止”，表示用户可以通过点击“停止”来终止当前循环
            self.start_button.config(text="停止")

            #这行代码创建并启动一个新的线程来执行 self.start_loop 方法。这样做的目的是将循环的执行放到后台线程中，以便不会阻塞主线程，保持界面的响应。
            #target=self.start_loop：指定这个线程要执行的函数是 self.start_loop。self.start_loop 是另一个方法，它包含了循环打印内容的逻辑。
            #daemon=True：将该线程设置为守护线程，意味着当主程序退出时，该线程会被自动结束。
            #start()：启动线程
            threading.Thread(target=self.start_loop, daemon=True).start()
        # 表示如果当前循环正在
        else:
            self.is_running = False #设置布尔值【正在运行】为【false】
            self.start_button.config(text="开始")

    def pause(self):
        if self.is_running:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.pause_button.config(text="继续")
            else:
                self.pause_button.config(text="暂停")

    def start_loop(self):
        while self.is_running:
            if not self.is_paused:
                self.text_box.insert(tk.END, f"循环计数: {self.counter}\n")
                self.text_box.yview(tk.END)  # 滚动到底部
                self.counter += 1
            time.sleep(10)

# 创建主窗口
root = tk.Tk()
app = App(root)

# 启动GUI应用
root.mainloop()
