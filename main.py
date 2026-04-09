import sys
import numpy as np
import re
import time
import threading
from collections import deque

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Line, Color, Rectangle, InstructionGroup
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.utils import platform
from kivy.uix.popup import Popup

import os
import csv
from datetime import datetime


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
                    Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
                folder_path = os.path.join(base_path, '心电数据记录')
            except Exception:
                # 极端情况备用路径
                folder_path = '/storage/emulated/0/Download/心电数据记录'
        else:
            folder_path = os.path.join(os.getcwd(), '心电数据记录')

        if not os.path.exists(folder_path):
            try:
                os.makedirs(folder_path, exist_ok=True)
            except:
                pass
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
    return emoji_char


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
# 1. 真·支持安卓蓝牙直连的硬件线程 (延迟启动防闪退)
# ==========================================
class HardwareThread(threading.Thread):
    def __init__(self, data_callback, status_callback):
        super().__init__()
        self.data_callback = data_callback
        self.status_callback = status_callback
        self.running = True
        self.daemon = True

    def run(self):
        if platform == 'android':
            self.run_bluetooth_mode()
        else:
            self.run_serial_mode()

    def run_bluetooth_mode(self):
        self.status_callback("【蓝牙初始化】获取底层蓝牙适配器中...")
        time.sleep(1)  # 给系统一点反应时间
        try:
            from jnius import autoclass
            BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
            UUID = autoclass('java.util.UUID')
            adapter = BluetoothAdapter.getDefaultAdapter()

            if not adapter or not adapter.isEnabled():
                self.status_callback("❌ 【严重错误】蓝牙未开启！\n请下拉菜单打开蓝牙，并在系统里将 HC-05 成功配对！")
                return

            paired_devices = adapter.getBondedDevices().toArray()

            # 标准SPP串口通讯的 UUID
            SPP_UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

            target_device = None
            device_names = []
            for device in paired_devices:
                name = device.getName()
                if name:
                    device_names.append(name)
                    # HC-05、JDY-31、BT 等常见蓝牙模块名字都可以匹配
                    if ("HC" in name.upper() or "BT" in name.upper() or "JDY" in name.upper() or "LE" in name.upper()):
                        target_device = device
                        break

            if not target_device:
                self.status_callback(
                    f"❌ 蓝牙列表中没有发现可用的设备！\n系统已配对列表: {device_names}\n(请去设置里重新配对一次模块，如果是LE结尾也可尝试)")
                return

            self.status_callback(f"【尝试连接】锁定目标: {target_device.getName()}，正在建立底层射频通道...")

            # 使用 Insecure 方式增强连通率
            socket = target_device.createInsecureRfcommSocketToServiceRecord(SPP_UUID)
            socket.connect()

            InputStreamReader = autoclass('java.io.InputStreamReader')
            BufferedReader = autoclass('java.io.BufferedReader')
            java_reader = BufferedReader(InputStreamReader(socket.getInputStream()))

            self.status_callback("✅ 【通道打通】连接成功！\n等待并捕捉心电数据推流...")

            while self.running:
                line = java_reader.readLine()
                if line:
                    self.parse_and_emit(str(line).strip())

        except Exception as e:
            err_str = str(e)
            self.status_callback(
                f"【连接彻底失败】请看下方报错找原因:\n{err_str}\n\n(提示: read failed说明该芯片其实是纯BLE，不支持安卓经典蓝牙透传协议！)")

    def run_serial_mode(self):
        self.status_callback("⚠️ 电脑端屏蔽了此功能。请将生成的 APK 发送到华为平板安装运行！")
        while self.running:
            time.sleep(1)

    def parse_and_emit(self, line):
        try:
            m_ecg = re.search(r'ECG:([-+]?\d*\.?\d+)', line)
            m_bpm = re.search(r'BPM:(\d+)', line)
            m_hrv = re.search(r'HRV:(\d+)', line)

            ecg_val = float(m_ecg.group(1)) if m_ecg else 0.0
            bpm_val = int(m_bpm.group(1)) if m_bpm else 0
            hrv_val = int(m_hrv.group(1)) if m_hrv else 0

            rhythm_str = "Wait"
            if "Normal" in line:
                rhythm_str = "Normal"
            elif "AFib" in line:
                rhythm_str = "AFib"
            elif "PVC" in line:
                rhythm_str = "PVC"

            self.data_callback(ecg_val, bpm_val, hrv_val, rhythm_str)

            if bpm_val > 0 and rhythm_str != "Wait":
                app = App.get_running_app()
                if hasattr(app, 'csv_manager'):
                    app.csv_manager.save_data(bpm_val, hrv_val, rhythm_str)
        except Exception:
            pass

    def stop(self):
        self.running = False


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

        for lbl, y_val in self.y_labels:
            norm_y = (y_val + 60) / 120.0
            y_pos = plot_y + norm_y * plot_h
            lbl.pos = (self.x, y_pos - lbl.height / 2)
            if y_val == 0:
                self.grid_lines.add(Color(0.85, 0.85, 0.85, 1))
                self.grid_lines.add(Line(points=[plot_x, y_pos, plot_x + plot_w, y_pos], width=1.2))
            else:
                self.grid_lines.add(Color(0.94, 0.94, 0.94, 1))
                self.grid_lines.add(Line(points=[plot_x, y_pos, plot_x + plot_w, y_pos], width=1))

        for lbl, x_val in self.x_labels:
            x_pos = plot_x + (x_val / 1000.0) * plot_w
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

        if self.display_mode == 'FLAT':
            y = plot_y + ((0 - (-60.0)) / 120.0) * plot_h
            points = [plot_x, y, plot_x + plot_w, y]
        else:
            for i in range(self.data_len):
                idx = (self.ptr + i) % self.data_len
                val = max(-60.0, min(60.0, self.ecg_buffer[idx]))
                y = plot_y + ((val - (-60.0)) / 120.0) * plot_h
                x = plot_x + i * x_step
                points.extend([x, y])

        self.line.points = points


class ECGApp(App):
    def build(self):
        # 抛弃 Permission 枚举！直接用字符串原生请求，绝对不闪退
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
                print("Permission request fail:", e)

        self.title = "AI辅助心电预警系统"

        self.current_bpm = 0
        self.current_hrv = 0
        self.current_rhythm = "Normal"
        self.diag_status = 'IDLE'
        self.prep_countdown = 0
        self.valid_data_ticks = 0
        self.rhythm_history = deque(maxlen=10)

        self.last_valid_data_time = time.time()

        # 极度重要：启动时不加载硬件线程！
        self.hw_thread = None

        root = BoxLayout(orientation='vertical', padding=15, spacing=12)

        top_row = BoxLayout(size_hint_y=0.15, spacing=15)
        left_col = BoxLayout(orientation='horizontal', size_hint_x=0.25)
        self.heart_label = Label(text="❤", font_size='40sp', halign='center', valign='middle', font_name=EMOJI_FONT)
        self.bpm_label = Label(text="--", font_size='36sp', bold=True, color=get_color_from_hex('#333333'),
                               halign='center', valign='middle', font_name=FONT_NAME)
        left_col.add_widget(self.heart_label)
        left_col.add_widget(self.bpm_label)
        top_row.add_widget(left_col)

        mid_col = BoxLayout(orientation='vertical', size_hint_x=0.25)
        self.hrv_label = Label(text="HRV: -- ms", font_size='22sp', bold=True, color=get_color_from_hex('#555555'),
                               halign='center', valign='middle', font_name=FONT_NAME)
        mid_col.add_widget(self.hrv_label)
        top_row.add_widget(mid_col)

        right_col = BoxLayout(orientation='vertical', size_hint_x=0.5)
        self.status_label = Label(text="状态: 待机就绪", font_size='20sp', bold=True,
                                  color=get_color_from_hex('#555555'), halign='right', valign='middle',
                                  font_name=FONT_NAME)
        self.btn_diag = Button(text="开始连接及诊断波形", size_hint_y=0.6, font_size='18sp', bold=True,
                               background_color=get_color_from_hex('#0078D7'), color=(1, 1, 1, 1), font_name=FONT_NAME)

        # 按钮点下去才会连接！
        self.btn_diag.bind(on_press=self.start_manual_diagnosis)

        right_col.add_widget(self.status_label)
        right_col.add_widget(self.btn_diag)
        top_row.add_widget(right_col)
        root.add_widget(top_row)

        self.graph = ECGPlotWidget(size_hint_y=0.6)
        root.add_widget(self.graph)

        self.advice_box = RichLogBox(size_hint_y=0.25)
        self.advice_box.text = "💡 界面核心已成功加载！一切正常。\n\n请确认：你已在平板的“设置-蓝牙”里，连上了带有 HC/BT/LE 字样的硬件。\n准备好后，点击上方的蓝色按钮以呼叫蓝牙设备！"
        root.add_widget(self.advice_box)

        Clock.schedule_interval(self.update_ui, 0.5)
        self.heart_anim_event = Clock.schedule_interval(self.animate_heart, 0.8)

        # 启动时不崩的数据保存
        try:
            self.csv_manager = CSVDataManager()
        except:
            pass

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

    def start_manual_diagnosis(self, instance):
        # 【最关键一步】按下按钮才开始寻找蓝牙，完全杜绝开屏闪退！
        if not self.hw_thread or not self.hw_thread.is_alive():
            self.hw_thread = HardwareThread(self.on_serial_data, self.update_conn_ui)
            self.hw_thread.start()

        self.diag_status = 'PREPARING'
        self.prep_countdown = 6
        self.btn_diag.text = "消解杂波中..."
        self.btn_diag.disabled = True
        self.status_label.text = f"平复中: {self.prep_countdown}s"
        self.status_label.color = get_color_from_hex('#2980b9')
        self.bpm_label.text = "--"
        self.hrv_label.text = "HRV: -- ms"
        self.graph.display_mode = 'WAVE'

        self.last_valid_data_time = time.time()

    def update_ui(self, dt):
        now_time = time.time()
        is_disconnected = (now_time - self.last_valid_data_time) > 2.5

        if self.diag_status == 'IDLE':
            self.bpm_label.text = "--"
            self.hrv_label.text = "HRV: -- ms"
            self.graph.display_mode = 'FLAT'
            return

        # 如果线程压根没启动过，不算掉线
        if self.hw_thread and is_disconnected:
            self.bpm_label.text = "--"
            self.hrv_label.text = "HRV: -- ms"
            self.graph.display_mode = 'FLAT'
            if self.diag_status in ['PREPARING', 'RUNNING']:
                self.diag_status = 'IDLE'
                self.btn_diag.disabled = False
                self.btn_diag.text = "唤醒受阻重新连接"
                self.status_label.text = "底层连接未成立..."
                self.status_label.color = get_color_from_hex('#e74c3c')
            return
        else:
            if self.current_bpm > 0:
                self.bpm_label.text = str(self.current_bpm)
                self.hrv_label.text = f"HRV: {self.current_hrv} ms"

        if self.diag_status == 'PREPARING':
            self.prep_countdown -= 0.5
            if self.prep_countdown > 0:
                self.status_label.text = f"平复中: {int(self.prep_countdown)}s"
            else:
                self.diag_status = 'RUNNING'
                self.valid_data_ticks = 0
                self.rhythm_history.clear()
                self.status_label.text = "纯净推流采集中..."
            return

        if self.diag_status == 'DONE': return

        self.valid_data_ticks += 0.5
        if int(self.valid_data_ticks) > len(self.rhythm_history):
            self.rhythm_history.append(self.current_rhythm)

        if self.valid_data_ticks <= 10:
            prog = int((self.valid_data_ticks / 10.0) * 100)
            self.status_label.text = f"析出... {prog}%"
            return

        self.diag_status = 'DONE'
        self.btn_diag.disabled = False
        self.btn_diag.text = "开启全新捕获"
        self.status_label.text = "采集完成"

    def on_stop(self):
        if self.hw_thread:
            self.hw_thread.stop()


if __name__ == '__main__':
    ECGApp().run()
