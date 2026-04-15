import tkinter as tk
from tkinter import ttk
from src.MouseMacro import MouseMacro
from src.KeyboardMacro import KeyboardMacro

class IntegratedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GameClicker")
        self.root.geometry("500x650")
        self.root.configure(bg="#f0f0f0")
        
        # 點擊空白處取消選取文字框
        self.root.bind("<1>", lambda event: self.clear_focus(event))
        
        # 設置樣式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TNotebook", background="#f0f0f0")
        self.style.configure("TFrame", background="#f0f0f0")
        
        self.mouse_logic = MouseMacro()
        self.keyboard_logic = KeyboardMacro()
        
        # 變數定義
        self.infinite_var = tk.BooleanVar(value=True)
        self.auto_close_var = tk.BooleanVar(value=True) # 預設不勾選保持開啟 = 開啟自動關閉
        self.close_minutes_var = tk.StringVar(value="1")
        self.timer_job = None
        
        self.setup_ui()
        
        # 啟動監聽器
        self.mouse_logic.start_listener()
        self.keyboard_logic.start_hotkey_listener(self.toggle_kb_recording)
        self.update_timer() # 初始化計時器

    def clear_focus(self, event):
        if not isinstance(event.widget, tk.Entry):
            self.root.focus()

    def setup_ui(self):
        # 標題
        title_label = tk.Label(self.root, text="GameClicker", font=("Microsoft JhengHei", 18, "bold"), 
                              bg="#3f51b5", fg="white", pady=10)
        title_label.pack(fill="x")

        # 建立分頁控制
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=15, pady=5)
        
        # 建立分頁
        self.mouse_tab = ttk.Frame(self.notebook)
        self.keyboard_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.mouse_tab, text=" 🖱️ 滑鼠 ")
        self.notebook.add(self.keyboard_tab, text=" ⌨️ 鍵盤 ")
        
        self.setup_mouse_tab()
        self.setup_keyboard_tab()
        
        # 4. 全域設定 (自動關閉)
        global_frame = tk.LabelFrame(self.root, text=" 系統自動化 ", font=("Microsoft JhengHei", 10, "bold"))
        global_frame.pack(fill="x", padx=25, pady=5)
        
        f = tk.Frame(global_frame)
        f.pack(fill="x", padx=10, pady=5)
        
        tk.Checkbutton(f, text="保持開啟 (不自動關閉)", variable=self.auto_close_var, 
                      onvalue=False, offvalue=True, command=self.update_timer).pack(side="left")
        
        self.timer_entry_frame = tk.Frame(f)
        self.timer_entry_frame.pack(side="right")
        tk.Label(self.timer_entry_frame, text="關閉倒數(分):").pack(side="left")
        entry = tk.Entry(self.timer_entry_frame, textvariable=self.close_minutes_var, width=5)
        entry.pack(side="left", padx=5)
        self.close_minutes_var.trace_add("write", lambda *args: self.update_timer())

        # 公用狀態列
        self.status_frame = tk.Frame(self.root, bg="#e0e0e0", height=30)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_label = tk.Label(self.status_frame, text="狀態：待命", fg="#1a237e", bg="#e0e0e0", font=("Microsoft JhengHei", 10))
        self.status_label.pack(side="left", padx=10)

    def setup_mouse_tab(self):
        # 1. 播放設定區
        settings_frame = tk.LabelFrame(self.mouse_tab, text=" 播放設定 ", font=("Microsoft JhengHei", 10, "bold"))
        settings_frame.pack(fill="x", padx=10, pady=10)
        
        # 重複次數與無限次勾選並排
        rep_row = tk.Frame(settings_frame)
        rep_row.pack(fill="x", padx=8, pady=5)
        tk.Label(rep_row, text="重複次數:", width=10, anchor="w", font=("Microsoft JhengHei", 9)).pack(side="left")
        
        self.repeat_entry = tk.Entry(rep_row, textvariable=tk.StringVar(value="1"), font=("Consolas", 10), width=15)
        self.repeat_entry.pack(side="left", padx=5)
        # 綁定變數同步
        self.repeat_entry.bind("<KeyRelease>", lambda e: self.sync_config('repeat_count', self.repeat_entry.get()))
        
        tk.Checkbutton(rep_row, text="重複無限次", variable=self.infinite_var, 
                      command=self.sync_infinite).pack(side="left", padx=10)
        
        # 這裡也要統一比例
        self.create_input(settings_frame, "播放倍速:", "1.0", 'playback_speed')

        
        self.sync_infinite() # 初始化狀態

        # 2. 錄製控制區
        record_frame = tk.LabelFrame(self.mouse_tab, text=" 滑鼠錄製與播放 ", font=("Microsoft JhengHei", 10, "bold"))
        record_frame.pack(fill="x", padx=10, pady=10)
        
        m_btn_frame = tk.Frame(record_frame)
        m_btn_frame.pack(fill="x", pady=15)
        
        self.m_record_btn = tk.Button(m_btn_frame, text="⏺️ 錄製 (F10)", command=self.mouse_logic.toggle_recording,
                                     bg="#ff9800", fg="white", font=("Microsoft JhengHei", 10, "bold"), pady=15)
        self.m_record_btn.pack(side="left", expand=True, padx=10)
        
        self.m_play_btn = tk.Button(m_btn_frame, text="▶️ 播放 (F9)", command=self.mouse_logic.toggle_playback,
                                   bg="#2196f3", fg="white", font=("Microsoft JhengHei", 10, "bold"), pady=15)
        self.m_play_btn.pack(side="left", expand=True, padx=10)

        self.mouse_logic.status_callback = self.update_status

    def sync_infinite(self):
        is_inf = self.infinite_var.get()
        self.mouse_logic.update_config('infinite_loop', is_inf)
        if is_inf:
            self.repeat_entry.config(state="disabled")
        else:
            self.repeat_entry.config(state="normal")

    def update_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
            self.timer_job = None
            
        if self.auto_close_var.get():
            try:
                mins = float(self.close_minutes_var.get())
                if mins > 0:
                    self.timer_job = self.root.after(int(mins * 60 * 1000), self.root.destroy)
            except ValueError:
                pass

    def setup_keyboard_tab(self):
        # 1. 預設宏展示
        container = tk.LabelFrame(self.keyboard_tab, text=" 預設宏序列 ", font=("Microsoft JhengHei", 10, "bold"))
        container.pack(fill="x", padx=10, pady=5)
        
        rules = [
            ("按下 W 鍵", "執行 P -> D (50ms)"),
            ("按下 S 鍵", "執行 / -> D (50ms)"),
            ("按下 E 鍵", "執行 P -> F (50ms)"),
            ("按下 C 鍵", "執行 / -> F (50ms)")
        ]
        
        for trigger, action in rules:
            f = tk.Frame(container)
            f.pack(fill="x", padx=10, pady=2)
            tk.Label(f, text=trigger, font=("Microsoft JhengHei", 9), width=10, anchor="w").pack(side="left")
            tk.Label(f, text="➔", font=("Arial", 9)).pack(side="left", padx=5)
            tk.Label(f, text=action, font=("Consolas", 8, "italic"), fg="#2e7d32").pack(side="left")

        # 2. 鍵盤錄製區
        kb_record_frame = tk.LabelFrame(self.keyboard_tab, text=" 鍵盤錄製與播放 ", font=("Microsoft JhengHei", 10, "bold"))
        kb_record_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(kb_record_frame, text="熱鍵 'F10' 可切換錄製狀態", fg="#d32f2f", font=("Microsoft JhengHei", 9)).pack(pady=5)
        
        k_btn_frame = tk.Frame(kb_record_frame)
        k_btn_frame.pack(fill="x", pady=5)
        
        self.k_record_btn = tk.Button(k_btn_frame, text="開始錄製", command=self.keyboard_logic.start_recording,
                                     bg="#ff9800", fg="white", font=("Microsoft JhengHei", 9, "bold"))
        self.k_record_btn.pack(side="left", expand=True, padx=5, pady=5)
        
        self.k_stop_btn = tk.Button(k_btn_frame, text="停止錄製", command=self.keyboard_logic.stop_recording,
                                   bg="#f44336", fg="white", font=("Microsoft JhengHei", 9, "bold"))
        self.k_stop_btn.pack(side="left", expand=True, padx=5, pady=5)
        
        self.k_play_btn = tk.Button(kb_record_frame, text="▶️ 播放錄製內容", command=self.keyboard_logic.play_recording,
                                   bg="#2196f3", fg="white", font=("Microsoft JhengHei", 10, "bold"), pady=5)
        self.k_play_btn.pack(fill="x", padx=10, pady=5)

        # 3. 監控控制
        mon_frame = tk.LabelFrame(self.keyboard_tab, text=" 鍵盤監測控制 ", font=("Microsoft JhengHei", 10, "bold"))
        mon_frame.pack(fill="x", padx=10, pady=5)

        btn_container = tk.Frame(mon_frame)
        btn_container.pack(fill="x", pady=10)
        
        self.kb_start_btn = tk.Button(btn_container, text="啟動監測", command=self.start_keyboard, 
                                     bg="#4caf50", fg="white", font=("Microsoft JhengHei", 9, "bold"), 
                                     relief="raised", width=12)
        self.kb_start_btn.pack(side="left", expand=True, padx=10)
        
        self.kb_stop_btn = tk.Button(btn_container, text="停止監測", command=self.stop_keyboard, 
                                    bg="#f44336", fg="white", font=("Microsoft JhengHei", 9, "bold"), 
                                    relief="raised", state="disabled", width=12)
        self.kb_stop_btn.pack(side="right", expand=True, padx=10)

    def create_input(self, parent, label_text, default_val, config_key):
        frame = tk.Frame(parent, bg="#f0f0f0")
        frame.pack(fill="x", padx=8, pady=5)
        tk.Label(frame, text=label_text, width=10, anchor="w", bg="#f0f0f0", font=("Microsoft JhengHei", 9)).pack(side="left")
        
        var = tk.StringVar(value=default_val)
        entry = tk.Entry(frame, textvariable=var, font=("Consolas", 10), width=15)
        entry.pack(side="left", padx=5)
        
        var.trace_add("write", lambda *args: self.sync_config(config_key, var.get()))
        return entry



    def sync_config(self, key, value):
        try:
            self.mouse_logic.update_config(key, float(value))
        except ValueError:
            pass

    def toggle_kb_recording(self):

        if self.keyboard_logic.is_recording:
            self.keyboard_logic.stop_recording()
        else:
            self.keyboard_logic.start_recording()

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