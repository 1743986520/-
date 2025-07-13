import sys
import subprocess
import importlib

# 自動檢查並安裝缺失套件
def install_package(package_name):
    try:
        importlib.import_module(package_name)
    except ImportError:
        print(f"正在安裝缺失的套件: {package_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} 安裝完成！")

# 檢查並安裝必要的套件
for package in ["pyautogui", "tkinter"]:
    install_package(package)

# 導入套件
import tkinter as tk
from tkinter import messagebox
import pyautogui
import time

# 設置pyautogui的安全機制，避免失控
pyautogui.FAILSAFE = True

# 創建主視窗
window = tk.Tk()
window.title("超簡單連點器 - 支援無限模式")
window.geometry("300x250")

# 說明標籤
label = tk.Label(window, text="請輸入點擊間隔(秒)和次數\n移動到(0,0)可緊急停止")
label.pack(pady=10)

# 間隔時間輸入框
time_label = tk.Label(window, text="點擊間隔(秒):")
time_label.pack()
time_entry = tk.Entry(window)
time_entry.pack()
time_entry.insert(0, "0.5")  # 預設0.5秒

# 點擊次數輸入框
count_label = tk.Label(window, text="點擊次數(0為無限):")
count_label.pack()
count_entry = tk.Entry(window)
count_entry.pack()
count_entry.insert(0, "10")  # 預設10次

# 開始按鈕的函數
def start_clicking():
    try:
        interval = float(time_entry.get())
        count = int(count_entry.get())
        
        if interval <= 0:
            messagebox.showerror("錯誤", "間隔時間必須是正數！")
            return
        
        messagebox.showinfo("準備開始", "3秒後開始連點，請移動滑鼠到目標位置")
        time.sleep(3)
        
        if count == 0:  # 無限模式
            messagebox.showinfo("無限模式", "已進入無限連點，移動到(0,0)停止")
            while True:
                pyautogui.click()
                time.sleep(interval)
        else:  # 有限次數模式
            if count < 0:
                messagebox.showerror("錯誤", "點擊次數不能是負數！")
                return
            for i in range(count):
                pyautogui.click()
                time.sleep(interval)
            messagebox.showinfo("完成", "連點已結束！")
            
    except ValueError:
        messagebox.showerror("錯誤", "請輸入有效的數字！")

# 開始按鈕
start_button = tk.Button(window, text="開始連點", command=start_clicking)
start_button.pack(pady=20)

# 運行主循環
window.mainloop()