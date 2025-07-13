import os
import time
import random
import threading
import requests
from datetime import datetime
from zoneinfo import ZoneInfo

# 移除 termux 指令
# os.system("termux-wake-lock")

# 全局變量
total_size = 0
start_time = time.time()
lock = threading.Lock()

# 顏色（移除 ANSI 顏色碼）
colors = ["(≧∇≦)", "(♥ω♥*)", "(๑˃̵ᴗ˂̵)و"]

def generate_heart():
    """隨機生成 1 到 2 個愛心表情"""
    return "".join(random.choices(colors, k=random.randint(1, 2)))

def get_current_time():
    """獲取當前台灣時間"""
    return datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M")

def download_thread(thread_id):
    """單線程下載函數"""
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
        except Exception:
            elapsed_time = int(time.time() - start_time)
            print(f"[線程{thread_id}] 第{download_count}次下載 - {get_current_time()} "
                  f"運行時間：{elapsed_time} 秒 下載失敗", flush=True)
            continue

        # 更新總流量（加鎖保護）
        with lock:
            total_size += file_size
            current_total = total_size

        # 單位換算
        total_kb = current_total / 1024.0
        total_mb = total_kb / 1024.0
        total_gb = total_mb / 1024.0

        if total_gb >= 1:
            traffic_str = f"總流量：{total_gb:.2f} GB"
        elif total_mb >= 1:
            traffic_str = f"總流量：{total_mb:.2f} MB"
        else:
            traffic_str = f"總流量：{total_kb:.2f} KB"

        elapsed_time = int(time.time() - start_time)
        print(f"[線程{thread_id}] 第{download_count}次下載 - {traffic_str} {generate_heart()} "
              f"{get_current_time()} 運行時長：{elapsed_time} 秒", flush=True)

        # 每下載 3070 次時刪除 temp_file
        if download_count == 3070:
            print(f"[線程{thread_id}] 下載次數達到 3070，刪除 temp_file...", flush=True)
            try:
                if os.path.exists("temp_file"):
                    os.remove("temp_file")
            except Exception:
                pass
            download_count = 0

def main():
    threads = []
    for i in range(1, 5):  # 啟動 4 個下載線程
        t = threading.Thread(target=download_thread, args=(i,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

if __name__ == "__main__":
    main()
