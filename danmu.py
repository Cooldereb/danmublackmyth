import requests
import json
from logHandler import LogHandler  # 引入 LogHandler

# 创建日志处理实例
log_handler = LogHandler()

def fetch_danmu(roomid):
    """获取指定房间号的最新弹幕"""
    url = f'https://api.live.bilibili.com/xlive/web-room/v1/dM/gethistory?roomid={roomid}&room_type=0'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
        'Referer': f'https://live.bilibili.com/{roomid}',
        'Origin': 'https://live.bilibili.com',
    }

    try:
        # log_handler.log_info(f"开始获取房间 {roomid} 的弹幕数据...")  # 日志记录开始爬取
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            data = response.json()
            if data['code'] == 0 and 'data' in data:
                # log_handler.log_info(f"成功获取房间 {roomid} 的弹幕数据。")  # 日志记录成功获取弹幕
                return data['data']['room']  # 返回弹幕数据
            else:
                log_handler.log_warning(f"房间 {roomid} 未获取到弹幕数据。")  # 记录警告日志
                return []
        else:
            log_handler.log_error(f"请求失败，房间 {roomid} 状态码：{response.status_code}")  # 错误日志
            return []

    except Exception as e:
        log_handler.log_error(f"爬取房间 {roomid} 弹幕失败：{e}")  # 记录异常日志
        return []
