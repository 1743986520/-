#!/usr/bin/env python3
import os
import time
import random
import threading
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# 防止屏幕关闭（仅在 Termux 环境下有效）
os.system("termux-wake-lock")

# 全局变量：累计下载的字节数和脚本开始时间
total_size = 0
start_time = time.time()
lock = threading.Lock()  # 用于保护 total_size 的并发更新

# 定义颜色列表
colors = [
    "\033[31m", "\033[32m", "\033[33m",
    "\033[34m", "\033[35m", "\033[36m", "\033[37m"
]

def generate_heart():
    """
    随机生成 1 到 2 个彩色爱心表情。
    """
    heart_count = random.randint(1, 2)
    hearts = ""
    for _ in range(heart_count):
        color = random.choice(colors)
        hearts += f"{color}(≧∇≦)"
    return hearts

def get_current_time():
    """
    获取当前台湾时间，并返回带颜色的格式化字符串。
    """
    taipei_time = datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M")
    return f"\033[36m时间{taipei_time}\033[0m"

def download_thread(thread_id):
    """
    单线程下载函数，循环下载目标文件并输出日志。
    """
    global total_size, start_time
    download_count = 0
    url = "https://gw.alicdn.com/tfscom/TB1fASCxhjaK1RjSZKzXXXVwXXa.jpg"
    headers = {'User-Agent': 'Mozilla/5.0'}

    while True:
        download_count += 1

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            file_size = len(response.content)
        except Exception as e:
            elapsed_time = int(time.time() - start_time)
            print(f"\033[34m线程{thread_id} 第\033[31m{download_count}\033[34m次下载 - "
                  f"{get_current_time()} \033[33m系统运行时间：{elapsed_time} 秒\033[0m "
                  f"\033[31m下载失败\033[0m", flush=True)
            continue

        # 更新累计流量（加锁保证线程安全）
        with lock:
            total_size += file_size
            current_total = total_size

        # 单位换算
        total_kb = current_total / 1024.0
        total_mb = total_kb / 1024.0
        total_gb = total_mb / 1024.0

        elapsed_time = int(time.time() - start_time)
        if total_gb >= 1:
            traffic_str = f"\033[31m目前总消耗流量：{total_gb:.2f}\033[35m GB\033[0m"
        elif total_mb >= 1:
            traffic_str = f"\033[31m目前总消耗流量：{total_mb:.2f}\033[35m MB\033[0m"
        else:
            traffic_str = f"\033[31m目前总消耗流量：{total_kb:.2f}\033[35m KB\033[0m"

        print(f"\033[34m线程{thread_id} 第\033[31m{download_count}\033[34m次下载 - {traffic_str} "
              f"{generate_heart()} {get_current_time()} \033[33m运行时长：{elapsed_time} 秒\033[0m", flush=True)

        # 每下载 3070 次时删除 temp_file 文件，并重置计数器
        if download_count == 3070:
            print(f"\033[31m线程{thread_id} 下载次数达到3070次，删除文件...\033[0m", flush=True)
            try:
                if os.path.exists("temp_file"):
                    os.remove("temp_file")
            except Exception:
                pass
            download_count = 0

def main():
    threads = []
    # 启动 4 个下载线程
    for i in range(1, 5):
        t = threading.Thread(target=download_thread, args=(i,))
        t.start()
        threads.append(t)

    # 等待所有线程结束（实际上无限循环，不会退出）
    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
