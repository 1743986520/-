import yt_dlp
import os
import tkinter as tk
from tkinter import messagebox, ttk
import threading
import re

class VideoDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("影片下載器")
        self.download_path = r"D:\兮兮兮"
        os.makedirs(self.download_path, exist_ok=True)

        # 主框架
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 影片網址輸入
        ttk.Label(self.main_frame, text="影片網址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.url_entry = ttk.Entry(self.main_frame, width=50)
        self.url_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(self.main_frame, text="從剪貼簿提取", command=self.extract_url_from_clipboard).grid(row=0, column=3, padx=5)

        # 下載格式選擇
        ttk.Label(self.main_frame, text="下載格式:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.format_var = tk.StringVar(value="1")
        ttk.Radiobutton(self.main_frame, text="影片 (MP4)", variable=self.format_var, value="1").grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(self.main_frame, text="音訊 (MP3)", variable=self.format_var, value="2").grid(row=1, column=2, sticky=tk.W)

        # 播放清單選擇
        ttk.Label(self.main_frame, text="下載播放清單:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.playlist_var = tk.StringVar(value="是")
        ttk.Radiobutton(self.main_frame, text="是", variable=self.playlist_var, value="是").grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(self.main_frame, text="否", variable=self.playlist_var, value="否").grid(row=2, column=2, sticky=tk.W)

        # 自訂檔名
        ttk.Label(self.main_frame, text="自訂檔名 (選填):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.filename_entry = ttk.Entry(self.main_frame, width=50)
        self.filename_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 下載按鈕
        self.download_button = ttk.Button(self.main_frame, text="開始下載", command=self.start_download_thread)
        self.download_button.grid(row=4, column=0, columnspan=4, pady=10)

        # 進度條
        self.progress_bar = ttk.Progressbar(self.main_frame, length=400, mode="determinate")
        self.progress_bar.grid(row=5, column=0, columnspan=4, pady=5)

        # 狀態顯示
        self.status_label = ttk.Label(self.main_frame, text="請輸入網址並選擇選項", wraplength=500)
        self.status_label.grid(row=6, column=0, columnspan=4, pady=5)

        # 支援縮放
        self.main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def extract_url_from_clipboard(self):
        try:
            clipboard_content = self.root.clipboard_get()
            url_regex = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'
            match = re.search(url_regex, clipboard_content)
            if match:
                url = match.group(0)
                if not url.startswith("http"):
                    url = "https://" + url
                self.url_entry.delete(0, tk.END)
                self.url_entry.insert(0, url)
                self.status_label.config(text=f"已提取網址: {url}")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法從剪貼簿讀取網址: {e}")

    def start_download_thread(self):
        threading.Thread(target=self.download_video, daemon=True).start()

    def download_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("警告", "請輸入影片網址")
            return

        self.progress_bar["value"] = 0
        self.status_label.config(text="正在初始化下載...")
        self.download_button.config(state="disabled")

        ydl_opts = {
            "progress_hooks": [self.progress_hook],
            "outtmpl": os.path.join(self.download_path, "%(title)s.%(ext)s"),
            "noplaylist": (self.playlist_var.get() == "否"),
            "quiet": True,
            "no_warnings": True
        }

        filename = self.filename_entry.get().strip()
        if filename:
            ydl_opts["outtmpl"] = os.path.join(self.download_path, filename + ".%(ext)s")

        if self.format_var.get() == "2":  # MP3
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        else:  # MP4
            ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            self.status_label.config(text=f"下載失敗: {e}")
            messagebox.showerror("錯誤", f"下載過程發生錯誤: {e}")
        finally:
            self.download_button.config(state="normal")

    def progress_hook(self, d):
        if d["status"] == "downloading":
            percent = 0
            if "downloaded_bytes" in d and "total_bytes" in d:
                try:
                    percent = (d["downloaded_bytes"] / d["total_bytes"]) * 100
                except:
                    percent = 0
            elif "_percent_str" in d:
                try:
                    percent = float(d["_percent_str"].replace("%", "").strip())
                except:
                    percent = 0

            speed = d.get("speed", 0) or 0
            eta = d.get("eta", 0)
            speed_mb = speed / 1024 / 1024

            self.root.after(0, self.update_progress, percent,
                            f"下載中: {percent:.1f}% | 速度: {speed_mb:.2f} MB/s | ETA: {eta}s")

        elif d["status"] == "finished":
            self.root.after(0, self.update_progress, 100, "下載完成 ✅")

    def update_progress(self, value, text):
        self.progress_bar["value"] = value
        self.status_label.config(text=text)


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderGUI(root)
    root.mainloop()
