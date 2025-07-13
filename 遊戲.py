import sys
import subprocess
import importlib
import os
import json
import tkinter as tk
from tkinter import messagebox
from cryptography.fernet import Fernet

# 自動檢查並安裝缺失套件
def install_package(package_name):
    try:
        importlib.import_module(package_name)
    except ImportError:
        print(f"正在安裝缺失的套件: {package_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
        print(f"{package_name} 安裝完成！")

# 安裝必要的套件
install_package("tkinter")
install_package("cryptography")

# 存檔路徑
save_dir = r"D:\自製遊戲"
save_file = os.path.join(save_dir, "clicker_game_save.json")
key_file = os.path.join(save_dir, "encryption_key.key")

# 確保存檔目錄存在
os.makedirs(save_dir, exist_ok=True)

# 生成或載入加密金鑰
def get_encryption_key():
    if os.path.exists(key_file):
        with open(key_file, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        with open(key_file, "wb") as f:
            f.write(key)
        return key

encryption_key = get_encryption_key()
cipher = Fernet(encryption_key)

# 遊戲數據
class ClickerGame:
    def __init__(self):
        self.points = 0
        self.click_value = 1
        self.upgrade_cost = 10

    def load_game(self):
        if os.path.exists(save_file):
            try:
                with open(save_file, "rb") as f:
                    encrypted_data = f.read()
                decrypted_data = cipher.decrypt(encrypted_data)
                data = json.loads(decrypted_data.decode())
                self.points = data.get("points", 0)
                self.click_value = data.get("click_value", 1)
                self.upgrade_cost = data.get("upgrade_cost", 10)
            except Exception as e:
                print(f"載入存檔失敗: {e}，使用默認值")

    def save_game(self):
        data = {
            "points": self.points,
            "click_value": self.click_value,
            "upgrade_cost": self.upgrade_cost
        }
        json_data = json.dumps(data).encode()
        encrypted_data = cipher.encrypt(json_data)
        with open(save_file, "wb") as f:
            f.write(encrypted_data)

# GUI 設計
def create_game_window():
    game = ClickerGame()
    game.load_game()  # 載入存檔

    window = tk.Tk()
    window.title("點擊遊戲")
    window.geometry("400x300")

    # 顯示點數
    points_label = tk.Label(window, text=f"點數: {game.points}", font=("Arial", 14))
    points_label.pack(pady=20)

    # 顯示每次點擊收益
    click_value_label = tk.Label(window, text=f"每次點擊: {game.click_value} 點", font=("Arial", 12))
    click_value_label.pack()

    # 點擊按鈕
    def click_button():
        game.points += game.click_value
        points_label.config(text=f"點數: {game.points}")
        game.save_game()  # 每次點擊自動存檔

    click_btn = tk.Button(window, text="點我加分！", command=click_button, font=("Arial", 12))
    click_btn.pack(pady=20)

    # 升級按鈕
    def upgrade_click():
        if game.points >= game.upgrade_cost:
            game.points -= game.upgrade_cost
            game.click_value += 1
            game.upgrade_cost = int(game.upgrade_cost * 1.1)  # 升級費用每次增加 10%
            points_label.config(text=f"點數: {game.points}")
            click_value_label.config(text=f"每次點擊: {game.click_value} 點")
            upgrade_btn.config(text=f"升級點擊 (成本: {game.upgrade_cost} 點)")
            game.save_game()  # 升級後存檔
        else:
            messagebox.showwarning("警告", "點數不足，無法升級！")

    upgrade_btn = tk.Button(window, text=f"升級點擊 (成本: {game.upgrade_cost} 點)", 
                           command=upgrade_click, font=("Arial", 12))
    upgrade_btn.pack(pady=20)

    # 關閉視窗時存檔
    def on_closing():
        game.save_game()
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_closing)
    window.mainloop()

# 啟動遊戲
create_game_window()