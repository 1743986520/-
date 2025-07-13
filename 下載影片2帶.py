import yt_dlp
import os
import time

def download_video():
    download_path = "D:\\兮兮兮"  # 指定下載位置
    os.makedirs(download_path, exist_ok=True)  # 如果資料夾不存在則自動創建

    while True:
        url = input("輸入影片網址 (按 Enter 結束): ").strip()
        if not url:
            print("未輸入網址，結束下載。")
            break

        format_choice = input("選擇下載格式 (1: 影片 MP4, 2: 音訊 MP3): ").strip()

        if format_choice == "1":
            ydl_opts = {
                "format": "bestvideo+bestaudio/best",
                "outtmpl": os.path.join(download_path, "%(title)s.%(ext)s"),
                "noplaylist": False,
                "fragment_retries": 10,  # 片段下載失敗時最多重試 10 次
                "merge_output_format": "mp4",  # 合併輸出為 MP4 格式
                "concurrent_fragment_downloads": 10,  # 設定同時下載 10 個片段
            }
        elif format_choice == "2":
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": os.path.join(download_path, "%(title)s.mp3"),
                "noplaylist": False,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "fragment_retries": 10,
                "concurrent_fragment_downloads": 10,
            }
        else:
            print("無效選擇，請輸入 1 或 2。")
            continue

        playlist_choice = input("是否下載整個播放清單? (是/否): ").strip().lower()
        if playlist_choice == "否":
            ydl_opts["noplaylist"] = True

        # 記錄開始時間
        start_time = time.time()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("下載完成 ✅")
        except Exception as e:
            print(f"下載失敗 ❌: {e}")

        # 記錄結束時間並計算耗時
        end_time = time.time()
        total_time = end_time - start_time
        minutes, seconds = divmod(total_time, 60)
        print(f"總耗時: {int(minutes)} 分 {int(seconds)} 秒 ⏳")

        A = input("是否繼續下載? (是/否): ").strip()
        if A.lower() != "是":
            print("結束下載。")
            break

download_video()
