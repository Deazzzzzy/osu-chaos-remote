import tkinter as tk
from tkinter import ttk
import socket
import threading

class ModernControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("osu! Chaos Remote")
        self.root.geometry("540x920")
        self.root.configure(bg="#1e1e2e")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, True)
        
        # --- Цветовая палитра ---
        self.bg_color = "#1e1e2e"
        self.panel_color = "#313244"
        self.text_color = "#cdd6f4"
        self.accent_on = "#f38ba8"
        self.accent_off = "#a6e3a1"
        self.accent_red = "#f38ba8"
        self.accent_blue = "#89b4fa"
        self.accent_yellow = "#f9e2af"
        self.accent_earth = "#fab387"
        self.accent_blackout = "#cba6f7"
        self.accent_cyan = "#89dceb"
        self.accent_purple = "#b4befe"
        
        self.inv_x = False
        self.inv_y = False
        self.jam_k1 = False
        self.jam_k2 = False

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScale", background=self.panel_color, troughcolor=self.bg_color)
        
        # --- Настройка стилей вкладок ---
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.panel_color, foreground=self.text_color, padding=[10, 5], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.accent_blue)], foreground=[("selected", "#11111b")])
        style.configure("TFrame", background=self.bg_color)
        self._vol_timer = None
        
        # Заголовок
        header = tk.Label(root, text="OSU! DEBUFF CONTROL", font=("Segoe UI Black", 16), bg=self.bg_color, fg=self.accent_blue)
        header.pack(pady=(12, 4))
        
        # Блок подключения
        conn_frame = tk.Frame(root, bg=self.panel_color, padx=15, pady=5)
        conn_frame.pack(fill=tk.X, padx=20, pady=4)
        tk.Label(conn_frame, text="IP Игрока:", font=("Segoe UI", 10, "bold"), bg=self.panel_color, fg=self.text_color).pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(conn_frame, font=("Segoe UI", 11), bg=self.bg_color, fg=self.text_color, bd=0)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Создаем Notebook (Вкладки)
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=8)

        # Вкладка 1: Базовые (со скроллом)
        tab1_outer = ttk.Frame(notebook)
        notebook.add(tab1_outer, text="Базовые")
        
        tab1_canvas = tk.Canvas(tab1_outer, bg=self.bg_color, highlightthickness=0)
        tab1_scrollbar = ttk.Scrollbar(tab1_outer, orient="vertical", command=tab1_canvas.yview)
        tab1 = tk.Frame(tab1_canvas, bg=self.bg_color)
        
        tab1_canvas.configure(yscrollcommand=tab1_scrollbar.set)
        tab1_scrollbar.pack(side="right", fill="y")
        tab1_canvas.pack(side="left", fill="both", expand=True)
        tab1_window = tab1_canvas.create_window((0, 0), window=tab1, anchor="nw")
        
        def configure_tab1_canvas(event):
            tab1_canvas.itemconfig(tab1_window, width=event.width)
            
        def configure_tab1_frame(event):
            tab1_canvas.configure(scrollregion=tab1_canvas.bbox("all"))
            
        tab1_canvas.bind('<Configure>', configure_tab1_canvas)
        tab1.bind('<Configure>', configure_tab1_frame)

        # Вкладка 2: Курсор (со скроллом)
        tab_cursor_outer = ttk.Frame(notebook)
        notebook.add(tab_cursor_outer, text="Курсор")
        
        tab_cursor_canvas = tk.Canvas(tab_cursor_outer, bg=self.bg_color, highlightthickness=0)
        tab_cursor_scrollbar = ttk.Scrollbar(tab_cursor_outer, orient="vertical", command=tab_cursor_canvas.yview)
        tab_cursor = tk.Frame(tab_cursor_canvas, bg=self.bg_color)
        
        tab_cursor_canvas.configure(yscrollcommand=tab_cursor_scrollbar.set)
        tab_cursor_scrollbar.pack(side="right", fill="y")
        tab_cursor_canvas.pack(side="left", fill="both", expand=True)
        tab_cursor_window = tab_cursor_canvas.create_window((0, 0), window=tab_cursor, anchor="nw")
        
        def configure_tab_cursor_canvas(event):
            tab_cursor_canvas.itemconfig(tab_cursor_window, width=event.width)
            
        def configure_tab_cursor_frame(event):
            tab_cursor_canvas.configure(scrollregion=tab_cursor_canvas.bbox("all"))
            
        tab_cursor_canvas.bind('<Configure>', configure_tab_cursor_canvas)
        tab_cursor.bind('<Configure>', configure_tab_cursor_frame)
        
        # Вкладка 3: Искажения экрана (со скроллом)
        tab2_outer = ttk.Frame(notebook)
        notebook.add(tab2_outer, text="Искажения")
        
        tab2_canvas = tk.Canvas(tab2_outer, bg=self.bg_color, highlightthickness=0)
        tab2_scrollbar = ttk.Scrollbar(tab2_outer, orient="vertical", command=tab2_canvas.yview)
        tab2 = tk.Frame(tab2_canvas, bg=self.bg_color)
        
        tab2_canvas.configure(yscrollcommand=tab2_scrollbar.set)
        tab2_scrollbar.pack(side="right", fill="y")
        tab2_canvas.pack(side="left", fill="both", expand=True)
        tab2_window = tab2_canvas.create_window((0, 0), window=tab2, anchor="nw")
        
        def configure_tab2_canvas(event):
            tab2_canvas.itemconfig(tab2_window, width=event.width)
            
        def configure_tab2_frame(event):
            tab2_canvas.configure(scrollregion=tab2_canvas.bbox("all"))
            
        tab2_canvas.bind('<Configure>', configure_tab2_canvas)
        tab2.bind('<Configure>', configure_tab2_frame)

        # Вкладка 4: Ивенты & Троллинг (со скроллом)
        tab3_outer = ttk.Frame(notebook)
        notebook.add(tab3_outer, text="Ивенты")
        
        tab3_canvas = tk.Canvas(tab3_outer, bg=self.bg_color, highlightthickness=0)
        tab3_scrollbar = ttk.Scrollbar(tab3_outer, orient="vertical", command=tab3_canvas.yview)
        tab3 = tk.Frame(tab3_canvas, bg=self.bg_color)
        
        tab3_canvas.configure(yscrollcommand=tab3_scrollbar.set)
        tab3_scrollbar.pack(side="right", fill="y")
        tab3_canvas.pack(side="left", fill="both", expand=True)
        tab3_window = tab3_canvas.create_window((0, 0), window=tab3, anchor="nw")
        
        def configure_tab3_canvas(event):
            tab3_canvas.itemconfig(tab3_window, width=event.width)
            
        def configure_tab3_frame(event):
            tab3_canvas.configure(scrollregion=tab3_canvas.bbox("all"))
            
        tab3_canvas.bind('<Configure>', configure_tab3_canvas)
        tab3.bind('<Configure>', configure_tab3_frame)

        # Вкладка 5: Галлюцинации
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Галлюцинации")

        # Обработчик скролла мыши для всех вкладок
        def _on_mousewheel(event):
            delta = int(-1 * (event.delta / 120))
            if tab1_canvas.winfo_ismapped():
                tab1_canvas.yview_scroll(delta, "units")
            elif tab2_canvas.winfo_ismapped():
                tab2_canvas.yview_scroll(delta, "units")
            elif tab_cursor_canvas.winfo_ismapped():
                tab_cursor_canvas.yview_scroll(delta, "units")
            elif tab3_canvas.winfo_ismapped():
                tab3_canvas.yview_scroll(delta, "units")
                
        root.bind_all("<MouseWheel>", _on_mousewheel)

        # ==========================================
        # Вкладка 1: ГЕЙМПЛЕЙ (Хаос, Ветер, Магнит, Черная Дыра)
        # ==========================================
        
        # --- СЕКЦИЯ: ХАОС ---
        chaos_frame = tk.Frame(tab1, bg=self.panel_color, padx=15, pady=10)
        chaos_frame.pack(fill=tk.X, pady=5)
        self.chaos_header = tk.Label(chaos_frame, text="1. ХАОС (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.chaos_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame1 = tk.Frame(chaos_frame, bg=self.panel_color)
        btn_frame1.pack(fill=tk.X)
        tk.Button(btn_frame1, text="ВКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.send_command("CHAOS_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame1, text="ВЫКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("CHAOS_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        tk.Label(chaos_frame, text="Сила хаоса:", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, pady=(5, 0))
        self.chaos_slider = ttk.Scale(chaos_frame, from_=0.0, to=2.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"STRENGTH:{float(val):.2f}"))
        self.chaos_slider.set(1.0)
        self.chaos_slider.pack(fill=tk.X)

        # --- СЕКЦИЯ: ВЕТЕР ---
        wind_frame = tk.Frame(tab1, bg=self.panel_color, padx=15, pady=10)
        wind_frame.pack(fill=tk.X, pady=5)
        self.wind_header = tk.Label(wind_frame, text="2. ВЕТЕР (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.wind_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame2 = tk.Frame(wind_frame, bg=self.panel_color)
        btn_frame2.pack(fill=tk.X)
        tk.Button(btn_frame2, text="ВКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.send_command("WIND_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame2, text="ВЫКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("WIND_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        tk.Label(wind_frame, text="Сила ветра:", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, pady=(5, 0))
        self.wind_slider = ttk.Scale(wind_frame, from_=0.0, to=3.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"WIND_STRENGTH:{float(val):.2f}"))
        self.wind_slider.set(1.0)
        self.wind_slider.pack(fill=tk.X)
        
        tk.Label(wind_frame, text="Направление ветра (Градусы):", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, pady=(5, 0))
        self.dir_slider = ttk.Scale(wind_frame, from_=0.0, to=360.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"WIND_DIR:{float(val):.2f}"))
        self.dir_slider.set(0.0)
        self.dir_slider.pack(fill=tk.X)

        # --- СЕКЦИЯ: МАГНИТ (ОТТАЛКИВАНИЕ НОТ ОТ КУРСОРА) ---
        magnet_frame = tk.Frame(tab1, bg=self.panel_color, padx=15, pady=10)
        magnet_frame.pack(fill=tk.X, pady=5)
        self.magnet_header = tk.Label(magnet_frame, text="3. МАГНИТ НОТ (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.magnet_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame3 = tk.Frame(magnet_frame, bg=self.panel_color)
        btn_frame3.pack(fill=tk.X)
        tk.Button(btn_frame3, text="ВКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.send_command("MAGNET_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame3, text="ВЫКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("MAGNET_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        tk.Label(magnet_frame, text="Сила отталкивания:", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, pady=(5, 0))
        self.magnet_slider = ttk.Scale(magnet_frame, from_=0.0, to=3.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"MAGNET_STRENGTH:{float(val):.2f}"))
        self.magnet_slider.set(1.0)
        self.magnet_slider.pack(fill=tk.X)

        # --- СЕКЦИЯ: ЧЁРНАЯ ДЫРА (ГРАВИТАЦИЯ НОТ) ---
        bh_frame = tk.Frame(tab1, bg=self.panel_color, padx=15, pady=10)
        bh_frame.pack(fill=tk.X, pady=5)
        self.bh_header = tk.Label(bh_frame, text="4. ЧЁРНАЯ ДЫРА (ВЫКЛЮЧЕНА 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.bh_header.pack(anchor=tk.W, pady=(0, 5))
        tk.Label(bh_frame, text="Притягивает все ноты к центру экрана (256, 192). Искажает геометрию карты!", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 8))

        btn_frame_bh = tk.Frame(bh_frame, bg=self.panel_color)
        btn_frame_bh.pack(fill=tk.X, pady=2)
        tk.Button(btn_frame_bh, text="ВКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_blackout, fg="#11111b", bd=0, command=lambda: self.send_command("BLACK_HOLE_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame_bh, text="ВЫКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("BLACK_HOLE_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        btn_bh_presets = tk.Frame(bh_frame, bg=self.panel_color)
        btn_bh_presets.pack(fill=tk.X, pady=(5, 2))
        tk.Button(btn_bh_presets, text="0.5x (Слабая)", font=("Segoe UI", 8, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.set_bh_strength(0.5)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_bh_presets, text="1.0x (Норма)", font=("Segoe UI", 8, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.set_bh_strength(1.0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_bh_presets, text="2.0x (Сильная)", font=("Segoe UI", 8, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.set_bh_strength(2.0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_bh_presets, text="4.0x (СИНГУЛЯРНОСТЬ)", font=("Segoe UI", 8, "bold"), bg=self.accent_red, fg="#11111b", bd=0, command=lambda: self.set_bh_strength(4.0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        tk.Label(bh_frame, text="Сила гравитации:", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, pady=(5, 0))
        self.bh_slider = ttk.Scale(bh_frame, from_=0.0, to=4.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"BLACK_HOLE_STRENGTH:{float(val):.2f}"))
        self.bh_slider.set(1.0)
        self.bh_slider.pack(fill=tk.X)

        # ==========================================
        # Вкладка 2: КУРСОР (Физика, Лаг, Шизофрения, Ограничения)
        # ==========================================

        # --- СЕКЦИЯ: МАГНИТНОЕ ОТТАЛКИВАНИЕ ОТ НОТ (НОВОЕ В ФАЗЕ 4) ---
        repulsion_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=12)
        repulsion_frame.pack(fill=tk.X, pady=5)
        self.repulsion_header = tk.Label(repulsion_frame, text="ОТТАЛКИВАНИЕ КУРСОРА ОТ НОТ (ВЫКЛЮЧЕНО 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.repulsion_header.pack(anchor=tk.W, pady=(0, 4))
        tk.Label(repulsion_frame, text="Курсор физически отталкивается в сторону при приближении к нотам!", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 6))

        btn_rep = tk.Frame(repulsion_frame, bg=self.panel_color)
        btn_rep.pack(fill=tk.X, pady=2)
        tk.Button(btn_rep, text="ВКЛЮЧИТЬ ОТТАЛКИВАНИЕ 🧲", font=("Segoe UI", 9, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.send_command("REPULSION_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_rep, text="ВЫКЛЮЧИТЬ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("REPULSION_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ТРЯСУЩИЕСЯ РУКИ (ДЖИТТЕР) (НОВОЕ В ФАЗЕ 4) ---
        jitter_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=12)
        jitter_frame.pack(fill=tk.X, pady=5)
        self.jitter_header = tk.Label(jitter_frame, text="ТРЯСУЩИЕСЯ РУКИ (ДЖИТТЕР: 0 px 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.jitter_header.pack(anchor=tk.W, pady=(0, 4))
        tk.Label(jitter_frame, text="Высокочастотная вибрация курсора (эффект дрожания рук от адреналина)", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 6))

        btn_jit_presets = tk.Frame(jitter_frame, bg=self.panel_color)
        btn_jit_presets.pack(fill=tk.X, pady=2)
        tk.Button(btn_jit_presets, text="ВЫКЛ (0)", font=("Segoe UI", 8, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.set_jitter(0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_jit_presets, text="8px (Легкий)", font=("Segoe UI", 8, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.set_jitter(8)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_jit_presets, text="18px (Средний)", font=("Segoe UI", 8, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.set_jitter(18)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_jit_presets, text="35px (ПАНИКА 🫨)", font=("Segoe UI", 8, "bold"), bg=self.accent_red, fg="#11111b", bd=0, command=lambda: self.set_jitter(35)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.jitter_slider = ttk.Scale(jitter_frame, from_=0, to=50, orient=tk.HORIZONTAL, command=self.on_jitter_slider_change)
        self.jitter_slider.set(0)
        self.jitter_slider.pack(fill=tk.X, pady=(6, 2))

        # --- СЕКЦИЯ: ИНПУТ-ЛАГ ---
        lag_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=12)
        lag_frame.pack(fill=tk.X, pady=5)
        self.lag_header = tk.Label(lag_frame, text="ИНПУТ-ЛАГ (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.lag_header.pack(anchor=tk.W, pady=(0, 4))
        tk.Label(lag_frame, text="Физически задерживает координаты и клики. Ломает мышечную память!", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 6))

        btn_lag_row1 = tk.Frame(lag_frame, bg=self.panel_color)
        btn_lag_row1.pack(fill=tk.X, pady=2)
        tk.Button(btn_lag_row1, text="ВЫКЛ (0 ms)", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.set_input_lag(0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_lag_row1, text="50 ms", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.set_input_lag(50)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_lag_row1, text="100 ms", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.set_input_lag(100)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        btn_lag_row2 = tk.Frame(lag_frame, bg=self.panel_color)
        btn_lag_row2.pack(fill=tk.X, pady=2)
        tk.Button(btn_lag_row2, text="200 ms", font=("Segoe UI", 9, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.set_input_lag(200)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_lag_row2, text="300 ms", font=("Segoe UI", 9, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.set_input_lag(300)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_lag_row2, text="500 ms (АД)", font=("Segoe UI", 9, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.set_input_lag(500)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.lag_label = tk.Label(lag_frame, text="Задержка: 0 ms", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color)
        self.lag_label.pack(anchor=tk.W, pady=(6, 0))
        self.lag_slider = ttk.Scale(lag_frame, from_=0, to=500, orient=tk.HORIZONTAL, command=self.on_lag_slider_change)
        self.lag_slider.set(0)
        self.lag_slider.pack(fill=tk.X, pady=(2, 4))

        # --- СЕКЦИЯ: ФЕЙКОВЫЕ КУРСОРЫ (ШИЗОФРЕНИЯ) ---
        cursor_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=12)
        cursor_frame.pack(fill=tk.X, pady=5)
        self.clones_header = tk.Label(cursor_frame, text="ФЕЙКОВЫЕ КУРСОРЫ (ШИЗОФРЕНИЯ)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.clones_header.pack(anchor=tk.W, pady=(0, 4))
        tk.Label(cursor_frame, text="Курсоры-обманки, копирующие клики и сбивающие с толку", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 5))

        btn_fcf_clones = tk.Frame(cursor_frame, bg=self.panel_color)
        btn_fcf_clones.pack(fill=tk.X, pady=2)
        tk.Button(btn_fcf_clones, text="👥 АРМИЯ КЛОНОВ (10 КУРСОРОВ) 👥", font=("Segoe UI", 9, "bold"), bg="#f38ba8", fg="#11111b", bd=0, command=lambda: self.send_command("CLONES_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_fcf_clones, text="ВЫКЛЮЧИТЬ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("CLONES_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        btn_fcf_2 = tk.Frame(cursor_frame, bg=self.panel_color)
        btn_fcf_2.pack(fill=tk.X, pady=2)
        tk.Button(btn_fcf_2, text="ЗЕРКАЛО (X)", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_CURSORS:MIRROR_X")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_fcf_2, text="ЗЕРКАЛО (Y)", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_CURSORS:MIRROR_Y")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        btn_fcf_3 = tk.Frame(cursor_frame, bg=self.panel_color)
        btn_fcf_3.pack(fill=tk.X, pady=2)
        tk.Button(btn_fcf_3, text="ЦЕНТР ЗЕРКАЛО (X+Y)", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_CURSORS:MIRROR_XY")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_fcf_3, text="РОЙ КУРСОРОВ (SWARM)", font=("Segoe UI", 9, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_CURSORS:SWARM")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: НЕВИДИМЫЙ КУРСОР ---
        hide_cursor_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=12)
        hide_cursor_frame.pack(fill=tk.X, pady=5)
        self.hide_cursor_header = tk.Label(hide_cursor_frame, text="НЕВИДИМЫЙ КУРСОР (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.hide_cursor_header.pack(anchor=tk.W, pady=(0, 4))
        tk.Label(hide_cursor_frame, text="Скрывает сам спрайт курсора, оставляя только след", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 5))
        
        btn_hide_cursor = tk.Frame(hide_cursor_frame, bg=self.panel_color)
        btn_hide_cursor.pack(fill=tk.X, pady=2)
        tk.Button(btn_hide_cursor, text="СКРЫТЬ КУРСОР", font=("Segoe UI", 9, "bold"), bg=self.accent_red, fg="#11111b", bd=0, command=lambda: self.send_command("HIDE_CURSOR:ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_hide_cursor, text="ВЕРНУТЬ КУРСОР", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("HIDE_CURSOR:OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: КОЛЕСИКО ЗАГРУЗКИ (BUSY CURSOR) (ФАЗА 5) ---
        busy_cursor_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=12)
        busy_cursor_frame.pack(fill=tk.X, pady=5)
        self.busy_cursor_header = tk.Label(busy_cursor_frame, text="КОЛЁСИКО ЗАГРУЗКИ (BUSY CURSOR ⏳)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.busy_cursor_header.pack(anchor=tk.W, pady=(0, 4))
        tk.Label(busy_cursor_frame, text="Вращающийся синий спиннер прямо на кончике курсора!", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 5))
        
        btn_busy = tk.Frame(busy_cursor_frame, bg=self.panel_color)
        btn_busy.pack(fill=tk.X, pady=2)
        tk.Button(btn_busy, text="ВКЛЮЧИТЬ СПИННЕР ⏳", font=("Segoe UI", 9, "bold"), bg="#89dceb", fg="#11111b", bd=0, command=lambda: self.send_command("BUSY_CURSOR_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_busy, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("BUSY_CURSOR_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: РАЗМЕР КУРСОРА ---
        scale_cursor_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=12)
        scale_cursor_frame.pack(fill=tk.X, pady=5)
        self.cursor_scale_header = tk.Label(scale_cursor_frame, text="РАЗМЕР КУРСОРА (1.0x)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.cursor_scale_header.pack(anchor=tk.W, pady=(0, 4))

        btn_cscale_row = tk.Frame(scale_cursor_frame, bg=self.panel_color)
        btn_cscale_row.pack(fill=tk.X, pady=2)
        tk.Button(btn_cscale_row, text="0.2x (Микро)", font=("Segoe UI", 9, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(0.2)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cscale_row, text="0.5x", font=("Segoe UI", 9, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(0.5)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cscale_row, text="1.0x (Норма)", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(1.0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cscale_row, text="2.0x", font=("Segoe UI", 9, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(2.0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cscale_row, text="4.0x (Гигант)", font=("Segoe UI", 9, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(4.0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_cscale = tk.Frame(scale_cursor_frame, bg=self.panel_color)
        row_cscale.pack(fill=tk.X, pady=(6, 0))
        self.cursor_scale_slider = ttk.Scale(row_cscale, from_=0.1, to=5.0, orient=tk.HORIZONTAL, command=self.on_cursor_scale_change)
        self.cursor_scale_slider.set(1.0)
        self.cursor_scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row_cscale, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.set_cursor_scale(1.0)).pack(side=tk.RIGHT, padx=(5, 0))

        # --- СЕКЦИЯ: ИНВЕРСИЯ УПРАВЛЕНИЯ (X / Y) ---
        invert_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=12)
        invert_frame.pack(fill=tk.X, pady=5)
        self.invert_header = tk.Label(invert_frame, text="ИНВЕРСИЯ ОСЕЙ (ВЫКЛЮЧЕНА 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.invert_header.pack(anchor=tk.W, pady=(0, 4))

        row_inv_x = tk.Frame(invert_frame, bg=self.panel_color)
        row_inv_x.pack(fill=tk.X, pady=2)
        tk.Label(row_inv_x, text="Ось X (Горизонталь):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=20, anchor=tk.W).pack(side=tk.LEFT)
        self.btn_inv_x_on = tk.Button(row_inv_x, text="ИНВЕРСИЯ X", font=("Segoe UI", 9, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.send_command("INVERT_X_ON"))
        self.btn_inv_x_on.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.btn_inv_x_off = tk.Button(row_inv_x, text="НОРМА X", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("INVERT_X_OFF"))
        self.btn_inv_x_off.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_inv_y = tk.Frame(invert_frame, bg=self.panel_color)
        row_inv_y.pack(fill=tk.X, pady=2)
        tk.Label(row_inv_y, text="Ось Y (Вертикаль):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=20, anchor=tk.W).pack(side=tk.LEFT)
        self.btn_inv_y_on = tk.Button(row_inv_y, text="ИНВЕРСИЯ Y", font=("Segoe UI", 9, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.send_command("INVERT_Y_ON"))
        self.btn_inv_y_on.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        self.btn_inv_y_off = tk.Button(row_inv_y, text="НОРМА Y", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("INVERT_Y_OFF"))
        self.btn_inv_y_off.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_inv_all = tk.Frame(invert_frame, bg=self.panel_color)
        row_inv_all.pack(fill=tk.X, pady=(6, 2))
        tk.Button(row_inv_all, text="ИНВЕРТИРОВАТЬ ОБЕ ОСИ (X + Y)", font=("Segoe UI", 9, "bold"), bg="#fab387", fg="#11111b", bd=0, command=lambda: [self.send_command("INVERT_X_ON"), self.send_command("INVERT_Y_ON")]).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_inv_all, text="СБРОС В НОРМУ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("INVERT_RESET")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ЗАЛИПАНИЕ КНОПКИ (KEY JAM) ---
        jam_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=12)
        jam_frame.pack(fill=tk.X, pady=5)
        self.jam_header = tk.Label(jam_frame, text="ЗАЛИПАНИЕ КЛАВИШ (K1 / K2)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.jam_header.pack(anchor=tk.W, pady=(0, 4))

        row_jam_k1 = tk.Frame(jam_frame, bg=self.panel_color)
        row_jam_k1.pack(fill=tk.X, pady=2)
        self.lbl_k1 = tk.Label(row_jam_k1, text="Клавиша K1 (Левая):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=20, anchor=tk.W)
        self.lbl_k1.pack(side=tk.LEFT)
        tk.Button(row_jam_k1, text="ЗАЛИПЛА (БЛОК) ⚠️", font=("Segoe UI", 9, "bold"), bg=self.accent_red, fg="#11111b", bd=0, command=lambda: self.send_command("JAM_K1_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_jam_k1, text="РАБОТАЕТ ✅", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("JAM_K1_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_jam_k2 = tk.Frame(jam_frame, bg=self.panel_color)
        row_jam_k2.pack(fill=tk.X, pady=2)
        self.lbl_k2 = tk.Label(row_jam_k2, text="Клавиша K2 (Правая):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=20, anchor=tk.W)
        self.lbl_k2.pack(side=tk.LEFT)
        tk.Button(row_jam_k2, text="ЗАЛИПЛА (БЛОК) ⚠️", font=("Segoe UI", 9, "bold"), bg=self.accent_red, fg="#11111b", bd=0, command=lambda: self.send_command("JAM_K2_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_jam_k2, text="РАБОТАЕТ ✅", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("JAM_K2_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_jam_all = tk.Frame(jam_frame, bg=self.panel_color)
        row_jam_all.pack(fill=tk.X, pady=(6, 2))
        tk.Button(row_jam_all, text="РАЗБЛОКИРОВАТЬ ОБЕ КЛАВИШИ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("JAM_RESET")).pack(fill=tk.X, expand=True, padx=2)

        # ==========================================
        # Вкладка 3: ИСКАЖЕНИЯ (Камера, Туннель, Звук, Масштаб)
        # ==========================================

        # --- СЕКЦИЯ: ПЬЯНАЯ КАМЕРА & ТРЯСКА ЭКРАНА (НОВОЕ В ФАЗЕ 4) ---
        cam_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=12)
        cam_frame.pack(fill=tk.X, pady=5)
        self.cam_header = tk.Label(cam_frame, text="ПЬЯНАЯ КАМЕРА & ТРЯСКА ЭКРАНА", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.cam_header.pack(anchor=tk.W, pady=(0, 4))

        row_drunk = tk.Frame(cam_frame, bg=self.panel_color)
        row_drunk.pack(fill=tk.X, pady=2)
        self.lbl_drunk = tk.Label(row_drunk, text="Пьяная камера (Качка ±15°):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W)
        self.lbl_drunk.pack(side=tk.LEFT)
        tk.Button(row_drunk, text="ВКЛЮЧИТЬ 🍾", font=("Segoe UI", 9, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.send_command("DRUNK_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_drunk, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("DRUNK_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_shake = tk.Frame(cam_frame, bg=self.panel_color)
        row_shake.pack(fill=tk.X, pady=2)
        self.lbl_shake = tk.Label(row_shake, text="Тряска экрана (Землетряс):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W)
        self.lbl_shake.pack(side=tk.LEFT)
        tk.Button(row_shake, text="ВКЛЮЧИТЬ 🌋", font=("Segoe UI", 9, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.send_command("SHAKE_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_shake, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("SHAKE_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Фаза 5: Бочка 360° и Троттлинг 15 FPS
        row_barrel = tk.Frame(cam_frame, bg=self.panel_color)
        row_barrel.pack(fill=tk.X, pady=2)
        tk.Button(row_barrel, text="🌀 БОЧКА / ВРАЩЕНИЕ ЭКРАНА 360° (3.5s) 🔄", font=("Segoe UI", 9, "bold"), bg="#cba6f7", fg="#11111b", bd=0, command=lambda: self.send_command("BARREL_ROLL")).pack(fill=tk.X, expand=True, padx=2)

        # Управление FPS игрока (Фаза 5)
        fps_frame = tk.Frame(cam_frame, bg=self.bg_color, padx=10, pady=8, bd=1, relief=tk.SOLID)
        fps_frame.pack(fill=tk.X, pady=(6, 2))
        
        fps_top = tk.Frame(fps_frame, bg=self.bg_color)
        fps_top.pack(fill=tk.X)
        tk.Label(fps_top, text="⏱️ ОГРАНИЧЕНИЕ FPS ИГРОКА 🎮:", font=("Segoe UI", 9, "bold"), bg=self.bg_color, fg=self.accent_earth).pack(side=tk.LEFT)
        self.fps_status_lbl = tk.Label(fps_top, text="Без ограничений", font=("Segoe UI", 9, "bold"), bg=self.bg_color, fg=self.accent_off)
        self.fps_status_lbl.pack(side=tk.RIGHT)
        
        # Пресеты: 15, 30, 60, 120, 240, Сброс
        fps_btn_row1 = tk.Frame(fps_frame, bg=self.bg_color)
        fps_btn_row1.pack(fill=tk.X, pady=(6, 2))
        tk.Button(fps_btn_row1, text="15 FPS", font=("Segoe UI", 9, "bold"), bg="#fab387", fg="#11111b", bd=0, command=lambda: self.set_fps_target(15)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(fps_btn_row1, text="30 FPS", font=("Segoe UI", 9, "bold"), bg="#f9e2af", fg="#11111b", bd=0, command=lambda: self.set_fps_target(30)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(fps_btn_row1, text="60 FPS", font=("Segoe UI", 9, "bold"), bg="#a6e3a1", fg="#11111b", bd=0, command=lambda: self.set_fps_target(60)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        
        fps_btn_row2 = tk.Frame(fps_frame, bg=self.bg_color)
        fps_btn_row2.pack(fill=tk.X, pady=(2, 4))
        tk.Button(fps_btn_row2, text="120 FPS", font=("Segoe UI", 9, "bold"), bg="#89dceb", fg="#11111b", bd=0, command=lambda: self.set_fps_target(120)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(fps_btn_row2, text="240 FPS", font=("Segoe UI", 9, "bold"), bg="#89b4fa", fg="#11111b", bd=0, command=lambda: self.set_fps_target(240)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        tk.Button(fps_btn_row2, text="СБРОС ♾️", font=("Segoe UI", 9, "bold"), bg="#b4befe", fg="#11111b", bd=0, command=lambda: self.set_fps_target(0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=1)
        
        # Слайдер точной настройки FPS (10 - 240)
        fps_slider_row = tk.Frame(fps_frame, bg=self.bg_color)
        fps_slider_row.pack(fill=tk.X, pady=(4, 0))
        self.fps_slider = ttk.Scale(fps_slider_row, from_=10, to=240, value=60, orient=tk.HORIZONTAL, command=self.on_fps_slider_change)
        self.fps_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        tk.Button(fps_slider_row, text="Применить", font=("Segoe UI", 8, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=self.apply_fps_slider).pack(side=tk.RIGHT)

        # --- СЕКЦИЯ: ВИЗУАЛЬНЫЙ АД & НОТЫ (ФАЗА 5) ---
        vis_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=12)
        vis_frame.pack(fill=tk.X, pady=5)
        self.vis_header = tk.Label(vis_frame, text="ВИЗУАЛЬНЫЙ АД & ХАОС НОТ (ФАЗА 5) 👁️", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.vis_header.pack(anchor=tk.W, pady=(0, 4))

        row_cs_chaos = tk.Frame(vis_frame, bg=self.panel_color)
        row_cs_chaos.pack(fill=tk.X, pady=2)
        tk.Label(row_cs_chaos, text="Гигантизм vs Микро-ноты (CS):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W).pack(side=tk.LEFT)
        tk.Button(row_cs_chaos, text="ХАОС РАЗМЕРОВ 🎯", font=("Segoe UI", 9, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.send_command("CS_CHAOS_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_cs_chaos, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("CS_CHAOS_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_mosaic = tk.Frame(vis_frame, bg=self.panel_color)
        row_mosaic.pack(fill=tk.X, pady=2)
        tk.Label(row_mosaic, text="Эффект 144p (Мозаика):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W).pack(side=tk.LEFT)
        tk.Button(row_mosaic, text="144p РЕЖИМ 🔲", font=("Segoe UI", 9, "bold"), bg="#89dceb", fg="#11111b", bd=0, command=lambda: self.send_command("MOSAIC_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_mosaic, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("MOSAIC_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_invert = tk.Frame(vis_frame, bg=self.panel_color)
        row_invert.pack(fill=tk.X, pady=2)
        tk.Label(row_invert, text="Инверсия цветов (Негатив):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W).pack(side=tk.LEFT)
        tk.Button(row_invert, text="НЕГАТИВ 🌗", font=("Segoe UI", 9, "bold"), bg="#f9e2af", fg="#11111b", bd=0, command=lambda: self.send_command("INVERT_COLORS_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_invert, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("INVERT_COLORS_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ТУННЕЛЬНОЕ ЗРЕНИЕ & НЕВИДИМЫЕ СЛАЙДЕРЫ (НОВОЕ В ФАЗЕ 4) ---
        tunnel_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=12)
        tunnel_frame.pack(fill=tk.X, pady=5)
        self.tunnel_header = tk.Label(tunnel_frame, text="ТУННЕЛЬНОЕ ЗРЕНИЕ & НЕВИДИМЫЕ СЛАЙДЕРЫ", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.tunnel_header.pack(anchor=tk.W, pady=(0, 4))

        row_tunnel = tk.Frame(tunnel_frame, bg=self.panel_color)
        row_tunnel.pack(fill=tk.X, pady=2)
        self.lbl_tunnel = tk.Label(row_tunnel, text="Туннельное зрение (Фонарик):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W)
        self.lbl_tunnel.pack(side=tk.LEFT)
        tk.Button(row_tunnel, text="ВКЛЮЧИТЬ 🔦", font=("Segoe UI", 9, "bold"), bg=self.accent_cyan, fg="#11111b", bd=0, command=lambda: self.send_command("TUNNEL_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_tunnel, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("TUNNEL_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_ghost = tk.Frame(tunnel_frame, bg=self.panel_color)
        row_ghost.pack(fill=tk.X, pady=2)
        self.lbl_ghost = tk.Label(row_ghost, text="Невидимка-слайдеры (Тела):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W)
        self.lbl_ghost.pack(side=tk.LEFT)
        tk.Button(row_ghost, text="ВКЛЮЧИТЬ 👻", font=("Segoe UI", 9, "bold"), bg=self.accent_purple, fg="#11111b", bd=0, command=lambda: self.send_command("GHOST_SLIDERS_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_ghost, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("GHOST_SLIDERS_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ЗВУКОВЫЕ ЭФФЕКТЫ (AUDIO HAVOC) (ФАЗА 4 + ФАЗА 5) ---
        audio_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=12)
        audio_frame.pack(fill=tk.X, pady=5)
        self.audio_header = tk.Label(audio_frame, text="ЗВУКОВЫЕ ЭФФЕКТЫ (AUDIO HAVOC)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.audio_header.pack(anchor=tk.W, pady=(0, 4))

        row_muffled = tk.Frame(audio_frame, bg=self.panel_color)
        row_muffled.pack(fill=tk.X, pady=2)
        self.lbl_muffled = tk.Label(row_muffled, text="Звук под водой (Low-Pass):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W)
        self.lbl_muffled.pack(side=tk.LEFT)
        tk.Button(row_muffled, text="ПОД ВОДУ 🌊", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.send_command("MUFFLED_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_muffled, text="НОРМА", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("MUFFLED_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_pan = tk.Frame(audio_frame, bg=self.panel_color)
        row_pan.pack(fill=tk.X, pady=2)
        self.lbl_pan = tk.Label(row_pan, text="8D Панорама (Вращение):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W)
        self.lbl_pan.pack(side=tk.LEFT)
        tk.Button(row_pan, text="ВКЛЮЧИТЬ 8D 🎧", font=("Segoe UI", 9, "bold"), bg="#f5c2e7", fg="#11111b", bd=0, command=lambda: self.send_command("PAN_SPIN_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_pan, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("PAN_SPIN_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # Фаза 5: Остановка винила (Tape Stop) и Эхо в соборе (Reverb)
        row_tape = tk.Frame(audio_frame, bg=self.panel_color)
        row_tape.pack(fill=tk.X, pady=2)
        tk.Button(row_tape, text="📼 ЗАЖЕВАЛО ПЛЕНКУ / ОСТАНОВКА ВИНИЛА (TAPE STOP) 🛑", font=("Segoe UI", 9, "bold"), bg="#fab387", fg="#11111b", bd=0, command=lambda: self.send_command("TAPE_STOP")).pack(fill=tk.X, expand=True, padx=2)

        row_reverb = tk.Frame(audio_frame, bg=self.panel_color)
        row_reverb.pack(fill=tk.X, pady=2)
        self.lbl_reverb = tk.Label(row_reverb, text="Эхо в соборе (Reverb):", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=26, anchor=tk.W)
        self.lbl_reverb.pack(side=tk.LEFT)
        tk.Button(row_reverb, text="ВКЛЮЧИТЬ ЭХО ⛪", font=("Segoe UI", 9, "bold"), bg="#cba6f7", fg="#11111b", bd=0, command=lambda: self.send_command("REVERB_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_reverb, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("REVERB_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ЗЕМЛЕТРЯСЕНИЕ (СЛАЙДЕР СИЛЫ) ---
        earth_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=10)
        earth_frame.pack(fill=tk.X, pady=5)
        self.earth_header = tk.Label(earth_frame, text="ЗЕМЛЕТРЯСЕНИЕ ИНТЕРФЕЙСА (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.earth_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame4 = tk.Frame(earth_frame, bg=self.panel_color)
        btn_frame4.pack(fill=tk.X)
        tk.Button(btn_frame4, text="ВКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.send_command("EARTHQUAKE_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame4, text="ВЫКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("EARTHQUAKE_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        tk.Label(earth_frame, text="Магнитуда землетрясения:", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, pady=(5, 0))
        self.earth_slider = ttk.Scale(earth_frame, from_=0.0, to=3.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"EARTHQUAKE_STRENGTH:{float(val):.2f}"))
        self.earth_slider.set(1.0)
        self.earth_slider.pack(fill=tk.X)

        # --- СЕКЦИЯ: СЛЕПОТА (Hidden) ---
        hidden_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=10)
        hidden_frame.pack(fill=tk.X, pady=5)
        self.hidden_header = tk.Label(hidden_frame, text="СЛЕПОТА (Hidden) (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.hidden_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame_hidden = tk.Frame(hidden_frame, bg=self.panel_color)
        btn_frame_hidden.pack(fill=tk.X)
        tk.Button(btn_frame_hidden, text="ВКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.send_command("HIDDEN_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame_hidden, text="ВЫКЛЮЧИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("HIDDEN_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ОТЗЕРКАЛИВАНИЕ ---
        mirror_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=10)
        mirror_frame.pack(fill=tk.X, pady=5)
        self.mirror_header = tk.Label(mirror_frame, text="ОТЗЕРКАЛИВАНИЕ", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.mirror_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame_mirror_x = tk.Frame(mirror_frame, bg=self.panel_color)
        btn_frame_mirror_x.pack(fill=tk.X, pady=2)
        tk.Button(btn_frame_mirror_x, text="ПОЛЕ ОСЬ X 🔛", font=("Segoe UI", 9, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.send_command("MIRROR_PLAYFIELD_X_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame_mirror_x, text="СБРОС ПОЛЯ X", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("MIRROR_PLAYFIELD_X_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        btn_frame_mirror_y = tk.Frame(mirror_frame, bg=self.panel_color)
        btn_frame_mirror_y.pack(fill=tk.X, pady=2)
        tk.Button(btn_frame_mirror_y, text="ПОЛЕ ОСЬ Y ↕️", font=("Segoe UI", 9, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.send_command("MIRROR_PLAYFIELD_Y_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame_mirror_y, text="СБРОС ПОЛЯ Y", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("MIRROR_PLAYFIELD_Y_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        btn_frame_mirror_hud = tk.Frame(mirror_frame, bg=self.panel_color)
        btn_frame_mirror_hud.pack(fill=tk.X, pady=2)
        tk.Button(btn_frame_mirror_hud, text="HUD ОСЬ X 🔛", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.send_command("MIRROR_HUD_X_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame_mirror_hud, text="СБРОС HUD X", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("MIRROR_HUD_X_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ИСКАЖЕНИЕ (Масштаб) ---
        scale_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=10)
        scale_frame.pack(fill=tk.X, pady=5)
        self.scale_header = tk.Label(scale_frame, text="ИСКАЖЕНИЕ МАСШТАБА", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.scale_header.pack(anchor=tk.W, pady=(0, 5))
        
        tk.Label(scale_frame, text="Игровое поле (Общий масштаб):", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W)
        row1 = tk.Frame(scale_frame, bg=self.panel_color)
        row1.pack(fill=tk.X, pady=(0, 5))
        self.scale_slider = ttk.Scale(row1, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"SCALE:{float(val):.2f}"))
        self.scale_slider.set(1.0)
        self.scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row1, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.scale_slider.set(1.0)).pack(side=tk.RIGHT, padx=(5, 0))

        tk.Label(scale_frame, text="Интерфейс (HUD) (Общий масштаб):", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W)
        row2 = tk.Frame(scale_frame, bg=self.panel_color)
        row2.pack(fill=tk.X, pady=(0, 5))
        self.hud_scale_slider = ttk.Scale(row2, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"HUD_SCALE:{float(val):.2f}"))
        self.hud_scale_slider.set(1.0)
        self.hud_scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row2, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.hud_scale_slider.set(1.0)).pack(side=tk.RIGHT, padx=(5, 0))

        # --- СЕКЦИЯ: УСКОРЕНИЕ ВРЕМЕНИ (Speed Rate) ---
        speed_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=10)
        speed_frame.pack(fill=tk.X, pady=5)
        self.speed_header = tk.Label(speed_frame, text="СКОРОСТЬ ИГРЫ (Time Rate)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.speed_header.pack(anchor=tk.W, pady=(0, 5))
        
        tk.Label(speed_frame, text="Множитель скорости:", font=("Segoe UI", 9), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W)
        row_speed = tk.Frame(speed_frame, bg=self.panel_color)
        row_speed.pack(fill=tk.X, pady=(0, 5))
        self.speed_slider = ttk.Scale(row_speed, from_=0.1, to=2.5, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"SPEED:{float(val):.2f}"))
        self.speed_slider.set(1.0)
        self.speed_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row_speed, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.speed_slider.set(1.0)).pack(side=tk.RIGHT, padx=(5, 0))

        self.pitch_var = tk.IntVar()
        self.pitch_checkbox = tk.Checkbutton(speed_frame, text="Эффект бурундука (изменять тональность)", variable=self.pitch_var, bg=self.panel_color, fg=self.text_color, selectcolor=self.bg_color, activebackground=self.panel_color, activeforeground=self.text_color, command=lambda: self.send_command("PITCH_ON" if self.pitch_var.get() else "PITCH_OFF"))
        self.pitch_checkbox.pack(anchor=tk.W, pady=(5,0))

        # --- СЕКЦИЯ: РАССИНХРОН ЗВУКА (Audio Desync) ---
        desync_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=10)
        desync_frame.pack(fill=tk.X, pady=5)
        self.desync_header = tk.Label(desync_frame, text="РАССИНХРОН ЗВУКА (0 ms 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.desync_header.pack(anchor=tk.W, pady=(0, 5))
        tk.Label(desync_frame, text="Сдвигает аудио относительно карты. Ломает чувство ритма!", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 8))

        btn_desync_row1 = tk.Frame(desync_frame, bg=self.panel_color)
        btn_desync_row1.pack(fill=tk.X, pady=2)
        tk.Button(btn_desync_row1, text="-150 ms (Спешит)", font=("Segoe UI", 8, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.set_audio_desync(-150)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_desync_row1, text="-75 ms", font=("Segoe UI", 8, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.set_audio_desync(-75)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_desync_row1, text="0 ms (Синхрон)", font=("Segoe UI", 8, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.set_audio_desync(0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_desync_row1, text="+75 ms", font=("Segoe UI", 8, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.set_audio_desync(75)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_desync_row1, text="+150 ms (Отстает)", font=("Segoe UI", 8, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.set_audio_desync(150)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_desync_slider = tk.Frame(desync_frame, bg=self.panel_color)
        row_desync_slider.pack(fill=tk.X, pady=(6, 0))
        self.desync_slider = ttk.Scale(row_desync_slider, from_=-300, to=300, orient=tk.HORIZONTAL, command=self.on_desync_slider_change)
        self.desync_slider.set(0)
        self.desync_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row_desync_slider, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.set_audio_desync(0)).pack(side=tk.RIGHT, padx=(5, 0))

        # --- СЕКЦИЯ: ХАМЕЛЕОН (ПОДМЕНА НОТ И ЦВЕТОВ) ---
        cham_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=10)
        cham_frame.pack(fill=tk.X, pady=5)
        self.cham_header = tk.Label(cham_frame, text="ХАМЕЛЕОН (ОБЫЧНЫЕ ЦВЕТА 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.cham_header.pack(anchor=tk.W, pady=(0, 5))

        btn_cham_row = tk.Frame(cham_frame, bg=self.panel_color)
        btn_cham_row.pack(fill=tk.X, pady=2)
        tk.Button(btn_cham_row, text="ОБЫЧНЫЕ (ВЫКЛ)", font=("Segoe UI", 8, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("CHAMELEON_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cham_row, text="ЧЕРНЫЕ (Стелс 🥷)", font=("Segoe UI", 8, "bold"), bg="#11111b", fg="#cdd6f4", bd=0, command=lambda: self.send_command("CHAMELEON_BLACK")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cham_row, text="РАДУГА (Диско 🌈)", font=("Segoe UI", 8, "bold"), bg="#f5c2e7", fg="#11111b", bd=0, command=lambda: self.send_command("CHAMELEON_RAINBOW")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cham_row, text="МОНОХРОМ (⚪)", font=("Segoe UI", 8, "bold"), bg="#a6adc8", fg="#11111b", bd=0, command=lambda: self.send_command("CHAMELEON_MONO")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # ==========================================
        # Вкладка 4: ИВЕНТЫ & СИСТЕМНЫЙ ТРОЛЛИНГ
        # ==========================================

        # --- СЕКЦИЯ: БЛЭКАУТ (Остановка времени) ---
        blackout_frame = tk.Frame(tab3, bg=self.panel_color, padx=15, pady=10)
        blackout_frame.pack(fill=tk.X, pady=5)
        self.blackout_header = tk.Label(blackout_frame, text="5. БЛЭКАУТ (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.blackout_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame5 = tk.Frame(blackout_frame, bg=self.panel_color)
        btn_frame5.pack(fill=tk.X)
        tk.Button(btn_frame5, text="ОСТАНОВИТЬ ВРЕМЯ", font=("Segoe UI", 10, "bold"), bg=self.accent_blackout, fg="#11111b", bd=0, command=lambda: self.send_command("FREEZE_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame5, text="ВОССТАНОВИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("FREEZE_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ВНЕЗАПНЫЕ ИВЕНТЫ ---
        screamer_frame = tk.Frame(tab3, bg=self.panel_color, padx=15, pady=10)
        screamer_frame.pack(fill=tk.X, pady=5)
        self.screamer_header = tk.Label(screamer_frame, text="6. ВНЕЗАПНЫЕ ИВЕНТЫ 🎭", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.screamer_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame6 = tk.Frame(screamer_frame, bg=self.panel_color)
        btn_frame6.pack(fill=tk.X, pady=(0, 5))
        tk.Button(btn_frame6, text="ПОЦЕЛУЙ 💋", font=("Segoe UI", 10, "bold"), bg="#ff7eb3", fg="#11111b", bd=0, command=lambda: self.send_command("KISS")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame6, text="ФЕЙКОВЫЙ МИСС ❌", font=("Segoe UI", 10, "bold"), bg="#f38ba8", fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_MISS")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        btn_frame_flash = tk.Frame(screamer_frame, bg=self.panel_color)
        btn_frame_flash.pack(fill=tk.X)
        tk.Button(btn_frame_flash, text="FLASHBANG 💥", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#11111b", bd=0, command=lambda: self.send_command("FLASHBANG")).pack(fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ТРОЛЛИНГ И СИСТЕМНЫЕ СБОИ (ФАЗА 3 + ФАЗА 4) ---
        troll_frame = tk.Frame(tab3, bg=self.panel_color, padx=15, pady=12)
        troll_frame.pack(fill=tk.X, pady=5)
        self.troll_header = tk.Label(troll_frame, text="7. СИСТЕМНЫЙ ТРОЛЛИНГ & ОБМАНКИ 🪟", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.troll_header.pack(anchor=tk.W, pady=(0, 4))
        tk.Label(troll_frame, text="Окна Windows, звуки железа, сбои мыши и донаты со звуком", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 8))

        # Ряд 1: Отключение мыши (Фаза 4)
        row_disconnect = tk.Frame(troll_frame, bg=self.panel_color)
        row_disconnect.pack(fill=tk.X, pady=2)
        tk.Button(row_disconnect, text="🔌 ОТКЛЮЧЕНИЕ МЫШИ (1.8s + Звук извлечения) 🖱️", font=("Segoe UI", 9, "bold"), bg="#f38ba8", fg="#11111b", bd=0, command=lambda: self.send_command("DEVICE_DISCONNECT")).pack(fill=tk.X, expand=True, padx=2)

        # Ряд 2: Экран обновления Windows (Фаза 4)
        row_update = tk.Frame(troll_frame, bg=self.panel_color)
        row_update.pack(fill=tk.X, pady=2)
        tk.Button(row_update, text="🔄 ОБНОВЛЕНИЕ WINDOWS (Пауза 3.5s + Спиннер) ⚙️", font=("Segoe UI", 9, "bold"), bg="#005a9e", fg="#ffffff", bd=0, command=lambda: self.send_command("TROLL:UPDATE")).pack(fill=tk.X, expand=True, padx=2)

        # Ряд 3: BSOD на весь экран
        row_troll_3 = tk.Frame(troll_frame, bg=self.panel_color)
        row_troll_3.pack(fill=tk.X, pady=2)
        tk.Button(row_troll_3, text="💻 СИНИЙ ЭКРАН СМЕРТИ (BSOD НА ВЕСЬ ЭКРАН) 💥", font=("Segoe UI", 9, "bold"), bg="#0078d7", fg="#ffffff", bd=0, command=lambda: self.send_command("TROLL:BSOD")).pack(fill=tk.X, expand=True, padx=2)

        # Ряд 4: Донат от Папича + Залипание клавиш (Фаза 4)
        row_p4_alerts = tk.Frame(troll_frame, bg=self.panel_color)
        row_p4_alerts.pack(fill=tk.X, pady=2)
        tk.Button(row_p4_alerts, text="💰 ДОНАТ ОТ ПАПИЧА (5000₽) 👑", font=("Segoe UI", 9, "bold"), bg="#fab387", fg="#11111b", bd=0, command=lambda: self.send_command("TROLL:DONATE")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_p4_alerts, text="⌨️ ЗАЛИПАНИЕ КЛАВИШ ⚠️", font=("Segoe UI", 9, "bold"), bg="#cba6f7", fg="#11111b", bd=0, command=lambda: self.send_command("TROLL:STICKYKEYS")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # Ряд 5: Отвал видеокарты / Глитч (Фаза 4)
        row_glitch = tk.Frame(troll_frame, bg=self.panel_color)
        row_glitch.pack(fill=tk.X, pady=2)
        tk.Button(row_glitch, text="📺 ОТВАЛ ВИДЕОКАРТЫ / МАТРИЧНЫЙ ГЛИТЧ ⚡", font=("Segoe UI", 9, "bold"), bg="#eba0ac", fg="#11111b", bd=0, command=lambda: self.send_command("TROLL:GLITCH")).pack(fill=tk.X, expand=True, padx=2)


        # Ряд 6: Батарея + Defender
        row_troll_1 = tk.Frame(troll_frame, bg=self.panel_color)
        row_troll_1.pack(fill=tk.X, pady=2)
        tk.Button(row_troll_1, text="БАТАРЕЯ 5% 🔋", font=("Segoe UI", 9, "bold"), bg="#f38ba8", fg="#11111b", bd=0, command=lambda: self.send_command("TROLL:BATTERY")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_troll_1, text="УГРОЗА DEFENDER 🛡️", font=("Segoe UI", 9, "bold"), bg="#fab387", fg="#11111b", bd=0, command=lambda: self.send_command("TROLL:DEFENDER")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # Ряд 7: Discord
        row_troll_2 = tk.Frame(troll_frame, bg=self.panel_color)
        row_troll_2.pack(fill=tk.X, pady=2)
        tk.Button(row_troll_2, text="ВХОДЯЩИЙ DISCORD 📞", font=("Segoe UI", 9, "bold"), bg="#5865F2", fg="#ffffff", bd=0, command=lambda: self.send_command("TROLL:DISCORD")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_troll_2, text="ДИСКОРД (ТОЛЬКО ЗВУК) 🔊", font=("Segoe UI", 9, "bold"), bg="#7289da", fg="#ffffff", bd=0, command=lambda: self.send_command("TROLL:DISCORD_AUDIO")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # Ряд 8: Telegram от Мамули (Фаза 5)
        row_troll_tg = tk.Frame(troll_frame, bg=self.panel_color)
        row_troll_tg.pack(fill=tk.X, pady=2)
        tk.Button(row_troll_tg, text="ЗВОНОК TELEGRAM (МАМУЛЯ ❤️) 📱", font=("Segoe UI", 9, "bold"), bg="#29b6f6", fg="#11111b", bd=0, command=lambda: self.send_command("TROLL:TELEGRAM")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_troll_tg, text="ТЕЛЕГРАМ (ТОЛЬКО ЗВУК) 🔔", font=("Segoe UI", 9, "bold"), bg="#0288d1", fg="#ffffff", bd=0, command=lambda: self.send_command("TROLL:TELEGRAM_AUDIO")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # Ряд 9: Steam + Водяной знак Windows (Фаза 5)
        row_troll_steam = tk.Frame(troll_frame, bg=self.panel_color)
        row_troll_steam.pack(fill=tk.X, pady=2)
        tk.Button(row_troll_steam, text="💬 STEAM СООБЩЕНИЕ (Сотка на шаурму) 🎮", font=("Segoe UI", 9, "bold"), bg="#1b2838", fg="#66c0f4", bd=0, command=lambda: self.send_command("TROLL:STEAM")).pack(fill=tk.X, expand=True, padx=2)

        row_watermark = tk.Frame(troll_frame, bg=self.panel_color)
        row_watermark.pack(fill=tk.X, pady=2)
        tk.Label(row_watermark, text="Водяной знак Активация Windows:", font=("Segoe UI", 9, "bold"), bg=self.panel_color, fg=self.text_color, width=30, anchor=tk.W).pack(side=tk.LEFT)
        tk.Button(row_watermark, text="ВКЛЮЧИТЬ", font=("Segoe UI", 9, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.send_command("WATERMARK_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_watermark, text="ВЫКЛ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("WATERMARK_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # ==========================================
        # Вкладка 5: ГАЛЛЮЦИНАЦИИ
        # ==========================================
        hal_frame = tk.Frame(tab4, bg=self.panel_color, padx=15, pady=15)
        hal_frame.pack(fill=tk.X, pady=5)
        tk.Label(hal_frame, text="РАДАР ФЕЙКОВЫХ НОТ", font=("Segoe UI", 12, "bold"), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, pady=(0, 10))
        tk.Label(hal_frame, text="Кликайте по радару, чтобы заспавнить фейковую ноту на экране игрока.", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 10))

        # Холст радара
        canvas_width = 512
        canvas_height = 384
        
        canvas_container = tk.Frame(hal_frame, bg=self.panel_color)
        canvas_container.pack(fill=tk.BOTH, expand=True)

        self.radar_canvas = tk.Canvas(canvas_container, width=canvas_width, height=canvas_height, bg="#1e1e2e", highlightthickness=1, highlightbackground=self.accent_blue)
        self.radar_canvas.pack(pady=10)

        for i in range(0, canvas_width, 64):
            self.radar_canvas.create_line(i, 0, i, canvas_height, fill="#313244", dash=(2, 2))
        for i in range(0, canvas_height, 64):
            self.radar_canvas.create_line(0, i, canvas_width, i, fill="#313244", dash=(2, 2))

        self.radar_canvas.bind("<Button-1>", self.on_radar_click)

        tk.Button(hal_frame, text="СЛУЧАЙНАЯ НОТА", font=("Segoe UI", 10, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=self.spawn_random_note).pack(fill=tk.X, pady=10)

        # Статус бар
        self.status_label = tk.Label(root, text="Готово к подключению", font=("Segoe UI", 9), bg=self.bg_color, fg="#6c7086")
        self.status_label.pack(side=tk.BOTTOM, pady=5)

    def set_jitter(self, val):
        self.jitter_slider.set(val)
        if val > 0:
            self.jitter_header.config(text=f"ТРЯСУЩИЕСЯ РУКИ (ДЖИТТЕР: {int(val)} px 🟢)", fg=self.accent_on)
        else:
            self.jitter_header.config(text="ТРЯСУЩИЕСЯ РУКИ (ДЖИТТЕР: 0 px 🔴)", fg=self.text_color)
        self.send_command(f"JITTER:{int(val)}")

    def on_jitter_slider_change(self, val):
        px = int(float(val))
        if px > 0:
            self.jitter_header.config(text=f"ТРЯСУЩИЕСЯ РУКИ (ДЖИТТЕР: {px} px 🟢)", fg=self.accent_on)
        else:
            self.jitter_header.config(text="ТРЯСУЩИЕСЯ РУКИ (ДЖИТТЕР: 0 px 🔴)", fg=self.text_color)
        self.send_command(f"JITTER:{px}")

    def set_input_lag(self, val_ms):
        self.lag_slider.set(val_ms)
        self.lag_label.config(text=f"Задержка: {int(val_ms)} ms")
        self.send_command(f"INPUT_LAG:{int(val_ms)}")

    def on_lag_slider_change(self, val):
        ms = int(float(val))
        self.lag_label.config(text=f"Задержка: {ms} ms")
        self.send_command(f"INPUT_LAG:{ms}")

    def set_cursor_scale(self, val):
        self.cursor_scale_slider.set(val)
        self.cursor_scale_header.config(text=f"РАЗМЕР КУРСОРА ({val:.1f}x)")
        self.send_command(f"CURSOR_SCALE:{val:.2f}")

    def set_bh_strength(self, val):
        self.bh_slider.set(val)
        self.send_command(f"BLACK_HOLE_STRENGTH:{val:.2f}")

    def set_audio_desync(self, val_ms):
        self.desync_slider.set(val_ms)
        self.desync_header.config(text=f"РАССИНХРОН ЗВУКА ({int(val_ms):+d} ms 🟢)" if val_ms != 0 else "РАССИНХРОН ЗВУКА (0 ms 🔴)", fg=self.accent_on if val_ms != 0 else self.text_color)
        self.send_command(f"AUDIO_DESYNC:{int(val_ms)}")

    def on_desync_slider_change(self, val):
        ms = int(float(val))
        self.desync_header.config(text=f"РАССИНХРОН ЗВУКА ({ms:+d} ms 🟢)" if ms != 0 else "РАССИНХРОН ЗВУКА (0 ms 🔴)", fg=self.accent_on if ms != 0 else self.text_color)
        self.send_command(f"AUDIO_DESYNC:{ms}")

    def on_cursor_scale_change(self, val):
        scale = float(val)
        self.cursor_scale_header.config(text=f"РАЗМЕР КУРСОРА ({scale:.1f}x)")
        self.send_command(f"CURSOR_SCALE:{scale:.2f}")

    def _update_invert_header(self):
        if self.inv_x and self.inv_y:
            self.invert_header.config(text="ИНВЕРСИЯ ОСЕЙ (X + Y ВКЛЮЧЕНЫ 🟢)", fg=self.accent_on)
        elif self.inv_x:
            self.invert_header.config(text="ИНВЕРСИЯ ОСЕЙ (ОСЬ X ВКЛЮЧЕНА 🟢)", fg=self.accent_yellow)
        elif self.inv_y:
            self.invert_header.config(text="ИНВЕРСИЯ ОСЕЙ (ОСЬ Y ВКЛЮЧЕНА 🟢)", fg=self.accent_yellow)
        else:
            self.invert_header.config(text="ИНВЕРСИЯ ОСЕЙ (ВЫКЛЮЧЕНА 🔴)", fg=self.text_color)

    def _update_jam_header(self):
        if self.jam_k1 and self.jam_k2:
            self.jam_header.config(text="ЗАЛИПАНИЕ КЛАВИШ (ОБЕ ЗАЛИПЛИ! ⛔)", fg=self.accent_on)
        elif self.jam_k1 or self.jam_k2:
            jammed = "K1" if self.jam_k1 else "K2"
            self.jam_header.config(text=f"ЗАЛИПАНИЕ КЛАВИШ ({jammed} ЗАЛИПЛА ⚠️)", fg=self.accent_yellow)
        else:
            self.jam_header.config(text="ЗАЛИПАНИЕ КЛАВИШ (K1 / K2)", fg=self.text_color)

    def update_ui_state(self, command):
        if command == "CHAOS_ON":
            self.chaos_header.config(text="1. ХАОС (ВКЛЮЧЕН 🟢)", fg=self.accent_on)
        elif command == "CHAOS_OFF":
            self.chaos_header.config(text="1. ХАОС (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "WIND_ON":
            self.wind_header.config(text="2. ВЕТЕР (ВКЛЮЧЕН 🟢)", fg=self.accent_blue)
        elif command == "WIND_OFF":
            self.wind_header.config(text="2. ВЕТЕР (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "MAGNET_ON":
            self.magnet_header.config(text="3. МАГНИТ НОТ (ВКЛЮЧЕН 🟢)", fg=self.accent_yellow)
        elif command == "MAGNET_OFF":
            self.magnet_header.config(text="3. МАГНИТ НОТ (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "EARTHQUAKE_ON":
            self.earth_header.config(text="ЗЕМЛЕТРЯСЕНИЕ (ВКЛЮЧЕН 🟢)", fg=self.accent_earth)
        elif command == "EARTHQUAKE_OFF":
            self.earth_header.config(text="ЗЕМЛЕТРЯСЕНИЕ (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "FREEZE_ON":
            self.blackout_header.config(text="5. БЛЭКАУТ (ВКЛЮЧЕН 🟢)", fg=self.accent_blackout)
        elif command == "FREEZE_OFF":
            self.blackout_header.config(text="5. БЛЭКАУТ (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "HIDDEN_ON":
            self.hidden_header.config(text="СЛЕПОТА (Hidden) (ВКЛЮЧЕН 🟢)", fg=self.accent_on)
        elif command == "HIDDEN_OFF":
            self.hidden_header.config(text="СЛЕПОТА (Hidden) (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "REPULSION_ON":
            self.repulsion_header.config(text="ОТТАЛКИВАНИЕ КУРСОРА ОТ НОТ (ВКЛЮЧЕНО 🟢)", fg=self.accent_yellow)
        elif command == "REPULSION_OFF":
            self.repulsion_header.config(text="ОТТАЛКИВАНИЕ КУРСОРА ОТ НОТ (ВЫКЛЮЧЕНО 🔴)", fg=self.text_color)
        elif command == "CLONES_ON":
            self.clones_header.config(text="ФЕЙКОВЫЕ КУРСОРЫ: АРМИЯ КЛОНОВ (10) 🟢", fg=self.accent_on)
        elif command == "CLONES_OFF":
            self.clones_header.config(text="ФЕЙКОВЫЕ КУРСОРЫ (ШИЗОФРЕНИЯ)", fg=self.text_color)
        elif command == "DRUNK_ON":
            self.lbl_drunk.config(text="Пьяная камера (КАЧКА 🟢):", fg=self.accent_yellow)
        elif command == "DRUNK_OFF":
            self.lbl_drunk.config(text="Пьяная камера (Качка ±15°):", fg=self.text_color)
        elif command == "SHAKE_ON":
            self.lbl_shake.config(text="Тряска экрана (ТРЯСЕТ 🟢):", fg=self.accent_earth)
        elif command == "SHAKE_OFF":
            self.lbl_shake.config(text="Тряска экрана (Землетряс):", fg=self.text_color)
        elif command == "TUNNEL_ON":
            self.lbl_tunnel.config(text="Туннельное зрение (ФОНАРИК 🟢):", fg=self.accent_cyan)
        elif command == "TUNNEL_OFF":
            self.lbl_tunnel.config(text="Туннельное зрение (Фонарик):", fg=self.text_color)
        elif command == "GHOST_SLIDERS_ON":
            self.lbl_ghost.config(text="Невидимка-слайдеры (НЕВИДИМЫ 🟢):", fg=self.accent_purple)
        elif command == "GHOST_SLIDERS_OFF":
            self.lbl_ghost.config(text="Невидимка-слайдеры (Тела):", fg=self.text_color)
        elif command == "MUFFLED_ON":
            self.lbl_muffled.config(text="Звук под водой (LOW-PASS 🟢):", fg=self.accent_blue)
        elif command == "MUFFLED_OFF":
            self.lbl_muffled.config(text="Звук под водой (Low-Pass):", fg=self.text_color)
        elif command == "PAN_SPIN_ON":
            self.lbl_pan.config(text="8D Панорама (ВРАЩЕНИЕ 🟢):", fg="#f5c2e7")
        elif command == "PAN_SPIN_OFF":
            self.lbl_pan.config(text="8D Панорама (Вращение):", fg=self.text_color)
        elif command.startswith("INPUT_LAG:"):
            try:
                ms = int(float(command.split(":")[1]))
                if ms > 0:
                    self.lag_header.config(text=f"ИНПУТ-ЛАГ ({ms} ms 🟢)", fg=self.accent_on)
                else:
                    self.lag_header.config(text="ИНПУТ-ЛАГ (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
            except:
                pass
        elif command == "HIDE_CURSOR:ON":
            self.hide_cursor_header.config(text="НЕВИДИМЫЙ КУРСОР (ВКЛЮЧЕН 🟢)", fg=self.accent_on)
        elif command == "HIDE_CURSOR:OFF":
            self.hide_cursor_header.config(text="НЕВИДИМЫЙ КУРСОР (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command.startswith("CURSOR_SCALE:"):
            try:
                scale = float(command.split(":")[1])
                self.cursor_scale_header.config(text=f"РАЗМЕР КУРСОРА ({scale:.1f}x)", fg=self.accent_yellow if scale != 1.0 else self.text_color)
            except:
                pass
        elif command == "INVERT_X_ON":
            self.inv_x = True
            self._update_invert_header()
        elif command == "INVERT_X_OFF":
            self.inv_x = False
            self._update_invert_header()
        elif command == "INVERT_Y_ON":
            self.inv_y = True
            self._update_invert_header()
        elif command == "INVERT_Y_OFF":
            self.inv_y = False
            self._update_invert_header()
        elif command == "INVERT_RESET":
            self.inv_x = False
            self.inv_y = False
            self._update_invert_header()
        elif command == "JAM_K1_ON":
            self.jam_k1 = True
            self.lbl_k1.config(fg=self.accent_red, text="Клавиша K1: ЗАЛИПЛА ⚠️")
            self._update_jam_header()
        elif command == "JAM_K1_OFF":
            self.jam_k1 = False
            self.lbl_k1.config(fg=self.text_color, text="Клавиша K1 (Левая):")
            self._update_jam_header()
        elif command == "JAM_K2_ON":
            self.jam_k2 = True
            self.lbl_k2.config(fg=self.accent_red, text="Клавиша K2: ЗАЛИПЛА ⚠️")
            self._update_jam_header()
        elif command == "JAM_K2_OFF":
            self.jam_k2 = False
            self.lbl_k2.config(fg=self.text_color, text="Клавиша K2 (Правая):")
            self._update_jam_header()
        elif command == "JAM_RESET":
            self.jam_k1 = False
            self.jam_k2 = False
            self.lbl_k1.config(fg=self.text_color, text="Клавиша K1 (Левая):")
            self.lbl_k2.config(fg=self.text_color, text="Клавиша K2 (Правая):")
            self._update_jam_header()
        elif command == "BLACK_HOLE_ON":
            self.bh_header.config(text="4. ЧЁРНАЯ ДЫРА (ВКЛЮЧЕНА 🟣)", fg=self.accent_blackout)
        elif command == "BLACK_HOLE_OFF":
            self.bh_header.config(text="4. ЧЁРНАЯ ДЫРА (ВЫКЛЮЧЕНА 🔴)", fg=self.text_color)
        elif command == "CHAMELEON_OFF":
            self.cham_header.config(text="ХАМЕЛЕОН (ОБЫЧНЫЕ ЦВЕТА 🔴)", fg=self.text_color)
        elif command == "CHAMELEON_BLACK":
            self.cham_header.config(text="ХАМЕЛЕОН (ЧЁРНЫЙ СТЕЛС 🟢)", fg="#89b4fa")
        elif command == "CHAMELEON_RAINBOW":
            self.cham_header.config(text="ХАМЕЛЕОН (РАДУЖНЫЙ ДИСКО 🟢)", fg="#f5c2e7")
        elif command == "CHAMELEON_MONO":
            self.cham_header.config(text="ХАМЕЛЕОН (МОНОХРОМНЫЙ 🟢)", fg="#a6adc8")
        elif command == "DEVICE_DISCONNECT":
            self.troll_header.config(text="ТРОЛЛИНГ: МЫШЬ ОТКЛЮЧЕНА 🔌", fg="#f38ba8")
        elif command == "TROLL:UPDATE":
            self.troll_header.config(text="ТРОЛЛИНГ: ОБНОВЛЕНИЕ WINDOWS 🔄", fg="#89dceb")
        elif command == "TROLL:DONATE":
            self.troll_header.config(text="ТРОЛЛИНГ: ДОНАТ ОТ ПАПИЧА 💰", fg="#fab387")
        elif command == "TROLL:STICKYKEYS":
            self.troll_header.config(text="ТРОЛЛИНГ: ЗАЛИПАНИЕ КЛАВИШ ⌨️", fg="#cba6f7")
        elif command == "TROLL:GLITCH":
            self.troll_header.config(text="ТРОЛЛИНГ: ОТВАЛ ВИДЕОКАРТЫ ⚡", fg="#eba0ac")
        elif command == "TROLL:BATTERY":
            self.troll_header.config(text="ТРОЛЛИНГ: БАТАРЕЯ 5% 🔋", fg="#f38ba8")
        elif command == "TROLL:DISCORD":
            self.troll_header.config(text="ТРОЛЛИНГ: ЗВОНОК DISCORD 📞", fg="#89b4fa")
        elif command == "TROLL:DISCORD_AUDIO":
            self.troll_header.config(text="ТРОЛЛИНГ: ЗВОНОК (ТОЛЬКО ЗВУК) 🔊", fg="#7289da")
        elif command == "TROLL:BSOD":
            self.troll_header.config(text="ТРОЛЛИНГ: СИНИЙ ЭКРАН (BSOD) 💻", fg="#89dceb")
        elif command == "TROLL:DEFENDER":
            self.troll_header.config(text="ТРОЛЛИНГ: ЗАЩИТНИК DEFENDER 🛡️", fg="#fab387")
        elif command in ("TROLL:TELEGRAM", "TROLL_TELEGRAM"):
            self.troll_header.config(text="ТРОЛЛИНГ: ЗВОНОК В ТЕЛЕГРАМ (МАМУЛЯ ❤️) 📱", fg="#29b6f6")
        elif command in ("TROLL:TELEGRAM_AUDIO", "TROLL_TELEGRAM_AUDIO"):
            self.troll_header.config(text="ТРОЛЛИНГ: ТЕЛЕГРАМ (ТОЛЬКО ЗВУК) 🔔", fg="#0288d1")
        elif command in ("TROLL:STEAM", "TROLL_STEAM"):
            self.troll_header.config(text="ТРОЛЛИНГ: STEAM СООБЩЕНИЕ (ШАУРМА) 🎮", fg="#66c0f4")
        elif command == "WATERMARK_ON":
            self.troll_header.config(text="ТРОЛЛИНГ: ВОДЯНОЙ ЗНАК WINDOWS 🪟", fg=self.accent_on)
        elif command == "WATERMARK_OFF":
            self.troll_header.config(text="7. СИСТЕМНЫЙ ТРОЛЛИНГ & ОБМАНКИ 🪟", fg=self.text_color)
        elif command == "BUSY_CURSOR_ON":
            self.busy_cursor_header.config(text="КОЛЁСИКО ЗАГРУЗКИ (ВКЛЮЧЕНО 🟢)", fg=self.accent_on)
        elif command == "BUSY_CURSOR_OFF":
            self.busy_cursor_header.config(text="КОЛЁСИКО ЗАГРУЗКИ (BUSY CURSOR ⏳)", fg=self.text_color)
        elif command == "CS_CHAOS_ON":
            self.vis_header.config(text="ХАОС НОТ: ГИГАНТИЗМ VS МИКРО 🟢", fg=self.accent_on)
        elif command == "CS_CHAOS_OFF":
            self.vis_header.config(text="ВИЗУАЛЬНЫЙ АД & ХАОС НОТ (ФАЗА 5) 👁️", fg=self.text_color)
        elif command == "MOSAIC_ON":
            self.vis_header.config(text="ВИЗУАЛЬНЫЙ АД: 144p МОЗАИКА 🟢", fg="#89dceb")
        elif command == "MOSAIC_OFF":
            self.vis_header.config(text="ВИЗУАЛЬНЫЙ АД & ХАОС НОТ (ФАЗА 5) 👁️", fg=self.text_color)
        elif command == "INVERT_COLORS_ON":
            self.vis_header.config(text="ВИЗУАЛЬНЫЙ АД: НЕГАТИВ / ИНВЕРСИЯ 🟢", fg="#f9e2af")
        elif command == "INVERT_COLORS_OFF":
            self.vis_header.config(text="ВИЗУАЛЬНЫЙ АД & ХАОС НОТ (ФАЗА 5) 👁️", fg=self.text_color)
        elif command == "BARREL_ROLL":
            self.cam_header.config(text="КАМЕРА: БОЧКА 360° 🔄", fg="#cba6f7")
        elif command.startswith("SET_FPS:"):
            fps_val = command.split(":")[1]
            txt = "СБРОС FPS (БЕЗ ОГРАНИЧЕНИЙ)" if fps_val == "0" else f"FPS ОГРАНИЧЕН: {fps_val} FPS"
            self.cam_header.config(text=f"КАМЕРА: {txt} ⏱️", fg="#fab387")

        elif command == "TAPE_STOP":
            self.audio_header.config(text="ЗВУК: ЗАЖЕВАЛО ПЛЕНКУ / TAPE STOP 🛑", fg="#fab387")
        elif command == "REVERB_ON":
            self.lbl_reverb.config(text="Эхо в соборе: ВКЛ ⛪", fg=self.accent_on)
        elif command == "REVERB_OFF":
            self.lbl_reverb.config(text="Эхо в соборе (Reverb):", fg=self.text_color)

    def send_command(self, command: str):
        ip = self.ip_entry.get().strip()
        def task():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect((ip, 9000))
                s.send(command.encode('utf-8'))
                s.close()
                self.root.after(0, lambda: self.status_label.config(text=f"Успех: Отправлено '{command}'", fg=self.accent_off))
                self.root.after(0, lambda: self.update_ui_state(command))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(text=f"Ошибка сети", fg=self.accent_on))
        threading.Thread(target=task, daemon=True).start()

    def set_fps_target(self, fps):
        if fps <= 0:
            self.fps_status_lbl.config(text="Без ограничений", fg=self.accent_off)
            self.send_command("SET_FPS:0")
        else:
            self.fps_status_lbl.config(text=f"{fps} FPS", fg=self.accent_earth)
            self.fps_slider.set(fps)
            self.send_command(f"SET_FPS:{fps}")

    def on_fps_slider_change(self, val):
        fps_int = int(float(val))
        self.fps_status_lbl.config(text=f"{fps_int} FPS (слайдер)", fg=self.accent_yellow)

    def apply_fps_slider(self):
        fps_int = int(self.fps_slider.get())
        self.set_fps_target(fps_int)



    def on_radar_click(self, event):
        x = event.x
        y = event.y
        if 0 <= x <= 512 and 0 <= y <= 384:
            self.send_command(f"FAKE_NOTE:{x}:{y}")
            r = 10
            blip = self.radar_canvas.create_oval(x-r, y-r, x+r, y+r, outline=self.accent_blue, width=2)
            self.root.after(300, lambda: self.radar_canvas.delete(blip))

    def spawn_random_note(self):
        import random
        x = random.uniform(10, 502)
        y = random.uniform(10, 374)
        self.send_command(f"FAKE_NOTE:{x:.2f}:{y:.2f}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernControlPanel(root)
    root.mainloop()
