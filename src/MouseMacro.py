import math
import time
import threading
from pynput import mouse, keyboard

class MouseMacro:
    def __init__(self):
        self.is_running = False
        self.current_mode = None
        self.start_pos = (0, 0)
        self.mouse_ctrl = mouse.Controller()
        self.config = {
            'radius': 100,
            'omega': 5.0,
            'amp': 150,
            'speed': 400,
            'pause': 0.5,
            'hotkeys': {'f': 'circle', 'g': 'vertical', 'h': 'horizontal'}
        }
        self.status_callback = None
        self.listener = None

    def update_config(self, key, value):
        self.config[key] = value

    def motion_loop(self):
        start_time = time.time()
        direction = 1
        last_update = time.time()
        current_offset = 0
        
        radius = float(self.config['radius'])
        omega = float(self.config['omega'])
        amp = float(self.config['amp'])
        speed = float(self.config['speed'])
        pause = float(self.config['pause'])

        while self.is_running:
            now = time.time()
            dt = now - last_update
            last_update = now
            
            if self.current_mode == 'circle':
                elapsed = now - start_time
                theta = omega * elapsed
                tx = self.start_pos[0] + radius * math.cos(theta)
                ty = self.start_pos[1] + radius * math.sin(theta)
                self.mouse_ctrl.position = (tx, ty)
            elif self.current_mode in ['vertical', 'horizontal']:
                current_offset += direction * speed * dt
                if abs(current_offset) >= amp:
                    current_offset = amp if direction == 1 else -amp
                    self.update_pos(current_offset)
                    time.sleep(pause)
                    direction *= -1
                    last_update = time.time()
                else:
                    self.update_pos(current_offset)
            time.sleep(0.01)

    def update_pos(self, offset):
        if self.current_mode == 'vertical':
            self.mouse_ctrl.position = (self.start_pos[0], self.start_pos[1] + offset)
        else: # horizontal
            self.mouse_ctrl.position = (self.start_pos[0] + offset, self.start_pos[1])

    def toggle(self, mode):
        if self.is_running and self.current_mode == mode:
            self.is_running = False
            if self.status_callback:
                self.status_callback("待命")
        else:
            self.is_running = True
            self.current_mode = mode
            self.start_pos = self.mouse_ctrl.position
            if self.status_callback:
                self.status_callback(f"運行中 ({mode})", "green")
            threading.Thread(target=self.motion_loop, daemon=True).start()

    def start_listener(self):
        def on_press(key):
            try:
                k = key.char
                if k in self.config['hotkeys']:
                    self.toggle(self.config['hotkeys'][k])
            except:
                pass
        
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def stop_listener(self):
        if self.listener:
            self.listener.stop()