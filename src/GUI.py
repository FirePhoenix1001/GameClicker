import tkinter as tk
from tkinter import ttk
from src.MouseMacro import MouseMacro
from src.KeyboardMacro import KeyboardMacro

class IntegratedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GameClicker Pro 整合工具")
        self.root.geometry("500x700")
        self.root.configure(bg="#f0f0f0")
        
        # 設置樣式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TFrame", background="#f0f0f0")
        
        self.mouse_logic = MouseMacro()
        self.keyboard_logic = KeyboardMacro()
        
        self.setup_ui()
        
        # 啟動監聽器
        self.mouse_logic.start_listener()
        
    def setup_ui(self):
        # 標題
        title_label = tk.Label(self.root, text="GameClicker 終極整合版", font=("Microsoft JhengHei", 18, "bold"), 
                              bg="#3f51b5", fg="white", pady=10)
        title_label.pack(fill="x")

        # 建立分頁控制
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=15, pady=15)
        
        # 建立分頁
        self.mouse_tab = ttk.Frame(self.notebook)
        self.keyboard_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.mouse_tab, text=" 🖱️ 滑鼠宏 ")
        self.notebook.add(self.keyboard_tab, text=" ⌨️ 鍵盤宏 ")
        
        self.setup_mouse_tab()
        self.setup_keyboard_tab()
        
        # 公用狀態列
        self.status_frame = tk.Frame(self.root, bg="#e0e0e0", height=30)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_label = tk.Label(self.status_frame, text="狀態：待命", fg="#1a237e", bg="#e0e0e0", font=("Microsoft JhengHei", 10))
        self.status_label.pack(side="left", padx=10)

    def setup_mouse_tab(self):
        # 1. 圓周運動設定區
        circle_frame = tk.LabelFrame(self.mouse_tab, text=" 圓周運動設定 ", font=("Microsoft JhengHei", 10, "bold"))
        circle_frame.pack(fill="x", padx=10, pady=10)
        self.create_input(circle_frame, "半徑 (px):", "100", 'radius')
        self.create_input(circle_frame, "角速度:", "5.0", 'omega')

        # 2. 往返運動設定區
        linear_frame = tk.LabelFrame(self.mouse_tab, text=" 往返運動設定 ", font=("Microsoft JhengHei", 10, "bold"))
        linear_frame.pack(fill="x", padx=10, pady=10)
        self.create_input(linear_frame, "振幅 (px):", "150", 'amp')
        self.create_input(linear_frame, "移動速度:", "400", 'speed')
        self.create_input(linear_frame, "頂點停頓 (秒):", "0.5", 'pause')

        # 3. 熱鍵設定
        key_frame = tk.LabelFrame(self.mouse_tab, text=" 熱鍵設定 ", font=("Microsoft JhengHei", 10, "bold"))
        key_frame.pack(fill="x", padx=10, pady=10)
        
        # 這裡需要特殊的同步邏輯給熱鍵
        self.create_hotkey_input(key_frame, "圓周熱鍵:", "f", 'circle')
        self.create_hotkey_input(key_frame, "上下熱鍵:", "g", 'vertical')
        self.create_hotkey_input(key_frame, "左右熱鍵:", "h", 'horizontal')

        self.mouse_logic.status_callback = self.update_status

    def setup_keyboard_tab(self):
        container = tk.Frame(self.keyboard_tab, bg="#ffffff", bd=1, relief="sunken")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(container, text="錄製的鍵盤宏序列", font=("Microsoft JhengHei", 12, "bold"), bg="#ffffff").pack(pady=10)
        
        rules = [
            ("按下 W 鍵", "執行 P -> D (50ms)"),
            ("按下 S 鍵", "執行 / -> D (50ms)"),
            ("按下 E 鍵", "執行 P -> F (50ms)"),
            ("按下 C 鍵", "執行 / -> F (50ms)")
        ]
        
        for trigger, action in rules:
            f = tk.Frame(container, bg="#ffffff")
            f.pack(fill="x", padx=20, pady=5)
            tk.Label(f, text=trigger, font=("Microsoft JhengHei", 10), bg="#ffffff", width=12, anchor="w").pack(side="left")
            tk.Label(f, text="➔", font=("Arial", 10), bg="#ffffff").pack(side="left", padx=10)
            tk.Label(f, text=action, font=("Consolas", 10, "italic"), bg="#ffffff", fg="#2e7d32").pack(side="left")

        btn_frame = tk.Frame(self.keyboard_tab)
        btn_frame.pack(side="bottom", fill="x", pady=20)
        
        self.kb_start_btn = tk.Button(btn_frame, text="啟動鍵盤監測", command=self.start_keyboard, 
                                     bg="#4caf50", fg="white", font=("Microsoft JhengHei", 11, "bold"), 
                                     relief="raised", padx=20, pady=10)
        self.kb_start_btn.pack(side="left", expand=True, padx=20)
        
        self.kb_stop_btn = tk.Button(btn_frame, text="停止鍵盤監測", command=self.stop_keyboard, 
                                    bg="#f44336", fg="white", font=("Microsoft JhengHei", 11, "bold"), 
                                    relief="raised", state="disabled", padx=20, pady=10)
        self.kb_stop_btn.pack(side="right", expand=True, padx=20)

    def create_input(self, parent, label_text, default_val, config_key):
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(fill="x", padx=10, pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="w", bg="#f0f0f0", font=("Microsoft JhengHei", 9)).pack(side="left")
        
        var = tk.StringVar(value=default_val)
        entry = tk.Entry(frame, textvariable=var, font=("Consolas", 10))
        entry.pack(side="right", expand=True, fill="x")
        
        var.trace_add("write", lambda *args: self.sync_config(config_key, var.get()))
        return entry

    def create_hotkey_input(self, parent, label_text, default_val, mode):
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(fill="x", padx=10, pady=5)
        tk.Label(frame, text=label_text, width=15, anchor="w", bg="#f0f0f0", font=("Microsoft JhengHei", 9)).pack(side="left")
        
        var = tk.StringVar(value=default_val)
        entry = tk.Entry(frame, textvariable=var, font=("Consolas", 10), width=5)
        entry.pack(side="right")
        
        var.trace_add("write", lambda *args: self.sync_hotkey(mode, var.get()))
        return entry

    def sync_config(self, key, value):
        try:
            self.mouse_logic.update_config(key, float(value))
        except ValueError:
            pass

    def sync_hotkey(self, mode, char):
        if char:
            # 更新 mouse_logic 中的 hotkeys 字典
            # 先移除舊的映射
            old_char = next((k for k, v in self.mouse_logic.config['hotkeys'].items() if v == mode), None)
            if old_char:
                del self.mouse_logic.config['hotkeys'][old_char]
            self.mouse_logic.config['hotkeys'][char.lower()] = mode

    def start_keyboard(self):
        self.keyboard_logic.start(self.update_status)
        self.kb_start_btn.config(state="disabled")
        self.kb_stop_btn.config(state="normal")

    def stop_keyboard(self):
        self.keyboard_logic.stop()
        self.kb_start_btn.config(state="normal")
        self.kb_stop_btn.config(state="disabled")

    def update_status(self, text, color="#1a237e"):
        self.status_label.config(text=f"狀態：{text}", fg=color)

if __name__ == "__main__":
    root = tk.Tk()
    app = IntegratedGUI(root)
    root.mainloop()