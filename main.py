import os, csv, re, time, threading, uuid
from datetime import datetime
from collections import deque, Counter

import numpy as np
import serial, serial.tools.list_ports

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Line, Color, Rectangle, InstructionGroup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.utils import get_color_from_hex, platform

FONT_NAME = 'simhei.ttf'
EMOJI_FONT = 'seguiemj.ttf'
Window.clearcolor = get_color_from_hex('#F9F9F9')


def E(ch):
    return f"[font={EMOJI_FONT}]{ch}[/font]"


class CSVDataManager:
    def __init__(self):
        self.last_save_time = 0
        self.save_folder = self.get_save_folder()
        self.clean_7days_old_files()

    def get_save_folder(self):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE,
                    Permission.BLUETOOTH,
                    Permission.BLUETOOTH_ADMIN,
                    Permission.ACCESS_FINE_LOCATION
                ])
                from jnius import autoclass
                Environment = autoclass('android.os.Environment')
                base = Environment.getExternalStoragePublicDirectory(
                    Environment.DIRECTORY_DOWNLOADS
                ).getAbsolutePath()
                folder = os.path.join(base, '心电数据记录')
            except Exception:
                folder = os.path.join(os.getcwd(), '心电数据记录')
        else:
            folder = os.path.join(os.getcwd(), '心电数据记录')
        os.makedirs(folder, exist_ok=True)
        return folder

    def get_today_filename(self):
        return os.path.join(self.save_folder, f"ECG_Log_{datetime.now().strftime('%Y-%m-%d')}.csv")

    def save_data(self, bpm, hrv, rhythm):
        now = time.time()
        if now - self.last_save_time < 5.0 and rhythm == "Normal":
            return
        self.last_save_time = now
        path = self.get_today_filename()
        exists = os.path.isfile(path)
        try:
            with open(path, 'a', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                if not exists:
                    w.writerow(['记录时间', '心率(BPM)', 'HRV(ms)', '心律状态'])
                w.writerow([datetime.now().strftime('%H:%M:%S'), bpm, hrv, rhythm])
        except Exception as e:
            print("CSV 保存失败:", e)

    def clean_7days_old_files(self):
        try:
            now = datetime.now()
            for fn in os.listdir(self.save_folder):
                if fn.startswith("ECG_Log_") and fn.endswith(".csv"):
                    ds = fn.replace("ECG_Log_", "").replace(".csv", "")
                    try:
                        if (now - datetime.strptime(ds, '%Y-%m-%d')).days > 7:
                            os.remove(os.path.join(self.save_folder, fn))
                    except Exception:
                        pass
        except Exception:
            pass


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
        self.bg.pos, self.bg.size = self.pos, self.size
        self.border.rectangle = (self.x, self.y, self.width, self.height)
        self.text_size = (self.width - 30, self.height - 30)


class HardwareThread(threading.Thread):
    STATUS_MAP = {"Invalid": 0, "Wait": 1, "Normal": 2, "AFib": 3, "PVC": 4}
    LINE_PATTERN = re.compile(
        r'ADC:\s*(\d+)\s*\|\s*'
        r'ECG:\s*([+-]?\d+(?:\.\d+)?)\s*\|\s*'
        r'BPM:\s*(\d+)\s*\|\s*'
        r'RR:\s*(\d+)\s*\|\s*'
        r'HRV:\s*(\d+)\s*\|\s*'
        r'(Invalid|Wait|Normal|AFib|PVC)\s*$',
        re.IGNORECASE
    )

    def __init__(self, data_cb, status_cb):
        super().__init__()
        self.data_callback = data_cb
        self.status_callback = status_cb
        self.running = True
        self.ser = None
        self.sock = None
        self.in_stream = None
        self.rx_buffer = ""
        self.last_port = None
        self.last_link_name = None
        self.rhythm_window = deque(maxlen=5)
        self.last_stable_rhythm = "Wait"

    def emit_status(self, msg):
        Clock.schedule_once(lambda dt: self.status_callback(msg), 0)

    def emit_data(self, *args):
        Clock.schedule_once(lambda dt: self.data_callback(*args), 0)

    def normalize_rhythm(self, s):
        s = s.strip().lower()
        return {"invalid": "Invalid", "wait": "Wait", "normal": "Normal", "afib": "AFib", "pvc": "PVC"}.get(s, "Wait")

    def smooth_rhythm(self, rhythm):
        self.rhythm_window.append(rhythm)
        if "Invalid" in self.rhythm_window:
            self.last_stable_rhythm = "Invalid"
            return "Invalid"
        cnt = Counter(self.rhythm_window)
        stable = max(cnt, key=cnt.get)
        if cnt[stable] >= 2:
            self.last_stable_rhythm = stable
        return self.last_stable_rhythm

    def run(self):
        if platform == 'android':
            self.run_android_mode()
        else:
            self.run_pc_mode()

    # ---------- PC: USB串口 + 蓝牙串口(HC-05) ----------
    def scan_ports(self):
        try:
            return list(serial.tools.list_ports.comports())
        except Exception as e:
            self.emit_status(f"【错误】串口扫描失败: {e}")
            return []

    def find_candidate_ports(self):
        ports = self.scan_ports()
        if not ports:
            return []
        first_kw = ['HC-05', 'HC05', 'BLUETOOTH', 'STANDARD SERIAL OVER BLUETOOTH LINK']
        other_kw = ['USB', 'SERIAL', 'CH340', 'CH341', 'CP210', 'UART', 'STM', 'ARDUINO', 'STLINK', 'VIRTUAL']
        pri, sec, oth = [], [], []
        for p in ports:
            text = f"{p.device} {p.description} {p.manufacturer} {p.hwid}".upper()
            if any(k in text for k in first_kw):
                pri.append(p.device)
            elif any(k in text for k in other_kw):
                sec.append(p.device)
            else:
                oth.append(p.device)
        out = []
        for x in pri + sec + oth:
            if x not in out:
                out.append(x)
        return out

    def open_serial(self):
        candidates = self.find_candidate_ports()
        if not candidates:
            self.emit_status("【扫描中】未检测到 USB/蓝牙串口设备，等待重试...")
            return None
        self.emit_status("【扫描中】候选链路: " + ", ".join(candidates))
        for port in candidates:
            try:
                ser = serial.Serial(port=port, baudrate=115200, timeout=0.03)
                time.sleep(0.8)
                ser.reset_input_buffer()
                self.last_port = port
                self.last_link_name = port
                self.emit_status(f"【已连接】链路: {port}")
                return ser
            except Exception:
                continue
        self.emit_status("【扫描中】发现串口但无法打开，稍后重试...")
        return None

    def run_pc_mode(self):
        self.emit_status("【探测中】正在寻找 STM32 USB / HC-05 蓝牙串口...")
        while self.running:
            if self.ser is None:
                self.ser = self.open_serial()
                if self.ser is None:
                    time.sleep(1.0)
                    continue
            try:
                waiting = self.ser.in_waiting
                if waiting > 2048:
                    self.ser.reset_input_buffer()
                    self.rx_buffer = ""
                data = self.ser.read(waiting if waiting > 0 else 1)
                if not data:
                    time.sleep(0.005)
                    continue
                self.feed_text(data.decode('utf-8', errors='ignore'))
            except Exception as e:
                self.emit_status(f"【链路断开】{self.last_link_name or ''}，正在重连... {e}")
                self.close_link()
                time.sleep(1.0)

    # ---------- Android: HC-05 经典蓝牙 ----------
    def run_android_mode(self):
        self.emit_status("【探测中】正在连接 HC-05 蓝牙...")
        while self.running:
            if self.sock is None:
                if not self.open_android_hc05():
                    time.sleep(1.5)
                    continue
            try:
                avail = self.in_stream.available()
                if avail > 2048:
                    while self.in_stream.available() > 0:
                        self.in_stream.read()
                    self.rx_buffer = ""
                    continue
                if avail > 0:
                    buf = bytearray()
                    for _ in range(avail):
                        b = self.in_stream.read()
                        if b >= 0:
                            buf.append(b & 0xFF)
                    if buf:
                        self.feed_text(bytes(buf).decode('utf-8', errors='ignore'))
                else:
                    time.sleep(0.01)
            except Exception as e:
                self.emit_status(f"【蓝牙断开】HC-05，正在重连... {e}")
                self.close_link()
                time.sleep(1.5)

    def open_android_hc05(self):
        try:
            from android.permissions import request_permissions, Permission
            perms = [Permission.BLUETOOTH, Permission.BLUETOOTH_ADMIN, Permission.ACCESS_FINE_LOCATION]
            for p in ("BLUETOOTH_CONNECT", "BLUETOOTH_SCAN"):
                if hasattr(Permission, p):
                    perms.append(getattr(Permission, p))
            request_permissions(perms)

            from jnius import autoclass
            UUID = autoclass('java.util.UUID')
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            adapter = BluetoothAdapter.getDefaultAdapter()
            if adapter is None:
                self.emit_status("【错误】设备不支持蓝牙")
                return False
            if not adapter.isEnabled():
                self.emit_status("【提示】请先在手机系统里开启蓝牙，并完成 HC-05 配贴")
                return False

            bonded = adapter.getBondedDevices().toArray()
            dev = None
            for d in bonded:
                name = str(d.getName() or "").upper()
                addr = str(d.getAddress() or "")
                if "HC-05" in name or "HC05" in name:
                    dev = d
                    self.last_link_name = f"HC-05 ({addr})"
                    break

            if dev is None:
                self.emit_status("【提示】未找到已配对的 HC-05，请先在系统蓝牙中配对")
                return False

            spp = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
            try:
                adapter.cancelDiscovery()
            except Exception:
                pass

            sock = dev.createRfcommSocketToServiceRecord(spp)
            sock.connect()
            self.sock = sock
            self.in_stream = sock.getInputStream()
            self.last_link_name = f"HC-05 ({dev.getAddress()})"
            self.emit_status(f"【已连接】蓝牙: {self.last_link_name}")
            return True
        except Exception as e:
            self.emit_status(f"【蓝牙连接失败】{e}")
            self.close_link()
            return False

    # ---------- parse ----------
    def feed_text(self, text):
        if not text:
            return
        self.rx_buffer += text
        if len(self.rx_buffer) > 8192:
            self.rx_buffer = self.rx_buffer[-2048:]
        while '\n' in self.rx_buffer:
            line, self.rx_buffer = self.rx_buffer.split('\n', 1)
            line = line.replace('\r', '').strip()
            if line:
                self.parse_line(line)

    def parse_line(self, line):
        try:
            m = self.LINE_PATTERN.match(line)
            if not m:
                return
            adc_val, ecg_val, bpm_val, rr_val, hrv_val = int(m.group(1)), float(m.group(2)), int(m.group(3)), int(
                m.group(4)), int(m.group(5))
            raw_rhythm = self.normalize_rhythm(m.group(6))
            if not (0 <= adc_val <= 4095 and 0 <= bpm_val <= 240 and 0 <= rr_val <= 3000 and 0 <= hrv_val <= 3000):
                return
            ecg_val = max(-200.0, min(200.0, ecg_val))
            rhythm = self.smooth_rhythm(raw_rhythm)
            code = self.STATUS_MAP.get(rhythm, 1)
            self.emit_data(adc_val, ecg_val, bpm_val, rr_val, hrv_val, rhythm, code)

            if bpm_val > 0 and rhythm in ("Normal", "AFib", "PVC"):
                app = App.get_running_app()
                if app and hasattr(app, 'csv_manager'):
                    app.csv_manager.save_data(bpm_val, hrv_val, rhythm)
        except Exception as e:
            pass

    def close_link(self):
        try:
            if self.ser:
                self.ser.close()
        except Exception:
            pass
        try:
            if self.in_stream:
                self.in_stream.close()
        except Exception:
            pass
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
        self.ser = None
        self.sock = None
        self.in_stream = None
        self.rx_buffer = ""

    def stop(self):
        self.running = False
        self.close_link()


class ECGPlotWidget(FloatLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.data_len = 780
        self.ecg_buffer = np.zeros(self.data_len, dtype=float)
        self.ptr = 0
        self.display_mode = 'FLAT'

        # ===== 新加入：极速基线与滤波计算所需的变量 =====
        self.baseline = 0.0
        self.last_smoothed = 0.0

        # 保留原有的变量以防其他地方报错
        self.last_val = 0.0
        self.dc_out = 0.0
        self.lp1 = 0.0
        self.lp2 = 0.0
        self.med_buf = deque(maxlen=5)
        self.ma_buf = deque(maxlen=8)
        self.fixed_gain = 6
        self.display_gain = 6

        with self.canvas.before:
            Color(*get_color_from_hex('#FAFBFC'))
            self.bg = Rectangle()

            self.grid_lines = InstructionGroup()
            self.canvas.before.add(self.grid_lines)

        with self.canvas:
            Color(0.91, 0.30, 0.24, 0.12)
            self.glow_line = Line(points=[], width=4.0, cap='round', joint='round')

            Color(0.91, 0.30, 0.24, 0.22)
            self.mid_line = Line(points=[], width=2.4, cap='round', joint='round')

            Color(*get_color_from_hex('#e74c3c'))
            self.line = Line(points=[], width=1.65, cap='round', joint='round')

        self.y_labels = []
        for y_val in [60, 40, 20, 0, -20, -40, -60]:
            lbl = Label(
                text=str(y_val),
                color=get_color_from_hex('#A0A7B4'),
                font_size='11sp',
                size_hint=(None, None),
                size=(36, 20),
                font_name=FONT_NAME
            )
            self.add_widget(lbl)
            self.y_labels.append((lbl, y_val))

        self.x_labels = []
        for x_val in [0, 156, 312, 468, 624, 780]:
            lbl = Label(
                text=str(x_val),
                color=get_color_from_hex('#A0A7B4'),
                font_size='11sp',
                size_hint=(None, None),
                size=(42, 20),
                font_name=FONT_NAME
            )
            self.add_widget(lbl)
            self.x_labels.append((lbl, x_val))

        self.bind(pos=self.update_canvas, size=self.update_canvas)
        Clock.schedule_interval(self.render, 1.0 / 60.0)

    def update_canvas(self, *args):
        pad_left, pad_bottom, pad_right, pad_top = 42, 28, 12, 12
        plot_x = self.x + pad_left
        plot_y = self.y + pad_bottom
        plot_w = self.width - pad_left - pad_right
        plot_h = self.height - pad_bottom - pad_top

        self.bg.pos = (plot_x, plot_y)
        self.bg.size = (plot_w, plot_h)
        self.grid_lines.clear()

        self.grid_lines.add(Color(*get_color_from_hex('#FFFFFF')))
        self.grid_lines.add(Rectangle(pos=(plot_x, plot_y), size=(plot_w, plot_h)))

        for y_frac in np.linspace(0, 1, 13):
            y = plot_y + y_frac * plot_h
            self.grid_lines.add(Color(0.95, 0.96, 0.98, 1))
            self.grid_lines.add(Line(points=[plot_x, y, plot_x + plot_w, y], width=0.8))

        for x_frac in np.linspace(0, 1, 11):
            x = plot_x + x_frac * plot_w
            self.grid_lines.add(Color(0.96, 0.97, 0.985, 1))
            self.grid_lines.add(Line(points=[x, plot_y, x, plot_y + plot_h], width=0.8))

        for lbl, y_val in self.y_labels:
            y_pos = plot_y + ((y_val + 60) / 120.0) * plot_h
            lbl.pos = (self.x - 2, y_pos - lbl.height / 2)

            if y_val == 0:
                self.grid_lines.add(Color(*get_color_from_hex('#D7DEE8')))
                self.grid_lines.add(Line(points=[plot_x, y_pos, plot_x + plot_w, y_pos], width=1.4))
            else:
                self.grid_lines.add(Color(*get_color_from_hex('#ECEFF4')))
                self.grid_lines.add(Line(points=[plot_x, y_pos, plot_x + plot_w, y_pos], width=1.0))

        for lbl, x_val in self.x_labels:
            x_pos = plot_x + (x_val / float(self.data_len)) * plot_w
            lbl.pos = (x_pos - lbl.width / 2, self.y - 1)

            self.grid_lines.add(Color(*get_color_from_hex('#EEF2F6')))
            self.grid_lines.add(Line(points=[x_pos, plot_y, x_pos, plot_y + plot_h], width=1.0))

        self.grid_lines.add(Color(*get_color_from_hex('#DDE3EA')))
        self.grid_lines.add(Line(rectangle=(plot_x, plot_y, plot_w, plot_h), width=1.15))

        self.plot_rect = (plot_x, plot_y, plot_w, plot_h)

    # ==========================================
    # 核心重写：极速基线回正 + 智能抗噪低通算法
    # ==========================================
    def push_data(self, value):
        try:
            raw = float(value)

            # --- 1. 初始化级联滤波器 ---
            if not hasattr(self, 'init_flag') or not self.init_flag:
                self.dc_trend = raw
                self.lp1 = 0.0
                self.lp2 = 0.0
                self.lp3 = 0.0
                self.init_flag = True

            # --- 2. 剥离基线大波浪 (高通滤波器) ---
            # 权重 0.985，锁死 0 刻度线中心位，消除呼吸带来的上下漂移
            self.dc_trend = self.dc_trend * 0.985 + raw * 0.015
            ac_val = raw - self.dc_trend

            # --- 3. 三级医疗级平滑 (多次轻度打磨取代一次重度碾压) ---
            # 这三句代码是去毛刺的核心！
            # 它会将像刺猬一样的杂音“熔化”成一条圆润的线，同时保留高耸的 R 波大山
            self.lp1 = self.lp1 * 0.5 + ac_val * 0.5
            self.lp2 = self.lp2 * 0.5 + self.lp1 * 0.5
            self.lp3 = self.lp3 * 0.5 + self.lp2 * 0.5

            # --- 4. 补偿放大显示 ---
            # 因为经过了三道滤网，波形振幅会有所缩减，需要用 4.5 或 5.0 的倍率将其拉拔起来
            final_value = self.lp3 * 5.0

            # --- 5. 防越界保护 ---
            if final_value > 80: final_value = 80
            if final_value < -80: final_value = -80

            self.ecg_buffer[self.ptr] = final_value
            self.ptr = (self.ptr + 1) % self.data_len

        except Exception:
            pass

    def clear_wave(self):
        self.ecg_buffer[:] = 0
        self.ptr = 0
        self.init_flag = False  # 确保点重测时清理历史杂图

    def render(self, dt):
        if not hasattr(self, 'plot_rect'):
            return

        plot_x, plot_y, plot_w, plot_h = self.plot_rect
        if plot_w <= 0 or plot_h <= 0:
            return

        if self.display_mode == 'FLAT':
            y0 = plot_y + ((0 + 60.0) / 120.0) * plot_h
            pts = [plot_x, y0, plot_x + plot_w, y0]
            self.glow_line.points = pts
            self.mid_line.points = pts
            self.line.points = pts
            return

        pts = []
        x_step = plot_w / (self.data_len - 1)

        for i in range(self.data_len):
            idx = (self.ptr + i) % self.data_len
            val = max(-60.0, min(60.0, self.ecg_buffer[idx]))
            x = plot_x + i * x_step
            y = plot_y + ((val + 60.0) / 120.0) * plot_h
            pts.extend([x, y])

        self.glow_line.points = pts
        self.mid_line.points = pts
        self.line.points = pts


class ECGApp(App):
    def build(self):
        self.title = "心电预警系统"

        self.monitor_started = False
        self.current_adc = 0
        self.current_ecg = 0.0
        self.current_bpm = 0
        self.current_rr = 0
        self.current_hrv = 0
        self.current_rhythm = "Wait"
        self.current_status_code = 1

        self.last_good_bpm = 0
        self.last_good_hrv = 0
        self.final_bpm = 0
        self.final_hrv = 0

        self.diag_status = 'IDLE'
        self.prep_countdown = 0.0
        self.valid_data_ticks = 0.0
        self.rhythm_history = deque(maxlen=20)
        self.stable_rhythm_window = deque(maxlen=6)

        self.last_sms_time = 0
        self.last_frame_time = 0
        self.last_valid_signal_time = 0

        self.adc_history = deque(maxlen=80)
        self.ecg_history = deque(maxlen=80)
        self.py_lead_off = False
        self.py_lead_msg = ""

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

        mid_col = BoxLayout(orientation='vertical', size_hint_x=0.25)
        self.hrv_label = Label(text="HRV: -- ms", font_size='22sp', bold=True, color=get_color_from_hex('#555555'),
                               halign='center', valign='middle', font_name=FONT_NAME)
        self.hrv_label.bind(size=self.hrv_label.setter('text_size'))
        mid_col.add_widget(self.hrv_label)

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

        top_row.add_widget(left_col)
        top_row.add_widget(mid_col)
        top_row.add_widget(right_col)
        root.add_widget(top_row)

        self.graph = ECGPlotWidget(size_hint_y=0.6)
        root.add_widget(self.graph)

        self.advice_box = RichLogBox(size_hint_y=0.25)
        self.advice_box.text = f"{E('💡')} 系统核心引擎启动，连接协议寻址中...\n(注：请确保单片机电极片已可靠粘连皮肤)"
        root.add_widget(self.advice_box)

        self.csv_manager = CSVDataManager()
        self.hw_thread = HardwareThread(self.on_serial_data, self.update_conn_ui)
        self.hw_thread.start()

        Clock.schedule_interval(self.update_ui, 0.5)
        self.heart_anim_event = Clock.schedule_interval(self.animate_heart, 0.8)
        return root

    def update_conn_ui(self, msg):
        self.advice_box.text = msg

    def check_py_lead_off(self):
        if len(self.adc_history) < 20 or len(self.ecg_history) < 20:
            self.py_lead_off, self.py_lead_msg = False, ""
            return
        adc_arr, ecg_arr = np.array(self.adc_history, dtype=float), np.array(self.ecg_history, dtype=float)
        adc_mean, adc_std = np.mean(adc_arr), np.std(adc_arr)
        ecg_std, ecg_pp = np.std(ecg_arr), np.max(ecg_arr) - np.min(ecg_arr)

        checks = [
            ((adc_mean < 80) or (adc_mean > 4015), "ADC贴边，疑似电极脱落/输入饱和"),
            (adc_std < 2.0, "ADC几乎无变化，疑似未接入有效信号"),
            ((ecg_pp < 0.8 and ecg_std < 0.25 and self.current_bpm == 0), "ECG几乎无波动且无有效心率，疑似电极脱落"),
            ((ecg_pp > 80 and self.current_bpm == 0), "ECG异常乱跳，疑似电极接触不良"),
            ((self.current_rhythm == "Wait" and ecg_pp < 1.0 and adc_std < 5.0),
             "长时间无稳定心律且波形过平，疑似导联异常")
        ]
        for cond, msg in checks:
            if cond:
                self.py_lead_off, self.py_lead_msg = True, msg
                return
        self.py_lead_off, self.py_lead_msg = False, ""

    def on_serial_data(self, adc_val, ecg_val, bpm_val, rr_val, hrv_val, rhythm_str, status_code):
        self.last_frame_time = time.time()
        self.current_adc, self.current_ecg, self.current_bpm = adc_val, ecg_val, bpm_val
        self.current_rr, self.current_hrv, self.current_status_code = rr_val, hrv_val, status_code

        self.stable_rhythm_window.append(rhythm_str)
        self.current_rhythm = (max({r: self.stable_rhythm_window.count(r) for r in set(self.stable_rhythm_window)},
                                   key=lambda k: self.stable_rhythm_window.count(k))
                               if len(self.stable_rhythm_window) >= 3 else rhythm_str)

        self.adc_history.append(adc_val)
        self.ecg_history.append(ecg_val)
        self.check_py_lead_off()

        if status_code != 0 and not self.py_lead_off:
            self.last_valid_signal_time = time.time()

        if not self.monitor_started:
            return

        if status_code != 0 and not self.py_lead_off:
            self.graph.push_data(ecg_val)

        if 35 <= bpm_val <= 200:
            self.last_good_bpm = bpm_val
        if 1 <= hrv_val <= 2000:
            self.last_good_hrv = hrv_val

    def animate_heart(self, dt):
        if not self.monitor_started:
            self.heart_label.font_size = 40
            self.heart_label.color = get_color_from_hex('#e74c3c')
            return

        bpm = self.current_bpm if self.current_bpm > 30 else self.last_good_bpm
        self.heart_label.font_size = 46
        self.heart_label.color = get_color_from_hex('#c0392b')
        Clock.schedule_once(lambda d: self.reset_heart(), 0.15)

        try:
            self.heart_anim_event.cancel()
        except Exception:
            pass
        self.heart_anim_event = Clock.schedule_interval(self.animate_heart, max(0.3, 60.0 / bpm) if bpm > 30 else 0.8)

    def reset_heart(self):
        self.heart_label.font_size = 40
        self.heart_label.color = get_color_from_hex('#e74c3c')

    def start_manual_diagnosis(self, instance):
        if (time.time() - self.last_frame_time) > 1.5:
            self.status_label.text = "状态: 未检测到串口数据"
            self.status_label.color = get_color_from_hex('#e74c3c')
            self.advice_box.text = "【提示】请先确认 STM32 已持续发送 printf 文本数据。"
            return

        self.monitor_started = True
        if self.current_status_code == 0 or self.py_lead_off:
            self.status_label.text = "状态: 导联异常"
            self.status_label.color = get_color_from_hex('#e74c3c')
            self.advice_box.text = "【提示】当前硬件判断为导联脱落/信号异常，请先修复电极接触。" if self.current_status_code == 0 \
                else f"【提示】{self.py_lead_msg or 'Python端判断疑似电极脱落/接触不良，请检查电极。'}"
            return

        self.graph.clear_wave()
        self.last_good_bpm = self.last_good_hrv = 0
        self.diag_status, self.prep_countdown, self.valid_data_ticks = 'PREPARING', 6.0, 0.0
        self.rhythm_history.clear()

        self.btn_diag.text = "消解杂波中..."
        self.btn_diag.disabled = True
        self.status_label.text = f"基线平复倒数: {int(self.prep_countdown)} 秒..."
        self.status_label.color = get_color_from_hex('#2980b9')
        self.bpm_label.text = "--"
        self.hrv_label.text = "HRV: -- ms"
        self.graph.display_mode = 'WAVE'
        self.last_valid_signal_time = time.time()
        self.advice_box.text = "【贴片平复期】侦测探头已唤醒。受电极接触与坐姿影响，前几秒数值易漂移。\n" \
                               f"   {E('👉')} 请保持深呼吸并贴紧皮肤，静候 6 秒消除物理干扰。"

    def finish_diag_logic(self):
        if self.last_good_bpm <= 0:
            self.final_bpm = self.final_hrv = 0
            self.status_label.text = "诊断结果: 无有效心率数据"
            self.status_label.color = get_color_from_hex('#c0392b')
            self.advice_box.text = "【结论快照】本轮未形成有效心率结果，请检查电极接触后重试。"
        else:
            self.final_bpm, self.final_hrv = self.last_good_bpm, self.last_good_hrv
            normal_cnt = self.rhythm_history.count("Normal")
            afib_cnt = self.rhythm_history.count("AFib")
            pvc_cnt = self.rhythm_history.count("PVC")
            total_valid = normal_cnt + afib_cnt + pvc_cnt

            if total_valid < 4:
                self.status_label.text = "诊断结果: 数据不足"
                self.status_label.color = get_color_from_hex('#7f8c8d')
                self.advice_box.text = "【结论快照】有效样本不足，本轮无法给出稳定结论，请延长采集后重试。"
            elif afib_cnt >= 4 and afib_cnt > normal_cnt and afib_cnt >= pvc_cnt:
                self.status_label.text = "诊断结果: 疑似房颤 (AFib)"
                self.status_label.color = get_color_from_hex('#c0392b')
                self.advice_box.text = f"{E('❌')} 【结论快照】捕捉到明显不规则RR间期序列，疑似房颤。"
                self.show_alert_popup("⚠️ 高危心电异常预警",
                                      "系统检测到连续不规则 RR 间期（疑似房颤），\n请及时进一步检查。")
            elif pvc_cnt >= 4 and pvc_cnt > normal_cnt and pvc_cnt > afib_cnt:
                self.status_label.text = "诊断结果: 室性早搏 (PVC)"
                self.status_label.color = get_color_from_hex('#d35400')
                self.advice_box.text = f"{E('⚠️')} 【结论快照】检测到节律提前与代偿间歇，疑似室性早搏。"
                self.show_alert_popup("⚠️ 注意: 节律异常", "系统检测到疑似早搏信号，\n若频繁出现建议进一步观察。")
            else:
                self.status_label.text = "诊断结果: 正常心律"
                self.status_label.color = get_color_from_hex('#27ae60')
                self.advice_box.text = f"{E('✅')} 【结论快照】心电节律整体平稳，当前结果倾向正常心律。"

        self.diag_status = 'DONE'
        self.btn_diag.disabled = False
        self.btn_diag.text = "复位并开启全新捕获"

    def update_ui(self, dt):
        now = time.time()
        serial_online = (now - self.last_frame_time) <= 1.5
        signal_valid = (now - self.last_valid_signal_time) <= 1.5

        if self.diag_status == 'IDLE':
            self.bpm_label.text = "--"
            self.hrv_label.text = "HRV: -- ms"
            self.graph.display_mode = 'FLAT'
            if not serial_online:
                self.status_label.text, self.status_label.color = "状态: 串口未连接", get_color_from_hex('#555555')
            elif self.current_status_code == 0 or self.py_lead_off:
                self.status_label.text, self.status_label.color = "状态: 导联异常", get_color_from_hex('#e74c3c')
            else:
                self.status_label.text = "状态: 待机就绪" if self.current_rhythm == "Wait" else f"状态: 数据接收正常"
                self.status_label.color = get_color_from_hex('#555555')
            return

        if not serial_online:
            self.bpm_label.text = "--"
            self.hrv_label.text = "HRV: -- ms"
            self.graph.display_mode = 'FLAT'
            if self.diag_status in ['PREPARING', 'RUNNING']:
                self.advice_box.text = f"{E('⚠️')}【检测中断警告：链路静默】\n未侦测到实时硬件波形！请确认：\n" \
                                       "1. 连接线是否插稳，COM通讯端是否被其他程序占用。\n2. 传感器导联金属片是否完全贴紧肌肤导电。"
                self.diag_status = 'IDLE'
                self.btn_diag.disabled = False
                self.btn_diag.text = "复位并开启全新捕获"
                self.status_label.text = "状态: 失去硬件连接响应"
                self.status_label.color = get_color_from_hex('#e74c3c')
            return

        if self.current_status_code == 0 or self.py_lead_off:
            self.bpm_label.text = "--"
            self.hrv_label.text = "HRV: -- ms"
            self.graph.display_mode = 'FLAT'
            self.status_label.text = "状态: 导联脱落 / 信号异常"
            self.status_label.color = get_color_from_hex('#e74c3c')
            if self.diag_status in ['PREPARING', 'RUNNING']:
                self.diag_status = 'IDLE'
                self.btn_diag.disabled = False
                self.btn_diag.text = "复位并开启全新捕获"
            if self.py_lead_msg:
                self.advice_box.text = f"【提示】{self.py_lead_msg}"
            return

        self.graph.display_mode = 'WAVE' if signal_valid else 'FLAT'
        show_bpm = self.current_bpm if 35 <= self.current_bpm <= 200 else self.last_good_bpm
        show_hrv = self.current_hrv if 1 <= self.current_hrv <= 2000 else self.last_good_hrv
        self.bpm_label.text = str(show_bpm) if show_bpm > 0 else "--"
        self.hrv_label.text = f"HRV: {show_hrv} ms" if show_hrv > 0 else "HRV: -- ms"

        if self.diag_status == 'PREPARING':
            self.prep_countdown -= 0.5
            if self.prep_countdown > 0:
                self.status_label.text = f"基线平复倒数: {int(self.prep_countdown)} 秒"
            else:
                self.diag_status, self.valid_data_ticks = 'RUNNING', 0.0
                self.rhythm_history.clear()
                self.status_label.text = "状态: 纯净数据抽样中..."
                self.status_label.color = get_color_from_hex('#D35400')
                self.advice_box.text = "【硬件握手成功】波形稳定入轨，启动内源测录。\n" \
                                       f"   {E('👉')} 请持续保持平稳状态，等待进度条走完。"
            return

        if self.diag_status == 'DONE':
            self.bpm_label.text = str(self.final_bpm) if self.final_bpm > 0 else "--"
            self.hrv_label.text = f"HRV: {self.final_hrv} ms" if self.final_hrv > 0 else "HRV: -- ms"
            return

        if self.diag_status == 'RUNNING':
            if self.current_bpm > 180:
                self.advice_box.text = f"{E('⚠️')}【高杂波阻滞】捕捉到过激杂音源，数据进度挂起等待排空..."
                self.valid_data_ticks = max(0, self.valid_data_ticks - 1)
                return

            self.valid_data_ticks += 0.5
            if self.current_rhythm in ("Normal", "AFib", "PVC") and 35 <= self.current_bpm <= 200:
                if int(self.valid_data_ticks) > len(self.rhythm_history):
                    self.rhythm_history.append(self.current_rhythm)

            if self.valid_data_ticks <= 10:
                self.status_label.text = f"智能深部析出... {int((self.valid_data_ticks / 10.0) * 100)}%"
            else:
                self.finish_diag_logic()

    def show_alert_popup(self, title_text, msg_text):
        box = BoxLayout(orientation='vertical', padding=20, spacing=20)
        lbl = Label(text=msg_text, font_name=FONT_NAME, font_size='18sp',
                    color=(1, 1, 1, 1), halign='center', valign='middle')
        lbl.bind(size=lbl.setter('text_size'))
        btn = Button(text="确认并关闭", size_hint_y=0.4, font_name=FONT_NAME,
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
        except Exception:
            pass


if __name__ == '__main__':
    ECGApp().run()
