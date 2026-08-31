using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using osu.Framework.Allocation;
using osu.Framework.Graphics;
using osu.Framework.Graphics.Containers;
using osu.Framework.Graphics.Shapes;
using osu.Framework.Localisation;
using osu.Game.Rulesets.Mods;
using osu.Game.Rulesets.Objects.Drawables;
using osu.Game.Rulesets.Osu.Objects;
using osu.Game.Rulesets.UI;
using osu.Game.Screens.Play;
using osuTK;
using osu.Framework.Graphics.Sprites;

namespace osu.Game.Rulesets.Osu.Mods
{
    public partial class OsuModChaos : Mod, IUpdatableByPlayfield, IApplicableToDrawableRuleset<OsuHitObject>, IApplicableToPlayer
    {
        public override string Name => "Chaos Remote";
        public override string Acronym => "CHR";
        public override ModType Type => ModType.Fun;
        public override LocalisableString Description => "Chaos & Wind controlled via remote TCP panel.";
        [Obsolete]
        public override double ScoreMultiplier => 1.0;

        // Chaos (Shake)
        public static volatile bool IsChaosActive = false;
        public static volatile float ChaosStrength = 1.0f;
        
        // Wind / Gravity
        public static volatile bool IsWindActive = false;
        public static volatile float WindStrength = 1.0f;
        public static volatile float WindDirection = 0f; // Degrees (0 = right, 90 = down)
        
        // Magnet (Repel notes from cursor)
        public static volatile bool IsMagnetActive = false;
        public static volatile float MagnetStrength = 1.0f;
        
        // Earthquake (Shake interface)
        public static volatile bool IsEarthquakeActive = false;
        public static volatile float EarthquakeStrength = 1.0f;
        
        // Interface Distortion
        public static volatile float PlayfieldScaleX = 1.0f;
        public static volatile float PlayfieldScaleY = 1.0f;
        public static volatile float HudScaleX = 1.0f;
        public static volatile float HudScaleY = 1.0f;
        
        // Blackout (Freeze Time)
        public static volatile bool IsFreezeActive = false;

        // Kiss & Fake Miss
        public static volatile bool IsKissActive = false;
        public static volatile bool IsFakeMissActive = false;

        // Flashbang & Hidden
        public static volatile bool IsFlashbangActive = false;
        public static volatile bool IsHiddenActive = false;

        // Mirror
        public static volatile bool IsMirrorPlayfieldX = false;
        public static volatile bool IsMirrorPlayfieldY = false;
        public static volatile bool IsMirrorHudX = false;
        public static volatile bool IsMirrorHudY = false;
        
        public static Player? PlayerInstance;
        private Container cachedHudOverlay;

        private static bool isServerRunning = false;
        private static readonly object lockObj = new object();
        private Random rnd = new Random();

        private WindOverlay? windOverlay;
        private BlackoutOverlay? blackoutOverlay;
        private ScreamerOverlay? screamerOverlay;
        private FlashbangOverlay? flashbangOverlay;

        public OsuModChaos()
        {
            StartServer();
        }

        public void ApplyToPlayer(Player player)
        {
            PlayerInstance = player;
        }

        private static void StartServer()
        {
            lock (lockObj)
            {
                if (isServerRunning) return;
                isServerRunning = true;

                Thread serverThread = new Thread(() =>
                {
                    try
                    {
                        TcpListener listener = new TcpListener(IPAddress.Any, 9000);
                        listener.Start();
                        while (true)
                        {
                            using (TcpClient client = listener.AcceptTcpClient())
                            using (NetworkStream stream = client.GetStream())
                            {
                                byte[] buffer = new byte[256];
                                int bytes = stream.Read(buffer, 0, buffer.Length);
                                string msg = Encoding.UTF8.GetString(buffer, 0, bytes).Trim();
                                
                                if (msg == "CHAOS_ON") IsChaosActive = true;
                                else if (msg == "CHAOS_OFF") IsChaosActive = false;
                                else if (msg.StartsWith("STRENGTH:"))
                                {
                                    if (float.TryParse(msg.Substring(9), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                        ChaosStrength = parsed;
                                }
                                else if (msg == "WIND_ON") IsWindActive = true;
                                else if (msg == "WIND_OFF") IsWindActive = false;
                                else if (msg.StartsWith("WIND_STRENGTH:"))
                                {
                                    if (float.TryParse(msg.Substring(14), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                        WindStrength = parsed;
                                }
                                else if (msg.StartsWith("WIND_DIR:"))
                                {
                                    if (float.TryParse(msg.Substring(9), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                        WindDirection = parsed;
                                }
                                else if (msg == "MAGNET_ON") IsMagnetActive = true;
                                else if (msg == "MAGNET_OFF") IsMagnetActive = false;
                                else if (msg.StartsWith("MAGNET_STRENGTH:"))
                                {
                                    if (float.TryParse(msg.Substring(16), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                        MagnetStrength = parsed;
                                }
                                else if (msg == "EARTHQUAKE_ON") IsEarthquakeActive = true;
                                else if (msg == "EARTHQUAKE_OFF") IsEarthquakeActive = false;
                                else if (msg.StartsWith("EARTHQUAKE_STRENGTH:"))
                                {
                                    if (float.TryParse(msg.Substring(20), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                        EarthquakeStrength = parsed;
                                }
                                else if (msg.StartsWith("FREEZE_ON"))
                                {
                                    IsFreezeActive = true;
                                }
                                else if (msg.StartsWith("FREEZE_OFF"))
                                {
                                    IsFreezeActive = false;
                                }
                                else if (msg.StartsWith("KISS"))
                                {
                                    IsKissActive = true;
                                }
                                else if (msg.StartsWith("FAKE_MISS"))
                                {
                                    IsFakeMissActive = true;
                                }
                                else if (msg.StartsWith("SCALE_X:"))
                                {
                                    if (float.TryParse(msg.Substring(8), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                        PlayfieldScaleX = parsed;
                                }
                                else if (msg.StartsWith("SCALE_Y:"))
                                {
                                    if (float.TryParse(msg.Substring(8), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                        PlayfieldScaleY = parsed;
                                }
                                else if (msg.StartsWith("HUD_SCALE_X:"))
                                {
                                    if (float.TryParse(msg.Substring(12), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                        HudScaleX = parsed;
                                }
                                else if (msg.StartsWith("HUD_SCALE_Y:"))
                                {
                                    if (float.TryParse(msg.Substring(12), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                        HudScaleY = parsed;
                                }
                                else if (msg.StartsWith("SCALE:"))
                                {
                                    if (float.TryParse(msg.Substring(6), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                    {
                                        PlayfieldScaleX = parsed;
                                        PlayfieldScaleY = parsed;
                                    }
                                }
                                else if (msg.StartsWith("HUD_SCALE:"))
                                {
                                    if (float.TryParse(msg.Substring(10), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float parsed))
                                    {
                                        HudScaleX = parsed;
                                        HudScaleY = parsed;
                                    }
                                }
                                else if (msg == "FLASHBANG") IsFlashbangActive = true;
                                else if (msg == "HIDDEN_ON") IsHiddenActive = true;
                                else if (msg == "HIDDEN_OFF") IsHiddenActive = false;
                                else if (msg == "MIRROR_PLAYFIELD_X_ON") IsMirrorPlayfieldX = true;
                                else if (msg == "MIRROR_PLAYFIELD_X_OFF") IsMirrorPlayfieldX = false;
                                else if (msg == "MIRROR_PLAYFIELD_Y_ON") IsMirrorPlayfieldY = true;
                                else if (msg == "MIRROR_PLAYFIELD_Y_OFF") IsMirrorPlayfieldY = false;
                                else if (msg == "MIRROR_HUD_X_ON") IsMirrorHudX = true;
                                else if (msg == "MIRROR_HUD_X_OFF") IsMirrorHudX = false;
                                else if (msg == "MIRROR_HUD_Y_ON") IsMirrorHudY = true;
                                else if (msg == "MIRROR_HUD_Y_OFF") IsMirrorHudY = false;
                            }
                        }
                    }
                    catch { } // Игнорируем ошибки сети
                });
                serverThread.IsBackground = true;
                serverThread.Start();
            }
        }

        public void ApplyToDrawableRuleset(DrawableRuleset<OsuHitObject> drawableRuleset)
        {
            // Добавляем слои поверх всего
            windOverlay = new WindOverlay();
            blackoutOverlay = new BlackoutOverlay();
            screamerOverlay = new ScreamerOverlay();
            flashbangOverlay = new FlashbangOverlay();
            
            drawableRuleset.Overlays.Add(windOverlay);
            drawableRuleset.Overlays.Add(blackoutOverlay);
            drawableRuleset.Overlays.Add(flashbangOverlay);
            drawableRuleset.Overlays.Add(screamerOverlay);
        }

        public void Update(Playfield playfield)
        {
            if (windOverlay != null)
            {
                windOverlay.IsActive = IsWindActive;
                windOverlay.Strength = WindStrength;
                windOverlay.Direction = WindDirection;
            }

            if (blackoutOverlay != null)
            {
                blackoutOverlay.IsActive = IsFreezeActive;
            }

            if (screamerOverlay != null)
            {
                if (IsKissActive)
                {
                    screamerOverlay.FireKiss();
                    IsKissActive = false;
                }
                if (IsFakeMissActive)
                {
                    screamerOverlay?.FireFakeMiss();
                    IsFakeMissActive = false;
                }
            }

            if (flashbangOverlay != null)
            {
                if (IsFlashbangActive)
                {
                    flashbangOverlay.FireFlashbang();
                    IsFlashbangActive = false;
                }
            }

            // HUD Scaling (via reflection)
            if (PlayerInstance != null)
            {
                if (cachedHudOverlay == null)
                {
                    var prop = typeof(Player).GetProperty("HUDOverlay", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
                    if (prop != null)
                        cachedHudOverlay = prop.GetValue(PlayerInstance) as Container;
                }

                if (cachedHudOverlay != null)
                {
                    float hx = HudScaleX * (IsMirrorHudX ? -1 : 1);
                    float hy = HudScaleY * (IsMirrorHudY ? -1 : 1);
                    cachedHudOverlay.Scale = new Vector2(hx, hy);
                }
            }

            float elapsed = (float)playfield.Clock.ElapsedFrameTime;

            float rad = MathHelper.DegreesToRadians(WindDirection);
            float driftX = (float)Math.Cos(rad);
            float driftY = (float)Math.Sin(rad);
            float driftAmount = (elapsed / 1000f) * 150f * WindStrength;

            Vector2? cursorPos = playfield.Cursor?.ActiveCursor?.DrawPosition;
            
            // Землетрясение (Тряска интерфейса) и Искажение
            float px = PlayfieldScaleX * (IsMirrorPlayfieldX ? -1 : 1);
            float py = PlayfieldScaleY * (IsMirrorPlayfieldY ? -1 : 1);
            Vector2 baseScale = new Vector2(px, py);

            if (IsEarthquakeActive)
            {
                playfield.Rotation = (float)(rnd.NextDouble() * 10 - 5) * EarthquakeStrength;
                playfield.Scale = baseScale + new Vector2((float)(rnd.NextDouble() * 0.4 - 0.2) * EarthquakeStrength);
            }
            else
            {
                playfield.Rotation = 0;
                playfield.Scale = baseScale;
            }

            foreach (var drawable in playfield.HitObjectContainer.AliveObjects)
            {
                if (drawable.HitObject is SliderRepeat || drawable.HitObject is SliderTailCircle)
                    continue;

                // Хаос (тряска)
                if (IsChaosActive)
                {
                    drawable.Rotation = (float)(rnd.NextDouble() * 20 - 10) * ChaosStrength;
                    float alphaBase = 1.0f - (0.8f * ChaosStrength);
                    drawable.Alpha = (float)(alphaBase + rnd.NextDouble() * (1.0f - alphaBase));
                }

                // Ветер (снос нот)
                if (IsWindActive)
                {
                    drawable.Position += new Vector2(driftX, driftY) * driftAmount;
                }

                // Магнит (отталкивание от курсора)
                if (IsMagnetActive && cursorPos.HasValue)
                {
                    Vector2 diff = drawable.Position - cursorPos.Value;
                    float distance = diff.Length;
                    
                    // Радиус срабатывания отталкивания
                    float radius = 150f;
                    
                    if (distance < radius && distance > 0.1f)
                    {
                        // Чем ближе курсор, тем сильнее отталкивание (от 0 до 1)
                        float force = (radius - distance) / radius;
                        
                        // Сдвигаем ноту от курсора
                        drawable.Position += diff.Normalized() * force * MagnetStrength * (elapsed / 2f);
                    }
                }

                if (drawable is osu.Game.Rulesets.Osu.Skinning.IHasApproachCircle approachObj && approachObj.ApproachCircle != null)
                {
                    if (IsHiddenActive)
                        approachObj.ApproachCircle.Colour = Colour4.Transparent;
                    else
                        approachObj.ApproachCircle.Colour = Colour4.White;
                }

                foreach (var nested in drawable.NestedHitObjects)
                {
                    if (nested is osu.Game.Rulesets.Osu.Skinning.IHasApproachCircle nestedApproachObj && nestedApproachObj.ApproachCircle != null)
                    {
                        if (IsHiddenActive)
                            nestedApproachObj.ApproachCircle.Colour = Colour4.Transparent;
                        else
                            nestedApproachObj.ApproachCircle.Colour = Colour4.White;
                    }
                }
            }
        }



        public partial class WindOverlay : Container
        {
            public bool IsActive;
            public float Strength = 1.0f;
            
            private float direction;
            public float Direction
            {
                get => direction;
                set
                {
                    direction = value;
                    Rotation = value;
                }
            }

            private double timeSinceLastSpawn;

            [BackgroundDependencyLoader]
            private void load()
            {
                RelativeSizeAxes = Axes.Both;
                Anchor = Anchor.Centre;
                Origin = Anchor.Centre;
                Size = new Vector2(2f); // В два раза больше экрана, чтобы при вращении углы не пустовали
            }

            protected override void Update()
            {
                base.Update();
                if (!IsActive) return;

                timeSinceLastSpawn += Clock.ElapsedFrameTime;
                
                // Спавним частицы (полосы)
                if (timeSinceLastSpawn > 20 / Math.Max(0.1f, Strength))
                {
                    timeSinceLastSpawn = 0;
                    spawnStreak();
                }
            }

            private void spawnStreak()
            {
                var rnd = new Random();
                var box = new Box
                {
                    RelativePositionAxes = Axes.Both,
                    X = -0.5f,
                    Y = (float)rnd.NextDouble() - 0.5f,
                    Width = 150 + (float)rnd.NextDouble() * 150,
                    Height = 2 + (float)rnd.NextDouble() * 3,
                    Colour = Colour4.White,
                    Alpha = 0.1f + (float)rnd.NextDouble() * 0.2f
                };

                Add(box);

                // Анимация пролета
                float duration = 1500f / Math.Max(0.1f, Strength);
                box.MoveToX(1.5f, duration).FadeOut(duration).Expire(true);
            }
        }

        public class BlackoutOverlay : Container
        {
            public bool IsActive;
            private bool wasActive;
            private Box blackoutBox;
            private osu.Framework.Audio.Sample.Sample powerDownSample;
            private osu.Framework.Audio.Sample.Sample powerUpSample;
            
            private System.Diagnostics.Stopwatch resumeTimer = new System.Diagnostics.Stopwatch();
            private bool isResuming;

            [BackgroundDependencyLoader]
            private void load(osu.Framework.Audio.AudioManager audio)
            {
                RelativeSizeAxes = Axes.Both;
                AlwaysPresent = true;
                
                Child = blackoutBox = new Box
                {
                    RelativeSizeAxes = Axes.Both,
                    Colour = Colour4.Black,
                    Alpha = 0
                };
                
                powerDownSample = audio.Samples.Get("Gameplay/failsound");
                powerUpSample = audio.Samples.Get("UI/default-select");
            }

            protected override void Update()
            {
                base.Update();
                
                if (IsActive && !wasActive)
                {
                    powerDownSample?.Play();
                    
                    if (PlayerInstance != null)
                    {
                        var prop = typeof(Player).GetProperty("GameplayClockContainer", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                        var clock = prop?.GetValue(PlayerInstance);
                        if (clock != null)
                        {
                            clock.GetType().GetMethod("Stop")?.Invoke(clock, null);
                        }
                    }

                    blackoutBox.Alpha = 1;
                    isResuming = false;
                    resumeTimer.Stop();
                    wasActive = true;
                }
                else if (!IsActive && wasActive)
                {
                    if (!isResuming)
                    {
                        powerUpSample?.Play();
                        isResuming = true;
                        resumeTimer.Restart();
                    }

                    float elapsed = (float)resumeTimer.Elapsed.TotalMilliseconds;
                    float duration = 1500f; // 1.5 seconds delay

                    if (elapsed < duration)
                    {
                        // Linear fade out
                        float progress = elapsed / duration;
                        blackoutBox.Alpha = 1f - progress;
                    }
                    else
                    {
                        blackoutBox.Alpha = 0;
                        
                        if (PlayerInstance != null)
                        {
                            var prop = typeof(Player).GetProperty("GameplayClockContainer", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                            var clock = prop?.GetValue(PlayerInstance);
                            if (clock != null)
                            {
                                clock.GetType().GetMethod("Start")?.Invoke(clock, null);
                            }
                        }

                        resumeTimer.Stop();
                        isResuming = false;
                        wasActive = false;
                    }
                }
            }
        }

        public class ScreamerOverlay : Container
        {
            private SpriteIcon icon;
            private osu.Framework.Audio.Sample.Sample fakeMissSample;
            private osu.Framework.Audio.Sample.Sample kissSample;
            
            [BackgroundDependencyLoader]
            private void load(osu.Framework.Audio.AudioManager audio)
            {
                RelativeSizeAxes = Axes.Both;
                AlwaysPresent = true;
                
                Child = icon = new SpriteIcon
                {
                    Anchor = Anchor.Centre,
                    Origin = Anchor.Centre,
                    Icon = FontAwesome.Solid.Heart, // Используем сердечко
                    Colour = Colour4.HotPink,
                    Size = new osuTK.Vector2(300),
                    Alpha = 0,
                    Scale = new osuTK.Vector2(0)
                };
                
                fakeMissSample = audio.Samples.Get("Gameplay/combobreak");
                kissSample = audio.Samples.Get("UI/default-select");
            }
            
            public void FireKiss()
            {
                kissSample?.Play();
                
                icon.ClearTransforms();
                icon.Alpha = 0;
                icon.Scale = new osuTK.Vector2(0);
                
                icon.FadeIn(100);
                icon.ScaleTo(1.5f, 150, Easing.OutElastic)
                    .Then().Delay(600)
                    .ScaleTo(0, 300, Easing.In)
                    .FadeOut(300);
            }
            
            public void FireFakeMiss()
            {
                fakeMissSample?.Play();
            }
        }

        public class FlashbangOverlay : Container
        {
            private Box flashBox;
            private osu.Framework.Audio.Sample.Sample flashbangSample;
            
            [BackgroundDependencyLoader]
            private void load(osu.Framework.Audio.AudioManager audio)
            {
                RelativeSizeAxes = Axes.Both;
                AlwaysPresent = true;
                
                Child = flashBox = new Box
                {
                    RelativeSizeAxes = Axes.Both,
                    Colour = Colour4.White,
                    Alpha = 0
                };
                
                flashbangSample = audio.Samples.Get("UI/overlay-pop-in"); 
            }
            
            public void FireFlashbang()
            {
                flashbangSample?.Play();
                flashBox.ClearTransforms();
                flashBox.Alpha = 1;
                flashBox.FadeOut(3000, Easing.OutQuint);
            }
        }
    }
}
