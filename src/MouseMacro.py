import time
import threading
from pynput import mouse, keyboard
import winsound

class MouseMacro:
    def __init__(self):
        self.is_running = False
        self.is_recording = False
        self.recorded_events = []
        self.mouse_ctrl = mouse.Controller()
        self.config = {
            'repeat_count': 1,
            'infinite_loop': True,
            'playback_speed': 1.0
        }
        self.status_callback = None
        self.listener = None
        self.record_listener = None
        self.start_time = 0

    def update_config(self, key, value):
        self.config[key] = value

    def play_sound(self, type='success'):
        try:
            if type == 'start': # 开始
                winsound.Beep(600, 200)
            elif type == 'stop': # 停止
                winsound.Beep(400, 200)
            elif type == 'notice':
                winsound.MessageBeep()
        except:
            pass

    def toggle_recording(self):
        if self.is_recording:
            self.stop_recording()
        else:
            self.start_recording()

    def toggle_playback(self):
        if self.is_running:
            self.stop_playback()
        else:
            self.play_recording()

    def start_recording(self):
        if self.is_recording: return
        self.is_recording = True
        self.recorded_events = []
        self.start_time = time.time()
        
        self.play_sound('start')
        if self.status_callback:
            self.status_callback("⏺️ 錄製中 (滑鼠)...", "red")

        def on_move(x, y):
            if self.is_recording:
                self.recorded_events.append(('move', x, y, time.time() - self.start_time))

        def on_click(x, y, button, pressed):
            if self.is_recording:
                self.recorded_events.append(('click', x, y, button, pressed, time.time() - self.start_time))

        self.record_listener = mouse.Listener(on_move=on_move, on_click=on_click)
        self.record_listener.start()

    def stop_recording(self):
        if not self.is_recording: return
        self.is_recording = False
        if self.record_listener:
            self.record_listener.stop()
        
        self.play_sound('stop')
        if self.status_callback:
            self.status_callback(f"✅ 錄製完成 ({len(self.recorded_events)} 節點)")

    def play_recording(self):
        if not self.recorded_events:
            if self.status_callback:
                self.status_callback("⚠️ 無錄製內容", "orange")
            return
        
        self.is_running = False
        time.sleep(0.01)
            
        self.is_running = True
        self.play_sound('start')
        if self.status_callback:
            self.status_callback("▶️ 播放中 (滑鼠)...", "blue")
            
        def run_play():
            repeat = int(self.config.get('repeat_count', 1))
            infinite = self.config.get('infinite_loop', True)
            speed = float(self.config.get('playback_speed', 1.0))
            if speed <= 0: speed = 1.0
            
            count = 0
            while self.is_running:
                start_play_time = time.time()
                for event in self.recorded_events:
                    if not self.is_running: break
                    
                    target_time = event[-1] / speed
                    while (time.time() - start_play_time) < target_time:
                        if not self.is_running: break
                        time.sleep(0.001)
                    
                    if event[0] == 'move':
                        self.mouse_ctrl.position = (event[1], event[2])
                    elif event[0] == 'click':
                        x, y, button, pressed, t = event[1:]
                        self.mouse_ctrl.position = (x, y)
                        if pressed:
                            self.mouse_ctrl.press(button)
                        else:
                            self.mouse_ctrl.release(button)
                
                count += 1
                if not infinite and count >= repeat:
                    break
                    
                if self.is_running:
                    if self.status_callback:
                        self.status_callback(f"▶️ 正在播放 (次數: {count}/{'∞' if infinite else repeat})", "blue")

            self.is_running = False
            self.play_sound('stop')
            if self.status_callback:
                self.status_callback("待命")

        threading.Thread(target=run_play, daemon=True).start()

    def stop_playback(self):
        self.is_running = False

    def start_listener(self):
        def on_press(key):
            try:
                if key == keyboard.Key.f10:
                    self.toggle_recording()
                elif key == keyboard.Key.f9:
                    self.toggle_playback()
            except:
                pass
        
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def stop_listener(self):
        if self.listener:
            self.listener.stop()
        if self.record_listener:
            self.record_listener.stop()