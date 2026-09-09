import tkinter as tk
from tkinter import ttk
import socket
import threading
import time
import ctypes

class ModernControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("osu! Chaos Remote • Control Panel")
        self.root.geometry("560x900")
        self.root.minsize(500, 700)
        self.root.configure(bg="#181825")  # Catppuccin Mantle
        self.root.attributes("-topmost", True)
        self.root.resizable(True, True)

        # High DPI awareness for Windows
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass

        # --- Цветовая палитра (Catppuccin Mocha + Glow Accents) ---
        self.bg_color = "#181825"         # Mantle
        self.card_color = "#1e1e2e"       # Base
        self.panel_color = "#24273a"      # Surface 0
        self.surface1 = "#313244"         # Surface 1
        self.surface2 = "#45475a"         # Surface 2
        self.text_color = "#cdd6f4"       # Text
        self.text_dim = "#a6adc8"         # Subtext
        self.border_color = "#363a4f"     # Subtle border

        self.accent_green = "#a6e3a1"     # Success / Active (Green)
        self.accent_red = "#f38ba8"       # Danger / Off / Panic (Red)
        self.accent_blue = "#89b4fa"      # Primary Blue
        self.accent_yellow = "#f9e2af"    # Warning / Yellow
        self.accent_peach = "#fab387"     # Orange / Peach
        self.accent_mauve = "#cba6f7"     # Special / Purple
        self.accent_cyan = "#89dceb"      # Cyan
        self.accent_pink = "#f5c2e7"      # Pink
        self.accent_dark = "#11111b"      # Crust

        # Состояния тумблеров (True = Активен, False = Выключен)
        self.toggle_states = {
            "CHAOS": False,
            "WIND": False,
            "MAGNET": False,
            "BLACK_HOLE": False,
            "GRAVITY": False,
            "REPULSION": False,
            "CLONES": False,
            "HIDE_CURSOR": False,
            "BUSY_CURSOR": False,
            "INVERT_X": False,
            "INVERT_Y": False,
            "JAM_K1": False,
            "JAM_K2": False,
            "DRUNK": False,
            "CAROUSEL": False,
            "CS_CHAOS": False,
            "MOSAIC": False,
            "INVERT_COLORS": False,
            "TUNNEL": False,
            "GHOST_SLIDERS": False,
            "MUFFLED": False,
            "PAN_SPIN": False,
            "REVERB": False,
            "BASS_BOOST": False,
            "EARTHQUAKE": False,
            "HIDDEN": False,
            "FREEZE": False,
            "WATERMARK": False,
            "FLY": False,
            "MIRROR_PF_X": False,
            "MIRROR_PF_Y": False,
            "MIRROR_HUD_X": False,
            "PITCH": False,
        }

        # Реестр виджетов тумблеров для синхронного обновления
        self.toggle_widgets = {}

        # Настройки слайдеров по умолчанию
        self.cs_min_val = 0.40
        self.cs_max_val = 1.70

        # Настройки задержки вызова ивентов (для переключения окон)
        self.event_delay_enabled = tk.BooleanVar(value=True)
        self.event_delay_seconds = tk.DoubleVar(value=3.0)
        self.delay_scope = tk.StringVar(value="events")
        self._countdown_job = None
        self._countdown_end_time = 0
        self._countdown_cmd = ""

        # Статус соединения (Auto-Ping)
        self.is_connected = False
        self._stop_ping = threading.Event()

        # Настройка стилей ttk
        self.setup_styles()

        # Построение интерфейса
        self.build_header()
        self.build_quick_bar()
        self.build_search_dropdown()
        self.build_countdown_banner()
        self.build_tabs()
        self.build_footer()

        # Привязка горячих клавиш
        self.root.bind("<Control-r>", lambda e: self.reset_all_debuffs())
        self.root.bind("<Control-R>", lambda e: self.reset_all_debuffs())
        self.root.bind("<Control-f>", lambda e: self.focus_search())
        self.root.bind("<Control-F>", lambda e: self.focus_search())
        self.root.bind("<Escape>", lambda e: self.on_escape_key())

        # Запуск фонового пинга сокета osu!
        self.start_ping_thread()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TNotebook", background=self.bg_color, borderwidth=0, tabmargins=[0, 0, 0, 0])
        style.configure(
            "TNotebook.Tab",
            background=self.panel_color,
            foreground=self.text_dim,
            padding=[14, 8],
            font=("Segoe UI", 9, "bold"),
            borderwidth=0
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", self.accent_blue), ("active", self.surface1)],
            foreground=[("selected", self.accent_dark), ("active", "#ffffff")]
        )
        style.configure("TFrame", background=self.bg_color)
        style.configure(
            "TScale",
            background=self.panel_color,
            troughcolor=self.bg_color,
            sliderlength=18,
            sliderthickness=16
        )
        style.configure(
            "Vertical.TScrollbar",
            background=self.panel_color,
            troughcolor=self.bg_color,
            borderwidth=0,
            arrowsize=12
        )

    # =========================================================================
    # ВЕРХНЯЯ ПАНЕЛЬ: ЗАГОЛОВОК, ПИНГ, RESET ALL, НАСТРОЙКИ
    # =========================================================================
    def build_header(self):
        top_bar = tk.Frame(self.root, bg=self.bg_color)
        top_bar.pack(fill=tk.X, padx=16, pady=(10, 4))

        # Левая часть: логотип и заголовок
        left_box = tk.Frame(top_bar, bg=self.bg_color)
        left_box.pack(side=tk.LEFT, fill=tk.Y)

        title_lbl = tk.Label(
            left_box,
            text="OSU! CHAOS CONTROL",
            font=("Segoe UI Black", 14),
            bg=self.bg_color,
            fg=self.accent_blue
        )
        title_lbl.pack(anchor=tk.W)

        # Индикатор пинга/подключения
        self.ping_indicator = tk.Label(
            left_box,
            text="● ПРОВЕРКА СЕТИ...",
            font=("Segoe UI", 8, "bold"),
            bg=self.bg_color,
            fg=self.accent_yellow,
            cursor="hand2"
        )
        self.ping_indicator.pack(anchor=tk.W)
        self.ping_indicator.bind("<Button-1>", lambda e: self.check_connection_now())

        # Правая часть: кнопки действий
        right_box = tk.Frame(top_bar, bg=self.bg_color)
        right_box.pack(side=tk.RIGHT, fill=tk.Y)

        # Кнопка ПАНИКА / СБРОСИТЬ ВСЁ (Reset All)
        self.panic_btn = tk.Button(
            right_box,
            text="🚨 СБРОСИТЬ ВСЁ",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_red,
            fg=self.accent_dark,
            activebackground="#e06c75",
            activeforeground=self.accent_dark,
            bd=0,
            padx=10,
            pady=4,
            cursor="hand2",
            command=self.reset_all_debuffs
        )
        self.panic_btn.pack(side=tk.LEFT, padx=(0, 6))

        # Бейдж задержки
        self.delay_badge = tk.Label(
            right_box,
            text="⏱️ 3с",
            font=("Segoe UI", 9, "bold"),
            bg=self.panel_color,
            fg=self.accent_yellow,
            padx=8,
            pady=4,
            cursor="hand2"
        )
        self.delay_badge.pack(side=tk.LEFT, padx=(0, 6))
        self.delay_badge.bind("<Button-1>", lambda e: self.open_settings())

        # Шестеренка настроек
        self.settings_btn = tk.Button(
            right_box,
            text="⚙️",
            font=("Segoe UI", 12),
            bg=self.panel_color,
            fg=self.text_color,
            activebackground=self.accent_blue,
            activeforeground=self.accent_dark,
            bd=0,
            padx=7,
            pady=2,
            cursor="hand2",
            command=self.open_settings
        )
        self.settings_btn.pack(side=tk.LEFT)

        # Строка ввода IP (компактная карточка)
        ip_frame = tk.Frame(self.root, bg=self.panel_color, padx=10, pady=4)
        ip_frame.pack(fill=tk.X, padx=16, pady=(4, 6))

        tk.Label(
            ip_frame,
            text="IP Игрока:",
            font=("Segoe UI", 9, "bold"),
            bg=self.panel_color,
            fg=self.text_dim
        ).pack(side=tk.LEFT)

        self.ip_entry = tk.Entry(
            ip_frame,
            font=("Consolas", 10, "bold"),
            bg=self.bg_color,
            fg=self.accent_green,
            bd=0,
            insertbackground=self.accent_green
        )
        self.ip_entry.insert(0, "127.0.0.1")
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 8))
        self.ip_entry.bind("<FocusOut>", lambda e: self.check_connection_now())

        check_btn = tk.Button(
            ip_frame,
            text="Проверить 📶",
            font=("Segoe UI", 8, "bold"),
            bg=self.surface1,
            fg=self.text_color,
            activebackground=self.accent_blue,
            activeforeground=self.accent_dark,
            bd=0,
            padx=6,
            pady=1,
            cursor="hand2",
            command=self.check_connection_now
        )
        check_btn.pack(side=tk.RIGHT)

    # =========================================================================
    # БЫСТРЫЙ ПОИСК И ПАНЕЛЬ ИЗБРАННОГО
    # =========================================================================
    def build_quick_bar(self):
        quick_frame = tk.Frame(self.root, bg=self.bg_color)
        quick_frame.pack(fill=tk.X, padx=16, pady=(0, 6))

        # 1. Поле быстрого поиска (Search Bar)
        search_box = tk.Frame(quick_frame, bg=self.panel_color, padx=8, pady=3)
        search_box.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            search_box,
            text="🔍",
            font=("Segoe UI", 10),
            bg=self.panel_color,
            fg=self.text_dim
        ).pack(side=tk.LEFT, padx=(0, 6))

        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(
            search_box,
            textvariable=self.search_var,
            font=("Segoe UI", 9),
            bg=self.panel_color,
            fg=self.text_color,
            bd=0,
            insertbackground=self.text_color
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.insert(0, "Быстрый поиск (Ctrl+F)...")
        self.search_entry.bind("<FocusIn>", self._on_search_focus_in)
        self.search_entry.bind("<FocusOut>", self._on_search_focus_out)
        self.search_var.trace_add("write", self._on_search_change)

        self.search_clear_btn = tk.Label(
            search_box,
            text="✕",
            font=("Segoe UI", 9, "bold"),
            bg=self.panel_color,
            fg=self.text_dim,
            cursor="hand2"
        )
        self.search_clear_btn.pack(side=tk.RIGHT, padx=4)
        self.search_clear_btn.bind("<Button-1>", lambda e: self.clear_search())

        # 2. Панель избранного / Топ-5 частых пранков
        fav_frame = tk.Frame(quick_frame, bg=self.bg_color)
        fav_frame.pack(fill=tk.X)

        tk.Label(
            fav_frame,
            text="⭐ Топ:",
            font=("Segoe UI", 8, "bold"),
            bg=self.bg_color,
            fg=self.accent_yellow
        ).pack(side=tk.LEFT, padx=(0, 4))

        top_actions = [
            ("🧩 Каптча", "TROLL:CAPTCHA", self.accent_green),
            ("🌪️ Срыв мыши", "TROLL:SPINOUT", self.accent_peach),
            ("💻 BSOD", "TROLL:BSOD", self.accent_blue),
            ("📱 Мамуля", "TROLL:TELEGRAM", self.accent_cyan),
            ("🫨 Дрожание", "JITTER:25", self.accent_mauve),
        ]

        for text, cmd, color in top_actions:
            btn = tk.Button(
                fav_frame,
                text=text,
                font=("Segoe UI", 8, "bold"),
                bg=self.panel_color,
                fg=color,
                activebackground=color,
                activeforeground=self.accent_dark,
                bd=0,
                padx=6,
                pady=2,
                cursor="hand2",
                command=lambda c=cmd: self.send_command(c)
            )
            btn.pack(side=tk.LEFT, padx=2, fill=tk.X, expand=True)

    def _init_search_database(self):
        return [
            ("Каптча: Случайная (Пауза)", "TROLL:CAPTCHA:RANDOM", "Пранк", self.accent_green),
            ("Каптча: Математика 2x2", "TROLL:CAPTCHA:MATH", "Пранк", self.accent_green),
            ("Каптча: reCAPTCHA (Я не робот)", "TROLL:CAPTCHA:RECAPTCHA", "Пранк", self.accent_green),
            ("Каптча: Загадка osu! 2x2", "TROLL:CAPTCHA:TRIVIA", "Пранк", self.accent_green),
            ("Срыв сенсора мыши (в угол)", "TROLL:SPINOUT", "Курсор", self.accent_peach),
            ("Отключение мыши (1.8s + звук)", "DEVICE_DISCONNECT", "Курсор", self.accent_red),
            ("Синий экран смерти (BSOD)", "TROLL:BSOD", "Пранк", self.accent_blue),
            ("Звонок Telegram (Мамуля)", "TROLL:TELEGRAM", "Пранк", self.accent_cyan),
            ("Звонок Discord", "TROLL:DISCORD", "Пранк", "#5865F2"),
            ("Steam сообщение (Шаурма)", "TROLL:STEAM", "Пранк", "#66c0f4"),
            ("3D Стук в дверь (звук)", "TROLL:KNOCK", "Звук", self.accent_yellow),
            ("Писк комара (звук 1)", "TROLL:MOSQUITO:1", "Звук", self.accent_yellow),
            ("Донат от Папича (5000₽)", "TROLL:DONATE", "Пранк", self.accent_peach),
            ("Обновление Windows (3.5s)", "TROLL:UPDATE", "Пранк", self.accent_blue),
            ("Отвал видеокарты (Глитч)", "TROLL:GLITCH", "Пранк", self.accent_pink),
            ("Сбой видеодрайвера (Черный экран)", "TROLL:GPU_CRASH", "Пранк", "#76b900"),
            ("Залипание клавиш Windows", "TROLL:STICKYKEYS", "Пранк", self.accent_mauve),
            ("Трясущиеся руки (Джиттер 25px)", "JITTER:25", "Курсор", self.accent_mauve),
            ("Инпут-лаг (200 ms)", "INPUT_LAG:200", "Курсор", self.accent_red),
            ("Армия клонов курсора (10)", "CLONES_ON", "Курсор", self.accent_pink),
            ("Скрыть курсор (Невидимка)", "HIDE_CURSOR:ON", "Курсор", self.accent_red),
            ("Колесико загрузки курсора", "BUSY_CURSOR_ON", "Курсор", self.accent_cyan),
            ("Бочка 360° (Вращение экрана)", "BARREL_ROLL", "Экран", self.accent_mauve),
            ("Пьяная камера (Качка)", "DRUNK_ON", "Экран", self.accent_yellow),
            ("Ограничение 15 FPS (Слайдшоу)", "SET_FPS:15", "Экран", self.accent_peach),
            ("Эффект 144p (Мозаика)", "MOSAIC_ON", "Экран", self.accent_cyan),
            ("Инверсия цветов (Негатив)", "INVERT_COLORS_ON", "Экран", self.accent_yellow),
            ("Туннельное зрение (Фонарик)", "TUNNEL_ON", "Экран", self.accent_cyan),
            ("Невидимые слайдеры", "GHOST_SLIDERS_ON", "Экран", self.accent_mauve),
            ("Звук под водой (Low-Pass)", "MUFFLED_ON", "Звук", self.accent_blue),
            ("8D Панорама (Вращение)", "PAN_SPIN_ON", "Звук", self.accent_pink),
            ("Остановка винила (Tape Stop)", "TAPE_STOP", "Звук", self.accent_peach),
            ("Эхо в соборе (Reverb)", "REVERB_ON", "Звук", self.accent_mauve),
            ("Bass Boost / Ear Rape", "BASS_BOOST_ON", "Звук", self.accent_red),
            ("Землетрясение интерфейса", "EARTHQUAKE_ON", "Экран", self.accent_peach),
            ("Flashbang (Вспышка)", "FLASHBANG", "Пранк", "#ffffff"),
            ("Блэкаут (Остановка времени)", "FREEZE_ON", "Геймплей", self.accent_mauve),
            ("Муха на мониторе", "FLY_ON", "Пранк", self.accent_green),
        ]

    def build_search_dropdown(self):
        self.search_results_frame = tk.Frame(
            self.root,
            bg=self.card_color,
            highlightthickness=1,
            highlightbackground=self.accent_blue,
            padx=6,
            pady=6
        )
        self.search_db = self._init_search_database()

    def _on_search_focus_in(self, event):
        if self.search_entry.get() == "Быстрый поиск (Ctrl+F)...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=self.text_color)

    def _on_search_focus_out(self, event):
        if not self.search_entry.get().strip():
            self.search_entry.insert(0, "Быстрый поиск (Ctrl+F)...")
            self.search_entry.config(fg=self.text_dim)

    def _on_search_change(self, *args):
        query = self.search_var.get().strip().lower()
        if not query or query == "быстрый поиск (ctrl+f)...":
            if self.search_results_frame.winfo_ismapped():
                self.search_results_frame.pack_forget()
            return

        matches = []
        for name, cmd, cat, col in self.search_db:
            if query in name.lower() or query in cat.lower() or query in cmd.lower():
                matches.append((name, cmd, cat, col))

        for child in self.search_results_frame.winfo_children():
            child.destroy()

        if not matches:
            tk.Label(
                self.search_results_frame,
                text="Ничего не найдено",
                font=("Segoe UI", 9),
                bg=self.card_color,
                fg=self.text_dim
            ).pack(pady=4)
        else:
            for name, cmd, cat, col in matches[:6]:
                row = tk.Frame(self.search_results_frame, bg=self.panel_color, padx=6, pady=3)
                row.pack(fill=tk.X, pady=2)

                tk.Label(
                    row,
                    text=f"[{cat}]",
                    font=("Segoe UI", 8, "bold"),
                    bg=self.panel_color,
                    fg=col,
                    width=9,
                    anchor=tk.W
                ).pack(side=tk.LEFT)

                tk.Label(
                    row,
                    text=name,
                    font=("Segoe UI", 9),
                    bg=self.panel_color,
                    fg=self.text_color,
                    anchor=tk.W
                ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=4)

                tk.Button(
                    row,
                    text="Запуск ▶",
                    font=("Segoe UI", 8, "bold"),
                    bg=col,
                    fg=self.accent_dark,
                    activebackground=self.accent_green,
                    activeforeground=self.accent_dark,
                    bd=0,
                    padx=8,
                    pady=1,
                    cursor="hand2",
                    command=lambda c=cmd: [self.clear_search(), self.send_command(c)]
                ).pack(side=tk.RIGHT)

        if not self.search_results_frame.winfo_ismapped():
            self.search_results_frame.pack(fill=tk.X, padx=16, pady=(0, 6), before=self.notebook)

    def clear_search(self):
        self.search_var.set("")
        if self.search_results_frame.winfo_ismapped():
            self.search_results_frame.pack_forget()
        self.root.focus_set()

    def focus_search(self):
        self.search_entry.focus_set()
        self.search_entry.select_range(0, tk.END)

    def on_escape_key(self):
        if self._countdown_job is not None:
            self.cancel_countdown()
        else:
            self.clear_search()

    # =========================================================================
    # БАННЕР ОБРАТНОГО ОТСЧЕТА (Alt-Tab Delay)
    # =========================================================================
    def build_countdown_banner(self):
        self.countdown_banner = tk.Frame(
            self.root,
            bg=self.panel_color,
            highlightthickness=1,
            highlightbackground=self.accent_yellow,
            padx=12,
            pady=8
        )
        top_row = tk.Frame(self.countdown_banner, bg=self.panel_color)
        top_row.pack(fill=tk.X)

        self.countdown_lbl = tk.Label(
            top_row,
            text="",
            font=("Segoe UI", 10, "bold"),
            bg=self.panel_color,
            fg=self.accent_yellow
        )
        self.countdown_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.countdown_cancel_btn = tk.Button(
            top_row,
            text="✕ Отмена (Esc)",
            font=("Segoe UI", 9, "bold"),
            bg=self.accent_red,
            fg=self.accent_dark,
            activebackground="#e06c75",
            activeforeground=self.accent_dark,
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.cancel_countdown
        )
        self.countdown_cancel_btn.pack(side=tk.RIGHT)

        self.countdown_canvas = tk.Canvas(
            self.countdown_banner,
            height=4,
            bg=self.bg_color,
            highlightthickness=0
        )
        self.countdown_canvas.pack(fill=tk.X, pady=(6, 0))

    # =========================================================================
    # ВКЛАДКИ (Notebook & Scrollbars)
    # =========================================================================
    def build_tabs(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=16, pady=4)

        # 1. Геймплей
        self.tab1, tab1_canvas = self._create_scrollable_tab(self.notebook, "⚡ Геймплей")
        # 2. Курсор & Ввод
        self.tab_cursor, tab_cursor_canvas = self._create_scrollable_tab(self.notebook, "🖱️ Курсор")
        # 3. Искажения & Аудио
        self.tab2, tab2_canvas = self._create_scrollable_tab(self.notebook, "🌀 Искажения")
        # 4. Пранки & Ивенты
        self.tab3, tab3_canvas = self._create_scrollable_tab(self.notebook, "🎭 Пранки")
        # 5. Радар нот
        self.tab4 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab4, text="🎯 Радар")

        def _on_mousewheel(event):
            delta = int(-1 * (event.delta / 120))
            selected_text = self.notebook.tab(self.notebook.select(), "text")
            if "Геймплей" in selected_text:
                tab1_canvas.yview_scroll(delta, "units")
            elif "Курсор" in selected_text:
                tab_cursor_canvas.yview_scroll(delta, "units")
            elif "Искажения" in selected_text:
                tab2_canvas.yview_scroll(delta, "units")
            elif "Пранки" in selected_text:
                tab3_canvas.yview_scroll(delta, "units")

        self.root.bind_all("<MouseWheel>", _on_mousewheel)

        self.populate_tab_gameplay(self.tab1)
        self.populate_tab_cursor(self.tab_cursor)
        self.populate_tab_distortions(self.tab2)
        self.populate_tab_pranks(self.tab3)
        self.populate_tab_radar(self.tab4)

    def _create_scrollable_tab(self, notebook, title):
        outer = ttk.Frame(notebook)
        notebook.add(outer, text=title)

        canvas = tk.Canvas(outer, bg=self.bg_color, highlightthickness=0)
        scrollbar = ttk.Scrollbar(outer, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg=self.bg_color)

        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        window_id = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_canvas_configure(e):
            canvas.itemconfig(window_id, width=e.width)

        def _on_inner_configure(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        canvas.bind("<Configure>", _on_canvas_configure)
        inner.bind("<Configure>", _on_inner_configure)

        return inner, canvas

    def create_card(self, parent, title: str, subtitle: str = None, accent_color: str = None):
        if accent_color is None:
            accent_color = self.accent_blue

        frame = tk.Frame(
            parent,
            bg=self.card_color,
            highlightthickness=1,
            highlightbackground=self.border_color,
            padx=14,
            pady=10
        )
        frame.pack(fill=tk.X, pady=4)

        header_row = tk.Frame(frame, bg=self.card_color)
        header_row.pack(fill=tk.X, pady=(0, 2))

        title_lbl = tk.Label(
            header_row,
            text=title,
            font=("Segoe UI", 10, "bold"),
            bg=self.card_color,
            fg=self.text_color
        )
        title_lbl.pack(side=tk.LEFT)

        if subtitle:
            sub_lbl = tk.Label(
                frame,
                text=subtitle,
                font=("Segoe UI", 8),
                bg=self.card_color,
                fg=self.text_dim,
                wraplength=480,
                justify=tk.LEFT
            )
            sub_lbl.pack(anchor=tk.W, pady=(0, 6))

        return frame, title_lbl

    def create_toggle_card(self, parent, key: str, title: str, subtitle: str, on_cmd: str, off_cmd: str, accent_color: str = None):
        if accent_color is None:
            accent_color = self.accent_green

        card, title_lbl = self.create_card(parent, title, subtitle, accent_color)

        btn_row = tk.Frame(card, bg=self.card_color)
        btn_row.pack(fill=tk.X, pady=(2, 0))

        status_badge = tk.Label(
            btn_row,
            text="⚪ ВЫКЛЮЧЕНО",
            font=("Segoe UI", 8, "bold"),
            bg=self.surface1,
            fg=self.text_dim,
            padx=8,
            pady=3
        )
        status_badge.pack(side=tk.LEFT, padx=(0, 8))

        toggle_btn = tk.Button(
            btn_row,
            text="ВКЛЮЧИТЬ ▶",
            font=("Segoe UI", 9, "bold"),
            bg=self.panel_color,
            fg=self.text_color,
            activebackground=accent_color,
            activeforeground=self.accent_dark,
            bd=0,
            padx=12,
            pady=3,
            cursor="hand2"
        )
        toggle_btn.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        def _on_click():
            is_active = self.toggle_states.get(key, False)
            new_state = not is_active
            cmd = on_cmd if new_state else off_cmd
            self.send_command(cmd)

        toggle_btn.config(command=_on_click)

        self.toggle_widgets[key] = {
            "btn": toggle_btn,
            "badge": status_badge,
            "title": title_lbl,
            "accent": accent_color,
            "base_title": title,
            "on_cmd": on_cmd,
            "off_cmd": off_cmd
        }

        return card

    def update_toggle_visual(self, key: str, is_on: bool):
        self.toggle_states[key] = is_on
        w = self.toggle_widgets.get(key)
        if not w:
            return

        accent = w["accent"]
        if is_on:
            if w.get("badge"):
                w["badge"].config(text="🟢 АКТИВЕН", bg=accent, fg=self.accent_dark)
            if w.get("btn"):
                if w.get("badge") is not None:
                    w["btn"].config(text="ВЫКЛЮЧИТЬ ⏹️", bg=self.accent_red, fg=self.accent_dark)
                else:
                    base_txt = w.get("base_text", "")
                    w["btn"].config(text=f"🟢 {base_txt}", bg=accent, fg=self.accent_dark)
            if w.get("title"):
                w["title"].config(fg=accent)
        else:
            if w.get("badge"):
                w["badge"].config(text="⚪ ВЫКЛЮЧЕНО", bg=self.surface1, fg=self.text_dim)
            if w.get("btn"):
                if w.get("badge") is not None:
                    w["btn"].config(text="ВКЛЮЧИТЬ ▶", bg=self.panel_color, fg=self.text_color)
                else:
                    base_txt = w.get("base_text", "")
                    w["btn"].config(text=f"⚪ {base_txt}", bg=self.surface1, fg=self.text_color)
            if w.get("title"):
                w["title"].config(fg=self.text_color)

    def create_slider_row(self, parent, label: str, from_val: float, to_val: float, default_val: float, format_str: str, on_change, reset_cmd: str = None):
        row = tk.Frame(parent, bg=self.card_color)
        row.pack(fill=tk.X, pady=(4, 2))

        top_info = tk.Frame(row, bg=self.card_color)
        top_info.pack(fill=tk.X, pady=(0, 2))

        lbl = tk.Label(top_info, text=label, font=("Segoe UI", 9), bg=self.card_color, fg=self.text_color)
        lbl.pack(side=tk.LEFT)

        initial_txt = format_str.format(int(round(default_val))) if "d" in format_str else format_str.format(default_val)
        val_badge = tk.Label(
            top_info,
            text=initial_txt,
            font=("Segoe UI", 9, "bold"),
            bg=self.surface1,
            fg=self.accent_yellow,
            padx=6,
            pady=1
        )
        val_badge.pack(side=tk.RIGHT)

        slider_frame = tk.Frame(row, bg=self.card_color)
        slider_frame.pack(fill=tk.X)

        scale = ttk.Scale(slider_frame, from_=from_val, to=to_val, orient=tk.HORIZONTAL)
        scale.set(default_val)
        scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        def _on_move(val):
            num = float(val)
            if "d" in format_str:
                val_badge.config(text=format_str.format(int(round(num))))
            else:
                val_badge.config(text=format_str.format(num))
            on_change(num)

        scale.config(command=_on_move)

        def _reset():
            scale.set(default_val)
            if "d" in format_str:
                val_badge.config(text=format_str.format(int(round(default_val))))
            else:
                val_badge.config(text=format_str.format(default_val))
            if reset_cmd:
                self.send_command(reset_cmd)
            else:
                on_change(default_val)

        reset_btn = tk.Button(
            slider_frame,
            text="⟲",
            font=("Segoe UI", 10),
            bg=self.surface1,
            fg=self.accent_blue,
            activebackground=self.accent_blue,
            activeforeground=self.accent_dark,
            bd=0,
            padx=6,
            pady=0,
            cursor="hand2",
            command=_reset
        )
        reset_btn.pack(side=tk.RIGHT)

        return scale, val_badge

    # =========================================================================
    # ВКЛАДКА 1: ГЕЙМПЛЕЙ (Хаос, Ветер, Магнит, Черная Дыра, Скорость, Гравитация)
    # =========================================================================
    def populate_tab_gameplay(self, tab):
        card1 = self.create_toggle_card(
            tab, "CHAOS", "1. ХАОС НОТ (РАЗБРОС)",
            "Случайное орбитальное смещение всех нот по синусоиде",
            "CHAOS_ON", "CHAOS_OFF", self.accent_peach
        )
        self.create_slider_row(
            card1, "Сила хаоса:", 0.0, 2.0, 1.0, "{:.2f}x",
            lambda v: self.send_command(f"STRENGTH:{v:.2f}")
        )

        card2 = self.create_toggle_card(
            tab, "WIND", "2. ВЕТЕР НА ИГРОВОМ ПОЛЕ",
            "Непрерывный поток ветра, сносящий круги в заданном направлении",
            "WIND_ON", "WIND_OFF", self.accent_blue
        )
        self.create_slider_row(
            card2, "Сила ветра:", 0.0, 3.0, 1.0, "{:.2f}x",
            lambda v: self.send_command(f"WIND_STRENGTH:{v:.2f}")
        )
        self.create_slider_row(
            card2, "Направление (Градусы):", 0.0, 360.0, 0.0, "{:.0f}°",
            lambda v: self.send_command(f"WIND_DIR:{v:.2f}")
        )

        card3 = self.create_toggle_card(
            tab, "MAGNET", "3. МАГНИТНОЕ ОТТАЛКИВАНИЕ НОТ",
            "Ноты физически отталкиваются от курсора игрока при приближении",
            "MAGNET_ON", "MAGNET_OFF", self.accent_yellow
        )
        self.create_slider_row(
            card3, "Сила отталкивания:", 0.0, 3.0, 1.0, "{:.2f}x",
            lambda v: self.send_command(f"MAGNET_STRENGTH:{v:.2f}")
        )

        card4 = self.create_toggle_card(
            tab, "BLACK_HOLE", "4. ЧЁРНАЯ ДЫРА (ГРАВИТАЦИЯ В ЦЕНТР)",
            "Затягивает все объекты карты в сингулярность (256, 192)",
            "BLACK_HOLE_ON", "BLACK_HOLE_OFF", self.accent_mauve
        )
        self.bh_scale, self.bh_badge = self.create_slider_row(
            card4, "Сила гравитации:", 0.0, 4.0, 1.0, "{:.2f}x",
            lambda v: self.send_command(f"BLACK_HOLE_STRENGTH:{v:.2f}")
        )

        p_row = tk.Frame(card4, bg=self.card_color)
        p_row.pack(fill=tk.X, pady=(4, 0))
        for txt, val in [("0.5x", 0.5), ("1.0x", 1.0), ("2.0x", 2.0), ("4.0x Сингулярность", 4.0)]:
            tk.Button(
                p_row, text=txt, font=("Segoe UI", 8, "bold"),
                bg=self.surface1, fg=self.text_color, activebackground=self.accent_mauve,
                activeforeground=self.accent_dark, bd=0, padx=6, pady=2, cursor="hand2",
                command=lambda v=val: [self.bh_scale.set(v), self.bh_badge.config(text=f"{v:.2f}x"), self.send_command(f"BLACK_HOLE_STRENGTH:{v:.2f}")]
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.create_toggle_card(
            tab, "GRAVITY", "5. ГРАВИТАЦИЯ (ПАДАЮЩИЕ НОТЫ)",
            "Ноты падают вниз под силой тяжести после появления",
            "GRAVITY_ON", "GRAVITY_OFF", self.accent_peach
        )

        card_speed, _ = self.create_card(tab, "6. СКОРОСТЬ ИГРЫ (TIME RATE)", "Ускорение или замедление воспроизведения карты", self.accent_cyan)
        self.create_slider_row(
            card_speed, "Множитель скорости:", 0.1, 2.5, 1.0, "{:.2f}x",
            lambda v: self.send_command(f"SPEED:{v:.2f}"), "SPEED:1.00"
        )
        self.pitch_var = tk.IntVar()
        chk_pitch = tk.Checkbutton(
            card_speed,
            text="Эффект бурундука (изменять тональность при смене скорости)",
            variable=self.pitch_var,
            font=("Segoe UI", 8),
            bg=self.card_color,
            fg=self.text_color,
            selectcolor=self.bg_color,
            activebackground=self.card_color,
            activeforeground=self.text_color,
            command=lambda: self.send_command("PITCH_ON" if self.pitch_var.get() else "PITCH_OFF")
        )
        chk_pitch.pack(anchor=tk.W, pady=(4, 0))

        card_scale, _ = self.create_card(tab, "7. МАСШТАБИРОВАНИЕ", "Искажение размера игрового поля и элементов интерфейса", self.accent_blue)
        self.create_slider_row(
            card_scale, "Игровое поле (Playfield):", 0.1, 2.0, 1.0, "{:.2f}x",
            lambda v: self.send_command(f"SCALE:{v:.2f}"), "SCALE:1.00"
        )
        self.create_slider_row(
            card_scale, "Интерфейс (HUD):", 0.1, 2.0, 1.0, "{:.2f}x",
            lambda v: self.send_command(f"HUD_SCALE:{v:.2f}"), "HUD_SCALE:1.00"
        )

    # =========================================================================
    # ВКЛАДКА 2: КУРСОР & ВВОД (Физика, Дрожание, Лаг, Мышь, Инверсия, Клавиши)
    # =========================================================================
    def populate_tab_cursor(self, tab):
        card_spin, _ = self.create_card(
            tab, "1. СРЫВ СЕНСОРА МЫШИ 🌪️",
            "Курсор за 80 мс срывается в угол с высокочастотным джиттером и звуком сбоя",
            self.accent_peach
        )
        btn_spin = tk.Button(
            card_spin,
            text="🌪️ СОРВАТЬ СЕНСОР МЫШИ В УГОЛ 🖱️",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_peach,
            fg=self.accent_dark,
            activebackground=self.accent_yellow,
            activeforeground=self.accent_dark,
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self.send_command("TROLL:SPINOUT")
        )
        btn_spin.pack(fill=tk.X, pady=2)

        self.create_toggle_card(
            tab, "REPULSION", "2. ОТТАЛКИВАНИЕ КУРСОРА ОТ НОТ 🧲",
            "Курсор физически смещается в сторону при наведении на хит-серклы",
            "REPULSION_ON", "REPULSION_OFF", self.accent_yellow
        )

        card_jit, _ = self.create_card(
            tab, "3. ТРЯСУЩИЕСЯ РУКИ (ДЖИТТЕР КУРСОРА)",
            "Высокочастотная вибрация курсора (эффект дрожания рук от адреналина)",
            self.accent_mauve
        )
        self.jit_scale, self.jit_badge = self.create_slider_row(
            card_jit, "Амплитуда джиттера:", 0, 50, 0, "{:.0f} px",
            lambda v: self.send_command(f"JITTER:{int(v)}"), "JITTER:0"
        )
        j_presets = tk.Frame(card_jit, bg=self.card_color)
        j_presets.pack(fill=tk.X, pady=(4, 0))
        for txt, val, col in [("0 px (Выкл)", 0, self.surface1), ("8 px", 8, self.surface1), ("18 px", 18, self.accent_yellow), ("35 px (Паника)", 35, self.accent_red)]:
            tk.Button(
                j_presets, text=txt, font=("Segoe UI", 8, "bold"),
                bg=col if col != self.surface1 else self.surface1,
                fg=self.accent_dark if col != self.surface1 else self.text_color,
                bd=0, padx=6, pady=2, cursor="hand2",
                command=lambda v=val: [self.jit_scale.set(v), self.jit_badge.config(text=f"{v} px"), self.send_command(f"JITTER:{v}")]
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        card_lag, _ = self.create_card(
            tab, "4. ИНПУТ-ЛАГ (ЗАДЕРЖКА КООРДИНАТ)",
            "Физически задерживает координаты и клики. Полностью ломает мышечную память!",
            self.accent_red
        )
        self.lag_scale, self.lag_badge = self.create_slider_row(
            card_lag, "Задержка ввода:", 0, 500, 0, "{:.0f} ms",
            lambda v: self.send_command(f"INPUT_LAG:{int(v)}"), "INPUT_LAG:0"
        )
        l_presets = tk.Frame(card_lag, bg=self.card_color)
        l_presets.pack(fill=tk.X, pady=(4, 0))
        for txt, val, col in [("Выкл", 0, self.surface1), ("50 ms", 50, self.surface1), ("100 ms", 100, self.surface1), ("200 ms", 200, self.accent_yellow), ("300 ms", 300, self.accent_peach), ("500 ms (Ад)", 500, self.accent_red)]:
            tk.Button(
                l_presets, text=txt, font=("Segoe UI", 8, "bold"),
                bg=col if col != self.surface1 else self.surface1,
                fg=self.accent_dark if col != self.surface1 else self.text_color,
                bd=0, padx=4, pady=2, cursor="hand2",
                command=lambda v=val: [self.lag_scale.set(v), self.lag_badge.config(text=f"{v} ms"), self.send_command(f"INPUT_LAG:{v}")]
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        card_clones = self.create_toggle_card(
            tab, "CLONES", "5. АРМИЯ КЛОНОВ (10 КУРСОРОВ) 👥",
            "Создает 10 курсоров-обманок, копирующих клики и траекторию игрока",
            "CLONES_ON", "CLONES_OFF", self.accent_pink
        )
        fc_row = tk.Frame(card_clones, bg=self.card_color)
        fc_row.pack(fill=tk.X, pady=(6, 0))
        for txt, cmd in [("Зеркало X", "FAKE_CURSORS:MIRROR_X"), ("Зеркало Y", "FAKE_CURSORS:MIRROR_Y"), ("X+Y", "FAKE_CURSORS:MIRROR_XY"), ("Рой (Swarm)", "FAKE_CURSORS:SWARM")]:
            tk.Button(
                fc_row, text=txt, font=("Segoe UI", 8, "bold"),
                bg=self.surface1, fg=self.text_color, activebackground=self.accent_blue,
                activeforeground=self.accent_dark, bd=0, padx=6, pady=2, cursor="hand2",
                command=lambda c=cmd: self.send_command(c)
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        self.create_toggle_card(
            tab, "HIDE_CURSOR", "6. НЕВИДИМЫЙ КУРСОР 👻",
            "Скрывает спрайт курсора, оставляя только хвостовой след",
            "HIDE_CURSOR:ON", "HIDE_CURSOR:OFF", self.accent_red
        )

        self.create_toggle_card(
            tab, "BUSY_CURSOR", "7. КОЛЁСИКО ЗАГРУЗКИ (BUSY CURSOR) ⏳",
            "Вращающийся системный спиннер Windows прямо на кончике курсора",
            "BUSY_CURSOR_ON", "BUSY_CURSOR_OFF", self.accent_cyan
        )

        card_cscale, _ = self.create_card(tab, "8. РАЗМЕР КУРСОРА", "Масштабирование спрайта курсора игрока", self.accent_yellow)
        self.cscale_slider, self.cscale_badge = self.create_slider_row(
            card_cscale, "Масштаб:", 0.1, 5.0, 1.0, "{:.2f}x",
            lambda v: self.send_command(f"CURSOR_SCALE:{v:.2f}"), "CURSOR_SCALE:1.00"
        )
        cs_presets = tk.Frame(card_cscale, bg=self.card_color)
        cs_presets.pack(fill=tk.X, pady=(4, 0))
        for txt, val in [("0.2x Микро", 0.2), ("0.5x", 0.5), ("1.0x Норма", 1.0), ("2.0x", 2.0), ("4.0x Гигант", 4.0)]:
            tk.Button(
                cs_presets, text=txt, font=("Segoe UI", 8, "bold"),
                bg=self.surface1, fg=self.text_color, activebackground=self.accent_yellow,
                activeforeground=self.accent_dark, bd=0, padx=4, pady=2, cursor="hand2",
                command=lambda v=val: [self.cscale_slider.set(v), self.cscale_badge.config(text=f"{v:.2f}x"), self.send_command(f"CURSOR_SCALE:{v:.2f}")]
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        card_inv, _ = self.create_card(tab, "9. ИНВЕРСИЯ ОСЕЙ УПРАВЛЕНИЯ", "Разворачивает движение мыши по горизонтали и/или вертикали", self.accent_peach)
        row_ix = tk.Frame(card_inv, bg=self.card_color)
        row_ix.pack(fill=tk.X, pady=2)
        tk.Label(row_ix, text="Ось X (Горизонталь):", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_color, width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.btn_inv_x = tk.Button(row_ix, text="⚪ НОРМА X", font=("Segoe UI", 8, "bold"), bg=self.surface1, fg=self.text_color, bd=0, padx=8, pady=2, cursor="hand2", command=self.toggle_inv_x)
        self.btn_inv_x.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        row_iy = tk.Frame(card_inv, bg=self.card_color)
        row_iy.pack(fill=tk.X, pady=2)
        tk.Label(row_iy, text="Ось Y (Вертикаль):", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_color, width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.btn_inv_y = tk.Button(row_iy, text="⚪ НОРМА Y", font=("Segoe UI", 8, "bold"), bg=self.surface1, fg=self.text_color, bd=0, padx=8, pady=2, cursor="hand2", command=self.toggle_inv_y)
        self.btn_inv_y.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        row_i_all = tk.Frame(card_inv, bg=self.card_color)
        row_i_all.pack(fill=tk.X, pady=(4, 0))
        tk.Button(row_i_all, text="ИНВЕРТИРОВАТЬ X+Y", font=("Segoe UI", 8, "bold"), bg=self.accent_peach, fg=self.accent_dark, bd=0, padx=6, pady=2, cursor="hand2", command=self.invert_both).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(row_i_all, text="Сброс в норму", font=("Segoe UI", 8, "bold"), bg=self.surface1, fg=self.text_color, bd=0, padx=6, pady=2, cursor="hand2", command=self.invert_reset).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        card_jam, _ = self.create_card(tab, "10. ЗАЛИПАНИЕ КЛАВИШ (K1 / K2)", "Блокирует клики выбранной клавиши (эмуляция зажатой кнопки)", self.accent_red)
        row_jk1 = tk.Frame(card_jam, bg=self.card_color)
        row_jk1.pack(fill=tk.X, pady=2)
        tk.Label(row_jk1, text="Клавиша K1 (Левая):", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_color, width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.btn_jam_k1 = tk.Button(row_jk1, text="⚪ РАБОТАЕТ", font=("Segoe UI", 8, "bold"), bg=self.surface1, fg=self.text_color, bd=0, padx=8, pady=2, cursor="hand2", command=self.toggle_jam_k1)
        self.btn_jam_k1.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        row_jk2 = tk.Frame(card_jam, bg=self.card_color)
        row_jk2.pack(fill=tk.X, pady=2)
        tk.Label(row_jk2, text="Клавиша K2 (Правая):", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_color, width=18, anchor=tk.W).pack(side=tk.LEFT)
        self.btn_jam_k2 = tk.Button(row_jk2, text="⚪ РАБОТАЕТ", font=("Segoe UI", 8, "bold"), bg=self.surface1, fg=self.text_color, bd=0, padx=8, pady=2, cursor="hand2", command=self.toggle_jam_k2)
        self.btn_jam_k2.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        tk.Button(card_jam, text="Разблокировать обе клавиши", font=("Segoe UI", 8, "bold"), bg=self.surface1, fg=self.text_color, bd=0, padx=6, pady=2, cursor="hand2", command=self.jam_reset).pack(fill=tk.X, pady=(4, 0))

    # =========================================================================
    # ВКЛАДКА 3: ИСКАЖЕНИЯ & АУДИО (Экран, Камера, Ноты, Звуки)
    # =========================================================================
    def populate_tab_distortions(self, tab):
        card_cam, _ = self.create_card(tab, "1. КАМЕРА & ВРАЩЕНИЕ ЭКРАНА", "Вращение и качка экрана во время игры", self.accent_mauve)
        row_c1 = tk.Frame(card_cam, bg=self.card_color)
        row_c1.pack(fill=tk.X, pady=2)
        self.create_toggle_btn(row_c1, "DRUNK", "🍾 Пьяная камера (Качка ±15°)", "DRUNK_ON", "DRUNK_OFF", self.accent_yellow)

        row_c2 = tk.Frame(card_cam, bg=self.card_color)
        row_c2.pack(fill=tk.X, pady=2)
        self.create_toggle_btn(row_c2, "CAROUSEL", "🌀 Вечная карусель 360°", "CAROUSEL_ON", "CAROUSEL_OFF", self.accent_mauve)

        tk.Button(
            card_cam,
            text="🔄 БОЧКА / ОДИН ОБОРОТ 360° (3.5s)",
            font=("Segoe UI", 9, "bold"),
            bg=self.surface1,
            fg=self.accent_mauve,
            activebackground=self.accent_mauve,
            activeforeground=self.accent_dark,
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=lambda: self.send_command("BARREL_ROLL")
        ).pack(fill=tk.X, pady=(4, 0))

        card_fps, _ = self.create_card(tab, "2. ОГРАНИЧЕНИЕ FPS (ТРОТТЛИНГ)", "Искусственное занижение частоты кадров игрока", self.accent_peach)
        self.fps_scale, self.fps_badge = self.create_slider_row(
            card_fps, "Целевой FPS:", 10, 240, 60, "{:.0f} FPS",
            lambda v: self.send_command(f"SET_FPS:{int(v)}"), "SET_FPS:0"
        )
        f_presets = tk.Frame(card_fps, bg=self.card_color)
        f_presets.pack(fill=tk.X, pady=(4, 0))
        for txt, val in [("15 FPS", 15), ("30 FPS", 30), ("60 FPS", 60), ("120 FPS", 120), ("Сброс ♾️", 0)]:
            tk.Button(
                f_presets, text=txt, font=("Segoe UI", 8, "bold"),
                bg=self.surface1, fg=self.text_color, activebackground=self.accent_peach,
                activeforeground=self.accent_dark, bd=0, padx=4, pady=2, cursor="hand2",
                command=lambda v=val: [self.fps_scale.set(v if v > 0 else 60), self.fps_badge.config(text=f"{v} FPS" if v > 0 else "Без лимита"), self.send_command(f"SET_FPS:{v}")]
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        card_cs = self.create_toggle_card(
            tab, "CS_CHAOS", "3. ХАОС РАЗМЕРОВ НОТ (CS CHAOS)",
            "Каждая нота получает случайный масштаб: от микроскопической до гигантской",
            "CS_CHAOS_ON", "CS_CHAOS_OFF", self.accent_peach
        )
        self.cs_min_scale, self.cs_min_badge = self.create_slider_row(
            card_cs, "Микро (Min scale):", 0.08, 1.00, 0.40, "{:.2f}x",
            self.on_cs_min_slider
        )
        self.cs_max_scale, self.cs_max_badge = self.create_slider_row(
            card_cs, "Гигантизм (Max scale):", 1.00, 3.50, 1.70, "{:.2f}x",
            self.on_cs_max_slider
        )

        card_vis, _ = self.create_card(tab, "4. ВИЗУАЛЬНЫЕ ДЕБАФФЫ", "Фильтры изображения и скрытие элементов", self.accent_cyan)
        grid_vis = tk.Frame(card_vis, bg=self.card_color)
        grid_vis.pack(fill=tk.X)
        self.create_toggle_btn(grid_vis, "MOSAIC", "🔲 Режим 144p (Мозаика)", "MOSAIC_ON", "MOSAIC_OFF", self.accent_cyan, side=tk.LEFT)
        self.create_toggle_btn(grid_vis, "INVERT_COLORS", "🌗 Негатив / Инверсия", "INVERT_COLORS_ON", "INVERT_COLORS_OFF", self.accent_yellow, side=tk.RIGHT)

        grid_vis2 = tk.Frame(card_vis, bg=self.card_color)
        grid_vis2.pack(fill=tk.X, pady=(4, 0))
        self.create_toggle_btn(grid_vis2, "TUNNEL", "🔦 Туннель (Фонарик)", "TUNNEL_ON", "TUNNEL_OFF", self.accent_cyan, side=tk.LEFT)
        self.create_toggle_btn(grid_vis2, "GHOST_SLIDERS", "👻 Невидимка-слайдеры", "GHOST_SLIDERS_ON", "GHOST_SLIDERS_OFF", self.accent_mauve, side=tk.RIGHT)

        card_shake, _ = self.create_card(tab, "5. ТРЯСКА & СКРЫТИЕ (HIDDEN)", "Землетрясение интерфейса и скрытие нот", self.accent_peach)
        row_sh = tk.Frame(card_shake, bg=self.card_color)
        row_sh.pack(fill=tk.X, pady=(0, 4))
        self.create_toggle_btn(row_sh, "EARTHQUAKE", "🌋 Землетрясение", "EARTHQUAKE_ON", "EARTHQUAKE_OFF", self.accent_peach, side=tk.LEFT)
        self.create_toggle_btn(row_sh, "HIDDEN", "🙈 Слепота (Hidden)", "HIDDEN_ON", "HIDDEN_OFF", self.accent_red, side=tk.RIGHT)
        self.create_slider_row(
            card_shake, "Магнитуда тряски:", 0.0, 3.0, 1.0, "{:.2f}x",
            lambda v: self.send_command(f"EARTHQUAKE_STRENGTH:{v:.2f}")
        )

        card_audio, _ = self.create_card(tab, "6. ЗВУКОВЫЕ ЭФФЕКТЫ (AUDIO HAVOC)", "Искажение аудиопотока и дезориентация", self.accent_blue)
        row_a1 = tk.Frame(card_audio, bg=self.card_color)
        row_a1.pack(fill=tk.X, pady=2)
        self.create_toggle_btn(row_a1, "MUFFLED", "🌊 Под водой (Low-Pass)", "MUFFLED_ON", "MUFFLED_OFF", self.accent_blue, side=tk.LEFT)
        self.create_toggle_btn(row_a1, "PAN_SPIN", "🎧 8D Панорама", "PAN_SPIN_ON", "PAN_SPIN_OFF", self.accent_pink, side=tk.RIGHT)

        row_a2 = tk.Frame(card_audio, bg=self.card_color)
        row_a2.pack(fill=tk.X, pady=2)
        self.create_toggle_btn(row_a2, "REVERB", "⛪ Эхо в соборе", "REVERB_ON", "REVERB_OFF", self.accent_mauve, side=tk.LEFT)
        self.create_toggle_btn(row_a2, "BASS_BOOST", "📢 Bass Boost / Ear Rape", "BASS_BOOST_ON", "BASS_BOOST_OFF", self.accent_red, side=tk.RIGHT)

        tk.Button(
            card_audio,
            text="📼 ЗАЖЕВАЛО ПЛЕНКУ / ОСТАНОВКА ВИНИЛА (TAPE STOP) 🛑",
            font=("Segoe UI", 9, "bold"),
            bg=self.surface1,
            fg=self.accent_peach,
            activebackground=self.accent_peach,
            activeforeground=self.accent_dark,
            bd=0,
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda: self.send_command("TAPE_STOP")
        ).pack(fill=tk.X, pady=(4, 0))

        card_desync, _ = self.create_card(tab, "7. РАССИНХРОН ЗВУКА (AUDIO OFFSET)", "Сдвигает аудио относительно хит-объектов", self.accent_yellow)
        self.desync_scale, self.desync_badge = self.create_slider_row(
            card_desync, "Сдвиг аудио:", -300, 300, 0, "{:+d} ms",
            lambda v: self.send_command(f"AUDIO_DESYNC:{int(v)}"), "AUDIO_DESYNC:0"
        )
        d_presets = tk.Frame(card_desync, bg=self.card_color)
        d_presets.pack(fill=tk.X, pady=(4, 0))
        for txt, val in [("-150ms (Спешит)", -150), ("-75ms", -75), ("0 (Синхрон)", 0), ("+75ms", 75), ("+150ms (Отстает)", 150)]:
            tk.Button(
                d_presets, text=txt, font=("Segoe UI", 8, "bold"),
                bg=self.surface1, fg=self.text_color, activebackground=self.accent_yellow,
                activeforeground=self.accent_dark, bd=0, padx=4, pady=2, cursor="hand2",
                command=lambda v=val: [self.desync_scale.set(v), self.desync_badge.config(text=f"{v:+d} ms"), self.send_command(f"AUDIO_DESYNC:{v}")]
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        card_cham, _ = self.create_card(tab, "8. ХАМЕЛЕОН (ЦВЕТА НОТ)", "Изменение палитры комбо-цветов хит-серклов", self.accent_pink)
        c_row = tk.Frame(card_cham, bg=self.card_color)
        c_row.pack(fill=tk.X)
        for txt, cmd, col in [("Обычные", "CHAMELEON_OFF", self.surface1), ("Черный стелс", "CHAMELEON_BLACK", self.accent_dark), ("Радуга Диско", "CHAMELEON_RAINBOW", self.accent_pink), ("Монохром", "CHAMELEON_MONO", self.text_dim)]:
            tk.Button(
                c_row, text=txt, font=("Segoe UI", 8, "bold"),
                bg=col if col != self.accent_dark else "#000000",
                fg=self.text_color if col != self.accent_pink else self.accent_dark,
                activebackground=self.accent_blue, activeforeground=self.accent_dark,
                bd=0, padx=4, pady=3, cursor="hand2",
                command=lambda c=cmd: self.send_command(c)
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        card_mir, _ = self.create_card(tab, "9. ОТЗЕРКАЛИВАНИЕ", "Инверсия осей отображения игрового поля и HUD", self.accent_peach)
        m_row = tk.Frame(card_mir, bg=self.card_color)
        m_row.pack(fill=tk.X)
        self.create_toggle_btn(m_row, "MIRROR_PF_X", "Поле Ось X", "MIRROR_PLAYFIELD_X_ON", "MIRROR_PLAYFIELD_X_OFF", self.accent_peach, side=tk.LEFT)
        self.create_toggle_btn(m_row, "MIRROR_PF_Y", "Поле Ось Y", "MIRROR_PLAYFIELD_Y_ON", "MIRROR_PLAYFIELD_Y_OFF", self.accent_peach, side=tk.LEFT)
        self.create_toggle_btn(m_row, "MIRROR_HUD_X", "HUD Ось X", "MIRROR_HUD_X_ON", "MIRROR_HUD_X_OFF", self.accent_blue, side=tk.RIGHT)

    def create_toggle_btn(self, parent, key: str, text: str, on_cmd: str, off_cmd: str, accent: str, side=tk.LEFT):
        btn = tk.Button(
            parent,
            text=f"⚪ {text}",
            font=("Segoe UI", 8, "bold"),
            bg=self.surface1,
            fg=self.text_color,
            activebackground=accent,
            activeforeground=self.accent_dark,
            bd=0,
            padx=8,
            pady=3,
            cursor="hand2"
        )
        btn.pack(side=side, fill=tk.X, expand=True, padx=2)

        def _click():
            st = self.toggle_states.get(key, False)
            cmd = on_cmd if not st else off_cmd
            self.send_command(cmd)

        btn.config(command=_click)
        self.toggle_widgets[key] = {
            "btn": btn,
            "badge": None,
            "title": None,
            "accent": accent,
            "base_text": text,
            "on_cmd": on_cmd,
            "off_cmd": off_cmd
        }
        return btn

    # =========================================================================
    # ВКЛАДКА 4: ПРАНКИ & ИВЕНТЫ (Каптча, Звонки, Ошибки, Звуки)
    # =========================================================================
    def populate_tab_pranks(self, tab):
        card_cap, _ = self.create_card(
            tab, "🧩 ИНТЕРАКТИВНАЯ КАПТЧА / ЗАГАДКА (ПАУЗА ИГРЫ)",
            "Останавливает трек и геймплей. Игрок обязан решить задачу, чтобы продолжить!",
            self.accent_green
        )
        tk.Button(
            card_cap,
            text="🎲 СЛУЧАЙНАЯ КАПТЧА (ВЫЗОВ С ПАУЗОЙ) ⏸️",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_green,
            fg=self.accent_dark,
            activebackground=self.accent_yellow,
            activeforeground=self.accent_dark,
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=lambda: self.send_command("TROLL:CAPTCHA:RANDOM")
        ).pack(fill=tk.X, pady=(0, 4))

        c_modes = tk.Frame(card_cap, bg=self.card_color)
        c_modes.pack(fill=tk.X)
        for txt, cmd, col in [("➕ Математика", "TROLL:CAPTCHA:MATH", self.accent_blue), ("🤖 reCAPTCHA", "TROLL:CAPTCHA:RECAPTCHA", self.accent_mauve), ("🧠 Загадка osu!", "TROLL:CAPTCHA:TRIVIA", self.accent_cyan)]:
            tk.Button(
                c_modes, text=txt, font=("Segoe UI", 8, "bold"),
                bg=self.surface1, fg=col, activebackground=col,
                activeforeground=self.accent_dark, bd=0, padx=6, pady=3, cursor="hand2",
                command=lambda c=cmd: self.send_command(c)
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        card_sys, _ = self.create_card(tab, "💻 СИСТЕМНЫЕ СБОИ WINDOWS", "Симуляция фатальных ошибок ОС и железа", self.accent_blue)
        tk.Button(
            card_sys,
            text="💻 СИНИЙ ЭКРАН СМЕРТИ (BSOD НА ВЕСЬ ЭКРАН 3.5s) 💥",
            font=("Segoe UI", 9, "bold"),
            bg="#0078d7",
            fg="#ffffff",
            activebackground=self.accent_cyan,
            activeforeground=self.accent_dark,
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=lambda: self.send_command("TROLL:BSOD")
        ).pack(fill=tk.X, pady=2)

        tk.Button(
            card_sys,
            text="🔄 ОБНОВЛЕНИЕ WINDOWS (Черный экран 3.5s со спиннером) ⚙️",
            font=("Segoe UI", 9, "bold"),
            bg="#005a9e",
            fg="#ffffff",
            activebackground=self.accent_blue,
            activeforeground=self.accent_dark,
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=lambda: self.send_command("TROLL:UPDATE")
        ).pack(fill=tk.X, pady=2)

        row_sys_btns = tk.Frame(card_sys, bg=self.card_color)
        row_sys_btns.pack(fill=tk.X, pady=2)
        tk.Button(
            row_sys_btns, text="⚡ Отвал видеокарты (Глитч)", font=("Segoe UI", 8, "bold"),
            bg=self.surface1, fg=self.accent_pink, bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda: self.send_command("TROLL:GLITCH")
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(
            row_sys_btns, text="🔌 Сбой GPU (1.3s черный)", font=("Segoe UI", 8, "bold"),
            bg=self.surface1, fg="#76b900", bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda: self.send_command("TROLL:GPU_CRASH")
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        row_sys_btns2 = tk.Frame(card_sys, bg=self.card_color)
        row_sys_btns2.pack(fill=tk.X, pady=2)
        tk.Button(
            row_sys_btns2, text="🔋 Батарея 5%", font=("Segoe UI", 8, "bold"),
            bg=self.surface1, fg=self.accent_red, bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda: self.send_command("TROLL:BATTERY")
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(
            row_sys_btns2, text="🛡️ Защитник Windows", font=("Segoe UI", 8, "bold"),
            bg=self.surface1, fg=self.accent_peach, bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda: self.send_command("TROLL:DEFENDER")
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=2)

        self.create_toggle_btn(card_sys, "WATERMARK", "Водяной знак Активация Windows", "WATERMARK_ON", "WATERMARK_OFF", self.accent_yellow)

        card_call, _ = self.create_card(tab, "📱 МЕССЕНДЖЕРЫ И ЗВОНКИ", "Фейковые входящие вызовы и сообщения со звуком", self.accent_cyan)
        row_tg = tk.Frame(card_call, bg=self.card_color)
        row_tg.pack(fill=tk.X, pady=2)
        tk.Button(
            row_tg, text="📱 Звонок Telegram (Мамуля ❤️)", font=("Segoe UI", 9, "bold"),
            bg="#29b6f6", fg=self.accent_dark, bd=0, padx=8, pady=3, cursor="hand2",
            command=lambda: self.send_command("TROLL:TELEGRAM")
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(
            row_tg, text="🔔 Звук звонка", font=("Segoe UI", 8, "bold"),
            bg=self.surface1, fg="#29b6f6", bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda: self.send_command("TROLL:TELEGRAM_AUDIO")
        ).pack(side=tk.RIGHT, padx=2)

        row_dc = tk.Frame(card_call, bg=self.card_color)
        row_dc.pack(fill=tk.X, pady=2)
        tk.Button(
            row_dc, text="📞 Входящий звонок Discord", font=("Segoe UI", 9, "bold"),
            bg="#5865F2", fg="#ffffff", bd=0, padx=8, pady=3, cursor="hand2",
            command=lambda: self.send_command("TROLL:DISCORD")
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(
            row_dc, text="🔊 Звук вызова", font=("Segoe UI", 8, "bold"),
            bg=self.surface1, fg="#7289da", bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda: self.send_command("TROLL:DISCORD_AUDIO")
        ).pack(side=tk.RIGHT, padx=2)

        tk.Button(
            card_call,
            text="💬 Steam сообщение (Сотка на шаурму) 🎮",
            font=("Segoe UI", 9, "bold"),
            bg="#1b2838",
            fg="#66c0f4",
            activebackground="#66c0f4",
            activeforeground=self.accent_dark,
            bd=0,
            padx=8,
            pady=3,
            cursor="hand2",
            command=lambda: self.send_command("TROLL:STEAM")
        ).pack(fill=tk.X, pady=2)

        card_snd, _ = self.create_card(tab, "🚪 3D АУДИО & ВНЕЗАПНЫЕ ЭФФЕКТЫ", "Звуки присутствия и визуальные вспышки", self.accent_peach)
        tk.Button(
            card_snd,
            text="🚪 3D СТУК В ДВЕРЬ (Звук за спиной) 🔊",
            font=("Segoe UI", 9, "bold"),
            bg=self.surface1,
            fg=self.accent_peach,
            activebackground=self.accent_peach,
            activeforeground=self.accent_dark,
            bd=0,
            padx=8,
            pady=4,
            cursor="hand2",
            command=lambda: self.send_command("TROLL:KNOCK")
        ).pack(fill=tk.X, pady=2)

        row_mosq = tk.Frame(card_snd, bg=self.card_color)
        row_mosq.pack(fill=tk.X, pady=2)
        tk.Label(row_mosq, text="🦟 Комар:", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_color, width=9, anchor=tk.W).pack(side=tk.LEFT)
        for txt, cmd, col in [("Звук 1", "TROLL:MOSQUITO:1", self.accent_green), ("Звук 2", "TROLL:MOSQUITO:2", self.accent_yellow), ("Звук 3", "TROLL:MOSQUITO:3", self.accent_peach), ("⏹️ Стоп", "TROLL:MOSQUITO:STOP", self.accent_red)]:
            tk.Button(
                row_mosq, text=txt, font=("Segoe UI", 8, "bold"),
                bg=self.surface1, fg=col, activebackground=col,
                activeforeground=self.accent_dark, bd=0, padx=6, pady=2, cursor="hand2",
                command=lambda c=cmd: self.send_command(c)
            ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_fun = tk.Frame(card_snd, bg=self.card_color)
        row_fun.pack(fill=tk.X, pady=2)
        tk.Button(
            row_fun, text="💰 Донат Папича (5000₽)", font=("Segoe UI", 8, "bold"),
            bg=self.surface1, fg=self.accent_peach, bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda: self.send_command("TROLL:DONATE")
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(
            row_fun, text="💥 Flashbang", font=("Segoe UI", 8, "bold"),
            bg=self.surface1, fg="#ffffff", bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda: self.send_command("FLASHBANG")
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        tk.Button(
            row_fun, text="❌ Фейк-мисс", font=("Segoe UI", 8, "bold"),
            bg=self.surface1, fg=self.accent_red, bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda: self.send_command("FAKE_MISS")
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)

        row_misc = tk.Frame(card_snd, bg=self.card_color)
        row_misc.pack(fill=tk.X, pady=(4, 0))
        self.create_toggle_btn(row_misc, "FREEZE", "⏳ Блэкаут (Пауза нот)", "FREEZE_ON", "FREEZE_OFF", self.accent_mauve, side=tk.LEFT)
        self.create_toggle_btn(row_misc, "FLY", "🪰 Муха на мониторе", "FLY_ON", "FLY_OFF", self.accent_green, side=tk.RIGHT)

    # =========================================================================
    # ВКЛАДКА 5: РАДАР ФЕЙКОВЫХ НОТ (ГАЛЛЮЦИНАЦИИ)
    # =========================================================================
    def populate_tab_radar(self, tab):
        card_rad, _ = self.create_card(
            tab, "🎯 ИНТЕРАКТИВНЫЙ РАДАР СПАВНА НОТ",
            "Кликайте по сетке, чтобы мгновенно создать иллюзию хит-серкла на экране игрока",
            self.accent_blue
        )

        canvas_width = 480
        canvas_height = 360

        self.radar_canvas = tk.Canvas(
            card_rad,
            width=canvas_width,
            height=canvas_height,
            bg="#11111b",
            highlightthickness=1,
            highlightbackground=self.accent_blue
        )
        self.radar_canvas.pack(pady=8)

        for i in range(0, canvas_width, 48):
            self.radar_canvas.create_line(i, 0, i, canvas_height, fill="#24273a", dash=(2, 2))
        for i in range(0, canvas_height, 48):
            self.radar_canvas.create_line(0, i, canvas_width, i, fill="#24273a", dash=(2, 2))

        self.radar_canvas.create_line(canvas_width // 2, 0, canvas_width // 2, canvas_height, fill="#313244", width=1)
        self.radar_canvas.create_line(0, canvas_height // 2, canvas_width, canvas_height // 2, fill="#313244", width=1)

        self.radar_canvas.bind("<Button-1>", self.on_radar_click)

        tk.Button(
            card_rad,
            text="🎲 ЗАСПАВНИТЬ СЛУЧАЙНУЮ НОТУ",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_blue,
            fg=self.accent_dark,
            activebackground=self.accent_green,
            activeforeground=self.accent_dark,
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.spawn_random_note
        ).pack(fill=tk.X, pady=(6, 0))

    # =========================================================================
    # НИЖНЯЯ ПАНЕЛЬ СТАТУСА
    # =========================================================================
    def build_footer(self):
        footer_frame = tk.Frame(self.root, bg=self.bg_color, padx=16, pady=6)
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_label = tk.Label(
            footer_frame,
            text="💡 Готов к отправке команд • Рекомендуемый мод в игре: 'Chaos Remote' (CHR)",
            font=("Segoe UI", 8, "bold"),
            bg=self.bg_color,
            fg=self.text_dim,
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        hotkey_lbl = tk.Label(
            footer_frame,
            text="Ctrl+R: Сброс  |  Ctrl+F: Поиск  |  Esc: Отмена",
            font=("Segoe UI", 8),
            bg=self.bg_color,
            fg=self.surface2
        )
        hotkey_lbl.pack(side=tk.RIGHT)

    # =========================================================================
    # ЛОГИКА ОТПРАВКИ КОМАНД, ЗАДЕРЖКИ И СЕТИ
    # =========================================================================
    def is_delayable_event(self, command: str) -> bool:
        cmd_upper = command.upper()
        if any(cmd_upper.startswith(prefix) for prefix in [
            "TROLL:", "TROLL_", "CAPTCHA", "SCREAMER", "MOSQUITO", "WATERMARK"
        ]):
            return True
        if cmd_upper in [
            "DEVICE_DISCONNECT", "MOUSE_DISCONNECT", "MOUSE_SPINOUT",
            "FLASHBANG", "KISS", "FAKE_MISS", "BARREL_ROLL", "TAPE_STOP",
            "FLY_ON", "FLY_OFF", "CS_CHAOS_ON", "CS_CHAOS_OFF",
            "INVERT_COLORS_ON", "INVERT_COLORS_OFF", "MOSAIC_ON", "MOSAIC_OFF",
            "BUSY_CURSOR_ON", "BUSY_CURSOR_OFF", "BLACK_HOLE_ON", "BLACK_HOLE_OFF"
        ]:
            return True
        return False

    def is_continuous_or_slider_cmd(self, command: str) -> bool:
        return command.startswith((
            "JITTER:", "CURSOR_SCALE:", "AUDIO_DESYNC:", "SET_FPS:", "SPAWN_NOTE:",
            "INPUT_LAG:", "CS_CHAOS_MIN:", "CS_CHAOS_MAX:", "CS_CHAOS_RANGE:",
            "BLACK_HOLE_STRENGTH:"
        ))

    def _execute_send(self, command: str):
        ip = self.ip_entry.get().strip()
        def task():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.5)
                s.connect((ip, 9000))
                s.send(command.encode("utf-8"))
                s.close()
                self.root.after(0, lambda: self._on_send_success(command))
            except Exception as ex:
                self.root.after(0, lambda: self._on_send_failure(command, str(ex)))
        threading.Thread(target=task, daemon=True).start()

    def _on_send_success(self, command: str):
        self.status_label.config(text=f"✔ Отправлено: '{command}'", fg=self.accent_green)
        self.update_ui_state(command)
        self._set_ping_status(True)

    def _on_send_failure(self, command: str, err: str):
        self.status_label.config(text=f"✖ Ошибка отправки '{command}': проверьте запуск osu! и IP", fg=self.accent_red)
        self._set_ping_status(False)

    def send_command(self, command: str, force_instant: bool = False):
        if force_instant or not self.event_delay_enabled.get() or self.is_continuous_or_slider_cmd(command):
            self._execute_send(command)
            return

        should_delay = True
        if self.delay_scope.get() == "events":
            should_delay = self.is_delayable_event(command)

        if not should_delay:
            self._execute_send(command)
            return

        if self._countdown_job is not None:
            self.root.after_cancel(self._countdown_job)
            self._countdown_job = None

        delay = float(self.event_delay_seconds.get())
        self._countdown_end_time = time.time() + delay
        self._countdown_cmd = command
        self._show_countdown(delay)

    def _show_countdown(self, total_delay: float):
        remaining = max(0.0, self._countdown_end_time - time.time())
        if remaining <= 0.05:
            if self.countdown_banner.winfo_ismapped():
                self.countdown_banner.pack_forget()
            self._countdown_job = None
            self._execute_send(self._countdown_cmd)
            return

        display_cmd = self._countdown_cmd
        if len(display_cmd) > 28:
            display_cmd = display_cmd[:25] + "..."

        self.countdown_lbl.config(text=f"⏳ [{remaining:.1f}с] Переключитесь в osu! Запуск '{display_cmd}'")

        progress_ratio = max(0.0, min(1.0, 1.0 - (remaining / max(0.1, total_delay))))
        canvas_w = self.countdown_canvas.winfo_width()
        if canvas_w < 50:
            canvas_w = 480
        self.countdown_canvas.delete("all")
        self.countdown_canvas.create_rectangle(0, 0, int(canvas_w * progress_ratio), 4, fill=self.accent_yellow, width=0)

        if not self.countdown_banner.winfo_ismapped():
            self.countdown_banner.pack(fill=tk.X, padx=16, pady=(0, 6), before=self.notebook)

        self.status_label.config(text=f"⏳ Переключитесь в окно osu! (до старта {remaining:.1f} сек)", fg=self.accent_yellow)
        self._countdown_job = self.root.after(80, lambda: self._show_countdown(total_delay))

    def cancel_countdown(self):
        if self._countdown_job is not None:
            self.root.after_cancel(self._countdown_job)
            self._countdown_job = None
        if self.countdown_banner.winfo_ismapped():
            self.countdown_banner.pack_forget()
        self.status_label.config(text="Запуск ивента отменен", fg=self.text_color)

    # =========================================================================
    # СБРОСИТЬ ВСЁ (RESET ALL / PANIC BUTTON)
    # =========================================================================
    def reset_all_debuffs(self):
        self.cancel_countdown()
        self.status_label.config(text="🚨 ЭКСТРЕННЫЙ СБРОС ВСЕХ ДЕБАФФОВ...", fg=self.accent_yellow)

        commands_to_reset = [
            "CHAOS_OFF", "WIND_OFF", "MAGNET_OFF", "BLACK_HOLE_OFF",
            "GRAVITY_OFF", "SCALE:1.00", "HUD_SCALE:1.00", "SPEED:1.00", "PITCH_OFF",
            "REPULSION_OFF", "JITTER:0", "INPUT_LAG:0", "CLONES_OFF", "HIDE_CURSOR:OFF",
            "BUSY_CURSOR_OFF", "CURSOR_SCALE:1.00", "INVERT_RESET", "JAM_RESET",
            "DRUNK_OFF", "CAROUSEL_OFF", "SET_FPS:0", "CS_CHAOS_OFF", "MOSAIC_OFF",
            "INVERT_COLORS_OFF", "TUNNEL_OFF", "GHOST_SLIDERS_OFF", "AUDIO_DESYNC:0",
            "CHAMELEON_OFF", "MIRROR_PLAYFIELD_X_OFF", "MIRROR_PLAYFIELD_Y_OFF",
            "MIRROR_HUD_X_OFF", "MUFFLED_OFF", "PAN_SPIN_OFF", "REVERB_OFF",
            "BASS_BOOST_OFF", "EARTHQUAKE_OFF", "HIDDEN_OFF", "FREEZE_OFF",
            "WATERMARK_OFF", "FLY_OFF", "TROLL:MOSQUITO:STOP"
        ]

        for k in self.toggle_states:
            self.update_toggle_visual(k, False)

        self.btn_inv_x.config(text="⚪ НОРМА X", bg=self.surface1, fg=self.text_color)
        self.btn_inv_y.config(text="⚪ НОРМА Y", bg=self.surface1, fg=self.text_color)
        self.btn_jam_k1.config(text="⚪ РАБОТАЕТ", bg=self.surface1, fg=self.text_color)
        self.btn_jam_k2.config(text="⚪ РАБОТАЕТ", bg=self.surface1, fg=self.text_color)

        if hasattr(self, "jit_scale"): self.jit_scale.set(0)
        if hasattr(self, "lag_scale"): self.lag_scale.set(0)
        if hasattr(self, "cscale_slider"): self.cscale_slider.set(1.0)
        if hasattr(self, "bh_scale"): self.bh_scale.set(1.0)
        if hasattr(self, "fps_scale"): self.fps_scale.set(60)
        if hasattr(self, "desync_scale"): self.desync_scale.set(0)

        ip = self.ip_entry.get().strip()
        def _send_all():
            try:
                for cmd in commands_to_reset:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.3)
                    s.connect((ip, 9000))
                    s.send(cmd.encode("utf-8"))
                    s.close()
                    time.sleep(0.01)
                self.root.after(0, lambda: self.status_label.config(text="✔ Все дебаффы успешно сброшены в норму!", fg=self.accent_green))
            except Exception as ex:
                self.root.after(0, lambda: self.status_label.config(text=f"✖ Ошибка сброса: {ex}", fg=self.accent_red))

        threading.Thread(target=_send_all, daemon=True).start()

    # =========================================================================
    # ФОНОВЫЙ ПИНГ СОКЕТА OSU!
    # =========================================================================
    def start_ping_thread(self):
        def _worker():
            while not self._stop_ping.is_set():
                ip = self.ip_entry.get().strip()
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(0.3)
                    s.connect((ip, 9000))
                    s.close()
                    self.root.after(0, lambda: self._set_ping_status(True))
                except Exception:
                    self.root.after(0, lambda: self._set_ping_status(False))
                time.sleep(2.5)

        t = threading.Thread(target=_worker, daemon=True)
        t.start()

    def check_connection_now(self):
        self.ping_indicator.config(text="● ПРОВЕРКА...", fg=self.accent_yellow)
        ip = self.ip_entry.get().strip()
        def _check():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.4)
                s.connect((ip, 9000))
                s.close()
                self.root.after(0, lambda: self._set_ping_status(True))
            except Exception:
                self.root.after(0, lambda: self._set_ping_status(False))
        threading.Thread(target=_check, daemon=True).start()

    def _set_ping_status(self, connected: bool):
        self.is_connected = connected
        if connected:
            self.ping_indicator.config(text="● ОНЛАЙН (osu! найден)", fg=self.accent_green)
        else:
            self.ping_indicator.config(text="● НЕ В СЕТИ (запустите мод в osu!)", fg=self.accent_red)

    # =========================================================================
    # ОБНОВЛЕНИЕ СОСТОЯНИЙ UI
    # =========================================================================
    def update_ui_state(self, command: str):
        cmd_map = {
            "CHAOS_ON": ("CHAOS", True), "CHAOS_OFF": ("CHAOS", False),
            "WIND_ON": ("WIND", True), "WIND_OFF": ("WIND", False),
            "MAGNET_ON": ("MAGNET", True), "MAGNET_OFF": ("MAGNET", False),
            "BLACK_HOLE_ON": ("BLACK_HOLE", True), "BLACK_HOLE_OFF": ("BLACK_HOLE", False),
            "GRAVITY_ON": ("GRAVITY", True), "GRAVITY_OFF": ("GRAVITY", False),
            "REPULSION_ON": ("REPULSION", True), "REPULSION_OFF": ("REPULSION", False),
            "CLONES_ON": ("CLONES", True), "CLONES_OFF": ("CLONES", False),
            "HIDE_CURSOR:ON": ("HIDE_CURSOR", True), "HIDE_CURSOR:OFF": ("HIDE_CURSOR", False),
            "BUSY_CURSOR_ON": ("BUSY_CURSOR", True), "BUSY_CURSOR_OFF": ("BUSY_CURSOR", False),
            "DRUNK_ON": ("DRUNK", True), "DRUNK_OFF": ("DRUNK", False),
            "CAROUSEL_ON": ("CAROUSEL", True), "CAROUSEL_OFF": ("CAROUSEL", False),
            "CS_CHAOS_ON": ("CS_CHAOS", True), "CS_CHAOS_OFF": ("CS_CHAOS", False),
            "MOSAIC_ON": ("MOSAIC", True), "MOSAIC_OFF": ("MOSAIC", False),
            "INVERT_COLORS_ON": ("INVERT_COLORS", True), "INVERT_COLORS_OFF": ("INVERT_COLORS", False),
            "TUNNEL_ON": ("TUNNEL", True), "TUNNEL_OFF": ("TUNNEL", False),
            "GHOST_SLIDERS_ON": ("GHOST_SLIDERS", True), "GHOST_SLIDERS_OFF": ("GHOST_SLIDERS", False),
            "MUFFLED_ON": ("MUFFLED", True), "MUFFLED_OFF": ("MUFFLED", False),
            "PAN_SPIN_ON": ("PAN_SPIN", True), "PAN_SPIN_OFF": ("PAN_SPIN", False),
            "REVERB_ON": ("REVERB", True), "REVERB_OFF": ("REVERB", False),
            "BASS_BOOST_ON": ("BASS_BOOST", True), "BASS_BOOST_OFF": ("BASS_BOOST", False),
            "EARTHQUAKE_ON": ("EARTHQUAKE", True), "EARTHQUAKE_OFF": ("EARTHQUAKE", False),
            "HIDDEN_ON": ("HIDDEN", True), "HIDDEN_OFF": ("HIDDEN", False),
            "FREEZE_ON": ("FREEZE", True), "FREEZE_OFF": ("FREEZE", False),
            "WATERMARK_ON": ("WATERMARK", True), "WATERMARK_OFF": ("WATERMARK", False),
            "FLY_ON": ("FLY", True), "FLY_OFF": ("FLY", False),
            "MIRROR_PLAYFIELD_X_ON": ("MIRROR_PF_X", True), "MIRROR_PLAYFIELD_X_OFF": ("MIRROR_PF_X", False),
            "MIRROR_PLAYFIELD_Y_ON": ("MIRROR_PF_Y", True), "MIRROR_PLAYFIELD_Y_OFF": ("MIRROR_PF_Y", False),
            "MIRROR_HUD_X_ON": ("MIRROR_HUD_X", True), "MIRROR_HUD_X_OFF": ("MIRROR_HUD_X", False),
        }

        if command in cmd_map:
            key, state = cmd_map[command]
            self.update_toggle_visual(key, state)
            return

        if command == "INVERT_X_ON":
            self.toggle_states["INVERT_X"] = True
            self.btn_inv_x.config(text="🟢 ИНВЕРСИЯ X", bg=self.accent_peach, fg=self.accent_dark)
        elif command == "INVERT_X_OFF":
            self.toggle_states["INVERT_X"] = False
            self.btn_inv_x.config(text="⚪ НОРМА X", bg=self.surface1, fg=self.text_color)
        elif command == "INVERT_Y_ON":
            self.toggle_states["INVERT_Y"] = True
            self.btn_inv_y.config(text="🟢 ИНВЕРСИЯ Y", bg=self.accent_peach, fg=self.accent_dark)
        elif command == "INVERT_Y_OFF":
            self.toggle_states["INVERT_Y"] = False
            self.btn_inv_y.config(text="⚪ НОРМА Y", bg=self.surface1, fg=self.text_color)
        elif command == "INVERT_RESET":
            self.toggle_states["INVERT_X"] = False
            self.toggle_states["INVERT_Y"] = False
            self.btn_inv_x.config(text="⚪ НОРМА X", bg=self.surface1, fg=self.text_color)
            self.btn_inv_y.config(text="⚪ НОРМА Y", bg=self.surface1, fg=self.text_color)

        elif command == "JAM_K1_ON":
            self.toggle_states["JAM_K1"] = True
            self.btn_jam_k1.config(text="⛔ ЗАЛИПЛА", bg=self.accent_red, fg=self.accent_dark)
        elif command == "JAM_K1_OFF":
            self.toggle_states["JAM_K1"] = False
            self.btn_jam_k1.config(text="⚪ РАБОТАЕТ", bg=self.surface1, fg=self.text_color)
        elif command == "JAM_K2_ON":
            self.toggle_states["JAM_K2"] = True
            self.btn_jam_k2.config(text="⛔ ЗАЛИПЛА", bg=self.accent_red, fg=self.accent_dark)
        elif command == "JAM_K2_OFF":
            self.toggle_states["JAM_K2"] = False
            self.btn_jam_k2.config(text="⚪ РАБОТАЕТ", bg=self.surface1, fg=self.text_color)
        elif command == "JAM_RESET":
            self.toggle_states["JAM_K1"] = False
            self.toggle_states["JAM_K2"] = False
            self.btn_jam_k1.config(text="⚪ РАБОТАЕТ", bg=self.surface1, fg=self.text_color)
            self.btn_jam_k2.config(text="⚪ РАБОТАЕТ", bg=self.surface1, fg=self.text_color)

    def toggle_inv_x(self):
        st = self.toggle_states.get("INVERT_X", False)
        self.send_command("INVERT_X_OFF" if st else "INVERT_X_ON")

    def toggle_inv_y(self):
        st = self.toggle_states.get("INVERT_Y", False)
        self.send_command("INVERT_Y_OFF" if st else "INVERT_Y_ON")

    def invert_both(self):
        self.send_command("INVERT_X_ON")
        self.send_command("INVERT_Y_ON")

    def invert_reset(self):
        self.send_command("INVERT_RESET")

    def toggle_jam_k1(self):
        st = self.toggle_states.get("JAM_K1", False)
        self.send_command("JAM_K1_OFF" if st else "JAM_K1_ON")

    def toggle_jam_k2(self):
        st = self.toggle_states.get("JAM_K2", False)
        self.send_command("JAM_K2_OFF" if st else "JAM_K2_ON")

    def jam_reset(self):
        self.send_command("JAM_RESET")

    def on_cs_min_slider(self, val):
        self.cs_min_val = float(val)
        self.send_command(f"CS_CHAOS_MIN:{self.cs_min_val:.2f}")

    def on_cs_max_slider(self, val):
        self.cs_max_val = float(val)
        self.send_command(f"CS_CHAOS_MAX:{self.cs_max_val:.2f}")

    # =========================================================================
    # ОКНО НАСТРОЕК (ЗАДЕРЖКА ВЫЗОВА ИВЕНТОВ)
    # =========================================================================
    def open_settings(self):
        if hasattr(self, "settings_win") and self.settings_win and self.settings_win.winfo_exists():
            self.settings_win.lift()
            self.settings_win.focus_force()
            return

        self.settings_win = tk.Toplevel(self.root)
        self.settings_win.title("Настройки панели")
        self.settings_win.geometry("440x480")
        self.settings_win.configure(bg=self.bg_color)
        self.settings_win.resizable(False, False)
        self.settings_win.attributes("-topmost", True)
        self.settings_win.transient(self.root)

        try:
            x = self.root.winfo_x() + 40
            y = self.root.winfo_y() + 60
            self.settings_win.geometry(f"+{x}+{y}")
        except Exception:
            pass

        tk.Label(
            self.settings_win,
            text="⚙️ НАСТРОЙКИ ЗАДЕРЖКИ (АЛЬТ-ТАБ)",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_color,
            fg=self.accent_blue
        ).pack(pady=(16, 8))

        card = tk.Frame(self.settings_win, bg=self.card_color, padx=16, pady=12)
        card.pack(fill=tk.X, padx=16, pady=6)

        tk.Label(
            card,
            text="Дает время переключиться на окно osu!, чтобы игра не уходила в паузу от потери фокуса Windows.",
            font=("Segoe UI", 8),
            bg=self.card_color,
            fg=self.text_dim,
            wraplength=380,
            justify=tk.LEFT
        ).pack(anchor=tk.W, pady=(0, 8))

        chk = tk.Checkbutton(
            card,
            text="Включить обратный отсчет перед ивентами",
            variable=self.event_delay_enabled,
            font=("Segoe UI", 9, "bold"),
            bg=self.card_color,
            fg=self.text_color,
            selectcolor=self.bg_color,
            activebackground=self.card_color,
            activeforeground=self.text_color,
            command=self._update_delay_badge
        )
        chk.pack(anchor=tk.W, pady=(0, 6))

        self.settings_delay_lbl = tk.Label(
            card,
            text=f"Задержка: {self.event_delay_seconds.get():.1f} сек",
            font=("Segoe UI", 9, "bold"),
            bg=self.card_color,
            fg=self.accent_yellow
        )
        self.settings_delay_lbl.pack(anchor=tk.W)

        scale = ttk.Scale(
            card,
            from_=1.0,
            to=10.0,
            value=self.event_delay_seconds.get(),
            command=self._on_settings_scale_move
        )
        scale.pack(fill=tk.X, pady=(4, 8))

        p_row = tk.Frame(card, bg=self.card_color)
        p_row.pack(fill=tk.X, pady=(0, 8))
        for sec in [1.0, 2.0, 3.0, 5.0]:
            btn_txt = f"{int(sec)}с ⭐" if sec == 3.0 else f"{int(sec)}с"
            tk.Button(
                p_row, text=btn_txt, font=("Segoe UI", 8, "bold"),
                bg=self.surface1 if sec != 3.0 else self.accent_blue,
                fg=self.text_color if sec != 3.0 else self.accent_dark,
                bd=0, padx=6, pady=2, cursor="hand2",
                command=lambda s=sec, sc=scale: self._set_settings_preset(s, sc)
            ).pack(side=tk.LEFT, padx=3)

        tk.Label(card, text="Применять задержку к:", font=("Segoe UI", 9, "bold"), bg=self.card_color, fg=self.text_color).pack(anchor=tk.W, pady=(6, 2))
        tk.Radiobutton(
            card, text="Только к ивентам и пранкам (Каптча, BSOD, Мышь...)",
            variable=self.delay_scope, value="events", font=("Segoe UI", 8),
            bg=self.card_color, fg=self.text_color, selectcolor=self.bg_color,
            activebackground=self.card_color, activeforeground=self.text_color
        ).pack(anchor=tk.W)
        tk.Radiobutton(
            card, text="Ко всем действиям без исключения",
            variable=self.delay_scope, value="all", font=("Segoe UI", 8),
            bg=self.card_color, fg=self.text_color, selectcolor=self.bg_color,
            activebackground=self.card_color, activeforeground=self.text_color
        ).pack(anchor=tk.W)

        tk.Button(
            self.settings_win,
            text="СОХРАНИТЬ И ЗАКРЫТЬ",
            font=("Segoe UI", 10, "bold"),
            bg=self.accent_green,
            fg=self.accent_dark,
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=self.settings_win.destroy
        ).pack(pady=(12, 16))

    def _on_settings_scale_move(self, val):
        sec = round(float(val) * 2) / 2
        self.event_delay_seconds.set(sec)
        if hasattr(self, "settings_delay_lbl") and self.settings_delay_lbl.winfo_exists():
            self.settings_delay_lbl.config(text=f"Задержка: {sec:.1f} сек")
        self._update_delay_badge()

    def _set_settings_preset(self, sec: float, scale_widget):
        self.event_delay_seconds.set(sec)
        scale_widget.set(sec)
        if hasattr(self, "settings_delay_lbl") and self.settings_delay_lbl.winfo_exists():
            self.settings_delay_lbl.config(text=f"Задержка: {sec:.1f} сек")
        self._update_delay_badge()

    def _update_delay_badge(self):
        if hasattr(self, "delay_badge"):
            if self.event_delay_enabled.get():
                sec = self.event_delay_seconds.get()
                sec_str = f"{int(sec)}с" if sec.is_integer() else f"{sec:.1f}с"
                self.delay_badge.config(text=f"⏱️ {sec_str}", fg=self.accent_yellow)
            else:
                self.delay_badge.config(text="⏱️ ВЫКЛ", fg=self.text_dim)

    # =========================================================================
    # РАДАР: КЛИКИ И СПАВН НОТ
    # =========================================================================
    def on_radar_click(self, event):
        x = event.x
        y = event.y
        if 0 <= x <= 480 and 0 <= y <= 360:
            osu_x = (x / 480.0) * 512.0
            osu_y = (y / 360.0) * 384.0
            self.send_command(f"FAKE_NOTE:{osu_x:.2f}:{osu_y:.2f}")

            r = 10
            blip = self.radar_canvas.create_oval(
                x - r, y - r, x + r, y + r,
                outline=self.accent_green, width=2, fill=self.surface1
            )
            self.root.after(350, lambda: self.radar_canvas.delete(blip))

    def spawn_random_note(self):
        import random
        osu_x = random.uniform(20, 492)
        osu_y = random.uniform(20, 364)
        self.send_command(f"FAKE_NOTE:{osu_x:.2f}:{osu_y:.2f}")

        cx = (osu_x / 512.0) * 480.0
        cy = (osu_y / 384.0) * 360.0
        r = 10
        blip = self.radar_canvas.create_oval(
            cx - r, cy - r, cx + r, cy + r,
            outline=self.accent_pink, width=2, fill=self.surface1
        )
        self.root.after(350, lambda: self.radar_canvas.delete(blip))


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernControlPanel(root)
    root.mainloop()
