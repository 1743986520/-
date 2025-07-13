import psutil
import tkinter as tk
from tkinter import ttk
import time
import ctypes

# 初始記錄網路流量
net_io_old = psutil.net_io_counters()

# 嘗試獲取螢幕更新率（Hz）
def get_refresh_rate():
    user32 = ctypes.windll.user32
    dc = user32.GetDC(0)
    refresh_rate = ctypes.windll.gdi32.GetDeviceCaps(dc, 116)  # 116 = VREFRESH
    user32.ReleaseDC(0, dc)
    return refresh_rate

def update_stats():
    global net_io_old

    cpu_percent = psutil.cpu_percent()
    memory = psutil.virtual_memory()

    used_mem_gb = round(memory.used / (1024 ** 3), 2)
    total_mem_gb = round(memory.total / (1024 ** 3), 2)

    net_io_new = psutil.net_io_counters()
    bytes_sent = net_io_new.bytes_sent - net_io_old.bytes_sent
    bytes_recv = net_io_new.bytes_recv - net_io_old.bytes_recv
    net_io_old = net_io_new

    upload_speed = round(bytes_sent / 1024, 1)   # KB/s
    download_speed = round(bytes_recv / 1024, 1) # KB/s

    refresh_rate = get_refresh_rate()

    cpu_label.config(text=f"CPU 使用率：{cpu_percent}%")
    mem_label.config(text=f"記憶體使用：{used_mem_gb} / {total_mem_gb} GB")
    refresh_label.config(text=f"螢幕更新率：{refresh_rate} Hz")
    net_label.config(text=f"上傳：{upload_speed} KB/s　下載：{download_speed} KB/s")

    root.after(1000, update_stats)

# GUI 設定
root = tk.Tk()
root.title("系統資源監控")
root.geometry("360x200")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", background="#1e1e1e", foreground="white", font=("Microsoft JhengHei", 12))

cpu_label = ttk.Label(root, text="CPU 使用率：")
cpu_label.pack(pady=5)

mem_label = ttk.Label(root, text="記憶體使用：")
mem_label.pack(pady=5)

refresh_label = ttk.Label(root, text="螢幕更新率：")
refresh_label.pack(pady=5)

net_label = ttk.Label(root, text="上傳 / 下載速度：")
net_label.pack(pady=5)

update_stats()
root.mainloop()
