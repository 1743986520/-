import os
import time
import sys
import subprocess
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

class WiFiCrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi密码安全性测试工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 变量
        self.is_scanning = False
        self.is_cracking = False
        self.stop_requested = False
        
        self.setup_ui()
        self.check_system()
    
    def setup_ui(self):
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 系统信息
        sys_frame = ttk.LabelFrame(main_frame, text="系统信息", padding="5")
        sys_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.sys_label = ttk.Label(sys_frame, text="检测系统中...")
        self.sys_label.grid(row=0, column=0, sticky=tk.W)
        
        # WiFi接口设置
        interface_frame = ttk.LabelFrame(main_frame, text="网络接口设置", padding="5")
        interface_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(interface_frame, text="网络接口:").grid(row=0, column=0, sticky=tk.W)
        self.interface_var = tk.StringVar(value="wlan0")
        interface_combo = ttk.Combobox(interface_frame, textvariable=self.interface_var, width=15)
        interface_combo['values'] = ('wlan0', 'wlan1', 'en0', 'en1', 'Wi-Fi')
        interface_combo.grid(row=0, column=1, padx=5)
        
        ttk.Button(interface_frame, text="检查接口", command=self.check_interface).grid(row=0, column=2, padx=5)
        self.interface_status = ttk.Label(interface_frame, text="未检查")
        self.interface_status.grid(row=0, column=3, padx=5)
        
        # 扫描区域
        scan_frame = ttk.LabelFrame(main_frame, text="WiFi网络扫描", padding="5")
        scan_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(scan_frame, text="扫描可用网络", command=self.scan_wifi).grid(row=0, column=0, pady=5)
        self.scan_status = ttk.Label(scan_frame, text="就绪")
        self.scan_status.grid(row=0, column=1, padx=5)
        
        # 网络列表
        ttk.Label(scan_frame, text="可用网络:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        # 创建树状视图显示网络
        columns = ('SSID', 'BSSID', '信号强度', '加密方式')
        self.network_tree = ttk.Treeview(scan_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.network_tree.heading(col, text=col)
            self.network_tree.column(col, width=120)
        
        self.network_tree.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(scan_frame, orient=tk.VERTICAL, command=self.network_tree.yview)
        self.network_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=2, column=4, sticky=(tk.N, tk.S))
        
        # 目标网络设置
        target_frame = ttk.LabelFrame(main_frame, text="目标网络设置", padding="5")
        target_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(target_frame, text="SSID:").grid(row=0, column=0, sticky=tk.W)
        self.ssid_var = tk.StringVar()
        ttk.Entry(target_frame, textvariable=self.ssid_var, width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(target_frame, text="BSSID:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.bssid_var = tk.StringVar()
        ttk.Entry(target_frame, textvariable=self.bssid_var, width=20).grid(row=0, column=3, padx=5)
        
        # 字典文件选择
        dict_frame = ttk.LabelFrame(main_frame, text="密码字典设置", padding="5")
        dict_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(dict_frame, text="字典文件:").grid(row=0, column=0, sticky=tk.W)
        self.dict_var = tk.StringVar()
        ttk.Entry(dict_frame, textvariable=self.dict_var, width=50).grid(row=0, column=1, padx=5)
        ttk.Button(dict_frame, text="浏览", command=self.browse_dict).grid(row=0, column=2, padx=5)
        
        # 破解设置
        crack_frame = ttk.LabelFrame(main_frame, text="破解设置", padding="5")
        crack_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(crack_frame, text="尝试间隔(秒):").grid(row=0, column=0, sticky=tk.W)
        self.timeout_var = tk.StringVar(value="2")
        ttk.Entry(crack_frame, textvariable=self.timeout_var, width=10).grid(row=0, column=1, padx=5)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=2, pady=10)
        
        self.start_btn = ttk.Button(button_frame, text="开始测试", command=self.start_crack)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_btn = ttk.Button(button_frame, text="停止", command=self.stop_crack, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="操作日志", padding="5")
        log_frame.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 进度条
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 配置权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 绑定事件
        self.network_tree.bind('<<TreeviewSelect>>', self.on_network_select)
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def check_system(self):
        """检查系统兼容性"""
        if sys.platform.startswith('win'):
            self.sys_label.config(text="Windows系统 detected")
            self.interface_var.set("Wi-Fi")
            self.log_message("Windows系统 detected，使用netsh命令")
        elif sys.platform.startswith('linux'):
            self.sys_label.config(text="Linux系统 detected")
            self.log_message("Linux系统 detected，使用nmcli命令")
        elif sys.platform.startswith('darwin'):
            self.sys_label.config(text="macOS系统 detected")
            self.interface_var.set("en0")
            self.log_message("macOS系统 detected，使用airport命令")
        else:
            self.sys_label.config(text="不支持的操作系统")
            self.log_message("错误：不支持的操作系统")
    
    def check_interface(self):
        """检查网络接口"""
        interface = self.interface_var.get()
        self.log_message(f"检查接口: {interface}")
        
        try:
            if sys.platform.startswith('win'):
                result = subprocess.run(['netsh', 'wlan', 'show', 'interfaces'], 
                                      capture_output=True, text=True, encoding='gbk')
                if "无无线接口" in result.stdout or "No wireless interface" in result.stdout:
                    self.interface_status.config(text="未找到接口", foreground="red")
                    self.log_message("错误：未找到无线接口")
                else:
                    self.interface_status.config(text="接口正常", foreground="green")
                    self.log_message("无线接口检查正常")
            
            else:
                result = os.popen(f"ifconfig {interface} 2>&1").read()
                if "error" in result.lower() or "not found" in result.lower():
                    self.interface_status.config(text="未找到接口", foreground="red")
                    self.log_message(f"错误：未找到接口 {interface}")
                else:
                    self.interface_status.config(text="接口正常", foreground="green")
                    self.log_message(f"接口 {interface} 检查正常")
                    
        except Exception as e:
            self.interface_status.config(text="检查失败", foreground="red")
            self.log_message(f"检查接口时出错: {e}")
    
    def scan_wifi(self):
        """扫描WiFi网络"""
        if self.is_scanning:
            return
        
        self.is_scanning = True
        self.scan_status.config(text="扫描中...", foreground="blue")
        self.log_message("开始扫描WiFi网络...")
        
        # 清空现有网络列表
        for item in self.network_tree.get_children():
            self.network_tree.delete(item)
        
        # 在新线程中执行扫描
        threading.Thread(target=self._scan_wifi_thread, daemon=True).start()
    
    def _scan_wifi_thread(self):
        """扫描线程"""
        interface = self.interface_var.get()
        
        try:
            networks = []
            
            if sys.platform.startswith('win'):
                # Windows扫描
                result = subprocess.run(['netsh', 'wlan', 'show', 'networks', 'mode=bssid'],
                                      capture_output=True, text=True, encoding='gbk')
                
                lines = result.stdout.split('\n')
                current_ssid = None
                current_bssid = None
                current_signal = None
                
                for line in lines:
                    line = line.strip()
                    if 'SSID' in line and 'BSSID' not in line:
                        current_ssid = line.split(':', 1)[1].strip()
                    elif 'BSSID' in line:
                        current_bssid = line.split(':', 1)[1].strip()
                    elif '信号' in line or 'Signal' in line:
                        current_signal = line.split(':', 1)[1].strip()
                        if current_ssid and current_bssid:
                            networks.append((current_ssid, current_bssid, current_signal, 'WPA2'))
                            current_ssid = current_bssid = current_signal = None
            
            elif sys.platform.startswith('linux'):
                # Linux扫描
                result = os.popen(f"nmcli -t -f SSID,BSSID,SIGNAL,SECURITY dev wifi list ifname {interface}").read()
                for line in result.split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 4:
                            networks.append((parts[0], parts[1], f"{parts[2]}%", parts[3]))
            
            # 更新UI
            self.root.after(0, self._update_network_list, networks)
            
        except Exception as e:
            self.root.after(0, self.log_message, f"扫描失败: {e}")
        finally:
            self.root.after(0, self._scan_complete)
    
    def _update_network_list(self, networks):
        """更新网络列表"""
        for network in networks:
            self.network_tree.insert('', 'end', values=network)
        self.log_message(f"找到 {len(networks)} 个网络")
    
    def _scan_complete(self):
        """扫描完成"""
        self.is_scanning = False
        self.scan_status.config(text="扫描完成", foreground="green")
    
    def on_network_select(self, event):
        """网络选择事件"""
        selection = self.network_tree.selection()
        if selection:
            item = self.network_tree.item(selection[0])
            values = item['values']
            if values:
                self.ssid_var.set(values[0])
                if len(values) > 1:
                    self.bssid_var.set(values[1])
    
    def browse_dict(self):
        """浏览字典文件"""
        filename = filedialog.askopenfilename(
            title="选择密码字典文件",
            filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
        )
        if filename:
            self.dict_var.set(filename)
            self.log_message(f"选择字典文件: {filename}")
    
    def start_crack(self):
        """开始破解"""
        if self.is_cracking:
            return
        
        ssid = self.ssid_var.get().strip()
        bssid = self.bssid_var.get().strip()
        dict_file = self.dict_var.get().strip()
        
        if not ssid:
            messagebox.showerror("错误", "请输入SSID")
            return
        
        if not dict_file or not os.path.exists(dict_file):
            messagebox.showerror("错误", "请选择有效的字典文件")
            return
        
        try:
            timeout = float(self.timeout_var.get())
        except ValueError:
            timeout = 2
        
        self.is_cracking = True
        self.stop_requested = False
        self.start_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.progress.start()
        
        self.log_message(f"开始测试WiFi: {ssid}")
        self.log_message(f"使用字典: {dict_file}")
        
        # 在新线程中执行破解
        threading.Thread(target=self._crack_thread, 
                        args=(ssid, bssid, dict_file, timeout), 
                        daemon=True).start()
    
    def stop_crack(self):
        """停止破解"""
        self.stop_requested = True
        self.log_message("停止请求已发送...")
    
    def _crack_thread(self, ssid, bssid, dict_file, timeout):
        """破解线程"""
        attempts = 0
        start_time = datetime.now()
        
        try:
            with open(dict_file, 'r', encoding='utf-8', errors='ignore') as f:
                total_lines = sum(1 for _ in f)
                f.seek(0)
                
                for line_num, line in enumerate(f, 1):
                    if self.stop_requested:
                        break
                    
                    password = line.strip()
                    if not password:
                        continue
                    
                    attempts += 1
                    progress = (line_num / total_lines) * 100
                    
                    self.root.after(0, self._update_crack_status, attempts, password, progress)
                    
                    # 这里简化了实际的破解逻辑
                    # 实际使用时需要根据系统调用相应的命令
                    time.sleep(0.1)  # 模拟破解尝试
                    
                    # 模拟成功情况（实际使用时需要真实验证）
                    if password == "12345678":  # 示例成功密码
                        self.root.after(0, self._crack_success, ssid, password, attempts, start_time)
                        break
                    
                    time.sleep(timeout)
                
                else:
                    self.root.after(0, self._crack_failed, attempts, start_time)
                    
        except Exception as e:
            self.root.after(0, self.log_message, f"破解过程中出错: {e}")
        finally:
            self.root.after(0, self._crack_complete)
    
    def _update_crack_status(self, attempts, password, progress):
        """更新破解状态"""
        self.log_message(f"尝试 #{attempts}: {password}")
    
    def _crack_success(self, ssid, password, attempts, start_time):
        """破解成功"""
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        self.log_message("=" * 50)
        self.log_message("✓ 密码破解成功!")
        self.log_message(f"WiFi名称: {ssid}")
        self.log_message(f"密码: {password}")
        self.log_message(f"尝试次数: {attempts}")
        self.log_message(f"耗时: {duration:.2f} 秒")
        self.log_message("=" * 50)
        
        messagebox.showinfo("成功", f"密码破解成功!\n密码: {password}")
    
    def _crack_failed(self, attempts, start_time):
        """破解失败"""
        duration = (datetime.now() - start_time).total_seconds()
        
        self.log_message("=" * 50)
        self.log_message("✗ 密码破解失败")
        self.log_message(f"尝试次数: {attempts}")
        self.log_message(f"耗时: {duration:.2f} 秒")
        self.log_message("=" * 50)
        
        messagebox.showinfo("失败", "未在字典中找到正确密码")
    
    def _crack_complete(self):
        """破解完成"""
        self.is_cracking = False
        self.stop_requested = False
        self.start_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.progress.stop()

def main():
    """主函数"""
    root = tk.Tk()
    app = WiFiCrackerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()