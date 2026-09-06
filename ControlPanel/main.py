import tkinter as tk
from tkinter import ttk
import socket
import threading

class ModernControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("osu! Chaos Remote")
        self.root.geometry("540x880")
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
        
        self.inv_x = False
        self.inv_y = False
        self.jam_k1 = False
        self.jam_k2 = False

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScale", background=self.panel_color, troughcolor=self.bg_color)
        
        # --- Настройка стилей вкладок ---
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.panel_color, foreground=self.text_color, padding=[12, 5], font=("Segoe UI", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", self.accent_blue)], foreground=[("selected", "#11111b")])
        style.configure("TFrame", background=self.bg_color)
        
        # Заголовок
        header = tk.Label(root, text="OSU! DEBUFF CONTROL", font=("Segoe UI Black", 16), bg=self.bg_color, fg=self.accent_blue)
        header.pack(pady=(15, 5))
        
        # Блок подключения
        conn_frame = tk.Frame(root, bg=self.panel_color, padx=15, pady=5)
        conn_frame.pack(fill=tk.X, padx=20, pady=5)
        tk.Label(conn_frame, text="IP Игрока:", font=("Segoe UI", 10, "bold"), bg=self.panel_color, fg=self.text_color).pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(conn_frame, font=("Segoe UI", 11), bg=self.bg_color, fg=self.text_color, bd=0)
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(10, 0))
        
        # Создаем Notebook (Вкладки)
        notebook = ttk.Notebook(root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Вкладка 1: Основные эффекты (со скроллом)
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
        
        def _on_mousewheel(event):
            if tab1_canvas.winfo_ismapped():
                tab1_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif tab2_canvas.winfo_ismapped():
                tab2_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            elif tab_cursor_canvas.winfo_ismapped():
                tab_cursor_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                
        root.bind_all("<MouseWheel>", _on_mousewheel)

        # Вкладка 4: События
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Ивенты")

        # Вкладка 5: Галлюцинации
        tab4 = ttk.Frame(notebook)
        notebook.add(tab4, text="Галлюцинации")

        # ==========================================
        # Вкладка 1: ГЕЙМПЛЕЙ (Хаос, Ветер, Магнит)
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

        # --- СЕКЦИЯ: МАГНИТ ---
        magnet_frame = tk.Frame(tab1, bg=self.panel_color, padx=15, pady=10)
        magnet_frame.pack(fill=tk.X, pady=5)
        self.magnet_header = tk.Label(magnet_frame, text="3. МАГНИТ (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
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
        # Вкладка 2: КУРСОР (Инпут-лаг, Шизофрения, Невидимость)
        # ==========================================

        # --- СЕКЦИЯ: ИНПУТ-ЛАГ (РЕАЛЬНАЯ ЗАДЕРЖКА ВВОДА) ---
        lag_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=15)
        lag_frame.pack(fill=tk.X, pady=5)
        self.lag_header = tk.Label(lag_frame, text="ИНПУТ-ЛАГ (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.lag_header.pack(anchor=tk.W, pady=(0, 5))
        tk.Label(lag_frame, text="Физически задерживает координаты и клики. Ломает мышечную память!", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8", wraplength=450, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 8))

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
        self.lag_label.pack(anchor=tk.W, pady=(10, 0))
        self.lag_slider = ttk.Scale(lag_frame, from_=0, to=500, orient=tk.HORIZONTAL, command=self.on_lag_slider_change)
        self.lag_slider.set(0)
        self.lag_slider.pack(fill=tk.X, pady=(2, 5))

        # --- СЕКЦИЯ: ФЕЙКОВЫЕ КУРСОРЫ (ШИЗОФРЕНИЯ) ---
        cursor_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=15)
        cursor_frame.pack(fill=tk.X, pady=5)
        tk.Label(cursor_frame, text="ФЕЙКОВЫЕ КУРСОРЫ (ШИЗОФРЕНИЯ)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color).pack(anchor=tk.W, pady=(0, 5))
        tk.Label(cursor_frame, text="Курсоры-обманки, копирующие клики", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 5))

        btn_fcf_1 = tk.Frame(cursor_frame, bg=self.panel_color)
        btn_fcf_1.pack(fill=tk.X, pady=2)
        tk.Button(btn_fcf_1, text="ВЫКЛЮЧИТЬ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_CURSORS:OFF")).pack(fill=tk.X, expand=True, padx=2)

        btn_fcf_2 = tk.Frame(cursor_frame, bg=self.panel_color)
        btn_fcf_2.pack(fill=tk.X, pady=2)
        tk.Button(btn_fcf_2, text="ЗЕРКАЛО (X)", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_CURSORS:MIRROR_X")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_fcf_2, text="ЗЕРКАЛО (Y)", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_CURSORS:MIRROR_Y")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        btn_fcf_3 = tk.Frame(cursor_frame, bg=self.panel_color)
        btn_fcf_3.pack(fill=tk.X, pady=2)
        tk.Button(btn_fcf_3, text="ЦЕНТРАЛЬНОЕ ЗЕРКАЛО (X+Y)", font=("Segoe UI", 9, "bold"), bg=self.accent_blue, fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_CURSORS:MIRROR_XY")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_fcf_3, text="РОЙ КУРСОРОВ (ОТСТАЮЩИЙ)", font=("Segoe UI", 9, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_CURSORS:SWARM")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: НЕВИДИМЫЙ КУРСОР ---
        hide_cursor_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=15)
        hide_cursor_frame.pack(fill=tk.X, pady=5)
        self.hide_cursor_header = tk.Label(hide_cursor_frame, text="НЕВИДИМЫЙ КУРСОР (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.hide_cursor_header.pack(anchor=tk.W, pady=(0, 5))
        tk.Label(hide_cursor_frame, text="Скрывает сам спрайт курсора, оставляя только след", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 5))
        
        btn_hide_cursor = tk.Frame(hide_cursor_frame, bg=self.panel_color)
        btn_hide_cursor.pack(fill=tk.X, pady=2)
        tk.Button(btn_hide_cursor, text="СКРЫТЬ КУРСОР", font=("Segoe UI", 9, "bold"), bg=self.accent_red, fg="#11111b", bd=0, command=lambda: self.send_command("HIDE_CURSOR:ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_hide_cursor, text="ВЕРНУТЬ КУРСОР", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("HIDE_CURSOR:OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: РАЗМЕР КУРСОРА (МИКРО / ГИГАНТСКИЙ) ---
        scale_cursor_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=15)
        scale_cursor_frame.pack(fill=tk.X, pady=5)
        self.cursor_scale_header = tk.Label(scale_cursor_frame, text="РАЗМЕР КУРСОРА (1.0x)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.cursor_scale_header.pack(anchor=tk.W, pady=(0, 5))
        tk.Label(scale_cursor_frame, text="Уменьшает в микро-точку или раздувает до гигантского размера", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 8))

        btn_cscale_row = tk.Frame(scale_cursor_frame, bg=self.panel_color)
        btn_cscale_row.pack(fill=tk.X, pady=2)
        tk.Button(btn_cscale_row, text="0.2x (Микро)", font=("Segoe UI", 9, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(0.2)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cscale_row, text="0.5x", font=("Segoe UI", 9, "bold"), bg=self.accent_yellow, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(0.5)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cscale_row, text="1.0x (Норма)", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(1.0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cscale_row, text="2.0x", font=("Segoe UI", 9, "bold"), bg=self.accent_earth, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(2.0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cscale_row, text="4.0x (Гигант)", font=("Segoe UI", 9, "bold"), bg=self.accent_on, fg="#11111b", bd=0, command=lambda: self.set_cursor_scale(4.0)).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_cscale = tk.Frame(scale_cursor_frame, bg=self.panel_color)
        row_cscale.pack(fill=tk.X, pady=(8, 0))
        self.cursor_scale_slider = ttk.Scale(row_cscale, from_=0.1, to=5.0, orient=tk.HORIZONTAL, command=self.on_cursor_scale_change)
        self.cursor_scale_slider.set(1.0)
        self.cursor_scale_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row_cscale, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.set_cursor_scale(1.0)).pack(side=tk.RIGHT, padx=(5, 0))

        # --- СЕКЦИЯ: ИНВЕРСИЯ УПРАВЛЕНИЯ (X / Y) ---
        invert_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=15)
        invert_frame.pack(fill=tk.X, pady=5)
        self.invert_header = tk.Label(invert_frame, text="ИНВЕРСИЯ ОСЕЙ (ВЫКЛЮЧЕНА 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.invert_header.pack(anchor=tk.W, pady=(0, 5))
        tk.Label(invert_frame, text="Зеркально переворачивает координаты реального курсора по осям X и Y", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 8))

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
        tk.Button(row_inv_all, text="СБРОСИТЬ ВСЁ В НОРМУ", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("INVERT_RESET")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ЗАЛИПАНИЕ КНОПКИ (KEY JAM) ---
        jam_frame = tk.Frame(tab_cursor, bg=self.panel_color, padx=15, pady=15)
        jam_frame.pack(fill=tk.X, pady=5)
        self.jam_header = tk.Label(jam_frame, text="ЗАЛИПАНИЕ КЛАВИШ (K1 / K2)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.jam_header.pack(anchor=tk.W, pady=(0, 5))
        tk.Label(jam_frame, text="Блокирует клики выбранной клавиши (эмуляция заевшей кнопки / сингл-тап)", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 8))

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
        # Вкладка 3: ЭКРАН (Землетрясение, Искажение)
        # ==========================================

        # --- СЕКЦИЯ: ЗЕМЛЕТРЯСЕНИЕ ---
        earth_frame = tk.Frame(tab2, bg=self.panel_color, padx=15, pady=10)
        earth_frame.pack(fill=tk.X, pady=5)
        self.earth_header = tk.Label(earth_frame, text="4. ЗЕМЛЕТРЯСЕНИЕ (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
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
        self.scale_header = tk.Label(scale_frame, text="5. ИСКАЖЕНИЕ (Масштаб)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
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

        # --- Раздельный масштаб (Расширенные настройки) ---
        self.adv_frame = tk.Frame(scale_frame, bg=self.panel_color)
        
        tk.Label(self.adv_frame, text="Игровое поле - Ширина (X):", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W)
        row3 = tk.Frame(self.adv_frame, bg=self.panel_color)
        row3.pack(fill=tk.X, pady=(0, 5))
        self.scale_x_slider = ttk.Scale(row3, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"SCALE_X:{float(val):.2f}"))
        self.scale_x_slider.set(1.0)
        self.scale_x_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row3, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.scale_x_slider.set(1.0)).pack(side=tk.RIGHT, padx=(5, 0))

        tk.Label(self.adv_frame, text="Игровое поле - Высота (Y):", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W)
        row4 = tk.Frame(self.adv_frame, bg=self.panel_color)
        row4.pack(fill=tk.X, pady=(0, 5))
        self.scale_y_slider = ttk.Scale(row4, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"SCALE_Y:{float(val):.2f}"))
        self.scale_y_slider.set(1.0)
        self.scale_y_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row4, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.scale_y_slider.set(1.0)).pack(side=tk.RIGHT, padx=(5, 0))

        tk.Label(self.adv_frame, text="Интерфейс (HUD) - Ширина (X):", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W)
        row5 = tk.Frame(self.adv_frame, bg=self.panel_color)
        row5.pack(fill=tk.X, pady=(0, 5))
        self.hud_scale_x_slider = ttk.Scale(row5, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"HUD_SCALE_X:{float(val):.2f}"))
        self.hud_scale_x_slider.set(1.0)
        self.hud_scale_x_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row5, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.hud_scale_x_slider.set(1.0)).pack(side=tk.RIGHT, padx=(5, 0))

        tk.Label(self.adv_frame, text="Интерфейс (HUD) - Высота (Y):", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W)
        row6 = tk.Frame(self.adv_frame, bg=self.panel_color)
        row6.pack(fill=tk.X, pady=(0, 5))
        self.hud_scale_y_slider = ttk.Scale(row6, from_=0.1, to=2.0, orient=tk.HORIZONTAL, command=lambda val: self.send_command(f"HUD_SCALE_Y:{float(val):.2f}"))
        self.hud_scale_y_slider.set(1.0)
        self.hud_scale_y_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(row6, text="⟲", font=("Segoe UI", 12), bg=self.panel_color, fg=self.accent_blue, bd=0, cursor="hand2", command=lambda: self.hud_scale_y_slider.set(1.0)).pack(side=tk.RIGHT, padx=(5, 0))

        btn_frame7 = tk.Frame(scale_frame, bg=self.panel_color)
        
        def toggle_adv():
            if self.adv_frame.winfo_ismapped():
                self.adv_frame.pack_forget()
                self.btn_adv.config(text="Расширенные настройки ▼")
            else:
                self.adv_frame.pack(fill=tk.X, pady=5, before=btn_frame7)
                self.btn_adv.config(text="Скрыть настройки ▲")

        self.btn_adv = tk.Button(scale_frame, text="Расширенные настройки ▼", font=("Segoe UI", 9), bg=self.panel_color, fg=self.accent_blue, bd=0, command=toggle_adv)
        self.btn_adv.pack(anchor=tk.W, pady=(5,0))
        btn_frame7.pack(fill=tk.X, pady=(10,0))
        
        tk.Button(btn_frame7, text="СБРОС МАСШТАБА", font=("Segoe UI", 9, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: [self.scale_slider.set(1.0), self.hud_scale_slider.set(1.0), self.scale_x_slider.set(1.0), self.scale_y_slider.set(1.0), self.hud_scale_x_slider.set(1.0), self.hud_scale_y_slider.set(1.0)]).pack(fill=tk.X, expand=True, padx=2)

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
        tk.Label(desync_frame, text="Сдвигает аудио относительно тайминга карты. Ломает чувство ритма!", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 8))

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
        tk.Label(cham_frame, text="Подменяет цвета всех нот, слайдеров и подходных кругов", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 8))

        btn_cham_row = tk.Frame(cham_frame, bg=self.panel_color)
        btn_cham_row.pack(fill=tk.X, pady=2)
        tk.Button(btn_cham_row, text="ОБЫЧНЫЕ (ВЫКЛ)", font=("Segoe UI", 8, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("CHAMELEON_OFF")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cham_row, text="ЧЕРНЫЕ (Стелс 🥷)", font=("Segoe UI", 8, "bold"), bg="#11111b", fg="#cdd6f4", bd=0, command=lambda: self.send_command("CHAMELEON_BLACK")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cham_row, text="РАДУГА (Диско 🌈)", font=("Segoe UI", 8, "bold"), bg="#f5c2e7", fg="#11111b", bd=0, command=lambda: self.send_command("CHAMELEON_RAINBOW")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_cham_row, text="МОНОХРОМ (⚪)", font=("Segoe UI", 8, "bold"), bg="#a6adc8", fg="#11111b", bd=0, command=lambda: self.send_command("CHAMELEON_MONO")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)


        # ==========================================
        # Вкладка 3: ИВЕНТЫ (Блэкаут, Поцелуй)
        # ==========================================

        # --- СЕКЦИЯ: БЛЭКАУТ (Остановка времени) ---
        blackout_frame = tk.Frame(tab3, bg=self.panel_color, padx=15, pady=10)
        blackout_frame.pack(fill=tk.X, pady=5)
        self.blackout_header = tk.Label(blackout_frame, text="6. БЛЭКАУТ (ВЫКЛЮЧЕН 🔴)", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.blackout_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame5 = tk.Frame(blackout_frame, bg=self.panel_color)
        btn_frame5.pack(fill=tk.X)
        tk.Button(btn_frame5, text="ОСТАНОВИТЬ ВРЕМЯ", font=("Segoe UI", 10, "bold"), bg=self.accent_blackout, fg="#11111b", bd=0, command=lambda: self.send_command("FREEZE_ON")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame5, text="ВОССТАНОВИТЬ", font=("Segoe UI", 10, "bold"), bg=self.accent_off, fg="#11111b", bd=0, command=lambda: self.send_command("FREEZE_OFF")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ВНЕЗАПНЫЕ ИВЕНТЫ ---
        screamer_frame = tk.Frame(tab3, bg=self.panel_color, padx=15, pady=10)
        screamer_frame.pack(fill=tk.X, pady=5)
        self.screamer_header = tk.Label(screamer_frame, text="7. ВНЕЗАПНЫЕ ИВЕНТЫ 🎭", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.screamer_header.pack(anchor=tk.W, pady=(0, 5))
        
        btn_frame6 = tk.Frame(screamer_frame, bg=self.panel_color)
        btn_frame6.pack(fill=tk.X, pady=(0, 5))
        tk.Button(btn_frame6, text="ПОЦЕЛУЙ 💋", font=("Segoe UI", 10, "bold"), bg="#ff7eb3", fg="#11111b", bd=0, command=lambda: self.send_command("KISS")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(btn_frame6, text="ФЕЙКОВЫЙ МИСС ❌", font=("Segoe UI", 10, "bold"), bg="#f38ba8", fg="#11111b", bd=0, command=lambda: self.send_command("FAKE_MISS")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)
        
        btn_frame_flash = tk.Frame(screamer_frame, bg=self.panel_color)
        btn_frame_flash.pack(fill=tk.X)
        tk.Button(btn_frame_flash, text="FLASHBANG 💥", font=("Segoe UI", 10, "bold"), bg="#ffffff", fg="#11111b", bd=0, command=lambda: self.send_command("FLASHBANG")).pack(fill=tk.X, expand=True, padx=2)

        # --- СЕКЦИЯ: ТРОЛЛИНГ-УВЕДОМЛЕНИЯ ---
        troll_frame = tk.Frame(tab3, bg=self.panel_color, padx=15, pady=12)
        troll_frame.pack(fill=tk.X, pady=5)
        self.troll_header = tk.Label(troll_frame, text="8. ТРОЛЛИНГ-УВЕДОМЛЕНИЯ 🪟", font=("Segoe UI", 11, "bold"), bg=self.panel_color, fg=self.text_color)
        self.troll_header.pack(anchor=tk.W, pady=(0, 5))
        tk.Label(troll_frame, text="Фейковые системные окна, звонки и синий экран со звуком", font=("Segoe UI", 9), bg=self.panel_color, fg="#a6adc8").pack(anchor=tk.W, pady=(0, 8))

        row_troll_1 = tk.Frame(troll_frame, bg=self.panel_color)
        row_troll_1.pack(fill=tk.X, pady=3)
        tk.Button(row_troll_1, text="БАТАРЕЯ 5% 🔋", font=("Segoe UI", 9, "bold"), bg="#f38ba8", fg="#11111b", bd=0, command=lambda: self.send_command("TROLL:BATTERY")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_troll_1, text="ВХОДЯЩИЙ DISCORD 📞", font=("Segoe UI", 9, "bold"), bg="#5865F2", fg="#ffffff", bd=0, command=lambda: self.send_command("TROLL:DISCORD")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        row_troll_2 = tk.Frame(troll_frame, bg=self.panel_color)
        row_troll_2.pack(fill=tk.X, pady=3)
        tk.Button(row_troll_2, text="СИНИЙ ЭКРАН (BSOD) 💻", font=("Segoe UI", 9, "bold"), bg="#0078d7", fg="#ffffff", bd=0, command=lambda: self.send_command("TROLL:BSOD")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_troll_2, text="УГРОЗА DEFENDER 🛡️", font=("Segoe UI", 9, "bold"), bg="#fab387", fg="#11111b", bd=0, command=lambda: self.send_command("TROLL:DEFENDER")).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        # ==========================================
        # Вкладка 4: ГАЛЛЮЦИНАЦИИ
        # ==========================================
        # --- СЕКЦИЯ: РАДАР ---
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
        self.desync_header.config(text=f"РАССИНХРОН ЗВУКА ({int(val_ms):+d} ms)" if val_ms != 0 else "РАССИНХРОН ЗВУКА (0 ms 🔴)")
        self.send_command(f"AUDIO_DESYNC:{int(val_ms)}")

    def on_desync_slider_change(self, val):
        ms = int(float(val))
        self.desync_header.config(text=f"РАССИНХРОН ЗВУКА ({ms:+d} ms)" if ms != 0 else "РАССИНХРОН ЗВУКА (0 ms 🔴)")
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
            self.magnet_header.config(text="3. МАГНИТ (ВКЛЮЧЕН 🟢)", fg=self.accent_yellow)
        elif command == "MAGNET_OFF":
            self.magnet_header.config(text="3. МАГНИТ (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "EARTHQUAKE_ON":
            self.earth_header.config(text="4. ЗЕМЛЕТРЯСЕНИЕ (ВКЛЮЧЕН 🟢)", fg=self.accent_earth)
        elif command == "EARTHQUAKE_OFF":
            self.earth_header.config(text="4. ЗЕМЛЕТРЯСЕНИЕ (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "FREEZE_ON":
            self.blackout_header.config(text="5. БЛЭКАУТ (ВКЛЮЧЕН 🟢)", fg=self.accent_blackout)
        elif command == "FREEZE_OFF":
            self.blackout_header.config(text="5. БЛЭКАУТ (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "HIDDEN_ON":
            self.hidden_header.config(text="СЛЕПОТА (Hidden) (ВКЛЮЧЕН 🟢)", fg=self.accent_on)
        elif command == "HIDDEN_OFF":
            self.hidden_header.config(text="СЛЕПОТА (Hidden) (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
        elif command == "GHOST_ON":
            self.ghost_header.config(text="ПРИЗРАК (Blind) (ВКЛЮЧЕН 🟢)", fg=self.accent_on)
        elif command == "GHOST_OFF":
            self.ghost_header.config(text="ПРИЗРАК (Blind) (ВЫКЛЮЧЕН 🔴)", fg=self.text_color)
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
        elif command.startswith("AUDIO_DESYNC:"):
            try:
                ms = int(float(command.split(":")[1]))
                if ms != 0:
                    self.desync_header.config(text=f"РАССИНХРОН ЗВУКА ({ms:+d} ms 🟢)", fg=self.accent_on)
                else:
                    self.desync_header.config(text="РАССИНХРОН ЗВУКА (0 ms 🔴)", fg=self.text_color)
            except:
                pass
        elif command == "AUDIO_DESYNC_RESET":
            self.desync_header.config(text="РАССИНХРОН ЗВУКА (0 ms 🔴)", fg=self.text_color)
        elif command == "CHAMELEON_OFF":
            self.cham_header.config(text="ХАМЕЛЕОН (ОБЫЧНЫЕ ЦВЕТА 🔴)", fg=self.text_color)
        elif command == "CHAMELEON_BLACK":
            self.cham_header.config(text="ХАМЕЛЕОН (ЧЁРНЫЙ СТЕЛС 🟢)", fg="#89b4fa")
        elif command == "CHAMELEON_RAINBOW":
            self.cham_header.config(text="ХАМЕЛЕОН (РАДУЖНЫЙ ДИСКО 🟢)", fg="#f5c2e7")
        elif command == "CHAMELEON_MONO":
            self.cham_header.config(text="ХАМЕЛЕОН (МОНОХРОМНЫЙ 🟢)", fg="#a6adc8")
        elif command == "TROLL:BATTERY":
            self.troll_header.config(text="ТРОЛЛИНГ: БАТАРЕЯ 5% 🔋", fg="#f38ba8")
        elif command == "TROLL:DISCORD":
            self.troll_header.config(text="ТРОЛЛИНГ: ЗВОНОК DISCORD 📞", fg="#89b4fa")
        elif command == "TROLL:BSOD":
            self.troll_header.config(text="ТРОЛЛИНГ: СИНИЙ ЭКРАН (BSOD) 💻", fg="#89dceb")
        elif command == "TROLL:DEFENDER":
            self.troll_header.config(text="ТРОЛЛИНГ: ЗАЩИТНИК DEFENDER 🛡️", fg="#fab387")

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
