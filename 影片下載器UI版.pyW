import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp
import os
import threading
import re
from datetime import datetime

class VideoDownloaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("影片下載器")
        self.root.geometry("600x350")
        self.download_path = tk.StringVar(value=os.path.expanduser("~/Downloads"))  # 預設下載路徑
        self.log_path = os.path.join(os.path.expanduser("~/Downloads"), "下載紀錄.txt")
        self.url = tk.StringVar()
        self.format_var = tk.StringVar(value="video")
        self.playlist_var = tk.StringVar(value="否")

        self.create_widgets()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 影片網址
        ttk.Label(main_frame, text="影片網址：").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.url, width=50).grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="從剪貼簿提取", command=self.extract_url_from_clipboard).grid(row=0, column=3, padx=5)

        # 下載格式
        ttk.Label(main_frame, text="下載格式：").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(main_frame, text="影片 (MP4)", variable=self.format_var, value="video").grid(row=1, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="音訊 (MP3)", variable=self.format_var, value="audio").grid(row=1, column=2, sticky=tk.W)

        # 播放清單
        ttk.Label(main_frame, text="下載播放清單：").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Radiobutton(main_frame, text="是", variable=self.playlist_var, value="是").grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(main_frame, text="否", variable=self.playlist_var, value="否").grid(row=2, column=2, sticky=tk.W)

        # 自訂檔名
        ttk.Label(main_frame, text="自訂檔名 (選填)：").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.filename_entry = ttk.Entry(main_frame, width=50)
        self.filename_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        # 儲存路徑
        ttk.Label(main_frame, text="儲存路徑：").grid(row=4, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.download_path, width=50).grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        ttk.Button(main_frame, text="選擇資料夾", command=self.choose_path).grid(row=4, column=3, padx=5)

        # 下載按鈕
        self.download_button = ttk.Button(main_frame, text="開始下載", command=self.start_download_thread)
        self.download_button.grid(row=5, column=0, columnspan=4, pady=10)

        # 進度條
        self.progress_bar = ttk.Progressbar(main_frame, length=400, mode="determinate")
        self.progress_bar.grid(row=6, column=0, columnspan=4, pady=5)

        # 狀態顯示
        self.status_label = ttk.Label(main_frame, text="請輸入網址並選擇選項", wraplength=500)
        self.status_label.grid(row=7, column=0, columnspan=4, pady=5)

        # 支援縮放
        main_frame.columnconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

    def choose_path(self):
        path = filedialog.askdirectory()
        if path:
            self.download_path.set(path)
            self.log_path = os.path.join(path, "下載紀錄.txt")

    def extract_url_from_clipboard(self):
        try:
            clipboard_content = self.root.clipboard_get()
            url_regex = r'(https?://[^\s<>"]+|www\.[^\s<>"]+)'
            match = re.search(url_regex, clipboard_content)
            if match:
                url = match.group(0)
                if not url.startswith("http"):
                    url = "https://" + url
                self.url.set(url)
                self.status_label.config(text=f"已提取網址: {url}")
            else:
                messagebox.showerror("錯誤", "剪貼簿中無有效網址")
        except Exception as e:
            messagebox.showerror("錯誤", f"無法從剪貼簿讀取網址: {e}")

    def start_download_thread(self):
        if not self.url.get():
            messagebox.showwarning("警告", "請輸入影片網址")
            return
        if not self.download_path.get():
            messagebox.showwarning("警告", "請選擇儲存資料夾")
            return
        threading.Thread(target=self.download_video, daemon=True).start()

    def download_video(self):
        self.progress_bar["value"] = 0
        self.status_label.config(text="正在初始化下載...")
        self.download_button.config(state="disabled")

        os.makedirs(self.download_path.get(), exist_ok=True)
        ydl_opts = {
            "progress_hooks": [self.progress_hook],
            "outtmpl": os.path.join(self.download_path.get(), "%(title)s.%(ext)s"),
            "noplaylist": (self.playlist_var.get() == "否"),
            "quiet": True,
            "no_warnings": True
        }

        filename = self.filename_entry.get().strip()
        if filename:
            ydl_opts["outtmpl"] = os.path.join(self.download_path.get(), filename + ".%(ext)s")

        if self.format_var.get() == "audio":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        else:
            ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4"

        start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = "未知"
        success = False

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(self.url.get(), download=True)
                title = info_dict.get("title", filename if filename else "未知")
                success = True
                self.status_label.config(text="下載完成 ✅")
        except Exception as e:
            self.status_label.config(text=f"下載失敗: {e}")
            messagebox.showerror("錯誤", f"下載過程發生錯誤: {e}")  # 修正此行
        finally:
            self.download_button.config(state="normal")
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(f"[{start_time}] 狀態: {'成功 ✅' if success else '失敗 ❌'}\n")
                f.write(f"  名稱: {title}\n")
                f.write(f"  網址: {self.url.get()}\n\n")

    def progress_hook(self, d):
        if d["status"] == "downloading":
            percent = 0
            if "downloaded_bytes" in d and "total_bytes" in d:
                percent = (d["downloaded_bytes"] / d["total_bytes"]) * 100
            elif "_percent_str" in d:
                percent = float(d["_percent_str"].replace("%", "").strip())

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