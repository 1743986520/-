import psutil
import pyaudio
import serial
import time

ser = serial.Serial('COM3', 115200, timeout=1)  # 改成你的 COM 埠
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

while True:
    cpu_usage = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    ram_usage = ram.percent
    net_io = psutil.net_io_counters()
    bytes_sent = net_io.bytes_sent
    bytes_recv = net_io.bytes_recv
    time.sleep(1)
    net_io_new = psutil.net_io_counters()
    net_speed = (net_io_new.bytes_recv + net_io_new.bytes_sent - bytes_recv - bytes_sent) / 1024
    data = stream.read(CHUNK)
    max_amplitude = max(abs(int.from_bytes(data[i:i+2], 'little', signed=True)) for i in range(0, len(data), 2)) / 32768 * 100
    data_str = f"{cpu_usage:.1f},{ram_usage:.1f},{net_speed:.1f},{max_amplitude:.1f}\n"
    ser.write(data_str.encode())
    time.sleep(0.5)