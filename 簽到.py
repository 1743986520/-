import subprocess
import socket
import time

時間 = 0

def is_connected(host='8.8.8.8', port=53, timeout=3):
    """
    嘗試連線到 Google DNS（8.8.8.8:53），用來偵測是否有網路
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False

# 程序啟動時立即執行一次
print("程序啟動，正在檢查網路連線...")
while not is_connected():
    print("尚未連線，3 秒後重試...")
    time.sleep(3)

print("已連上網路，執行原神簽到腳本")
subprocess.run(r'D:\桌面\原神簽到.bat', shell=True)

while True:
    if 時間 == 72000:  # 20小時 = 20*60*60 = 72000秒
        print("正在檢查網路連線...")
        while not is_connected():
            print("尚未連線，3 秒後重試...")
            time.sleep(3)
        
        print("已連上網路，執行原神簽到腳本")
        subprocess.run(r'D:\桌面\原神簽到.bat', shell=True)
        時間 = 0  # 重置計時器
    
    時間 += 1
    time.sleep(1)  # 每秒增加計時器
    print(時間)    # 顯示當前計時器值