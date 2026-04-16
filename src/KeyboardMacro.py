from pynput import keyboard
import time
import threading
import keyboard as kb # 用於全域按鍵監測，因為 pynput 的 Listener 較重且難以實現 is_pressed 的邏輯

class KeyboardMacro:
    def __init__(self):
        self.is_running = False
        self.kb_ctrl = keyboard.Controller()
        self.thread = None
        # 預設規則列表：(trigger_key, response_key1, response_key2, delay)
        self.rules = [
            ['w', 'p', 'd', 0.05],
            ['s', '/', 'd', 0.05],
            ['e', 'p', 'f', 0.05],
            ['c', '/', 'f', 0.05]
        ]
        self.status_callback = None

    def trigger_keys(self, firstKey, secondKey, second):
        """執行按鍵宏：按下第一個鍵，延遲，按下第二個鍵，延遲，釋放第二個鍵，延遲，釋放第一個鍵"""
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
                self.status_callback(f"執行按鍵錯誤: {e}")

    def run_polling(self):
        # 記錄每個按鍵的狀態以防重複觸發
        pressed_states = {rule[0]: False for rule in self.rules}
        
        while self.is_running:
            try:
                for rule in self.rules:
                    trigger = rule[0]
                    if not trigger: continue
                    
                    try:
                        is_down = kb.is_pressed(trigger)
                    except:
                        is_down = False
                        
                    if is_down:
                        if not pressed_states.get(trigger, False):
                            # 觸發巨集
                            threading.Thread(target=self.trigger_keys, 
                                             args=(rule[1], rule[2], rule[3]), 
                                             daemon=True).start()
                            pressed_states[trigger] = True
                    else:
                        pressed_states[trigger] = False

                time.sleep(0.01)
            except Exception as e:
                if self.status_callback:
                    self.status_callback(f"監測循環錯誤: {e}")
                break

    def start(self, status_cb=None):
        if not self.is_running:
            self.is_running = True
            self.status_callback = status_cb
            self.thread = threading.Thread(target=self.run_polling, daemon=True)
            self.thread.start()
            if self.status_callback:
                self.status_callback("鍵盤宏監測已啟動", "#4caf50")

    def stop(self):
        self.is_running = False
        if self.status_callback:
            self.status_callback("鍵盤宏監測已停止", "#f44336")

    def update_rules(self, new_rules):
        """從 GUI 更新規則列表"""
        self.rules = new_rules