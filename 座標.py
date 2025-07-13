import pyautogui
import keyboard
import time
import os

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

print("實時顯示滑鼠座標，按下 Esc 鍵退出。")
time.sleep(1)

try:
    while True:
        if keyboard.is_pressed('esc'):
            print("已退出。")
            break
        x, y = pyautogui.position()
        clear_console()
        print(f"滑鼠位置：X = {x}, Y = {y}")
        time.sleep(0.05)
except KeyboardInterrupt:
    pass
