import keyboard
import time
import threading

class KeyboardMacro:
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.callbacks = {
            'w': ('p', 'd', 0.05),
            's': ('/', 'd', 0.05),
            'e': ('p', 'f', 0.05),
            'c': ('/', 'f', 0.05)
        }
        self.status_callback = None

    def trigger_keys(self, firstKey, secondKey, second):
        """一個通用的按鍵模擬函式"""
        if self.status_callback:
            self.status_callback(f"執行：{firstKey} + {secondKey}")
        keyboard.press(firstKey)
        time.sleep(second)
        keyboard.press(secondKey)
        time.sleep(second)
        keyboard.release(secondKey)
        time.sleep(second)
        keyboard.release(firstKey)

    def run_polling(self):
        w_pressed = s_pressed = e_pressed = c_pressed = False
        
        while self.is_running:
            try:
                # 檢查 'w'
                if keyboard.is_pressed('w'):
                    if not w_pressed:
                        self.trigger_keys(*self.callbacks['w'])
                        w_pressed = True
                else:
                    w_pressed = False

                # 檢查 's'
                if keyboard.is_pressed('s'):
                    if not s_pressed:
                        self.trigger_keys(*self.callbacks['s'])
                        s_pressed = True
                else:
                    s_pressed = False

                # 檢查 'e'
                if keyboard.is_pressed('e'):
                    if not e_pressed:
                        self.trigger_keys(*self.callbacks['e'])
                        e_pressed = True
                else:
                    e_pressed = False

                # 檢查 'c'
                if keyboard.is_pressed('c'):
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
                self.status_callback("鍵盤宏已啟動")

    def stop(self):
        self.is_running = False
        if self.status_callback:
            self.status_callback("鍵盤宏已停止")