import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import psutil
import re
import time

class USBHealthChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("USB 健康檢查工具")
        self.root.geometry("500x400")
        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self.root, text="選擇要檢查的 USB 隨身碟：")
        self.label.pack(pady=10)

        self.combo = ttk.Combobox(self.root, state="readonly")
        self.combo.pack(pady=5)

        self.refresh_button = ttk.Button(self.root, text="重新載入裝置", command=self.load_usb_devices)
        self.refresh_button.pack(pady=5)

        self.check_button = ttk.Button(self.root, text="開始檢查", command=self.start_check)
        self.check_button.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=10, fill='x', padx=20)

        self.output_text = tk.Text(self.root, height=10, wrap="word")
        self.output_text.pack(pady=10, fill='both', expand=True, padx=10)

        self.load_usb_devices()

    def load_usb_devices(self):
        self.combo['values'] = []
        self.usb_devices = []
        for part in psutil.disk_partitions():
            if 'removable' in part.opts or ('cdrom' not in part.opts and 'fixed' not in part.opts and part.device.startswith(('E:', 'F:', 'G:', 'H:', 'I:', 'J:', 'K:'))):
                self.usb_devices.append(part.device)
        if self.usb_devices:
            self.combo['values'] = self.usb_devices
            self.combo.current(0)
        else:
            messagebox.showwarning("找不到隨身碟", "未偵測到 USB 隨身碟，請插入後重新整理。")

    def start_check(self):
        selected = self.combo.get()
        if not selected:
            messagebox.showerror("錯誤", "請選擇一個磁碟機。")
            return
        self.output_text.delete(1.0, tk.END)
        self.progress.start()
        threading.Thread(target=self.check_disk, args=(selected,), daemon=True).start()

    def check_disk(self, drive_letter):
        start_time = time.time()
        try:
            process = subprocess.Popen(["chkdsk", drive_letter, "/f"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            output = ""
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                output += line
                self.update_output(line)
            process.wait()
            self.progress.stop()

            if "Windows has scanned the file system and found no problems" in output:
                health = "✅ 沒有發現錯誤，USB 裝置狀況良好"
            elif "bad sectors" in output and "0 KB" not in output:
                health = "⚠️ 偵測到壞軌，請儘速備份資料"
            else:
                health = "⚠️ 檢查完成，但結果無法明確判斷，請手動查看"

            elapsed = int(time.time() - start_time)
            self.update_output(f"\n---\n檢查完成：{health}\n用時：約 {elapsed} 秒\n")
            # 添加消息框显示检查结果
            messagebox.showinfo("檢查完成", health)

        except Exception as e:
            self.progress.stop()
            messagebox.showerror("錯誤", f"發生錯誤：{e}")

    def update_output(self, line):
        self.output_text.insert(tk.END, line)
        self.output_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = USBHealthChecker(root)
    root.mainloop()