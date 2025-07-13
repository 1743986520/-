import requests
import threading
import time
from flask import Flask, request, jsonify

# ===== 配置區 =====
DEVICE_ID = "PC_001"
TARGET_ID = "ESP_001"  # 目標 ESP32
SERVER = "http://192.168.1.100:5000"
LISTEN_PORT = 8000

app = Flask(__name__)
received_messages = []

# ===== 註冊設備 =====
def register_device():
    try:
        res = requests.post(f"{SERVER}/register", json={"id": DEVICE_ID})
        if res.ok:
            print(f"[註冊成功] 我的ID: {DEVICE_ID}")
        else:
            print("[註冊失敗]", res.text)
    except Exception as e:
        print("[連線錯誤]", e)

# ===== 傳送訊息 =====
def send_message(text):
    morse = "...."  # 模擬摩斯碼，可加轉換函數
    payload = {
        "from": DEVICE_ID,
        "to": TARGET_ID,
        "type": "message",
        "morse": morse,
        "text": text,
        "translation": text
    }
    try:
        res = requests.post(f"{SERVER}/send", json=payload)
        if res.ok:
            print(f"[已發送] {text} -> {TARGET_ID}")
        else:
            print("[發送失敗]", res.text)
    except Exception as e:
        print("[錯誤]", e)

# ===== 接收伺服器轉發訊息 =====
@app.route('/receive', methods=['POST'])
def receive():
    data = request.json
    from_id = data.get('from', '未知')
    content = data.get('text', '[無內容]')
    print(f"\n[收到訊息] 來自 {from_id}: {content}")
    received_messages.append(data)
    return jsonify({"status": "ok"})

# ===== 啟動接收伺服器 =====
def run_receiver():
    app.run(host="0.0.0.0", port=LISTEN_PORT)

# ===== 主互動流程 =====
def main_loop():
    while True:
        text = input("輸入訊息（或按 enter 跳過）: ")
        if text.strip():
            send_message(text)

# ===== 主程序 =====
if __name__ == "__main__":
    register_device()

    # 啟動 Flask server 作為背景執行緒
    threading.Thread(target=run_receiver, daemon=True).start()
    
    # 主回合互動
    time.sleep(1)
    print(f"聊天開始：你是 {DEVICE_ID}，目標是 {TARGET_ID}")
    main_loop()