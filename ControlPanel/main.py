import tkinter as tk
from tkinter import ttk
import socket
import threading

class ModernControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("osu! Chaos Remote")
        self.root.geometry("450x850")
        self.root.configure(bg="#1e1e2e")
        self.root.attributes("-topmost", True)
        self.root.resizable(False, True)
        
        # --- Цветовая палитра ---
        self.bg_color = "#1e1e2e"
        self.panel_color = "#313244"
        self.text_color = "#cdd6f4"
        self.accent_on = "#f38ba8"
        self.accent_off = "#a6e3a1"
        self.accent_blue = "#89b4fa"
        self.accent_yellow = "#f9e2af"
        self.accent_earth = "#fab387"
        self.accent_blackout = "#cba6f7"
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TScale", background=self.panel_color, troughcolor=self.bg_color)
        
        # --- Настройка стилей вкладок ---
        style.configure("TNotebook", background=self.bg_color, borderwidth=0)
        style.configure("TNotebook.Tab", background=self.panel_color, foreground=self.text_color, padding=[15, 5], font=("Segoe UI", 10, "bold"))
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

        # Вкладка 1: Основные эффекты
        tab1 = ttk.Frame(notebook)
        notebook.add(tab1, text="Геймплей")
        
        # Вкладка 2: Искажения экрана (со скроллом)
        tab2_outer = ttk.Frame(notebook)
        notebook.add(tab2_outer, text="Экран")
        
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
            # Прокрутка колесиком мыши только если курсор над tab2_canvas
            if tab2_canvas.winfo_ismapped():
                tab2_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
                
        # Привязываем скролл к root, но он будет работать только если вкладка открыта
        root.bind_all("<MouseWheel>", _on_mousewheel)

        # Вкладка 3: События
        tab3 = ttk.Frame(notebook)
        notebook.add(tab3, text="Ивенты")

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


        # ==========================================
        # Вкладка 2: ЭКРАН (Землетрясение, Искажение)
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

        # Статус бар
        self.status_label = tk.Label(root, text="Готово к подключению", font=("Segoe UI", 9), bg=self.bg_color, fg="#6c7086")
        self.status_label.pack(side=tk.BOTTOM, pady=5)

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

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernControlPanel(root)
    root.mainloop()
