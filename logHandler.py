import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

class LogHandler:
    def __init__(self, log_folder="logs", log_file_prefix="game_logs", max_size=1024*1024*5, backup_count=3):
        """
        初始化日志处理类。
        :param log_folder: 存储日志的文件夹
        :param log_file_prefix: 日志文件的前缀
        :param max_size: 单个日志文件的最大大小，单位字节
        :param backup_count: 日志文件的备份数量
        """
        self.log_folder = log_folder
        self.log_file_prefix = log_file_prefix
        self.max_size = max_size
        self.backup_count = backup_count

        # 如果日志文件夹不存在，创建该文件夹
        if not os.path.exists(self.log_folder):
            os.makedirs(self.log_folder)

        # 初始日志文件路径
        self.log_file = self.get_error_log_file_path()

        # 设置日志记录器
        self.logger = logging.getLogger('game_logger')
        self.set_up_logging()

    def set_up_logging(self):
        """配置日志记录器，设置日志文件大小自动切换"""
        # 错误日志文件
        error_log_file = self.get_error_log_file_path()
        error_handler = RotatingFileHandler(error_log_file, maxBytes=self.max_size, backupCount=self.backup_count)
        log_formatter = logging.Formatter('%(asctime)s - %(message)s')
        error_handler.setFormatter(log_formatter)

        # 添加处理器
        self.logger.addHandler(error_handler)
        self.logger.setLevel(logging.ERROR)  # 只记录错误日志

    def get_error_log_file_path(self):
        """获取当前时间的错误日志文件路径"""
        return os.path.join(self.log_folder, f"{self.log_file_prefix}_errors_{datetime.now().strftime('%Y%m%d%H%M%S')}.log")

    def log_error(self, message):
        """
        记录错误日志信息。
        :param message: 错误日志信息
        """
        self.logger.error(message)

    def view_logs(self):
        """
        查看并返回日志文件的内容。
        """
        try:
            with open(self.log_file, 'r', encoding="utf-8") as file:
                return file.read()
        except Exception as e:
            return f"无法读取日志文件：{e}"

    def generate_guide(self, guide_text="操作指南:\n1. 按 'w' 前进\n2. 按 's' 后退\n3. 按 'a' 向左\n4. 按 'd' 向右"):
        """
        生成操作指南文本文件。
        :param guide_text: 用户操作指南内容
        """
        try:
            guide_path = os.path.join(self.log_folder, "guide.md")
            with open(guide_path, "w", encoding="utf-8") as guide_file:
                guide_file.write(guide_text)
            self.log_error("操作指南已生成并保存为 'guide.md'")
        except Exception as e:
            self.log_error(f"生成操作指南失败：{e}")
