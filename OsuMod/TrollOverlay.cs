using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using osu.Framework.Allocation;
using osu.Framework.Audio.Track;
using osu.Framework.Graphics;
using osu.Framework.Graphics.Containers;
using osu.Framework.Graphics.Shapes;
using osu.Framework.Graphics.Sprites;
using osu.Framework.IO.Stores;
using osu.Game.Audio.Effects;
using osu.Game.Graphics;
using osu.Game.Graphics.Sprites;
using osuTK;

namespace osu.Game.Rulesets.Osu.Mods
{
    public partial class TrollOverlay : CompositeDrawable
    {
        [DllImport("user32.dll", SetLastError = true)]
        private static extern bool MessageBeep(uint uType);

        [DllImport("winmm.dll", EntryPoint = "mciSendStringW", CharSet = CharSet.Unicode)]
        private static extern int mciSendString(string command, StringBuilder? buffer, int bufferSize, IntPtr hwndCallback);

        [DllImport("winmm.dll", EntryPoint = "PlaySoundW", CharSet = CharSet.Unicode)]
        public static extern bool PlaySound(string pszSound, IntPtr hmod, uint fdwSound);
        public const uint SND_ASYNC = 0x0001;
        public const uint SND_FILENAME = 0x00020000;

        private const uint mb_iconhand = 0x00000010;
        private const uint mb_iconexclamation = 0x00000030;
        private const uint mb_iconasterisk = 0x00000040;

        private Container batteryToast = null!;
        private Container discordToast = null!;
        private Container bsodContainer = null!;
        private Container defenderToast = null!;
        private Container updateContainer = null!;
        private Container donationToast = null!;
        private Container stickyKeysDialog = null!;
        private Container glitchContainer = null!;
        private readonly List<Box> glitchSlices = new List<Box>();
        private osu.Game.Audio.Effects.AudioFilter? lowPassFilter;
        private SpriteIcon? updateSpinnerIcon;
        private readonly Random rnd = new Random();

        private osu.Framework.Audio.Sample.Sample? popInSample;
        private osu.Framework.Audio.Sample.Sample? combobreakSample;
        private ITrack? discordTrack;
        private static string? localAudioPath;

        public TrollOverlay()
        {
            RelativeSizeAxes = Axes.Both;
            AlwaysPresent = true;
        }

        [BackgroundDependencyLoader]
        private void load(osu.Framework.Audio.AudioManager audio)
        {
            popInSample = audio.Samples.Get("UI/overlay-pop-in");
            combobreakSample = audio.Samples.Get("Gameplay/combobreak");

            try
            {
                byte[]? audioBytes = null;
                var asm = typeof(TrollOverlay).Assembly;
                using (var stream = asm.GetManifestResourceStream("call_calling.mp3"))
                {
                    if (stream != null)
                    {
                        audioBytes = new byte[stream.Length];
                        stream.ReadExactly(audioBytes, 0, audioBytes.Length);
                    }
                }

                string diskPath = @"C:\Users\dizzy\Downloads\Osu_Debuffs\osu\osu.Game.Rulesets.Osu\Mods\call_calling.mp3";
                if (audioBytes == null && File.Exists(diskPath))
                {
                    audioBytes = File.ReadAllBytes(diskPath);
                }

                if (audioBytes != null)
                {
                    localAudioPath = Path.Combine(Path.GetTempPath(), "osu_discord_call.mp3");
                    File.WriteAllBytes(localAudioPath, audioBytes);

                    var store = new SingleFileResourceStore("call_calling.mp3", audioBytes);
                    var trackStore = audio.GetTrackStore(store);
                    discordTrack = trackStore.Get("call_calling.mp3");
                    if (discordTrack != null)
                    {
                        discordTrack.Looping = true;
                    }
                }
            }
            catch { }

            bsodContainer = createBsodContainer();
            updateContainer = createWindowsUpdateContainer();
            glitchContainer = createGlitchContainer();
            defenderToast = createDefenderToast();
            batteryToast = createBatteryToast();
            discordToast = createDiscordToast();
            donationToast = createDonationToast();
            stickyKeysDialog = createStickyKeysDialog();

            var children = new List<Drawable>
            {
                bsodContainer,
                updateContainer,
                glitchContainer,
                defenderToast,
                batteryToast,
                discordToast,
                donationToast,
                stickyKeysDialog,
            };

            try
            {
                lowPassFilter = new AudioFilter(audio.TrackMixer);
                children.Add(lowPassFilter);
            }
            catch { }

            InternalChildren = children.ToArray();
        }

        private Container createBatteryToast()
        {
            return new Container
            {
                Anchor = Anchor.BottomRight,
                Origin = Anchor.BottomRight,
                Position = new Vector2(-25, -25),
                Size = new Vector2(360, 105),
                Masking = true,
                CornerRadius = 8,
                BorderThickness = 1,
                BorderColour = Colour4.FromHex("#383838"),
                Alpha = 0,
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.FromHex("#1f1f1f")
                    },
                    new SpriteIcon
                    {
                        Icon = FontAwesome.Solid.BatteryQuarter,
                        Size = new Vector2(13),
                        Colour = Colour4.FromHex("#888888"),
                        Position = new Vector2(14, 10)
                    },
                    new OsuSpriteText
                    {
                        Text = "Состояние аккумулятора",
                        Font = OsuFont.GetFont(size: 11),
                        Colour = Colour4.FromHex("#999999"),
                        Position = new Vector2(34, 10)
                    },
                    new SpriteIcon
                    {
                        Icon = FontAwesome.Solid.ExclamationTriangle,
                        Size = new Vector2(26),
                        Colour = Colour4.FromHex("#ff5252"),
                        Position = new Vector2(16, 38)
                    },
                    new OsuSpriteText
                    {
                        Text = "Низкий заряд батареи (5%)",
                        Font = OsuFont.GetFont(size: 15, weight: FontWeight.SemiBold),
                        Colour = Colour4.White,
                        Position = new Vector2(52, 36)
                    },
                    new OsuSpriteText
                    {
                        Text = "Рекомендуется подключить ПК к сети питания.\nОсталось приблизительно 4 минуты.",
                        Font = OsuFont.GetFont(size: 11),
                        Colour = Colour4.FromHex("#b0b0b0"),
                        Position = new Vector2(52, 58)
                    }
                }
            };
        }

        private Container createDiscordToast()
        {
            return new Container
            {
                Anchor = Anchor.TopRight,
                Origin = Anchor.TopRight,
                Position = new Vector2(-25, 25),
                Size = new Vector2(330, 145),
                Masking = true,
                CornerRadius = 10,
                BorderThickness = 1,
                BorderColour = Colour4.FromHex("#3f4147"),
                Alpha = 0,
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.FromHex("#2b2d31")
                    },
                    new SpriteIcon
                    {
                        Icon = FontAwesome.Brands.Discord,
                        Size = new Vector2(16),
                        Colour = Colour4.FromHex("#5865F2"),
                        Position = new Vector2(16, 12)
                    },
                    new OsuSpriteText
                    {
                        Text = "DISCORD • Входящий вызов",
                        Font = OsuFont.GetFont(size: 11, weight: FontWeight.Bold),
                        Colour = Colour4.FromHex("#949ba4"),
                        Position = new Vector2(38, 12)
                    },
                    new CircularContainer
                    {
                        Position = new Vector2(16, 38),
                        Size = new Vector2(46),
                        Masking = true,
                        Children = new Drawable[]
                        {
                            new Box
                            {
                                RelativeSizeAxes = Axes.Both,
                                Colour = Colour4.FromHex("#5865F2")
                            },
                            new SpriteIcon
                            {
                                Anchor = Anchor.Centre,
                                Origin = Anchor.Centre,
                                Icon = FontAwesome.Solid.User,
                                Size = new Vector2(24),
                                Colour = Colour4.White
                            }
                        }
                    },
                    new OsuSpriteText
                    {
                        Text = "Best Friend",
                        Font = OsuFont.GetFont(size: 16, weight: FontWeight.Bold),
                        Colour = Colour4.White,
                        Position = new Vector2(72, 40)
                    },
                    new OsuSpriteText
                    {
                        Text = "Входящий аудиозвонок...",
                        Font = OsuFont.GetFont(size: 12),
                        Colour = Colour4.FromHex("#b5bac1"),
                        Position = new Vector2(72, 62)
                    },
                    new CircularContainer
                    {
                        Position = new Vector2(210, 92),
                        Size = new Vector2(36),
                        Masking = true,
                        Children = new Drawable[]
                        {
                            new Box
                            {
                                RelativeSizeAxes = Axes.Both,
                                Colour = Colour4.FromHex("#23a55a")
                            },
                            new SpriteIcon
                            {
                                Anchor = Anchor.Centre,
                                Origin = Anchor.Centre,
                                Icon = FontAwesome.Solid.Check,
                                Size = new Vector2(18),
                                Colour = Colour4.White
                            }
                        }
                    },
                    new CircularContainer
                    {
                        Position = new Vector2(265, 92),
                        Size = new Vector2(36),
                        Masking = true,
                        Children = new Drawable[]
                        {
                            new Box
                            {
                                RelativeSizeAxes = Axes.Both,
                                Colour = Colour4.FromHex("#f23f43")
                            },
                            new SpriteIcon
                            {
                                Anchor = Anchor.Centre,
                                Origin = Anchor.Centre,
                                Icon = FontAwesome.Solid.Times,
                                Size = new Vector2(18),
                                Colour = Colour4.White
                            }
                        }
                    }
                }
            };
        }

        private Container createDefenderToast()
        {
            return new Container
            {
                Anchor = Anchor.BottomRight,
                Origin = Anchor.BottomRight,
                Position = new Vector2(-25, -25),
                Size = new Vector2(360, 115),
                Masking = true,
                CornerRadius = 8,
                BorderThickness = 1,
                BorderColour = Colour4.FromHex("#383838"),
                Alpha = 0,
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.FromHex("#1f1f1f")
                    },
                    new SpriteIcon
                    {
                        Icon = FontAwesome.Solid.ShieldAlt,
                        Size = new Vector2(14),
                        Colour = Colour4.FromHex("#0078d7"),
                        Position = new Vector2(14, 10)
                    },
                    new OsuSpriteText
                    {
                        Text = "Безопасность Windows",
                        Font = OsuFont.GetFont(size: 11),
                        Colour = Colour4.FromHex("#999999"),
                        Position = new Vector2(34, 10)
                    },
                    new SpriteIcon
                    {
                        Icon = FontAwesome.Solid.ExclamationCircle,
                        Size = new Vector2(28),
                        Colour = Colour4.FromHex("#ff3333"),
                        Position = new Vector2(16, 40)
                    },
                    new OsuSpriteText
                    {
                        Text = "Обнаружена серьезная угроза!",
                        Font = OsuFont.GetFont(size: 15, weight: FontWeight.Bold),
                        Colour = Colour4.White,
                        Position = new Vector2(52, 36)
                    },
                    new OsuSpriteText
                    {
                        Text = "Trojan:Win32/Wacatac.B!ml\nЗащитник блокирует вредоносное действие.",
                        Font = OsuFont.GetFont(size: 11),
                        Colour = Colour4.FromHex("#b0b0b0"),
                        Position = new Vector2(52, 58)
                    }
                }
            };
        }

        private Container createBsodContainer()
        {
            return new Container
            {
                RelativeSizeAxes = Axes.Both,
                Anchor = Anchor.TopLeft,
                Origin = Anchor.TopLeft,
                Depth = float.MinValue,
                Alpha = 0,
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.FromHex("#0078d7")
                    },
                    new Container
                    {
                        Position = new Vector2(80, 60),
                        AutoSizeAxes = Axes.Both,
                        Children = new Drawable[]
                        {
                            new OsuSpriteText
                            {
                                Text = ":(",
                                Font = OsuFont.GetFont(size: 110, weight: FontWeight.Light),
                                Colour = Colour4.White,
                                Position = new Vector2(0, 0)
                            },
                            new OsuSpriteText
                            {
                                Text = "На вашем ПК возникла проблема, и его необходимо",
                                Font = OsuFont.GetFont(size: 26, weight: FontWeight.Regular),
                                Colour = Colour4.White,
                                Position = new Vector2(0, 140)
                            },
                            new OsuSpriteText
                            {
                                Text = "перезагрузить. Мы лишь собираем некоторые сведения об ошибке,",
                                Font = OsuFont.GetFont(size: 26, weight: FontWeight.Regular),
                                Colour = Colour4.White,
                                Position = new Vector2(0, 175)
                            },
                            new OsuSpriteText
                            {
                                Text = "а затем будет автоматически выполнена перезагрузка.",
                                Font = OsuFont.GetFont(size: 26, weight: FontWeight.Regular),
                                Colour = Colour4.White,
                                Position = new Vector2(0, 210)
                            },
                            new OsuSpriteText
                            {
                                Text = "48% завершено",
                                Font = OsuFont.GetFont(size: 22, weight: FontWeight.Light),
                                Colour = Colour4.White,
                                Position = new Vector2(0, 270)
                            },
                            new Container
                            {
                                Position = new Vector2(0, 330),
                                Size = new Vector2(90),
                                BorderThickness = 4,
                                BorderColour = Colour4.White,
                                Masking = true,
                                Child = new SpriteIcon
                                {
                                    Anchor = Anchor.Centre,
                                    Origin = Anchor.Centre,
                                    Icon = FontAwesome.Solid.Desktop,
                                    Size = new Vector2(40),
                                    Colour = Colour4.White
                                }
                            },
                            new OsuSpriteText
                            {
                                Text = "Для получения дополнительных сведений об этой проблеме и возможных способах",
                                Font = OsuFont.GetFont(size: 12),
                                Colour = Colour4.White,
                                Position = new Vector2(105, 330)
                            },
                            new OsuSpriteText
                            {
                                Text = "ее устранения посетите https://windows.com/stopcode",
                                Font = OsuFont.GetFont(size: 12),
                                Colour = Colour4.White,
                                Position = new Vector2(105, 348)
                            },
                            new OsuSpriteText
                            {
                                Text = "Код остановки: CRITICAL_PROCESS_DIED",
                                Font = OsuFont.GetFont(size: 13, weight: FontWeight.Bold),
                                Colour = Colour4.White,
                                Position = new Vector2(105, 375)
                            },
                            new OsuSpriteText
                            {
                                Text = "Что вызвало проблему: osu!.exe",
                                Font = OsuFont.GetFont(size: 12),
                                Colour = Colour4.White,
                                Position = new Vector2(105, 395)
                            }
                        }
                    }
                }
            };
        }

        private static void playSystemSound(uint soundType)
        {
            if (OperatingSystem.IsWindows())
            {
                try
                {
                    MessageBeep(soundType);
                }
                catch { }
            }
        }

        public void ShowBatteryAlert()
        {
            playSystemSound(mb_iconexclamation);
            popInSample?.Play();

            batteryToast.ClearTransforms();
            batteryToast.Alpha = 0;
            batteryToast.X = 380;
            batteryToast.FadeIn(200);
            batteryToast.MoveToX(-25, 300, Easing.OutCubic)
                .Delay(4000)
                .MoveToX(380, 250, Easing.InCubic)
                .FadeOut(250);
        }

        private void stopDiscordCallSound()
        {
            discordTrack?.Stop();

            if (OperatingSystem.IsWindows())
            {
                try
                {
                    mciSendString("stop disc_ring", null, 0, IntPtr.Zero);
                    mciSendString("close disc_ring", null, 0, IntPtr.Zero);
                }
                catch { }
            }
        }

        private void playDiscordAudio()
        {
            stopDiscordCallSound();

            bool played = false;

            if (discordTrack != null)
            {
                try
                {
                    discordTrack.Seek(0);
                    discordTrack.Start();
                    played = true;
                }
                catch { }
            }

            if (OperatingSystem.IsWindows())
            {
                try
                {
                    string target = localAudioPath ?? @"C:\Users\dizzy\Downloads\Osu_Debuffs\osu\osu.Game.Rulesets.Osu\Mods\call_calling.mp3";
                    if (File.Exists(target))
                    {
                        mciSendString("close disc_ring", null, 0, IntPtr.Zero);
                        mciSendString($"open \"{target}\" type mpegvideo alias disc_ring", null, 0, IntPtr.Zero);
                        mciSendString("play disc_ring", null, 0, IntPtr.Zero);
                        played = true;
                    }
                }
                catch { }
            }

            if (!played)
            {
                playSystemSound(mb_iconasterisk);
                popInSample?.Play();
            }

            Scheduler.AddDelayed(stopDiscordCallSound, 4300);
        }

        public void PlayDiscordSoundOnly()
        {
            playDiscordAudio();
        }

        public void ShowDiscordCall()
        {
            playDiscordAudio();

            discordToast.ClearTransforms();
            discordToast.Alpha = 0;
            discordToast.Y = -180;
            discordToast.FadeIn(150);
            discordToast.MoveToY(25, 300, Easing.OutBack);
            discordToast.RotateTo(2, 70).Then().RotateTo(-2, 70).Then().RotateTo(2, 70).Then().RotateTo(0, 70)
                .Delay(4000)
                .MoveToY(-180, 250, Easing.InCubic)
                .FadeOut(250);
        }

        public void ShowDefenderAlert()
        {
            playSystemSound(mb_iconexclamation);
            popInSample?.Play();

            defenderToast.ClearTransforms();
            defenderToast.Alpha = 0;
            defenderToast.X = 380;
            defenderToast.FadeIn(200);
            defenderToast.MoveToX(-25, 300, Easing.OutCubic)
                .Delay(4000)
                .MoveToX(380, 250, Easing.InCubic)
                .FadeOut(250);
        }

        public static void PlayWindowsSound(string filename)
        {
            if (OperatingSystem.IsWindows())
            {
                try
                {
                    string path = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.Windows), "Media", filename);
                    if (File.Exists(path))
                    {
                        PlaySound(path, IntPtr.Zero, SND_ASYNC | SND_FILENAME);
                        return;
                    }
                }
                catch { }
            }
            playSystemSound(mb_iconasterisk);
        }

        public void SetMuffled(bool muffled)
        {
            if (lowPassFilter == null) return;
            if (muffled)
                lowPassFilter.CutoffTo(380, 250, Easing.OutCubic);
            else
                lowPassFilter.CutoffTo(osu.Game.Audio.Effects.AudioFilter.MAX_LOWPASS_CUTOFF, 250, Easing.OutCubic);
        }

        private readonly System.Diagnostics.Stopwatch bsodTimer = new System.Diagnostics.Stopwatch();
        public bool IsBsodActive { get; private set; }
        public float BsodElapsed => (float)bsodTimer.Elapsed.TotalMilliseconds;

        public void ShowBsod()
        {
            playSystemSound(mb_iconhand);
            combobreakSample?.Play();

            bsodContainer.ClearTransforms();
            bsodContainer.Alpha = 1f;

            bsodTimer.Restart();
            IsBsodActive = true;
        }

        private readonly System.Diagnostics.Stopwatch updateTimer = new System.Diagnostics.Stopwatch();
        public bool IsUpdateActive { get; private set; }
        public float UpdateElapsed => (float)updateTimer.Elapsed.TotalMilliseconds;

        public void ShowWindowsUpdate()
        {
            PlayWindowsSound("Windows Shutdown.wav");

            updateContainer.ClearTransforms();
            updateContainer.Alpha = 1f;
            updateSpinnerIcon?.ClearTransforms();
            updateSpinnerIcon?.RotateTo(0).Then().RotateTo(360, 1800).Loop();

            updateTimer.Restart();
            IsUpdateActive = true;
        }

        public void ShowDonation()
        {
            PlayWindowsSound("chimes.wav");

            donationToast.ClearTransforms();
            donationToast.Alpha = 0;
            donationToast.Y = -180;
            donationToast.FadeIn(200);
            donationToast.MoveToY(25, 350, Easing.OutBack)
                .Delay(4000)
                .MoveToY(-180, 300, Easing.InBack)
                .FadeOut(300);
        }

        public void ShowStickyKeys()
        {
            PlayWindowsSound("Windows Exclamation.wav");

            stickyKeysDialog.ClearTransforms();
            stickyKeysDialog.Alpha = 0;
            stickyKeysDialog.FadeIn(80)
                .Delay(3600)
                .FadeOut(250);
        }

        private readonly System.Diagnostics.Stopwatch glitchTimer = new System.Diagnostics.Stopwatch();
        public bool IsGlitchActive { get; private set; }

        public void ShowGlitch()
        {
            PlayWindowsSound("Windows Hardware Fail.wav");

            glitchContainer.ClearTransforms();
            glitchContainer.Alpha = 1f;

            glitchTimer.Restart();
            IsGlitchActive = true;
        }

        private Container createWindowsUpdateContainer()
        {
            return new Container
            {
                RelativeSizeAxes = Axes.Both,
                Anchor = Anchor.TopLeft,
                Origin = Anchor.TopLeft,
                Depth = float.MinValue,
                Alpha = 0,
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.Black
                    },
                    new FillFlowContainer
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        AutoSizeAxes = Axes.Both,
                        Direction = FillDirection.Vertical,
                        Spacing = new Vector2(0, 16),
                        Children = new Drawable[]
                        {
                            new Container
                            {
                                Anchor = Anchor.TopCentre,
                                Origin = Anchor.TopCentre,
                                Size = new Vector2(50),
                                Child = updateSpinnerIcon = new SpriteIcon
                                {
                                    Anchor = Anchor.Centre,
                                    Origin = Anchor.Centre,
                                    Icon = FontAwesome.Solid.CircleNotch,
                                    Size = new Vector2(46),
                                    Colour = Colour4.White
                                }
                            },
                            new OsuSpriteText
                            {
                                Anchor = Anchor.TopCentre,
                                Origin = Anchor.TopCentre,
                                Text = "Идет работа с обновлениями  67%",
                                Font = OsuFont.GetFont(size: 26, weight: FontWeight.Light),
                                Colour = Colour4.White
                            },
                            new OsuSpriteText
                            {
                                Anchor = Anchor.TopCentre,
                                Origin = Anchor.TopCentre,
                                Text = "Не выключайте компьютер. Это займет некоторое время.",
                                Font = OsuFont.GetFont(size: 16),
                                Colour = Colour4.FromHex("#b0b0b0")
                            },
                            new OsuSpriteText
                            {
                                Anchor = Anchor.TopCentre,
                                Origin = Anchor.TopCentre,
                                Text = "Ваш компьютер может перезагрузиться несколько раз",
                                Font = OsuFont.GetFont(size: 13),
                                Colour = Colour4.FromHex("#707070")
                            }
                        }
                    }
                }
            };
        }

        private Container createDonationToast()
        {
            return new Container
            {
                Anchor = Anchor.TopCentre,
                Origin = Anchor.TopCentre,
                Position = new Vector2(0, -180),
                Size = new Vector2(460, 115),
                Masking = true,
                CornerRadius = 14,
                BorderThickness = 2,
                BorderColour = Colour4.FromHex("#ff9800"),
                Alpha = 0,
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.FromHex("#181824")
                    },
                    new Box
                    {
                        Anchor = Anchor.TopLeft,
                        Origin = Anchor.TopLeft,
                        RelativeSizeAxes = Axes.X,
                        Height = 4,
                        Colour = Colour4.FromHex("#ff9800")
                    },
                    new Container
                    {
                        Anchor = Anchor.CentreLeft,
                        Origin = Anchor.CentreLeft,
                        Position = new Vector2(18, 0),
                        Size = new Vector2(56),
                        Masking = true,
                        CornerRadius = 28,
                        Children = new Drawable[]
                        {
                            new Box
                            {
                                RelativeSizeAxes = Axes.Both,
                                Colour = Colour4.FromHex("#ff9800").Opacity(0.2f)
                            },
                            new SpriteIcon
                            {
                                Anchor = Anchor.Centre,
                                Origin = Anchor.Centre,
                                Icon = FontAwesome.Solid.Coins,
                                Size = new Vector2(28),
                                Colour = Colour4.FromHex("#ffd700")
                            }
                        }
                    },
                    new FillFlowContainer
                    {
                        Anchor = Anchor.CentreLeft,
                        Origin = Anchor.CentreLeft,
                        Position = new Vector2(90, 0),
                        AutoSizeAxes = Axes.Both,
                        Direction = FillDirection.Vertical,
                        Spacing = new Vector2(0, 4),
                        Children = new Drawable[]
                        {
                            new OsuSpriteText
                            {
                                Text = "DONATIONALERTS",
                                Font = OsuFont.GetFont(size: 11, weight: FontWeight.Bold),
                                Colour = Colour4.FromHex("#ff9800")
                            },
                            new OsuSpriteText
                            {
                                Text = "Папич — 5 000 ₽",
                                Font = OsuFont.GetFont(size: 19, weight: FontWeight.Bold),
                                Colour = Colour4.White
                            },
                            new OsuSpriteText
                            {
                                Text = "«Удали игру и не позорься»",
                                Font = OsuFont.GetFont(size: 14, weight: FontWeight.Medium, italics: true),
                                Colour = Colour4.FromHex("#dddddd")
                            }
                        }
                    }
                }
            };
        }

        private Container createStickyKeysDialog()
        {
            return new Container
            {
                Anchor = Anchor.Centre,
                Origin = Anchor.Centre,
                Size = new Vector2(450, 220),
                Masking = true,
                CornerRadius = 8,
                BorderThickness = 1,
                BorderColour = Colour4.FromHex("#7a7a7a"),
                Alpha = 0,
                Children = new Drawable[]
                {
                    new Box
                    {
                        RelativeSizeAxes = Axes.Both,
                        Colour = Colour4.FromHex("#f0f0f0")
                    },
                    new Container
                    {
                        RelativeSizeAxes = Axes.X,
                        Height = 32,
                        Children = new Drawable[]
                        {
                            new Box
                            {
                                RelativeSizeAxes = Axes.Both,
                                Colour = Colour4.White
                            },
                            new OsuSpriteText
                            {
                                Anchor = Anchor.CentreLeft,
                                Origin = Anchor.CentreLeft,
                                Position = new Vector2(12, 0),
                                Text = "Залипание клавиш",
                                Font = OsuFont.GetFont(size: 13, weight: FontWeight.SemiBold),
                                Colour = Colour4.Black
                            },
                            new SpriteIcon
                            {
                                Anchor = Anchor.CentreRight,
                                Origin = Anchor.CentreRight,
                                Position = new Vector2(-12, 0),
                                Icon = FontAwesome.Solid.Times,
                                Size = new Vector2(12),
                                Colour = Colour4.FromHex("#666666")
                            }
                        }
                    },
                    new Container
                    {
                        Position = new Vector2(18, 46),
                        Size = new Vector2(414, 115),
                        Children = new Drawable[]
                        {
                            new SpriteIcon
                            {
                                Position = new Vector2(0, 4),
                                Icon = FontAwesome.Solid.Keyboard,
                                Size = new Vector2(36),
                                Colour = Colour4.FromHex("#0078d7")
                            },
                            new OsuSpriteText
                            {
                                Position = new Vector2(50, 0),
                                Text = "Вы хотите включить залипание клавиш?",
                                Font = OsuFont.GetFont(size: 13, weight: FontWeight.Bold),
                                Colour = Colour4.Black
                            },
                            new OsuSpriteText
                            {
                                Position = new Vector2(50, 24),
                                Text = "Залипание клавиш позволяет использовать клавиши SHIFT, CTRL,\nALT или клавишу Windows, нажимая их по очереди.\n\nЧтобы отключить залипание клавиш, нажмите SHIFT пять раз.",
                                Font = OsuFont.GetFont(size: 11),
                                Colour = Colour4.FromHex("#333333")
                            }
                        }
                    },
                    new FillFlowContainer
                    {
                        Anchor = Anchor.BottomRight,
                        Origin = Anchor.BottomRight,
                        Position = new Vector2(-18, -14),
                        AutoSizeAxes = Axes.Both,
                        Direction = FillDirection.Horizontal,
                        Spacing = new Vector2(10, 0),
                        Children = new Drawable[]
                        {
                            new Container
                            {
                                Size = new Vector2(80, 26),
                                Masking = true,
                                CornerRadius = 4,
                                Children = new Drawable[]
                                {
                                    new Box
                                    {
                                        RelativeSizeAxes = Axes.Both,
                                        Colour = Colour4.FromHex("#0078d7")
                                    },
                                    new OsuSpriteText
                                    {
                                        Anchor = Anchor.Centre,
                                        Origin = Anchor.Centre,
                                        Text = "Да",
                                        Font = OsuFont.GetFont(size: 12, weight: FontWeight.SemiBold),
                                        Colour = Colour4.White
                                    }
                                }
                            },
                            new Container
                            {
                                Size = new Vector2(80, 26),
                                Masking = true,
                                CornerRadius = 4,
                                BorderThickness = 1,
                                BorderColour = Colour4.FromHex("#cccccc"),
                                Children = new Drawable[]
                                {
                                    new Box
                                    {
                                        RelativeSizeAxes = Axes.Both,
                                        Colour = Colour4.FromHex("#e6e6e6")
                                    },
                                    new OsuSpriteText
                                    {
                                        Anchor = Anchor.Centre,
                                        Origin = Anchor.Centre,
                                        Text = "Нет",
                                        Font = OsuFont.GetFont(size: 12),
                                        Colour = Colour4.Black
                                    }
                                }
                            }
                        }
                    }
                }
            };
        }

        private Container createGlitchContainer()
        {
            var container = new Container
            {
                RelativeSizeAxes = Axes.Both,
                Anchor = Anchor.TopLeft,
                Origin = Anchor.TopLeft,
                Depth = float.MinValue,
                Alpha = 0
            };

            for (int i = 0; i < 14; i++)
            {
                var slice = new Box
                {
                    RelativeSizeAxes = Axes.X,
                    Height = 25,
                    Colour = (i % 3 == 0) ? Colour4.FromHex("#ff0055").Opacity(0.65f)
                           : (i % 3 == 1) ? Colour4.FromHex("#00ffee").Opacity(0.65f)
                           : Colour4.FromHex("#55ff00").Opacity(0.5f),
                    Y = i * 50
                };
                glitchSlices.Add(slice);
                container.Add(slice);
            }

            return container;
        }

        protected override void Update()
        {
            base.Update();

            if (IsBsodActive)
            {
                float elapsed = BsodElapsed;
                const float holdDuration = 3000f;
                const float fadeDuration = 400f;
                const float totalDuration = holdDuration + fadeDuration;

                if (elapsed < holdDuration)
                {
                    bsodContainer.Alpha = 1f;
                }
                else if (elapsed < totalDuration)
                {
                    float progress = (elapsed - holdDuration) / fadeDuration;
                    bsodContainer.Alpha = 1f - progress;
                }
                else
                {
                    bsodContainer.Alpha = 0f;
                    bsodTimer.Stop();
                    IsBsodActive = false;
                }
            }

            if (IsUpdateActive)
            {
                float elapsed = UpdateElapsed;
                const float holdDuration = 3500f;
                const float fadeDuration = 400f;
                const float totalDuration = holdDuration + fadeDuration;

                if (elapsed < holdDuration)
                {
                    updateContainer.Alpha = 1f;
                }
                else if (elapsed < totalDuration)
                {
                    float progress = (elapsed - holdDuration) / fadeDuration;
                    updateContainer.Alpha = 1f - progress;
                }
                else
                {
                    updateContainer.Alpha = 0f;
                    updateTimer.Stop();
                    IsUpdateActive = false;
                }
            }

            if (IsGlitchActive)
            {
                float elapsed = (float)glitchTimer.Elapsed.TotalMilliseconds;
                if (elapsed < 1400f)
                {
                    glitchContainer.Alpha = 1f;
                    for (int i = 0; i < glitchSlices.Count; i++)
                    {
                        glitchSlices[i].Y = (float)rnd.NextDouble() * Math.Max(DrawHeight, 600f);
                        glitchSlices[i].Height = (float)rnd.Next(6, 60);
                        glitchSlices[i].X = (float)(rnd.NextDouble() * 80 - 40);
                        glitchSlices[i].Alpha = (float)(rnd.NextDouble() * 0.7 + 0.3);
                    }
                }
                else
                {
                    glitchContainer.Alpha = 0f;
                    glitchTimer.Stop();
                    IsGlitchActive = false;
                }
            }
        }

        public void ScheduleDelayed(Action action, double delay)
        {
            Scheduler.AddDelayed(action, delay);
        }
    }

    public class SingleFileResourceStore : IResourceStore<byte[]>
    {
        private readonly string name;
        private readonly byte[] data;

        public SingleFileResourceStore(string name, byte[] data)
        {
            this.name = name;
            this.data = data;
        }

        public byte[]? Get(string lookup) => data;
        public System.Threading.Tasks.Task<byte[]?> GetAsync(string lookup, System.Threading.CancellationToken ct = default) => System.Threading.Tasks.Task.FromResult<byte[]?>(data);
        public Stream? GetStream(string lookup) => new MemoryStream(data);
        public IEnumerable<string> GetAvailableResources() => new[] { name };
        public void Dispose() { }
    }
}
