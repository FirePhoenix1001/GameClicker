from pynput import keyboard
import time
import threading

class KeyboardMacro:
    def __init__(self):
        self.is_running = False
        self.is_recording = False
        self.recorded_events = []
        self.kb_ctrl = keyboard.Controller()
        self.thread = None
        self.callbacks = {
            'w': ('p', 'd', 0.05),
            's': ('/', 'd', 0.05),
            'e': ('p', 'f', 0.05),
            'c': ('/', 'f', 0.05)
        }
        self.status_callback = None
        self.record_listener = None
        self.hotkey_listener = None
        self.start_time = 0

    def trigger_keys(self, firstKey, secondKey, second):
        """一個通用的按鍵模擬函式"""
        if self.status_callback:
            self.status_callback(f"執行：{firstKey} + {secondKey}")
        # 使用 pynput 以保持一致
        try:
            self.kb_ctrl.press(firstKey)
            time.sleep(second)
            self.kb_ctrl.press(secondKey)
            time.sleep(second)
            self.kb_ctrl.release(secondKey)
            time.sleep(second)
            self.kb_ctrl.release(firstKey)
        except Exception as e:
            if self.status_callback:
                self.status_callback(f"錯誤: {e}")

    def run_polling(self):
        # 這裡原本是用 keyboard 庫的 is_pressed，我們保留 logic 但可以考慮改進
        import keyboard as kb # 局部導入以避免命名衝突
        w_pressed = s_pressed = e_pressed = c_pressed = False
        
        while self.is_running:
            try:
                # 檢查 'w'
                if kb.is_pressed('w'):
                    if not w_pressed:
                        self.trigger_keys(*self.callbacks['w'])
                        w_pressed = True
                else:
                    w_pressed = False

                # 檢查 's'
                if kb.is_pressed('s'):
                    if not s_pressed:
                        self.trigger_keys(*self.callbacks['s'])
                        s_pressed = True
                else:
                    s_pressed = False

                # 檢查 'e'
                if kb.is_pressed('e'):
                    if not e_pressed:
                        self.trigger_keys(*self.callbacks['e'])
                        e_pressed = True
                else:
                    e_pressed = False

                # 檢查 'c'
                if kb.is_pressed('c'):
                    if not c_pressed:
                        self.trigger_keys(*self.callbacks['c'])
                        c_pressed = True
                else:
                    c_pressed = False

                time.sleep(0.01)
            except Exception as e:
                if self.status_callback:
                    self.status_callback(f"錯誤: {e}")
                break

    def start(self, status_cb=None):
        if not self.is_running:
            self.is_running = True
            self.status_callback = status_cb
            self.thread = threading.Thread(target=self.run_polling, daemon=True)
            self.thread.start()
            if self.status_callback:
                self.status_callback("鍵盤宏監測已啟動")

    def stop(self):
        self.is_running = False
        if self.status_callback:
            self.status_callback("鍵盤宏監測已停止")

    def start_recording(self):
        if self.is_recording: return
        self.is_recording = True
        self.recorded_events = []
        self.start_time = time.time()
        
        if self.status_callback:
            self.status_callback("錄製中 (鍵盤)...", "red")

        def on_press(key):
            if self.is_recording:
                # 避免錄製到停止鍵 (假設停止鍵是固定的或由 GUI 傳入)
                self.recorded_events.append(('press', key, time.time() - self.start_time))

        def on_release(key):
            if self.is_recording:
                self.recorded_events.append(('release', key, time.time() - self.start_time))

        self.record_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self.record_listener.start()

    def stop_recording(self):
        if not self.is_recording: return
        self.is_recording = False
        if self.record_listener:
            self.record_listener.stop()
        if self.status_callback:
            self.status_callback(f"錄製完成 ({len(self.recorded_events)} 按鍵事件)")

    def play_recording(self):
        if not self.recorded_events:
            if self.status_callback:
                self.status_callback("無錄製內容", "orange")
            return
        
        self.is_running = True
        if self.status_callback:
            self.status_callback("播放中 (鍵盤)...", "blue")
            
        def run_play():
            start_play_time = time.time()
            for event in self.recorded_events:
                if not self.is_running: break
                
                target_time = event[-1]
                while (time.time() - start_play_time) < target_time:
                    if not self.is_running: break
                    time.sleep(0.001)
                
                type, key, t = event
                try:
                    if type == 'press':
                        self.kb_ctrl.press(key)
                    else:
                        self.kb_ctrl.release(key)
                except:
                    pass
            
            self.is_running = False
            if self.status_callback:
                self.status_callback("待命")

        threading.Thread(target=run_play, daemon=True).start()

    def start_hotkey_listener(self, toggle_record_cb):
        # 這裡可以設置全域熱鍵來啟動/停止錄製
        def on_press(key):
            try:
                # 假設預設用 F10 當作 停止錄製 (或者切換)
                if key == keyboard.Key.f10:
                    toggle_record_cb()
            except:
                pass
        
        self.hotkey_listener = keyboard.Listener(on_press=on_press)
        self.hotkey_listener.start()