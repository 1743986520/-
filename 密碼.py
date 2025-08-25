import tkinter as tk
from tkinter import messagebox, filedialog
import string
import itertools

BATCH_SIZE = 10000  # 每次寫入檔案的緩存條數

def generate_passwords(chars, min_len, max_len, output_file, update_callback=None):
    with open(output_file, "w", encoding="utf-8") as f:
        for length in range(min_len, max_len + 1):
            buffer = []
            for i, combo in enumerate(itertools.product(chars, repeat=length), start=1):
                buffer.append("".join(combo))
                if len(buffer) >= BATCH_SIZE:
                    f.write("\n".join(buffer) + "\n")
                    buffer.clear()
                    if update_callback:
                        update_callback(i)
            if buffer:
                f.write("\n".join(buffer) + "\n")

def start_generation():
    try:
        min_len = int(entry_min.get())
        max_len = int(entry_max.get())
        if min_len > max_len or min_len <= 0:
            messagebox.showerror("錯誤", "請確認密碼長度範圍")
            return
        
        chars = ""
        if var_numbers.get(): chars += string.digits
        if var_letters.get(): chars += string.ascii_letters
        if var_symbols.get(): chars += string.punctuation
        
        if not chars:
            messagebox.showerror("錯誤", "請至少選擇一種字元類型")
            return
        
        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt")],
            title="選擇輸出檔案"
        )
        if not output_file:
            return
        
        label_status.config(text="正在生成字典，請稍候...")
        window.update()
        
        def update_progress(count):
            label_status.config(text=f"已生成約 {count} 條...")
            window.update()
        
        generate_passwords(chars, min_len, max_len, output_file, update_progress)
        label_status.config(text=f"完成！字典已儲存到 {output_file}")
    except ValueError:
        messagebox.showerror("錯誤", "請輸入正確的數字")

# GUI
window = tk.Tk()
window.title("WiFi 密碼字典生成器 (加速版)")
window.geometry("400x250")

tk.Label(window, text="最短密碼長度:").pack()
entry_min = tk.Entry(window)
entry_min.pack()
entry_min.insert(0, "6")

tk.Label(window, text="最長密碼長度:").pack()
entry_max = tk.Entry(window)
entry_max.pack()
entry_max.insert(0, "8")

var_numbers = tk.BooleanVar(value=True)
var_letters = tk.BooleanVar(value=True)
var_symbols = tk.BooleanVar(value=False)

tk.Checkbutton(window, text="包含數字", variable=var_numbers).pack()
tk.Checkbutton(window, text="包含字母", variable=var_letters).pack()
tk.Checkbutton(window, text="包含符號", variable=var_symbols).pack()

tk.Button(window, text="開始生成字典", command=start_generation).pack(pady=10)
label_status = tk.Label(window, text="")
label_status.pack()

window.mainloop()