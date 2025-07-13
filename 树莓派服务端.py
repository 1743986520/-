from flask import Flask, request, jsonify
import sqlite3
import time
import requests
from datetime import datetime

app = Flask(__name__)

# ===== 数据库配置 =====
DB_FILE = 'comm.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # 消息记录表
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 type TEXT, from_id TEXT, to_id TEXT,
                 morse TEXT, text TEXT, 
                 translation TEXT,
                 timestamp TEXT)''')
    
    # 警报记录表  
    c.execute('''CREATE TABLE IF NOT EXISTS alerts
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 from_id TEXT, to_id TEXT,
                 timestamp TEXT)''')
    
    # 设备注册表
    c.execute('''CREATE TABLE IF NOT EXISTS devices
                 (id TEXT PRIMARY KEY,
                 ip TEXT,
                 last_seen TEXT)''')
    
    conn.commit()
    conn.close()

init_db()

# ===== API路由 =====
@app.route('/register', methods=['POST'])
def register():
    """设备注册接口"""
    data = request.json
    device_id = data['id']
    ip = request.remote_addr
    ts = datetime.now().isoformat()  # 标准化时间格式
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("REPLACE INTO devices VALUES (?, ?, ?)", 
              (device_id, ip, ts))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "ip": ip})

@app.route('/send', methods=['POST'])
def send_message():
    """消息处理接口"""
    data = request.json
    data['timestamp'] = datetime.now().isoformat()
    
    # 存储到数据库
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''INSERT INTO messages 
                 (type, from_id, to_id, morse, text, translation, timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (data['type'], data['from'], data['to'],
               data['morse'], data['text'],
               data.get('translation', ''),
               data['timestamp']))
    conn.commit()
    conn.close()
    
    # 转发给目标设备
    forward_to_target(data['to'], data)
    return jsonify({"status": "sent"})

@app.route('/alert', methods=['POST'])
def handle_alert():
    """紧急警报接口"""
    data = request.json
    data['timestamp'] = datetime.now().isoformat()
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO alerts (from_id, to_id, timestamp) VALUES (?, ?, ?)",
              (data['from'], data['to'], data['timestamp']))
    conn.commit()
    conn.close()
    
    forward_to_target(data['to'], data)
    return jsonify({"status": "alert_triggered"})

# ===== 消息转发函数 =====
def forward_to_target(target_id, payload):
    """转发消息到目标设备"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT ip FROM devices WHERE id=?", (target_id,))
    target = c.fetchone()
    conn.close()
    
    if target:
        try:
            requests.post(
                f"http://{target[0]}:8000/receive",
                json=payload,
                timeout=3
            )
        except requests.exceptions.RequestException as e:
            print(f"转发失败: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)