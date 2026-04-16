import tkinter as tk
from tkinter import ttk
from src.MouseMacro import MouseMacro
from src.KeyboardMacro import KeyboardMacro

class IntegratedGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("GameClicker")
        self.root.geometry("550x700")
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
        self.auto_close_var = tk.BooleanVar(value=True) 
        self.close_minutes_var = tk.StringVar(value="1")
        self.timer_job = None
        
        # 鍵盤規則 UI 相關
        self.kb_rule_rows = []
        
        self.setup_ui()
        
        # 啟動監聽器
        self.mouse_logic.start_listener()
        self.update_timer() # 初始化計時器

    def clear_focus(self, event):
        if not isinstance(event.widget, tk.Entry):
            self.root.focus()

    def setup_ui(self):
        # 標題
        title_label = tk.Label(self.root, text="GameClicker Pro", font=("Microsoft JhengHei", 18, "bold"), 
                               bg="#3f51b5", fg="white", pady=10)
        title_label.pack(fill="x")

        # 建立分頁控制
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=15, pady=5)
        
        # 建立分頁
        self.mouse_tab = ttk.Frame(self.notebook)
        self.keyboard_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.mouse_tab, text=" 🖱️ 滑鼠錄製 ")
        self.notebook.add(self.keyboard_tab, text=" ⌨️ 鍵盤監測 ")
        
        self.setup_mouse_tab()
        self.setup_keyboard_tab()
        
        # 全域設定 (自動關閉)
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
        
        rep_row = tk.Frame(settings_frame)
        rep_row.pack(fill="x", padx=8, pady=5)
        tk.Label(rep_row, text="重複次數:", width=10, anchor="w", font=("Microsoft JhengHei", 9)).pack(side="left")
        
        self.repeat_entry = tk.Entry(rep_row, textvariable=tk.StringVar(value="1"), font=("Consolas", 10), width=15)
        self.repeat_entry.pack(side="left", padx=5)
        self.repeat_entry.bind("<KeyRelease>", lambda e: self.sync_config('repeat_count', self.repeat_entry.get()))
        
        tk.Checkbutton(rep_row, text="重複無限次", variable=self.infinite_var, 
                      command=self.sync_infinite).pack(side="left", padx=10)
        
        self.create_input(settings_frame, "播放倍速:", "1.0", 'playback_speed')
        self.sync_infinite() 

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

    def setup_keyboard_tab(self):
        # 鍵盤監測設定區域
        mon_frame = tk.LabelFrame(self.keyboard_tab, text=" 鍵盤監測控制 ", font=("Microsoft JhengHei", 10, "bold"))
        mon_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # 按鈕區
        btn_panel = tk.Frame(mon_frame)
        btn_panel.pack(fill="x", padx=10, pady=5)

        tk.Button(btn_panel, text="➕ 新增監測", command=self.add_rule_row, bg="#e3f2fd").pack(side="left", padx=2)
        tk.Button(btn_panel, text="➖ 刪除最後", command=self.remove_last_rule_row, bg="#ffebee").pack(side="left", padx=2)

        self.kb_start_btn = tk.Button(btn_panel, text=" ▶️ 啟動監測  ", command=self.start_keyboard, 
                                     bg="#4caf50", fg="white", font=("Microsoft JhengHei", 9, "bold"))
        self.kb_start_btn.pack(side="right", padx=5)
        
        self.kb_stop_btn = tk.Button(btn_panel, text=" ⏹️ 停止  ", command=self.stop_keyboard, 
                                    bg="#f44336", fg="white", font=("Microsoft JhengHei", 9, "bold"), 
                                    state="disabled")
        self.kb_stop_btn.pack(side="right", padx=5)

        # --- 表格容器 ---
        table_container = tk.Frame(mon_frame)
        table_container.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        # 1. 表頭 (使用 Grid 並預留捲軸寬度)
        header_frame = tk.Frame(table_container, bg="#e0e0e0")
        header_frame.pack(fill="x")
        
        # 使用 uniform 參數確保四列寬度完全一致
        for i in range(4):
            header_frame.columnconfigure(i, weight=1, uniform="kb_table")
        # 預留捲軸寬度 (通常 16-18px)
        header_frame.columnconfigure(4, minsize=20)

        headers = ["觸發按鍵", "回饋鍵 1", "回饋鍵 2", "延遲(秒)"]
        for i, text in enumerate(headers):
            tk.Label(header_frame, text=text, font=("Microsoft JhengHei", 9, "bold"), 
                     bg="#e0e0e0", pady=8, anchor="center", justify="center").grid(row=0, column=i, sticky="nsew")

        # 2. 滾動區域 (Canvas)
        canvas_box = tk.Frame(table_container)
        canvas_box.pack(fill="both", expand=True)
        
        # 設置 borderwidth=0, highlightthickness=0 以消除間隙
        self.kb_canvas = tk.Canvas(canvas_box, bg="#fff", highlightthickness=0, borderwidth=0)
        self.kb_scrollbar = ttk.Scrollbar(canvas_box, orient="vertical", command=self.kb_canvas.yview)
        self.kb_scrollable_frame = tk.Frame(self.kb_canvas, bg="#fff")

        # 綁定捲軸區域更新
        def update_scroll_region(event):
            self.kb_canvas.configure(scrollregion=self.kb_canvas.bbox("all"))

        self.kb_scrollable_frame.bind("<Configure>", update_scroll_region)

        # 建立畫布視窗
        self.kb_canvas_window = self.kb_canvas.create_window((0, 0), window=self.kb_scrollable_frame, anchor="nw")
        
        # 同步內容寬度
        def sync_width(event):
            self.kb_canvas.itemconfig(self.kb_canvas_window, width=event.width)
        
        self.kb_canvas.bind("<Configure>", sync_width)
        self.kb_canvas.configure(yscrollcommand=self.kb_scrollbar.set)

        # 綁定滑鼠滾輪
        def _on_mousewheel(event):
            self.kb_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        self.kb_canvas.bind_all("<MouseWheel>", _on_mousewheel)

        self.kb_canvas.pack(side="left", fill="both", expand=True)
        self.kb_scrollbar.pack(side="right", fill="y")

        # 初始化預設規則
        for rule in [['w', 'p', 'd', '0.05'], ['s', '/', 'd', '0.05'], ['e', 'p', 'f', '0.05'], ['c', '/', 'f', '0.05']]:
            self.add_rule_row(rule)

    def add_rule_row(self, data=None):
        if data is None:
            data = ['', '', '', '0.05']
            
        row_frame = tk.Frame(self.kb_scrollable_frame, bg="#fff", pady=2)
        row_frame.pack(fill="x", expand=True)
        
        v_trigger = tk.StringVar(value=data[0])
        v_res1 = tk.StringVar(value=data[1])
        v_res2 = tk.StringVar(value=data[2])
        v_delay = tk.StringVar(value=data[3])
        
        # 設置寬度一致並對齊
        for i in range(4):
            row_frame.columnconfigure(i, weight=1, uniform="kb_table")

        e_trigger = tk.Entry(row_frame, textvariable=v_trigger, width=8, justify="center")
        e_trigger.grid(row=0, column=0, sticky="ew", padx=1)
        
        e_res1 = tk.Entry(row_frame, textvariable=v_res1, width=8, justify="center")
        e_res1.grid(row=0, column=1, sticky="ew", padx=1)
        
        e_res2 = tk.Entry(row_frame, textvariable=v_res2, width=8, justify="center")
        e_res2.grid(row=0, column=2, sticky="ew", padx=1)
        
        e_delay = tk.Entry(row_frame, textvariable=v_delay, width=8, justify="center")
        e_delay.grid(row=0, column=3, sticky="ew", padx=1)
        
        self.kb_rule_rows.append({
            'frame': row_frame,
            'vars': [v_trigger, v_res1, v_res2, v_delay]
        })

    def remove_last_rule_row(self):
        if self.kb_rule_rows:
            last_row = self.kb_rule_rows.pop()
            last_row['frame'].destroy()

    def sync_kb_rules(self):
        rules = []
        for row in self.kb_rule_rows:
            v = [var.get().strip() for var in row['vars']]
            if v[0]: # 必須有觸發鍵
                try:
                    rules.append([v[0], v[1], v[2], float(v[3])])
                except ValueError:
                    rules.append([v[0], v[1], v[2], 0.05])
        self.keyboard_logic.update_rules(rules)

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

    def start_keyboard(self):
        self.sync_kb_rules()
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