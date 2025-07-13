import pyautogui
import time

def ask_and_repeat_clicks():
    points = []

    print("🔧 輸入你要依序點擊的座標。輸入 'q' 結束輸入。")
    while True:
        x_input = input("請輸入 X 座標（或輸入 q 結束）：")
        if x_input.lower() == 'q':
            break
        y_input = input("請輸入 Y 座標：")
        try:
            x = int(x_input)
            y = int(y_input)
            points.append((x, y))
        except ValueError:
            print("⚠️ 輸入錯誤，請重新輸入。")

    if not points:
        print("❌ 沒有輸入任何點，程式結束。")
        return

    try:
        repeat_count = int(input("🔁 請輸入要重複整組點擊幾輪："))
        delay = float(input("⌛ 每個點之間延遲幾秒（例如 0.5）："))
    except ValueError:
        print("❌ 輸入錯誤，程式結束。")
        return

    print("\n🚀 即將開始點擊所有座標，請在 3 秒內準備好畫面。")
    time.sleep(3)

    for round_num in range(repeat_count):
        print(f"\n🔁 第 {round_num+1} 輪開始")
        for index, (x, y) in enumerate(points):
            print(f"👉 點擊第 {index+1} 點：({x}, {y})")
            pyautogui.click(x, y)
            time.sleep(delay)

    print("\n✅ 所有點擊完成！")

if __name__ == "__main__":
    ask_and_repeat_clicks()
