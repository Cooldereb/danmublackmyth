import time
import threading
import pyautogui
from logHandler import LogHandler

# 初始化日志处理器
log_handler = LogHandler()

# 预输入相关
pre_input_queue = []  # 存储预输入的指令
pre_input_duration = 0.5  # 执行完一条预输入指令后再执行下一条的默认间隔
max_pre_input_count = 5  # 最大预输入数量

# 线程 & 中断相关
pre_input_thread = None  # 预输入执行的线程
interrupt_pre_input = False  # 是否中断（打断）正在执行的预输入指令
queue_lock = threading.Lock()  # 用于保护对队列和中断标志的访问


def handle_danmu_action(danmu_text):
    """
    根据弹幕内容执行对应的动作 (主入口)。
    新增逻辑：
      1) 若弹幕中含有中文逗号，说明是多条预输入指令 -> 加入队列并启动线程。
      2) 若无逗号，则直接在这里进行处理(可能打断预输入)。
    """
    stripped_text = danmu_text.strip()

    # ============ 如果含有中文逗号 => 预输入多条指令 ============
    if '，' in stripped_text:
        add_to_pre_input_queue(stripped_text)  # 拆分并加入队列
        start_pre_input_thread()  # 启动/重启执行线程
        return

    # ============ 若无逗号 => 可能需要打断预输入并直接执行 ============
    # 这里演示“任何新弹幕都打断”，你可改成仅“翻滚”或其他指令才打断
    with queue_lock:
        if pre_input_thread and pre_input_thread.is_alive():
            # 若线程正在执行预输入 => 设置中断标志
            global interrupt_pre_input
            interrupt_pre_input = True
            log_handler.log_error(f"检测到新弹幕 [{stripped_text}]，中断当前预输入队列...")

    # 执行单条指令
    # 先检查是否是特殊指令
    for command, action in SPECIAL_COMMANDS.items():
        if stripped_text.startswith(command):
            action(stripped_text)
            return

    # 再检查 ACTION_MAPPING
    for keywords, keys, duration in ACTION_MAPPING:
        if any(stripped_text == word for word in keywords):
            if isinstance(keys, str):  # 单键
                perform_key(keys, duration)
            elif isinstance(keys, tuple):  # 组合键
                perform_combo_keys(keys, duration)
            elif keys in ["scroll_up", "scroll_down"]:  # 滚轮操作
                perform_scroll(keys)
            return

    # 未匹配 => 报错
    log_handler.log_error(f"未能识别弹幕内容: {danmu_text}")


def add_to_pre_input_queue(danmu_text):
    """
    将含中文逗号 '，' 的多条指令拆分，并加入预输入队列(最多5条)。
    """
    global pre_input_queue
    commands = danmu_text.split('，')
    commands = [cmd.strip() for cmd in commands if cmd.strip()]

    with queue_lock:
        if len(pre_input_queue) + len(commands) <= max_pre_input_count:
            pre_input_queue.extend(commands)
            log_handler.log_error(f"预输入队列已更新: {pre_input_queue}")
        else:
            log_handler.log_error(f"预输入队列已满，无法添加更多指令：{commands}")


def start_pre_input_thread():
    """
    启动(或重启)一个新的线程来执行预输入队列。
    若已有线程在运行，通常不必重启；这里直接重启可以覆盖掉前一个线程(或打断)。
    """
    global pre_input_thread, interrupt_pre_input

    with queue_lock:
        # 若已有线程在跑，先中断它
        if pre_input_thread and pre_input_thread.is_alive():
            interrupt_pre_input = True

    # 启动一个新线程来执行
    t = threading.Thread(target=execute_pre_input_thread_func, daemon=True)
    pre_input_thread = t
    t.start()


def execute_pre_input_thread_func():
    """
    线程函数：顺序执行 pre_input_queue 中的指令，每条之间sleep pre_input_duration。
    若发现 interrupt_pre_input = True，则立刻中断执行剩余队列。
    """
    global pre_input_queue, interrupt_pre_input

    log_handler.log_error("预输入线程启动，开始执行队列...")

    while True:
        with queue_lock:
            # 若队列空 或 被中断 => 退出
            if not pre_input_queue or interrupt_pre_input:
                break
            cmd = pre_input_queue.pop(0)  # 取队列头

        # 执行指令
        log_handler.log_error(f"执行预输入指令: {cmd}")
        handle_single_command(cmd)

        # 每执行一条，sleep一下
        time.sleep(pre_input_duration)

        # 执行后再检查中断
        with queue_lock:
            if interrupt_pre_input:
                break

    with queue_lock:
        # 线程退出前，重置标志 & 清空队列(可选)
        log_handler.log_error("预输入线程结束.")
        interrupt_pre_input = False
        pre_input_queue = []


def handle_single_command(cmd):
    """
    仅执行单条弹幕指令(不处理逗号拆分、不考虑预输入队列)。
    这是给线程内部使用，避免互相递归调用 handle_danmu_action。
    """
    stripped_text = cmd.strip()

    # 检查是否为特殊指令
    for command, action in SPECIAL_COMMANDS.items():
        if stripped_text.startswith(command):
            action(stripped_text)
            return

    # 普通指令
    for keywords, keys, duration in ACTION_MAPPING:
        if any(stripped_text == word for word in keywords):
            if isinstance(keys, str):
                perform_key(keys, duration)
            elif isinstance(keys, tuple):
                perform_combo_keys(keys, duration)
            elif keys in ["scroll_up", "scroll_down"]:
                perform_scroll(keys)
            return

    log_handler.log_error(f"未能识别(预输入)弹幕内容: {cmd}")


# ============ 基础操作函数 ============
def perform_key(key, duration=0.5):
    pyautogui.keyDown(key)
    time.sleep(duration)
    pyautogui.keyUp(key)


def perform_combo_keys(keys, duration=0.5):
    for k in keys:
        pyautogui.keyDown(k)
    time.sleep(duration)
    for k in keys:
        pyautogui.keyUp(k)


def perform_scroll(direction):
    pyautogui.scroll(1 if direction == 'scroll_up' else -1)


def perform_combo_clicks(button, interval, duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        pyautogui.click(button=button)
        time.sleep(interval)


# ============ 特殊动作函数 ============
def perform_charged_attack(danmu_text):
    """
    执行重攻击，分为两部分：
    - 按下右键 0.2 秒：这是普通的重攻击。
    - '重攻击1'，'重攻击2'，'重攻击3'：表示蓄力攻击，按下右键 2.5 秒。
    """
    try:
        # 默认重攻击1，不带数字则执行按下右键 0.2 秒
        num_segments = 1
        if '重攻击' in danmu_text:
            parts = danmu_text.split('重攻击')
            if len(parts) > 1 and parts[1].strip().isdigit():
                num_segments = int(parts[1].strip())  # 根据数字设置段数（1、2、3）

        # 执行普通重攻击
        pyautogui.mouseDown(button='right')
        time.sleep(0.2)  # 按下右键 0.2 秒
        pyautogui.mouseUp(button='right')

        # 执行蓄力攻击，每段 2.5 秒
        for _ in range(num_segments):
            pyautogui.mouseDown(button='right')
            time.sleep(2.5)  # 每段蓄力 2.5 秒
            pyautogui.mouseUp(button='right')

    except Exception as e:
        log_handler.log_error(f"重攻击执行失败: {e}")


def perform_stick_spin(danmu_text):
    try:
        duration = 0.5
        if '棍花' in danmu_text:
            parts = danmu_text.split('棍花')
            if len(parts) > 1 and parts[1].strip().replace('.', '', 1).isdigit():
                duration = float(parts[1].strip())
                duration = max(0.1, min(5, duration))
        pyautogui.keyDown('v')
        time.sleep(duration)
        pyautogui.keyUp('v')
    except Exception as e:
        log_handler.log_error(f"棍花操作失败: {e}")


def perform_jump_attack(danmu_text):
    try:
        pyautogui.keyDown('ctrl')
        time.sleep(0.2)
        pyautogui.keyUp('ctrl')
        time.sleep(0.1)
        pyautogui.click(button='left')
    except Exception as e:
        log_handler.log_error(f"跳跃攻击执行失败: {e}")


def perform_combo1(_):
    perform_combo_clicks(button='left', interval=0.1, duration=4.5)


def perform_sprint(danmu_text):
    """
    疾跑/冲刺指令(与原先相同)，省略多余注释
    """
    try:
        text = danmu_text.replace("疾跑", "").replace("冲刺", "").strip()
        duration = 1.0
        direction_map = {
            "前进": ('w',),
            "后退": ('s',),
            "向左": ('a',),
            "向右": ('d',),
            "左前": ('a', 'w'),
            "右前": ('d', 'w'),
            "左后": ('a', 's'),
            "右后": ('d', 's'),
        }

        # ...解析 text, direction, duration, 参考之前的写法(省略)
        # 这里简化为默认前进1秒
        pyautogui.keyDown('shift')
        pyautogui.keyDown('w')
        time.sleep(duration)
        pyautogui.keyUp('w')
        pyautogui.keyUp('shift')

    except Exception as e:
        log_handler.log_error(f"疾跑/冲刺执行失败: {e}")


def perform_lock_target():
    try:
        pyautogui.mouseDown(button='middle')
        time.sleep(0.1)
        pyautogui.mouseUp(button='middle')
    except Exception as e:
        log_handler.log_error(f"锁定敌人操作失败: {e}")


# ============ 普通指令映射表 ============
ACTION_MAPPING = [
    (["前进", "向前走", "往前", "前面", "走前面", "前行"], 'w', 0.5),
    (["后退", "向后走", "往后", "后面", "退后", "撤退", "向后"], 's', 0.5),
    (["向左", "左转", "往左", "左边", "左移", "左拐", "左行"], 'a', 0.5),
    (["向右", "右转", "往右", "右边", "右移", "右拐", "右行"], 'd', 0.5),
    (["左前"], ('a', 'w'), 0.5),
    (["右前"], ('d', 'w'), 0.5),
    (["左后"], ('a', 's'), 0.5),
    (["右后"], ('d', 's'), 0.5),
    (["喝药", "喝酒", "回复", "回血", "恢复"], 'r', 0.2),
    (["翻滚"], 'space', 0.2),
]

# ============ 特殊指令映射表 ============
SPECIAL_COMMANDS = {
    "连招1": perform_combo1,
    "重攻击": perform_charged_attack,
    "棍花": perform_stick_spin,
    "跳跃攻击": perform_jump_attack,
    "疾跑": perform_sprint,
    "冲刺": perform_sprint,
    "锁定敌人": perform_lock_target,
}
