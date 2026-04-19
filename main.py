import sys
import numpy as np
import re
import time
import threading
import serial
import serial.tools.list_ports
from collections import deque

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Line, Color, Rectangle, InstructionGroup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.utils import platform
from kivy.uix.popup import Popup

#-----csv-----
import os
import csv
from datetime import datetime, timedelta

class CSVDataManager:
    def __init__(self):
        self.last_save_time = 0
        self.save_folder = self.get_android_public_folder()
        self.clean_7days_old_files()

    def get_android_public_folder(self):
        if platform == 'android':
            try:
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
                base_path = Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_DOWNLOADS
                ).getAbsolutePath()
                folder_path = os.path.join(base_path, '心电数据记录')
            except:
                folder_path = '/storage/emulated/0/Download/心电数据记录'
        else:
            folder_path = os.path.join(os.getcwd(), '心电数据记录')

        if not os.path.exists(folder_path):
            os.makedirs(folder_path, exist_ok=True)
        return folder_path

    def get_today_filename(self):
        today_str = datetime.now().strftime('%Y-%m-%d')
        filename = f"ECG_Log_{today_str}.csv"
        return os.path.join(self.save_folder, filename)

    def save_data(self, bpm, hrv, rhythm):
        current_time = time.time()
        if current_time - self.last_save_time < 5.0 and rhythm == "Normal":
            return
        self.last_save_time = current_time
        filepath = self.get_today_filename()
        file_exists = os.path.isfile(filepath)
        try:
            with open(filepath, mode='a', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(['记录时间', '心率 (BPM)', 'RR波动差/HRV (ms)', '心律状态'])
                time_str = datetime.now().strftime('%H:%M:%S')
                writer.writerow([time_str, bpm, hrv, rhythm])
        except Exception:
            pass

    def clean_7days_old_files(self):
        try:
            now = datetime.now()
            for filename in os.listdir(self.save_folder):
                if filename.startswith("ECG_Log_") and filename.endswith(".csv"):
                    date_str = filename.replace("ECG_Log_", "").replace(".csv", "")
                    try:
                        file_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if (now - file_date).days > 7:
                            os.remove(os.path.join(self.save_folder, filename))
                    except ValueError:
                        pass
        except Exception:
            pass

# === 全局样式 ===
FONT_NAME = 'simhei.ttf'
EMOJI_FONT = 'seguiemj.ttf'
Window.clearcolor = get_color_from_hex('#F9F9F9')

def E(emoji_char):
    return f"[font={EMOJI_FONT}]{emoji_char}[/font]"

class RichLogBox(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.markup = True
        self.halign = 'left'
        self.valign = 'top'
        self.font_name = FONT_NAME
        self.font_size = '16sp'
        self.color = get_color_from_hex('#333333')

        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)
            Color(0.8, 0.8, 0.8, 1)
            self.border = Line(rectangle=(self.x, self.y, self.width, self.height), width=1)
        self.bind(pos=self.update_bg, size=self.update_bg)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size
        self.border.rectangle = (self.x, self.y, self.width, self.height)
        self.text_size = (self.width - 30, self.height - 30)

# ==========================================
# 1. 硬件线程 (已加入无限断线重连不死机制)
# ==========================================
class HardwareThread(threading.Thread):
    def __init__(self, data_callback, status_callback):
        super().__init__()
        self.data_callback = data_callback
        self.status_callback = status_callback
        self.running = True
        self.daemon = True

    def run(self):
        try:
            if platform == 'android':
                self.run_bluetooth_mode()
            else:
                self.run_serial_mode()
        except Exception as e:
            self.status_callback(f"【链路大崩溃】: {str(e)}")

    def run_bluetooth_mode(self):
        import time
        from jnius import autoclass
        
        # 【断点重试大循环】就算断线了也不会死，等5秒就重试
        while self.running:
            self.status_callback("【探测中】正在寻找并连接已配对的 HC-05...\n(如果有系统弹窗，请务必点击允许权限！)")
            socket = None
            try:
                BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
                UUID = autoclass('java.util.UUID')
                InputStreamReader = autoclass('java.io.InputStreamReader')
                BufferedReader = autoclass('java.io.BufferedReader')

                adapter = BluetoothAdapter.getDefaultAdapter()

                if adapter is None or not adapter.isEnabled():
                    self.status_callback("【错误】检测到手机未打开蓝牙\n请打开蓝牙后，系统将在5秒后自动重连...")
                    time.sleep(5)
                    continue

                try:
                    if adapter.isDiscovering():
                        adapter.cancelDiscovery()
                except:
                    pass

                paired_devices = adapter.getBondedDevices().toArray()
                if not paired_devices:
                    self.status_callback("【错误】空空如也！未发现任何已配对设备\n请切出APP，去设置里配对 HC-05。5秒后重试...")
                    time.sleep(5)
                    continue

                target_device = None
                for device in paired_devices:
                    name = str(device.getName()).upper()
                    if "HC-05" in name or "HC05" in name or "HC" in name or "LINVOR" in name or "BT" in name:
                        target_device = device
                        break

                if not target_device:
                    self.status_callback("【错误】已有配对设备中没找到HC-05，请去系统蓝牙里确认。5秒后重试...")
                    time.sleep(5)
                    continue

                spp_uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
                try:
                    socket = target_device.createRfcommSocketToServiceRecord(spp_uuid)
                    socket.connect()
                except Exception:
                    if socket: socket.close()
                    socket = target_device.createInsecureRfcommSocketToServiceRecord(spp_uuid)
                    socket.connect()

                self.status_callback(f"【成功】蓝牙链路已打通 ({target_device.getName()})，开始接收波形！")
                reader = BufferedReader(InputStreamReader(socket.getInputStream()))

                # 只要连接建立，就一直在内部循环读取
                while self.running:
                    line = reader.readLine()
                    if line:
                        line = str(line).strip()
                        if line: self.parse_and_emit(line)

            except Exception as e:
                self.status_callback(f"【安卓蓝牙请求被系统拒绝】: {str(e)}\n\n(可能需要你去系统设置给这APP开「附近设备」和「定位」权限，5秒后再次尝试连接...)")
            finally:
                try:
                    if socket: socket.close()
                except: pass
            
            # 每次循环失败，休息5秒再重新冲击
            if self.running:
                time.sleep(5)

    def run_serial_mode(self):
        self.status_callback("【探测中】正在寻找 USB 链路...")
        ports = list(serial.tools.list_ports.comports())
        if not ports:
            self.status_callback("【错误】未检测到串口设备，请检查 CH340 驱动！")
            return

        port_name = ports[0].device
        try:
            ser = serial.Serial(port_name, 115200, timeout=0.05)
            ser.reset_input_buffer()

            while self.running:
                if ser.in_waiting > 500:
                    ser.reset_input_buffer()
                line_bytes = ser.readline()
                if line_bytes:
                    try:
                        line = line_bytes.decode('utf-8', errors='ignore').strip()
                        if line: self.parse_and_emit(line)
                    except: continue
        except Exception as e:
            self.status_callback(f"【链路中断】: {str(e)}")

    def parse_and_emit(self, line):
        try:
            m_ecg = re.search(r'ECG:([-+]?\d*\.?\d+)', line)
            m_bpm = re.search(r'BPM:(\d+)', line)
            m_hrv = re.search(r'HRV:(\d+)', line)

            ecg_val = float(m_ecg.group(1)) if m_ecg else 0.0
            bpm_val = int(m_bpm.group(1)) if m_bpm else 0
            hrv_val = int(m_hrv.group(1)) if m_hrv else 0

            rhythm_str = "Wait"
            if "Normal" in line: rhythm_str = "Normal"
            elif "AFib" in line: rhythm_str = "AFib"
            elif "PVC" in line: rhythm_str = "PVC"

            self.data_callback(ecg_val, bpm_val, hrv_val, rhythm_str)

            if bpm_val > 0 and rhythm_str != "Wait":
                app = App.get_running_app()
                if hasattr(app, 'csv_manager'):
                    app.csv_manager.save_data(bpm_val, hrv_val, rhythm_str)
        except Exception:
            pass

    def stop(self):
        self.running = False

from kivy.uix.floatlayout import FloatLayout
class ECGPlotWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_len = 1000
        self.ecg_buffer = np.zeros(self.data_len)
        self.ptr = 0
        self.display_mode = 'FLAT'
        self.baseline = 0.0
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = Rectangle()
            self.grid_lines = InstructionGroup()
            self.canvas.before.add(self.grid_lines)
        with self.canvas:
            Color(*get_color_from_hex('#e74c3c'))
            self.line = Line(points=[], width=1.2)
        self.bind(pos=self.update_canvas, size=self.update_canvas)

        self.y_labels = []
        for y_val in [60, 40, 20, 0, -20, -40, -60]:
            lbl = Label(text=str(y_val), color=get_color_from_hex('#999999'),
                        font_size='12sp', size_hint=(None, None), size=(35, 20))
            self.add_widget(lbl)
            self.y_labels.append((lbl, y_val))

        self.x_labels = []
        for x_val in [0, 200, 400, 600, 800, 1000]:
            lbl = Label(text=str(x_val), color=get_color_from_hex('#999999'),
                        font_size='12sp', size_hint=(None, None), size=(40, 20))
            self.add_widget(lbl)
            self.x_labels.append((lbl, x_val))
        Clock.schedule_interval(self.render, 1.0 / 60.0)

    def update_canvas(self, *args):
        pad_left, pad_bottom, pad_right, pad_top = 40, 25, 10, 10
        plot_x = self.x + pad_left
        plot_y = self.y + pad_bottom
        plot_w = self.width - pad_left - pad_right
        plot_h = self.height - pad_bottom - pad_top
        self.bg.pos = (plot_x, plot_y)
        self.bg.size = (plot_w, plot_h)
        self.grid_lines.clear()

        y_range = 120.0
        for lbl, y_val in self.y_labels:
            norm_y = (y_val + 60) / y_range
            y_pos = plot_y + norm_y * plot_h
            lbl.pos = (self.x, y_pos - lbl.height / 2)
            if y_val == 0:
                self.grid_lines.add(Color(0.85, 0.85, 0.85, 1))
                self.grid_lines.add(Line(points=[plot_x, y_pos, plot_x + plot_w, y_pos], width=1.2))
            else:
                self.grid_lines.add(Color(0.94, 0.94, 0.94, 1))
                self.grid_lines.add(Line(points=[plot_x, y_pos, plot_x + plot_w, y_pos], width=1))

        x_range = 1000.0
        for lbl, x_val in self.x_labels:
            norm_x = x_val / x_range
            x_pos = plot_x + norm_x * plot_w
            lbl.pos = (x_pos - lbl.width / 2, self.y)
            self.grid_lines.add(Color(0.94, 0.94, 0.94, 1))
            self.grid_lines.add(Line(points=[x_pos, plot_y, x_pos, plot_y + plot_h], width=1))
        self.grid_lines.add(Color(0.8, 0.8, 0.8, 1))
        self.grid_lines.add(Line(rectangle=(plot_x, plot_y, plot_w, plot_h), width=1))
        self.plot_rect = (plot_x, plot_y, plot_w, plot_h)

    def push_data(self, value):
        self.baseline = self.baseline * 0.75 + value * 0.25
        clean_value = value - self.baseline
        if not hasattr(self, 'last_smoothed'): self.last_smoothed = 0
        self.last_smoothed = self.last_smoothed * 0.85 + clean_value * 0.15
        final_value = self.last_smoothed * 1.8
        if final_value > 80: final_value = 80
        if final_value < -80: final_value = -80
        self.ecg_buffer[self.ptr] = final_value
        self.ptr = (self.ptr + 1) % self.data_len

    def render(self, dt):
        if not hasattr(self, 'plot_rect'): return
        plot_x, plot_y, plot_w, plot_h = self.plot_rect
        if plot_w <= 0 or plot_h <= 0: return
        points = []
        x_step = plot_w / (self.data_len - 1)
        y_min, y_max = -60.0, 60.0
        y_range = y_max - y_min

        if self.display_mode == 'FLAT':
            norm_y = (0 - y_min) / y_range
            y = plot_y + norm_y * plot_h
            points = [plot_x, y, plot_x + plot_w, y]
        else:
            for i in range(self.data_len):
                idx = (self.ptr + i) % self.data_len
                val = max(y_min, min(y_max, self.ecg_buffer[idx]))
                norm_y = (val - y_min) / y_range
                points.extend([plot_x + i * x_step, plot_y + norm_y * plot_h])
        self.line.points = points

# ==========================================
# 3. 主应用 App
# ==========================================
class ECGApp(App):
    def build(self):
        # ★【关键修复】在这里动态提权，不管结果，把界面先搭起来
        if platform == 'android':
            try:
                from android.permissions import request_permissions
                request_permissions([
                    'android.permission.BLUETOOTH',
                    'android.permission.BLUETOOTH_ADMIN',
                    'android.permission.BLUETOOTH_CONNECT',
                    'android.permission.BLUETOOTH_SCAN',
                    'android.permission.ACCESS_FINE_LOCATION',
                    'android.permission.ACCESS_COARSE_LOCATION',
                    'android.permission.READ_EXTERNAL_STORAGE',
                    'android.permission.WRITE_EXTERNAL_STORAGE'
                ])
            except Exception as e:
                print("权限申请失败:", e)

        self.title = "AI辅助心电预警系统 "
        self.current_bpm = 0
        self.current_hrv = 0
        self.current_rhythm = "Normal"
        self.diag_status = 'IDLE'
        self.prep_countdown = 0
        self.valid_data_ticks = 0
        self.rhythm_history = deque(maxlen=10)
        self.last_sms_time = 0
        self.last_valid_data_time = 0

        root = BoxLayout(orientation='vertical', padding=15, spacing=12)

        top_row = BoxLayout(size_hint_y=0.15, spacing=15)
        left_col = BoxLayout(orientation='horizontal', size_hint_x=0.25)
        self.heart_label = Label(text="❤️", font_size='40sp', halign='center', valign='middle', font_name=EMOJI_FONT)
        self.heart_label.bind(size=self.heart_label.setter('text_size'))

        self.bpm_label = Label(text="--", font_size='36sp', bold=True, color=get_color_from_hex('#333333'),
                               halign='center', valign='middle', font_name=FONT_NAME)
        self.bpm_label.bind(size=self.bpm_label.setter('text_size'))
        left_col.add_widget(self.heart_label)
        left_col.add_widget(self.bpm_label)
        top_row.add_widget(left_col)

        mid_col = BoxLayout(orientation='vertical', size_hint_x=0.25)
        self.hrv_label = Label(text="HRV: -- ms", font_size='22sp', bold=True, color=get_color_from_hex('#555555'),
                               halign='center', valign='middle', font_name=FONT_NAME)
        self.hrv_label.bind(size=self.hrv_label.setter('text_size'))
        mid_col.add_widget(self.hrv_label)
        top_row.add_widget(mid_col)

        right_col = BoxLayout(orientation='vertical', size_hint_x=0.5)
        self.status_label = Label(text="状态: 待机就绪", font_size='20sp', bold=True,
                                  color=get_color_from_hex('#555555'), halign='right', valign='middle',
                                  font_name=FONT_NAME)
        self.status_label.bind(size=self.status_label.setter('text_size'))

        self.btn_diag = Button(text="开始进行诊断", size_hint_y=0.6, font_size='18sp', bold=True,
                               background_color=get_color_from_hex('#0078D7'), color=(1, 1, 1, 1), font_name=FONT_NAME)
        self.btn_diag.bind(on_press=self.start_manual_diagnosis)

        right_col.add_widget(self.status_label)
        right_col.add_widget(self.btn_diag)
        top_row.add_widget(right_col)
        root.add_widget(top_row)

        self.graph = ECGPlotWidget(size_hint_y=0.6)
        root.add_widget(self.graph)

        self.advice_box = RichLogBox(size_hint_y=0.25)
        self.advice_box.text = f"{E('💡')} 系统核心引擎就绪，正在准备连接..."
        root.add_widget(self.advice_box)

        Clock.schedule_interval(self.update_ui, 0.5)
        self.heart_anim_event = Clock.schedule_interval(self.animate_heart, 0.8)

        self.csv_manager = CSVDataManager()

        # ★【重大杀手锏修复】延迟 3.5 秒启动蓝牙探查，给足你点击弹窗“允许权限”的时间！
        self.hw_thread = HardwareThread(self.on_serial_data, self.update_conn_ui)
        Clock.schedule_once(lambda dt: self.hw_thread.start(), 3.5)

        return root

    def update_conn_ui(self, msg):
        Clock.schedule_once(lambda dt: setattr(self.advice_box, 'text', msg), 0)

    def on_serial_data(self, ecg_val, bpm_val, hrv_val, rhythm_str):
        self.last_valid_data_time = time.time()
        self.graph.push_data(ecg_val)
        if bpm_val > 0:
            self.current_bpm = bpm_val
            self.current_hrv = hrv_val
            if rhythm_str != "Wait":
                self.current_rhythm = rhythm_str

        if self.diag_status != 'IDLE':
            self.graph.display_mode = 'WAVE'

    def animate_heart(self, dt):
        self.heart_label.font_size = 46
        self.heart_label.color = get_color_from_hex('#c0392b')
        Clock.schedule_once(lambda dt: self.reset_heart(), 0.15)

        if self.current_bpm > 30 and self.diag_status != 'IDLE':
            interval = max(300, min(60000 // self.current_bpm, 2000))
            self.heart_anim_event.cancel()
            self.heart_anim_event = Clock.schedule_interval(self.animate_heart, interval / 1000.0)
        else:
            self.heart_anim_event.cancel()
            self.heart_anim_event = Clock.schedule_interval(self.animate_heart, 0.8)

    def reset_heart(self):
        self.heart_label.font_size = 40
        self.heart_label.color = get_color_from_hex('#e74c3c')

    # 注意：在底部文本框没提示【接收波形中...】之前，不要手快点这个按钮！不然会抢占底部信息的展示
    def start_manual_diagnosis(self, instance):
        self.diag_status = 'PREPARING'
        self.prep_countdown = 6
        self.btn_diag.text = "消解杂波中..."
        self.btn_diag.disabled = True
        self.status_label.text = f"基线平复倒数: {self.prep_countdown} 秒..."
        self.status_label.color = get_color_from_hex('#2980b9')
        self.bpm_label.text = "--"
        self.hrv_label.text = "HRV: -- ms"

        self.graph.display_mode = 'WAVE'
        self.last_valid_data_time = time.time()

        self.advice_box.text = (
            "【贴片平复期】侦测探头已唤醒。受电极接触与坐姿影响，前几秒数值易漂移。\n"
            f"   {E('👉')} 请保持深呼吸并贴紧皮肤，静候 6 秒消除物理干扰。"
        )

    def update_ui(self, dt):
        now_time = time.time()
        is_disconnected = (now_time - self.last_valid_data_time) > 2.0

        if self.diag_status == 'IDLE':
            self.bpm_label.text = "--"
            self.hrv_label.text = "HRV: -- ms"
            self.graph.display_mode = 'FLAT'
            return

        if is_disconnected:
            self.bpm_label.text = "--"
            self.hrv_label.text = "HRV: -- ms"
            self.graph.display_mode = 'FLAT'

            if self.diag_status in ['PREPARING', 'RUNNING']:
                self.advice_box.text = (
                    f"{E('⚠️')}【检测中断警告：链路静默】\n"
                    "未收到硬件波形，你的下述问题可能发生：\n"
                    "1. 蓝牙未能顺利连接（请耐心等待5秒一轮的自动重连）。\n"
                    "2. 传感器导联金属片松动了。"
                )
                self.diag_status = 'IDLE'
                self.btn_diag.disabled = False
                self.btn_diag.text = "复位并重新开始"
                self.status_label.text = "状态: 失去硬件连接"
                self.status_label.color = get_color_from_hex('#e74c3c')
            return
        else:
            if self.current_bpm > 0:
                self.bpm_label.text = str(self.current_bpm)
                self.hrv_label.text = f"HRV: {self.current_hrv} ms"

        if self.diag_status == 'PREPARING':
            self.prep_countdown -= 0.5
            if self.prep_countdown > 0:
                self.status_label.text = f"基线平复倒数: {int(self.prep_countdown)} 秒"
            else:
                self.diag_status = 'RUNNING'
                self.valid_data_ticks = 0
                self.rhythm_history.clear()
                self.status_label.text = "状态: 纯净数据抽样中..."
                self.status_label.color = get_color_from_hex('#D35400')
                self.advice_box.text = (
                    "【硬件握手成功】波形稳定入轨，启动内源测录。\n"
                    f"   {E('👉')} 请持续保持平稳状态，等待进度条走完。"
                )
            return

        if self.diag_status == 'DONE':
            return

        if self.current_bpm > 180:
            self.advice_box.text = f"{E('⚠️')}【高杂波阻滞】捕捉到过激杂音源，数据挂起..."
            self.valid_data_ticks = max(0, self.valid_data_ticks - 1)
            return

        self.valid_data_ticks += 0.5
        if int(self.valid_data_ticks) > len(self.rhythm_history):
            self.rhythm_history.append(self.current_rhythm)

        if self.valid_data_ticks <= 10:
            prog = int((self.valid_data_ticks / 10.0) * 100)
            self.status_label.text = f"智能深部析出... {prog}%"
            return

        afib = self.rhythm_history.count("AFib")
        pvc = self.rhythm_history.count("PVC")

        if afib >= 3:
            self.status_label.text = "诊断结果: 疑似房颤 (AFib)"
            self.status_label.color = get_color_from_hex('#c0392b')
            self.advice_box.text = f"{E('❌')} 【结论快照】强烈疑似心房颤动！请就医！"
            self.show_alert_popup("⚠️ 高危心电异常预警", "连续不规则 RR 间期，疑似房颤！")
        elif pvc >= 3:
            self.status_label.text = "诊断结果: 室性早搏 (PVC)"
            self.status_label.color = get_color_from_hex('#d35400')
            self.advice_box.text = f"{E('⚠️')} 【结论快照】捕捉到室性期前收缩(PVC)早搏。"
            self.show_alert_popup("⚠️ 注意: 节律异常", "捕捉到早搏信号，请注意休息。")
        else:
            self.status_label.text = "诊断结果: 正常心律"
            self.status_label.color = get_color_from_hex('#27ae60')
            self.advice_box.text = f"{E('✅')} 【结论快照】心房心室起搏平稳健康，周期排查完毕。"

        self.diag_status = 'DONE'
        self.btn_diag.disabled = False
        self.btn_diag.text = "复位开启全新捕获"

    def trigger_sms_alert(self, msg):
        now = time.time()
        if now - self.last_sms_time > 30:
            self.advice_box.text += f"\n\n{E('🔔')} 【系统分发】异常心动信号已通报管理端。"
            self.last_sms_time = now

    def show_alert_popup(self, title_text, msg_text):
        box = BoxLayout(orientation='vertical', padding=20, spacing=20)
        lbl = Label(text=msg_text, font_name=FONT_NAME, font_size='18sp',
                    color=(1, 1, 1, 1), halign='center', valign='middle')
        lbl.bind(size=lbl.setter('text_size'))
        btn = Button(text="确认关闭", size_hint_y=0.4, font_name=FONT_NAME,
                     font_size='18sp', bold=True, background_color=get_color_from_hex('#e74c3c'))
        box.add_widget(lbl)
        box.add_widget(btn)
        popup = Popup(title=title_text, content=box, size_hint=(0.7, 0.4),
                      title_font=FONT_NAME, title_color=(1, 0.2, 0.2, 1), auto_dismiss=False)
        btn.bind(on_press=popup.dismiss)
        popup.open()

    def on_stop(self):
        try:
            self.hw_thread.stop()
        except:
            pass

if __name__ == '__main__':
    ECGApp().run()
