using System;
using System.Collections.Generic;
using osu.Framework.Allocation;
using osu.Framework.Graphics;
using osu.Framework.Graphics.Containers;
using osu.Framework.Graphics.Shapes;
using osu.Framework.Graphics.Sprites;
using osu.Framework.Input.Events;
using osu.Framework.Platform;
using osu.Game.Graphics;
using osu.Game.Graphics.Sprites;
using osuTK;

namespace osu.Game.Rulesets.Osu.Mods
{
    public partial class CaptchaOverlay : CompositeDrawable
    {
        private readonly Container cursorContainer;
        private readonly Box dimBackdrop;
        private readonly Container modalCard;
        private readonly Container contentContainer;
        private readonly OsuSpriteText titleText;
        private readonly OsuSpriteText subtitleText;
        private readonly SpriteIcon headerIcon;
        private readonly Random rnd = new Random();

        public bool IsActive { get; private set; }

        public event Action? OnSolved;
        public event Action? OnFailed;

        public CaptchaOverlay()
        {
            RelativeSizeAxes = Axes.Both;
            Depth = -999999f;
            AlwaysPresent = true;
            Alpha = 0;

            InternalChildren = new Drawable[]
            {
                dimBackdrop = new Box
                {
                    RelativeSizeAxes = Axes.Both,
                    Colour = Colour4.Black.Opacity(0.88f)
                },
                modalCard = new Container
                {
                    Anchor = Anchor.Centre,
                    Origin = Anchor.Centre,
                    Width = 620,
                    AutoSizeAxes = Axes.Y,
                    Masking = true,
                    CornerRadius = 18,
                    BorderThickness = 3f,
                    BorderColour = Colour4.FromHex("#89b4fa"),
                    Children = new Drawable[]
                    {
                        new Box
                        {
                            RelativeSizeAxes = Axes.Both,
                            Colour = Colour4.FromHex("#1e1e2e")
                        },
                        new FillFlowContainer
                        {
                            RelativeSizeAxes = Axes.X,
                            AutoSizeAxes = Axes.Y,
                            Direction = FillDirection.Vertical,
                            Padding = new MarginPadding(22),
                            Spacing = new Vector2(0, 16),
                            Children = new Drawable[]
                            {
                                // Top Pause Status Banner
                                new Container
                                {
                                    Anchor = Anchor.TopCentre,
                                    Origin = Anchor.TopCentre,
                                    AutoSizeAxes = Axes.Both,
                                    Masking = true,
                                    CornerRadius = 6,
                                    Children = new Drawable[]
                                    {
                                        new Box
                                        {
                                            RelativeSizeAxes = Axes.Both,
                                            Colour = Colour4.FromHex("#313244")
                                        },
                                        new FillFlowContainer
                                        {
                                            AutoSizeAxes = Axes.Both,
                                            Direction = FillDirection.Horizontal,
                                            Spacing = new Vector2(6, 0),
                                            Padding = new MarginPadding { Horizontal = 14, Vertical = 5 },
                                            Children = new Drawable[]
                                            {
                                                new SpriteIcon
                                                {
                                                    Anchor = Anchor.CentreLeft,
                                                    Origin = Anchor.CentreLeft,
                                                    Icon = FontAwesome.Solid.Pause,
                                                    Size = new Vector2(10),
                                                    Colour = Colour4.FromHex("#fab387")
                                                },
                                                new OsuSpriteText
                                                {
                                                    Anchor = Anchor.CentreLeft,
                                                    Origin = Anchor.CentreLeft,
                                                    Text = "ИГРА ПРИОСТАНОВЛЕНА — РЕШИТЕ ЗАДАНИЕ ДЛЯ ПРОДОЛЖЕНИЯ",
                                                    Font = OsuFont.GetFont(size: 11, weight: FontWeight.Bold),
                                                    Colour = Colour4.FromHex("#fab387")
                                                }
                                            }
                                        }
                                    }
                                },
                                // Header bar
                                new Container
                                {
                                    RelativeSizeAxes = Axes.X,
                                    Height = 48,
                                    Children = new Drawable[]
                                    {
                                        headerIcon = new SpriteIcon
                                        {
                                            Anchor = Anchor.CentreLeft,
                                            Origin = Anchor.CentreLeft,
                                            Icon = FontAwesome.Solid.ShieldAlt,
                                            Size = new Vector2(34),
                                            Colour = Colour4.FromHex("#89b4fa")
                                        },
                                        new FillFlowContainer
                                        {
                                            Anchor = Anchor.CentreLeft,
                                            Origin = Anchor.CentreLeft,
                                            Position = new Vector2(46, 0),
                                            Direction = FillDirection.Vertical,
                                            AutoSizeAxes = Axes.Both,
                                            Children = new Drawable[]
                                            {
                                                titleText = new OsuSpriteText
                                                {
                                                    Text = "ПРОВЕРКА НА ЧЕЛОВЕКА",
                                                    Font = OsuFont.GetFont(size: 20, weight: FontWeight.Bold),
                                                    Colour = Colour4.White
                                                },
                                                subtitleText = new OsuSpriteText
                                                {
                                                    Text = "Выберите правильный ответ курсором, чтобы продолжить игру",
                                                    Font = OsuFont.GetFont(size: 13, weight: FontWeight.SemiBold),
                                                    Colour = Colour4.FromHex("#bac2de")
                                                }
                                            }
                                        }
                                    }
                                },
                                // Separator line
                                new Box
                                {
                                    RelativeSizeAxes = Axes.X,
                                    Height = 2,
                                    Colour = Colour4.FromHex("#45475a")
                                },
                                // Dynamic Challenge Content Area
                                contentContainer = new Container
                                {
                                    RelativeSizeAxes = Axes.X,
                                    AutoSizeAxes = Axes.Y
                                }
                            }
                        }
                    }
                },
                cursorContainer = new Container
                {
                    Size = new Vector2(28),
                    Origin = Anchor.Centre,
                    AlwaysPresent = true,
                    Alpha = 0,
                    Children = new Drawable[]
                    {
                        // Outer subtle glow
                        new Circle
                        {
                            Anchor = Anchor.Centre,
                            Origin = Anchor.Centre,
                            Size = new Vector2(28),
                            Colour = Colour4.FromHex("#89b4fa").Opacity(0.35f),
                        },
                        // Outer crisp ring
                        new Container
                        {
                            Anchor = Anchor.Centre,
                            Origin = Anchor.Centre,
                            Size = new Vector2(20),
                            Masking = true,
                            CornerRadius = 10,
                            BorderThickness = 2.5f,
                            BorderColour = Colour4.White,
                            Child = new Box { RelativeSizeAxes = Axes.Both, Colour = Colour4.Transparent }
                        },
                        // Center dot
                        new Circle
                        {
                            Anchor = Anchor.Centre,
                            Origin = Anchor.Centre,
                            Size = new Vector2(6),
                            Colour = Colour4.FromHex("#89b4fa"),
                        }
                    }
                }
            };
        }

        [BackgroundDependencyLoader]
        private void load(GameHost host)
        {
            Clock = host.UpdateThread.Clock;
            ProcessCustomClock = false;
        }

        public override bool ReceivePositionalInputAt(Vector2 screenSpacePos) => IsActive && base.ReceivePositionalInputAt(screenSpacePos);

        protected override bool OnMouseMove(MouseMoveEvent e)
        {
            if (IsActive)
            {
                cursorContainer.Position = e.MousePosition;
                return true;
            }
            return false;
        }

        protected override bool OnMouseDown(MouseDownEvent e)
        {
            if (!IsActive) return false;
            cursorContainer.ScaleTo(0.82f, 60, Easing.OutQuad);
            return true;
        }

        protected override void OnMouseUp(MouseUpEvent e)
        {
            if (IsActive)
                cursorContainer.ScaleTo(1.0f, 100, Easing.OutQuad);
            base.OnMouseUp(e);
        }

        protected override bool OnClick(ClickEvent e) => IsActive;

        protected override void Update()
        {
            base.Update();

            if (IsActive)
            {
                cursorContainer.Alpha = 1;
                var inputManager = GetContainingInputManager();
                if (inputManager != null)
                {
                    var mousePos = inputManager.CurrentState.Mouse.Position;
                    cursorContainer.Position = ToLocalSpace(mousePos);
                }
            }
            else
            {
                cursorContainer.Alpha = 0;
            }
        }

        public void ShowCaptcha(string mode = "RANDOM")
        {
            mode = mode.ToUpperInvariant().Trim();
            if (mode == "RANDOM")
            {
                int r = rnd.Next(3);
                mode = r switch
                {
                    0 => "MATH",
                    1 => "RECAPTCHA",
                    _ => "TRIVIA"
                };
            }

            contentContainer.Clear();

            switch (mode)
            {
                case "MATH":
                    buildMathChallenge();
                    break;

                case "RECAPTCHA":
                    buildRecaptchaChallenge();
                    break;

                case "TRIVIA":
                default:
                    buildTriviaChallenge();
                    break;
            }

            modalCard.ClearTransforms();
            modalCard.Scale = new Vector2(0.85f);
            modalCard.X = 0;
            modalCard.ScaleTo(1.0f, 250, Easing.OutBack);

            dimBackdrop.FadeTo(0.88f, 150);
            modalCard.FadeIn(150);
            this.FadeIn(150);
            IsActive = true;

            TrollOverlay.PlayWindowsSound("Windows Exclamation.wav");
        }

        private void handleSuccess()
        {
            TrollOverlay.PlayWindowsSound("chimes.wav");
            modalCard.FlashColour(Colour4.FromHex("#a6e3a1"), 350);

            Scheduler.AddDelayed(() =>
            {
                this.FadeOut(200);
                IsActive = false;
                OnSolved?.Invoke();
            }, 250);
        }

        private void handleFailure()
        {
            TrollOverlay.PlayWindowsSound("Windows Hardware Remove.wav");
            OnFailed?.Invoke();

            // Shake animation
            modalCard.MoveToX(-20, 45, Easing.OutSine)
                .Then().MoveToX(20, 90, Easing.InOutSine)
                .Then().MoveToX(-14, 75, Easing.InOutSine)
                .Then().MoveToX(14, 65, Easing.InOutSine)
                .Then().MoveToX(0, 45, Easing.InSine);

            modalCard.FlashColour(Colour4.FromHex("#f38ba8"), 350);

            // Give a new question after 400ms
            Scheduler.AddDelayed(() =>
            {
                if (IsActive)
                    ShowCaptcha("RANDOM");
            }, 400);
        }

        #region Challenge 1: Math Equation

        private void buildMathChallenge()
        {
            titleText.Text = "ПРОВЕРКА: МАТЕМАТИЧЕСКИЙ ТЕСТ";
            headerIcon.Icon = FontAwesome.Solid.Calculator;
            headerIcon.Colour = Colour4.FromHex("#89b4fa");

            int op = rnd.Next(3);
            int a, b, answer;
            string eqStr;

            if (op == 0) // Addition
            {
                a = rnd.Next(12, 78);
                b = rnd.Next(12, 78);
                answer = a + b;
                eqStr = $"{a} + {b} = ?";
            }
            else if (op == 1) // Subtraction
            {
                a = rnd.Next(35, 99);
                b = rnd.Next(11, a - 5);
                answer = a - b;
                eqStr = $"{a} - {b} = ?";
            }
            else // Multiplication
            {
                a = rnd.Next(4, 12);
                b = rnd.Next(4, 12);
                answer = a * b;
                eqStr = $"{a} × {b} = ?";
            }

            var answers = new List<int> { answer };
            while (answers.Count < 4)
            {
                int delta = rnd.Next(1, 9) * (rnd.Next(2) == 0 ? 1 : -1);
                int fake = Math.Max(1, answer + delta);
                if (!answers.Contains(fake))
                    answers.Add(fake);
            }

            // Shuffle answers
            for (int i = answers.Count - 1; i > 0; i--)
            {
                int k = rnd.Next(i + 1);
                (answers[i], answers[k]) = (answers[k], answers[i]);
            }

            var flow = new FillFlowContainer
            {
                RelativeSizeAxes = Axes.X,
                AutoSizeAxes = Axes.Y,
                Direction = FillDirection.Vertical,
                Spacing = new Vector2(0, 16)
            };

            // Equation display
            flow.Add(new Container
            {
                RelativeSizeAxes = Axes.X,
                Height = 72,
                Masking = true,
                CornerRadius = 12,
                BorderThickness = 2f,
                BorderColour = Colour4.FromHex("#45475a"),
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.FromHex("#11111b")
                    },
                    new OsuSpriteText
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        Text = eqStr,
                        Font = OsuFont.GetFont(size: 36, weight: FontWeight.Bold),
                        Colour = Colour4.FromHex("#89dceb")
                    }
                }
            });

            // 2x2 grid of options
            var buttonList = new List<CaptchaButton>();
            foreach (int val in answers)
            {
                bool isCorrect = (val == answer);
                buttonList.Add(new CaptchaButton(val.ToString(), () =>
                {
                    if (isCorrect) handleSuccess();
                    else handleFailure();
                }));
            }

            var optionsGrid = new GridContainer
            {
                RelativeSizeAxes = Axes.X,
                AutoSizeAxes = Axes.Y,
                RowDimensions = new[]
                {
                    new Dimension(GridSizeMode.AutoSize),
                    new Dimension(GridSizeMode.Absolute, 14),
                    new Dimension(GridSizeMode.AutoSize),
                },
                ColumnDimensions = new[]
                {
                    new Dimension(GridSizeMode.Distributed),
                    new Dimension(GridSizeMode.Absolute, 14),
                    new Dimension(GridSizeMode.Distributed),
                },
                Content = new[]
                {
                    new Drawable[] { buttonList[0], new Container(), buttonList[1] },
                    new Drawable[] { new Container(), new Container(), new Container() },
                    new Drawable[] { buttonList[2], new Container(), buttonList[3] },
                }
            };

            flow.Add(optionsGrid);
            contentContainer.Child = flow;
        }

        #endregion

        #region Challenge 2: reCAPTCHA "I am not a robot"

        private void buildRecaptchaChallenge()
        {
            titleText.Text = "СИСТЕМА БЕЗОПАСНОСТИ RECAPTCHA";
            headerIcon.Icon = FontAwesome.Solid.Robot;
            headerIcon.Colour = Colour4.FromHex("#a6e3a1");

            var recaptchaCard = new Container
            {
                Width = 380,
                Height = 92,
                Anchor = Anchor.Centre,
                Origin = Anchor.Centre,
                Masking = true,
                CornerRadius = 8,
                BorderThickness = 2f,
                BorderColour = Colour4.FromHex("#585b70"),
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.FromHex("#181825")
                    },
                    new RecaptchaCheckbox(() =>
                    {
                        handleSuccess();
                    }),
                    new FillFlowContainer
                    {
                        Anchor = Anchor.CentreRight,
                        Origin = Anchor.CentreRight,
                        Position = new Vector2(-16, 0),
                        Direction = FillDirection.Vertical,
                        AutoSizeAxes = Axes.Both,
                        Spacing = new Vector2(0, 3),
                        Children = new Drawable[]
                        {
                            new SpriteIcon
                            {
                                Anchor = Anchor.TopCentre,
                                Origin = Anchor.TopCentre,
                                Icon = FontAwesome.Solid.RedoAlt,
                                Size = new Vector2(24),
                                Colour = Colour4.FromHex("#89b4fa")
                            },
                            new OsuSpriteText
                            {
                                Anchor = Anchor.TopCentre,
                                Origin = Anchor.TopCentre,
                                Text = "reCAPTCHA",
                                Font = OsuFont.GetFont(size: 11, weight: FontWeight.Bold),
                                Colour = Colour4.FromHex("#cdd6f4")
                            },
                            new OsuSpriteText
                            {
                                Anchor = Anchor.TopCentre,
                                Origin = Anchor.TopCentre,
                                Text = "Конфиденциальность",
                                Font = OsuFont.GetFont(size: 9),
                                Colour = Colour4.FromHex("#a6adc8")
                            }
                        }
                    }
                }
            };

            contentContainer.Child = recaptchaCard;
        }

        #endregion

        #region Challenge 3: osu! Trivia / Riddles

        private record TriviaItem(string Question, string CorrectAnswer, string[] WrongAnswers);

        private static readonly TriviaItem[] triviaBank =
        {
            new TriviaItem("Число бога и главное проклятие в osu!:", "727", new[] { "1000", "99.9%", "404" }),
            new TriviaItem("Сколько клавиш нажимает истинный osu!-плеер?", "2 клавиши", new[] { "1 клавишу", "4 клавиши", "Весь клавиатурный ряд" }),
            new TriviaItem("Что делать, если выпал '100' на первой ноте?", "Рестарт (Quick Retry)", new[] { "Доиграть карту", "Заплакать", "Написать в саппорт" }),
            new TriviaItem("Что тяжелее: 1 кг мышек или 1 кг планшетов?", "Весят одинаково", new[] { "Мышки", "Планшеты", "Зависит от DPI" }),
            new TriviaItem("Сколько углов у ноты (Hit Circle)?", "0 углов", new[] { "1 угол", "360 углов", "4 угла" }),
            new TriviaItem("Как называется мод, ускоряющий трек в 1.5 раза?", "Double Time (DT)", new[] { "Nightcore (NC)", "Half Time (HT)", "Hard Rock (HR)" }),
            new TriviaItem("Если на вас летит поток нот на 250 BPM:", "Стримить изо всех сил", new[] { "Отпустить мышь", "Зажмурить глаза", "Выйти в лобби" }),
            new TriviaItem("Какое главное правило перед игрой на рекорд?", "Помыть руки с мылом", new[] { "Помолиться", "Удалить Discord", "Сломать пробел" }),
            new TriviaItem("Что происходит, когда кончается полоска HP?", "Окно Fail / Смерть", new[] { "Дают вторую жизнь", "Музыка играет дальше", "Звонит Мамуля" }),
            new TriviaItem("Какая клавиша по умолчанию активирует дым (Smoke)?", "Клавиша C", new[] { "Пробел", "Клавиша F", "Клавиша Z" }),
        };

        private void buildTriviaChallenge()
        {
            titleText.Text = "ПРОВЕРКА: ВОПРОС НА ЗНАНИЕ И ЛОГИКУ";
            headerIcon.Icon = FontAwesome.Solid.QuestionCircle;
            headerIcon.Colour = Colour4.FromHex("#fab387");

            var item = triviaBank[rnd.Next(triviaBank.Length)];

            var answers = new List<(string text, bool isCorrect)>
            {
                (item.CorrectAnswer, true)
            };
            foreach (var w in item.WrongAnswers)
                answers.Add((w, false));

            // Shuffle
            for (int i = answers.Count - 1; i > 0; i--)
            {
                int k = rnd.Next(i + 1);
                (answers[i], answers[k]) = (answers[k], answers[i]);
            }

            var flow = new FillFlowContainer
            {
                RelativeSizeAxes = Axes.X,
                AutoSizeAxes = Axes.Y,
                Direction = FillDirection.Vertical,
                Spacing = new Vector2(0, 16)
            };

            // Question box
            flow.Add(new Container
            {
                RelativeSizeAxes = Axes.X,
                AutoSizeAxes = Axes.Y,
                Padding = new MarginPadding(18),
                Masking = true,
                CornerRadius = 12,
                BorderThickness = 2f,
                BorderColour = Colour4.FromHex("#585b70"),
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.FromHex("#11111b")
                    },
                    new OsuSpriteText
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        Text = item.Question,
                        Font = OsuFont.GetFont(size: 20, weight: FontWeight.Bold),
                        Colour = Colour4.White
                    }
                }
            });

            // 2x2 grid of buttons
            var buttonList = new List<CaptchaButton>();
            foreach (var (text, isCorrect) in answers)
            {
                buttonList.Add(new CaptchaButton(text, () =>
                {
                    if (isCorrect) handleSuccess();
                    else handleFailure();
                }));
            }

            var optionsGrid = new GridContainer
            {
                RelativeSizeAxes = Axes.X,
                AutoSizeAxes = Axes.Y,
                RowDimensions = new[]
                {
                    new Dimension(GridSizeMode.AutoSize),
                    new Dimension(GridSizeMode.Absolute, 14),
                    new Dimension(GridSizeMode.AutoSize),
                },
                ColumnDimensions = new[]
                {
                    new Dimension(GridSizeMode.Distributed),
                    new Dimension(GridSizeMode.Absolute, 14),
                    new Dimension(GridSizeMode.Distributed),
                },
                Content = new[]
                {
                    new Drawable[] { buttonList[0], new Container(), buttonList[1] },
                    new Drawable[] { new Container(), new Container(), new Container() },
                    new Drawable[] { buttonList[2], new Container(), buttonList[3] },
                }
            };

            flow.Add(optionsGrid);
            contentContainer.Child = flow;
        }

        #endregion
    }

    public partial class CaptchaButton : ClickableContainer
    {
        private readonly Box background;
        private readonly OsuSpriteText label;

        public CaptchaButton(string text, Action onClick)
        {
            Action = onClick;
            RelativeSizeAxes = Axes.X;
            Height = 58;
            Masking = true;
            CornerRadius = 10;
            BorderThickness = 2f;
            BorderColour = Colour4.FromHex("#585b70");

            Children = new Drawable[]
            {
                background = new Box
                {
                    RelativeSizeAxes = Axes.Both,
                    Colour = Colour4.FromHex("#313244")
                },
                label = new OsuSpriteText
                {
                    Anchor = Anchor.Centre,
                    Origin = Anchor.Centre,
                    Text = text,
                    Font = OsuFont.GetFont(size: 17, weight: FontWeight.Bold),
                    Colour = Colour4.White,
                    Truncate = true,
                    MaxWidth = 260
                }
            };
        }

        protected override bool OnHover(HoverEvent e)
        {
            background.FadeColour(Colour4.FromHex("#45475a"), 100);
            BorderColour = Colour4.FromHex("#89b4fa");
            this.ScaleTo(1.03f, 100, Easing.OutQuad);
            return true;
        }

        protected override void OnHoverLost(HoverLostEvent e)
        {
            background.FadeColour(Colour4.FromHex("#313244"), 100);
            BorderColour = Colour4.FromHex("#585b70");
            this.ScaleTo(1.0f, 100, Easing.OutQuad);
        }

        protected override bool OnMouseDown(MouseDownEvent e)
        {
            this.ScaleTo(0.97f, 60);
            return base.OnMouseDown(e);
        }

        protected override void OnMouseUp(MouseUpEvent e)
        {
            this.ScaleTo(1.03f, 80);
            base.OnMouseUp(e);
        }
    }

    public partial class RecaptchaCheckbox : ClickableContainer
    {
        private readonly Container boxContainer;
        private readonly SpriteIcon checkIcon;
        private readonly SpriteIcon spinIcon;
        private bool isChecking;
        private readonly Action onVerified;

        public RecaptchaCheckbox(Action onVerified)
        {
            this.onVerified = onVerified;
            Anchor = Anchor.CentreLeft;
            Origin = Anchor.CentreLeft;
            Position = new Vector2(18, 0);
            AutoSizeAxes = Axes.Both;

            Action = onClicked;

            Children = new Drawable[]
            {
                new FillFlowContainer
                {
                    AutoSizeAxes = Axes.Both,
                    Direction = FillDirection.Horizontal,
                    Spacing = new Vector2(14, 0),
                    Children = new Drawable[]
                    {
                        boxContainer = new Container
                        {
                            Anchor = Anchor.CentreLeft,
                            Origin = Anchor.CentreLeft,
                            Size = new Vector2(30),
                            Masking = true,
                            CornerRadius = 6,
                            BorderThickness = 2.5f,
                            BorderColour = Colour4.FromHex("#89b4fa"),
                            Children = new Drawable[]
                            {
                                new Box
                                {
                                    RelativeSizeAxes = Axes.Both,
                                    Colour = Colour4.FromHex("#11111b")
                                },
                                spinIcon = new SpriteIcon
                                {
                                    Anchor = Anchor.Centre,
                                    Origin = Anchor.Centre,
                                    Icon = FontAwesome.Solid.CircleNotch,
                                    Size = new Vector2(18),
                                    Colour = Colour4.FromHex("#89b4fa"),
                                    Alpha = 0
                                },
                                checkIcon = new SpriteIcon
                                {
                                    Anchor = Anchor.Centre,
                                    Origin = Anchor.Centre,
                                    Icon = FontAwesome.Solid.Check,
                                    Size = new Vector2(20),
                                    Colour = Colour4.FromHex("#a6e3a1"),
                                    Alpha = 0
                                }
                            }
                        },
                        new OsuSpriteText
                        {
                            Anchor = Anchor.CentreLeft,
                            Origin = Anchor.CentreLeft,
                            Text = "Я не робот",
                            Font = OsuFont.GetFont(size: 18, weight: FontWeight.Bold),
                            Colour = Colour4.White
                        }
                    }
                }
            };
        }

        private void onClicked()
        {
            if (isChecking) return;
            isChecking = true;

            boxContainer.BorderColour = Colour4.FromHex("#89b4fa");
            spinIcon.Alpha = 1;
            spinIcon.RotateTo(0).Then().RotateTo(360, 450).Loop();

            Scheduler.AddDelayed(() =>
            {
                spinIcon.ClearTransforms();
                spinIcon.Alpha = 0;

                checkIcon.Alpha = 1;
                checkIcon.Scale = new Vector2(0.5f);
                checkIcon.ScaleTo(1.2f, 150, Easing.OutBack).Then().ScaleTo(1.0f, 100);

                boxContainer.BorderColour = Colour4.FromHex("#a6e3a1");

                Scheduler.AddDelayed(() =>
                {
                    onVerified?.Invoke();
                }, 300);
            }, 500);
        }

        protected override bool OnHover(HoverEvent e)
        {
            if (!isChecking)
                boxContainer.BorderColour = Colour4.FromHex("#cba6f7");
            return true;
        }

        protected override void OnHoverLost(HoverLostEvent e)
        {
            if (!isChecking)
                boxContainer.BorderColour = Colour4.FromHex("#89b4fa");
        }
    }
}
