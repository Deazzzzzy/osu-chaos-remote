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

        private const uint mb_iconhand = 0x00000010;
        private const uint mb_iconexclamation = 0x00000030;
        private const uint mb_iconasterisk = 0x00000040;

        private Container batteryToast = null!;
        private Container discordToast = null!;
        private Container bsodContainer = null!;
        private Container defenderToast = null!;

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

            InternalChildren = new Drawable[]
            {
                bsodContainer = createBsodContainer(),
                defenderToast = createDefenderToast(),
                batteryToast = createBatteryToast(),
                discordToast = createDiscordToast(),
            };
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

        public void ShowDiscordCall()
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

            discordToast.ClearTransforms();
            discordToast.Alpha = 0;
            discordToast.Y = -180;
            discordToast.FadeIn(150);
            discordToast.MoveToY(25, 300, Easing.OutBack);
            discordToast.RotateTo(2, 70).Then().RotateTo(-2, 70).Then().RotateTo(2, 70).Then().RotateTo(0, 70)
                .Delay(4000)
                .MoveToY(-180, 250, Easing.InCubic)
                .FadeOut(250);

            Scheduler.AddDelayed(stopDiscordCallSound, 4300);
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

        public void ShowBsod()
        {
            playSystemSound(mb_iconhand);
            combobreakSample?.Play();

            bsodContainer.ClearTransforms();
            bsodContainer.Alpha = 0;
            bsodContainer.FadeIn(40)
                .Delay(3000)
                .FadeOut(400);
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
