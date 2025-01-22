import os
import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread, Lock
from datetime import datetime
from logHandler import LogHandler
from controller import handle_danmu_action
from danmu import fetch_danmu
import random
import sys
import time

# 初始化日志处理器
log_handler = LogHandler()


class DanmuControllerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Danmu Controller")
        self.room_id = tk.StringVar()
        self.is_running = False
        self.running_lock = Lock()  # 用于线程安全
        self.operation_guide = self.load_embedded_guide()  # 嵌入的操作指南
        self.danmu_delay_range = [1000, 3000]  # 默认延迟范围设置
        self.first_danmu_ignored = True  # 标记是否已忽略第一次弹幕
        self.setup_ui()

        # 初始化日志路径
        self.initialize_logs_directory()

    def setup_ui(self):
        """设置 GUI 界面"""
        self.create_room_input_frame()
        self.create_control_frame()
        self.create_status_label()
        self.create_delay_settings_frame()

    def create_room_input_frame(self):
        """创建房间号输入框和控制按钮"""
        room_frame = ttk.LabelFrame(self.root, text="房间号")
        room_frame.pack(padx=10, pady=10, fill="x")
        ttk.Entry(room_frame, textvariable=self.room_id, width=30).pack(side="left", padx=5)
        ttk.Button(room_frame, text="开始连接", command=self.start_danmu_listener).pack(side="left", padx=5)
        ttk.Button(room_frame, text="停止连接", command=self.stop_danmu_listener).pack(side="left", padx=5)

    def create_control_frame(self):
        """创建功能按钮"""
        control_frame = ttk.LabelFrame(self.root, text="功能")
        control_frame.pack(padx=10, pady=10, fill="x")
        ttk.Button(control_frame, text="查看操作指南",
                   command=lambda: self.display_text_window("操作指南", self.operation_guide)).pack(side="left", padx=5)

    def create_status_label(self):
        """创建状态显示标签"""
        self.status_label = ttk.Label(self.root, text="状态: 未连接", anchor="w")
        self.status_label.pack(padx=10, pady=10, fill="x")

    def create_delay_settings_frame(self):
        """创建弹幕延迟范围设置框"""
        delay_frame = ttk.LabelFrame(self.root, text="弹幕延迟范围 (毫秒)")
        delay_frame.pack(padx=10, pady=10, fill="x")

        self.delay_min_var = tk.IntVar(value=self.danmu_delay_range[0])
        self.delay_max_var = tk.IntVar(value=self.danmu_delay_range[1])

        ttk.Label(delay_frame, text="最小延迟:").pack(side="left", padx=5)
        ttk.Entry(delay_frame, textvariable=self.delay_min_var, width=5).pack(side="left", padx=5)

        ttk.Label(delay_frame, text="最大延迟:").pack(side="left", padx=5)
        ttk.Entry(delay_frame, textvariable=self.delay_max_var, width=5).pack(side="left", padx=5)

    def initialize_logs_directory(self):
        """初始化日志文件夹，保存在当前目录下的 logs 文件夹中"""
        current_directory = os.path.dirname(os.path.abspath(__file__))
        logs_directory = os.path.join(current_directory, "logs")

        if not os.path.exists(logs_directory):
            os.makedirs(logs_directory)
            log_handler.log_error(f"日志文件夹已创建: {logs_directory}")

        log_file_name = datetime.now().strftime("%Y%m%d%H%M%S_logs.txt")
        log_handler.log_file = os.path.join(logs_directory, log_file_name)
        log_handler.set_up_logging()
        log_handler.log_error("日志文件已初始化")

    def start_danmu_listener(self):
        """开始弹幕监听"""
        if not self.room_id.get().isdigit():
            messagebox.showerror("错误", "请输入有效的房间号！")
            log_handler.log_error("无效的房间号")
            return
        with self.running_lock:
            self.is_running = True
            self.first_danmu_ignored = False  # 重置第一次弹幕忽略标记
        self.update_status("连接成功")
        Thread(target=self.listen_to_danmu, daemon=True).start()

    def stop_danmu_listener(self):
        """停止弹幕监听"""
        with self.running_lock:
            self.is_running = False
        self.update_status("已停止")
        log_handler.log_error("弹幕监听已停止")

    def listen_to_danmu(self):
        """监听弹幕并处理"""
        last_timestamp = None
        while True:
            with self.running_lock:
                if not self.is_running:
                    break
            try:
                danmu_list = fetch_danmu(self.room_id.get())
                if danmu_list:
                    latest_danmu = danmu_list[-1]
                    if latest_danmu['timeline'] != last_timestamp:
                        if not self.first_danmu_ignored:
                            # 忽略第一次弹幕
                            self.first_danmu_ignored = True
                            log_handler.log_error("第一次弹幕已忽略")
                        else:
                            log_handler.log_error(f"弹幕: {latest_danmu['text']}")
                            handle_danmu_action(latest_danmu['text'])
                        last_timestamp = latest_danmu['timeline']

                # 使用用户自定义的延迟范围，随机等待
                delay_min = self.delay_min_var.get()
                delay_max = self.delay_max_var.get()
                fetch_interval = random.uniform(delay_min, delay_max) / 1000
                # log_handler.log_error(f"下一次弹幕监听将在 {fetch_interval:.2f} 秒后进行...")
                time.sleep(fetch_interval)
            except Exception as e:
                log_handler.log_error(f"弹幕监听失败: {e}")

    def display_text_window(self, title, content):
        """通用文本显示窗口"""
        window = tk.Toplevel(self.root)
        window.title(title)
        text_area = tk.Text(window, wrap="word")
        text_area.insert("1.0", content)
        text_area.config(state="disabled")  # 禁用编辑
        text_area.pack(expand=True, fill="both")

    def update_status(self, status):
        """更新状态标签"""
        self.status_label.config(text=f"状态: {status}")

    @staticmethod
    def load_embedded_guide():
        """
        返回嵌入的操作指南内容。
        如果是打包后的环境，通过 PyInstaller 提供的路径读取。
        """
        try:
            if getattr(sys, 'frozen', False):  # 检查是否是打包的环境
                base_path = sys._MEIPASS  # PyInstaller 解压后的临时目录
            else:
                base_path = os.path.abspath(".")  # 开发环境下的当前目录

            guide_path = os.path.join(base_path, "guide.md")

            with open(guide_path, "r", encoding="utf-8") as file:
                return file.read()

        except FileNotFoundError:
            return "操作指南文件未找到！"
        except Exception as e:
            return f"加载操作指南时发生错误：{e}"


if __name__ == "__main__":
    root = tk.Tk()
    app = DanmuControllerApp(root)
    root.mainloop()
