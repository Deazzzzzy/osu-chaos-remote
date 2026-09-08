using System;
using System.Linq;
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
using osu.Game.Rulesets.Osu.UI;
using osu.Game.Rulesets.Osu.UI.Cursor;

namespace osu.Game.Rulesets.Osu.Mods
{
    public partial class OsuModChaos : Mod, IUpdatableByPlayfield, IApplicableToDrawableRuleset<OsuHitObject>, IApplicableToPlayer, IApplicableToTrack, IApplicableToDrawableHitObject
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
        
        // Speed
        public static volatile float SpeedChange = 1.0f;
        public static volatile bool AdjustPitch = false;

        // Input Lag
        public static volatile float InputLagMilliseconds = 0;

        // Cursor Scale Multiplier
        public static volatile float CursorScaleMultiplier = 1.0f;

        // Invert Controls
        public static volatile bool InvertX = false;
        public static volatile bool InvertY = false;

        // Key Jam
        public static volatile bool JamK1 = false;
        public static volatile bool JamK2 = false;

        // Black Hole (Gravity to center)
        public static volatile bool IsBlackHoleActive = false;
        public static volatile float BlackHoleStrength = 1.0f;

        // Audio Desync
        public static volatile float AudioDesyncMilliseconds = 0;

        // Chameleon Notes
        public enum ChameleonType { Off, Black, Rainbow, Monochrome }
        public static volatile ChameleonType ChameleonMode = ChameleonType.Off;
        private ChameleonType lastChameleonMode = ChameleonType.Off;

        // Troll Notifications
        public static volatile bool TriggerTrollBattery = false;
        public static volatile bool TriggerTrollDiscord = false;
        public static volatile bool TriggerTrollDiscordSoundOnly = false;
        public static volatile bool TriggerTrollBsod = false;
        public static volatile bool TriggerTrollDefender = false;

        // Phase 4 Troll Notifications
        public static volatile bool TriggerTrollUpdate = false;
        public static volatile bool TriggerTrollDonate = false;
        public static volatile bool TriggerTrollStickyKeys = false;
        public static volatile bool TriggerTrollGlitch = false;

        // Phase 4 Mouse & Cursor Trolling
        public static volatile bool IsMouseDisconnected = false;
        public static volatile bool TriggerMouseDisconnect = false;
        public static volatile float CursorJitterStrength = 0f;
        public static volatile bool IsCircleRepulsion = false;

        // Phase 4 Visual / Camera / Sliders
        public static volatile bool IsDrunkCamera = false;
        public static volatile bool IsScreenShake = false;
        public static volatile bool IsTunnelVision = false;
        public static volatile bool IsGhostSliders = false;

        // Phase 4 Audio Havoc
        public static volatile bool IsMuffledAudio = false;
        public static volatile bool IsAudioPanSpin = false;
        private readonly osu.Framework.Bindables.BindableDouble balanceAdjustment = new osu.Framework.Bindables.BindableDouble(0);

        // Phase 5 Troll Notifications & Overlays
        public static volatile bool TriggerTrollTelegram = false;
        public static volatile bool TriggerTrollTelegramAudioOnly = false;
        public static volatile bool TriggerTrollSteam = false;
        public static volatile bool IsWatermarkActive = false;
        public static volatile bool IsInvertColorsActive = false;
        public static volatile bool IsMosaicActive = false;

        // Phase 5 Cursor, Mechanics & Audio
        public static volatile bool IsBusyCursorActive = false;
        public static volatile bool TriggerBarrelRoll = false;
        private static readonly System.Diagnostics.Stopwatch barrelRollTimer = new System.Diagnostics.Stopwatch();
        public static volatile bool IsCsChaosActive = false;
        public static volatile bool TriggerFpsThrottle = false;
        public static volatile bool IsFpsThrottleActive = false;
        private static readonly System.Diagnostics.Stopwatch fpsThrottleTimer = new System.Diagnostics.Stopwatch();
        private Vector2 throttledPosition = Vector2.Zero;
        private float throttledRotation = 0f;
        private double lastThrottleSnapshotTime = 0;
        private Vector2? throttledCursorPos;
        private Vector2 throttledStutterOffset = Vector2.Zero;
        public static volatile bool TriggerTapeStop = false;
        private static readonly System.Diagnostics.Stopwatch tapeStopTimer = new System.Diagnostics.Stopwatch();
        public static volatile bool IsReverbActive = false;
        private SpriteIcon? busyCursorIcon;

        public static Playfield? CurrentPlayfield;
        public static GameplayCursorContainer? GameplayCursorInstance;
        private TrollOverlay? trollOverlay;
        public static volatile bool IsBsodRunning = false;
        private bool wasBsodActive = false;

        public static void StopGameplayClock()
        {
            if (PlayerInstance != null)
            {
                var prop = typeof(Player).GetProperty("GameplayClockContainer", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                var clock = prop?.GetValue(PlayerInstance);
                if (clock != null)
                {
                    clock.GetType().GetMethod("Stop")?.Invoke(clock, null);
                }
            }
        }

        public static void StartGameplayClock()
        {
            if (PlayerInstance != null)
            {
                var prop = typeof(Player).GetProperty("GameplayClockContainer", System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Instance);
                var clock = prop?.GetValue(PlayerInstance);
                if (clock != null)
                {
                    clock.GetType().GetMethod("Start")?.Invoke(clock, null);
                }
            }
        }

        public static Vector2 CalculateRepulsionOffset(Vector2 screenCursorPos)
        {
            if (CurrentPlayfield == null) return Vector2.Zero;

            Vector2 totalRepulsion = Vector2.Zero;
            const float radius = 130f;

            try
            {
                foreach (var obj in CurrentPlayfield.HitObjectContainer.AliveObjects)
                {
                    Vector2 screenObjPos = obj.ToScreenSpace(obj.OriginPosition);
                    Vector2 diff = screenCursorPos - screenObjPos;
                    float dist = diff.Length;
                    if (dist < radius && dist > 1f)
                    {
                        float force = (radius - dist) * 0.45f;
                        totalRepulsion += Vector2.Normalize(diff) * force;
                    }
                }
            }
            catch { }

            return totalRepulsion;
        }

        private readonly osu.Framework.Bindables.BindableDouble tempoAdjustment = new osu.Framework.Bindables.BindableDouble(1);
        private readonly osu.Framework.Bindables.BindableDouble frequencyAdjustment = new osu.Framework.Bindables.BindableDouble(1);
        
        public static Player? PlayerInstance;
        private Container cachedHudOverlay;

        private static bool isServerRunning = false;
        private static readonly object lockObj = new object();
        private Random rnd = new Random();

        private WindOverlay? windOverlay;
        private BlackoutOverlay? blackoutOverlay;
        public ScreamerOverlay screamerOverlay;
        public static FakeCursorOverlay FakeCursorOverlayInstance;
        public static HiddenCursorOverlay HiddenCursorOverlayInstance;
        private FlashbangOverlay? flashbangOverlay;
        private BlackHoleOverlay? blackHoleOverlay;
        public static HallucinationOverlay? HallucinationOverlayInstance;

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
                                else if (msg == "PITCH_ON") AdjustPitch = true;
                                else if (msg == "PITCH_OFF") AdjustPitch = false;
                                else if (msg.StartsWith("SPEED:"))
                                {
                                    if (float.TryParse(msg.Substring(6), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float speed))
                                        SpeedChange = speed;
                                }
                                else if (msg.StartsWith("FAKE_NOTE:"))
                                {
                                    var parts = msg.Substring(10).Split(':');
                                    if (parts.Length == 2 && float.TryParse(parts[0], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float x)
                                                          && float.TryParse(parts[1], System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float y))
                                    {
                                        if (HallucinationOverlayInstance != null)
                                        {
                                            HallucinationOverlayInstance.ScheduleAction(() => {
                                                if (PlayerInstance != null)
                                                {
                                                    var beatmap = PlayerInstance.GameplayState.Beatmap;
                                                    float cs = beatmap.BeatmapInfo.Difficulty.CircleSize;
                                                    float ar = beatmap.BeatmapInfo.Difficulty.ApproachRate;
                                                    
                                                    // osu! standard scale and AR logic
                                                    float scale = (1.0f - 0.7f * (cs - 5) / 5) / 2f;
                                                    double preempt = osu.Game.Beatmaps.IBeatmapDifficultyInfo.DifficultyRange(ar, 1800, 1200, 450);
                                                    
                                                    // Default osu combo color
                                                    var color = osuTK.Graphics.Color4.White;

                                                    var playfield = HallucinationOverlayInstance.Playfield;
                                                    if (playfield != null)
                                                    {
                                                        HallucinationOverlayInstance.SpawnFakeNote(new osuTK.Vector2(x, y), scale, preempt, color);
                                                    }
                                                }
                                            });
                                        }
                                    }
                                }
                                else if (msg.StartsWith("FAKE_CURSORS:"))
                                {
                                    string mode = msg.Split(':')[1];
                                    if (HallucinationOverlayInstance != null)
                                    {
                                        HallucinationOverlayInstance.ScheduleAction(() => {
                                            FakeCursorOverlayInstance?.SetMode(mode);
                                        });
                                    }
                                }
                                else if (msg.StartsWith("HIDE_CURSOR:"))
                                {
                                    bool isHidden = msg.Split(':')[1] == "ON";
                                    if (HallucinationOverlayInstance != null)
                                    {
                                        HallucinationOverlayInstance.ScheduleAction(() => {
                                            HiddenCursorOverlayInstance?.SetHidden(isHidden);
                                        });
                                    }
                                }
                                else if (msg.StartsWith("INPUT_LAG:"))
                                {
                                    if (float.TryParse(msg.Substring(10), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float lagMs))
                                    {
                                        InputLagMilliseconds = Math.Max(0f, lagMs);
                                    }
                                }
                                else if (msg.StartsWith("CURSOR_SCALE:"))
                                {
                                    if (float.TryParse(msg.Substring(13), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float scale))
                                    {
                                        CursorScaleMultiplier = Math.Clamp(scale, 0.05f, 10.0f);
                                    }
                                }
                                else if (msg == "INVERT_X_ON") InvertX = true;
                                else if (msg == "INVERT_X_OFF") InvertX = false;
                                else if (msg == "INVERT_Y_ON") InvertY = true;
                                else if (msg == "INVERT_Y_OFF") InvertY = false;
                                else if (msg == "INVERT_RESET") { InvertX = false; InvertY = false; }
                                else if (msg == "JAM_K1_ON") JamK1 = true;
                                else if (msg == "JAM_K1_OFF") JamK1 = false;
                                else if (msg == "JAM_K2_ON") JamK2 = true;
                                else if (msg == "JAM_K2_OFF") JamK2 = false;
                                else if (msg == "JAM_RESET") { JamK1 = false; JamK2 = false; }
                                else if (msg == "BLACK_HOLE_ON") IsBlackHoleActive = true;
                                else if (msg == "BLACK_HOLE_OFF") IsBlackHoleActive = false;
                                else if (msg.StartsWith("BLACK_HOLE_STRENGTH:"))
                                {
                                    if (float.TryParse(msg.Substring(20), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float bhStrength))
                                        BlackHoleStrength = bhStrength;
                                }
                                else if (msg.StartsWith("AUDIO_DESYNC:"))
                                {
                                    if (float.TryParse(msg.Substring(13), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float desyncMs))
                                    {
                                        AudioDesyncMilliseconds = desyncMs;
                                        osu.Game.Beatmaps.FramedBeatmapClock.ExternalAudioOffset = desyncMs;
                                    }
                                }
                                else if (msg == "AUDIO_DESYNC_RESET")
                                {
                                    AudioDesyncMilliseconds = 0;
                                    osu.Game.Beatmaps.FramedBeatmapClock.ExternalAudioOffset = 0;
                                }
                                else if (msg == "CHAMELEON_OFF") ChameleonMode = ChameleonType.Off;
                                else if (msg == "CHAMELEON_BLACK") ChameleonMode = ChameleonType.Black;
                                else if (msg == "CHAMELEON_RAINBOW") ChameleonMode = ChameleonType.Rainbow;
                                else if (msg == "CHAMELEON_MONO") ChameleonMode = ChameleonType.Monochrome;
                                else if (msg == "TROLL_BATTERY" || msg == "TROLL:BATTERY") TriggerTrollBattery = true;
                                else if (msg == "TROLL_DISCORD" || msg == "TROLL:DISCORD") TriggerTrollDiscord = true;
                                else if (msg == "TROLL_DISCORD_AUDIO" || msg == "TROLL:DISCORD_AUDIO" || msg == "TROLL:DISCORD_SOUND_ONLY") TriggerTrollDiscordSoundOnly = true;
                                else if (msg == "TROLL_BSOD" || msg == "TROLL:BSOD") TriggerTrollBsod = true;
                                else if (msg == "TROLL_DEFENDER" || msg == "TROLL:DEFENDER") TriggerTrollDefender = true;
                                else if (msg == "TROLL_UPDATE" || msg == "TROLL:UPDATE") TriggerTrollUpdate = true;
                                else if (msg == "TROLL_DONATE" || msg == "TROLL:DONATE") TriggerTrollDonate = true;
                                else if (msg == "TROLL_STICKYKEYS" || msg == "TROLL:STICKYKEYS") TriggerTrollStickyKeys = true;
                                else if (msg == "TROLL_GLITCH" || msg == "TROLL:GLITCH") TriggerTrollGlitch = true;
                                else if (msg == "DEVICE_DISCONNECT" || msg == "MOUSE_DISCONNECT") TriggerMouseDisconnect = true;
                                else if (msg == "REPULSION_ON") IsCircleRepulsion = true;
                                else if (msg == "REPULSION_OFF") IsCircleRepulsion = false;
                                else if (msg.StartsWith("JITTER:"))
                                {
                                    if (float.TryParse(msg.Substring(7), System.Globalization.NumberStyles.Float, System.Globalization.CultureInfo.InvariantCulture, out float j))
                                        CursorJitterStrength = Math.Max(0f, j);
                                }
                                else if (msg == "JITTER_ON") CursorJitterStrength = 18f;
                                else if (msg == "JITTER_OFF") CursorJitterStrength = 0f;
                                else if (msg == "CLONES_ON")
                                {
                                    HallucinationOverlayInstance?.ScheduleAction(() => FakeCursorOverlayInstance?.SetMode("ARMY"));
                                }
                                else if (msg == "CLONES_OFF")
                                {
                                    HallucinationOverlayInstance?.ScheduleAction(() => FakeCursorOverlayInstance?.SetMode("OFF"));
                                }
                                else if (msg == "DRUNK_ON") IsDrunkCamera = true;
                                else if (msg == "DRUNK_OFF") IsDrunkCamera = false;
                                else if (msg == "SHAKE_ON") IsScreenShake = true;
                                else if (msg == "SHAKE_OFF") IsScreenShake = false;
                                else if (msg == "TUNNEL_ON") IsTunnelVision = true;
                                else if (msg == "TUNNEL_OFF") IsTunnelVision = false;
                                else if (msg == "GHOST_SLIDERS_ON") IsGhostSliders = true;
                                else if (msg == "GHOST_SLIDERS_OFF") IsGhostSliders = false;
                                else if (msg == "MUFFLED_ON") IsMuffledAudio = true;
                                else if (msg == "MUFFLED_OFF") IsMuffledAudio = false;
                                else if (msg == "PAN_SPIN_ON") IsAudioPanSpin = true;
                                else if (msg == "PAN_SPIN_OFF") IsAudioPanSpin = false;
                                else if (msg == "TROLL_TELEGRAM" || msg == "TROLL:TELEGRAM") TriggerTrollTelegram = true;
                                else if (msg == "TROLL_TELEGRAM_AUDIO" || msg == "TROLL:TELEGRAM_AUDIO" || msg == "TROLL:TELEGRAM_SOUND_ONLY") TriggerTrollTelegramAudioOnly = true;
                                else if (msg == "TROLL_STEAM" || msg == "TROLL:STEAM") TriggerTrollSteam = true;
                                else if (msg == "WATERMARK_ON") IsWatermarkActive = true;
                                else if (msg == "WATERMARK_OFF") IsWatermarkActive = false;
                                else if (msg == "INVERT_COLORS_ON") IsInvertColorsActive = true;
                                else if (msg == "INVERT_COLORS_OFF") IsInvertColorsActive = false;
                                else if (msg == "MOSAIC_ON") IsMosaicActive = true;
                                else if (msg == "MOSAIC_OFF") IsMosaicActive = false;
                                else if (msg == "BUSY_CURSOR_ON") IsBusyCursorActive = true;
                                else if (msg == "BUSY_CURSOR_OFF") IsBusyCursorActive = false;
                                else if (msg == "BARREL_ROLL") TriggerBarrelRoll = true;
                                else if (msg == "CS_CHAOS_ON") IsCsChaosActive = true;
                                else if (msg == "CS_CHAOS_OFF") IsCsChaosActive = false;
                                else if (msg == "FPS_THROTTLE") TriggerFpsThrottle = true;
                                else if (msg == "TAPE_STOP") TriggerTapeStop = true;
                                else if (msg == "REVERB_ON") IsReverbActive = true;
                                else if (msg == "REVERB_OFF") IsReverbActive = false;
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
            var osuRuleset = (DrawableOsuRuleset)drawableRuleset;
            osuRuleset.KeyBindingInputManager.Add(new KeyJamInterceptor());

            // Добавляем слои поверх всего
            windOverlay = new WindOverlay();
            blackoutOverlay = new BlackoutOverlay();
            screamerOverlay = new ScreamerOverlay();
            flashbangOverlay = new FlashbangOverlay();
            HallucinationOverlayInstance = new HallucinationOverlay();
            
            // Note: drawableRuleset.Cursor is GameplayCursorContainer
            GameplayCursorInstance = (GameplayCursorContainer)drawableRuleset.Cursor;
            FakeCursorOverlayInstance = new FakeCursorOverlay(GameplayCursorInstance);
            HiddenCursorOverlayInstance = new HiddenCursorOverlay(GameplayCursorInstance);

            HallucinationOverlayInstance.Playfield = drawableRuleset.Playfield;
            
            drawableRuleset.Overlays.Add(windOverlay);
            drawableRuleset.Overlays.Add(blackoutOverlay);
            drawableRuleset.Overlays.Add(flashbangOverlay);
            drawableRuleset.Overlays.Add(screamerOverlay);

            trollOverlay = new TrollOverlay { Depth = float.MinValue };
            drawableRuleset.Overlays.Add(trollOverlay);
            
            try
            {
                tunnelVisionMod = new OsuModFlashlight();
                tunnelVisionMod.ComboBasedSize.Value = false;
                tunnelVisionMod.SizeMultiplier.Value = 1.0f;
                tunnelVisionMod.ApplyToDrawableRuleset(drawableRuleset);

                tunnelVisionContainer = drawableRuleset.Overlays.OfType<Container>().FirstOrDefault(c => c.Children.Any(child => child is osu.Game.Rulesets.Mods.ModFlashlight<OsuHitObject>.Flashlight));
                if (tunnelVisionContainer != null)
                {
                    tunnelVisionContainer.Alpha = 0;
                }
            }
            catch { }

            try
            {
                var targetPlayfield = drawableRuleset.Playfield;
                if (drawableRuleset.PlayfieldAdjustmentContainer.Remove(targetPlayfield, false))
                {
                    bufferedPlayfield = new BufferedContainer(cachedFrameBuffer: false)
                    {
                        RelativeSizeAxes = Axes.Both,
                        RedrawOnScale = false,
                        Child = targetPlayfield
                    };
                    drawableRuleset.PlayfieldAdjustmentContainer.Add(bufferedPlayfield);
                }
            }
            catch { }

            blackHoleOverlay = new BlackHoleOverlay();
            drawableRuleset.PlayfieldAdjustmentContainer.Add(blackHoleOverlay);

            drawableRuleset.PlayfieldAdjustmentContainer.Add(HallucinationOverlayInstance);
            drawableRuleset.PlayfieldAdjustmentContainer.Add(FakeCursorOverlayInstance);
            drawableRuleset.PlayfieldAdjustmentContainer.Add(HiddenCursorOverlayInstance);

            busyCursorOverlay = new Container
            {
                RelativeSizeAxes = Axes.Both,
                Depth = float.MinValue + 10,
                AlwaysPresent = true,
                Alpha = 0
            };
            busyCursorIcon = new SpriteIcon
            {
                Origin = Anchor.Centre,
                Icon = FontAwesome.Solid.CircleNotch,
                Size = new Vector2(30),
                Colour = Colour4.FromHex("#00a2ed")
            };
            busyCursorOverlay.Add(busyCursorIcon);
            drawableRuleset.Overlays.Add(busyCursorOverlay);
        }

        private Container? busyCursorOverlay;
        private BufferedContainer? bufferedPlayfield;
        private bool lastMosaicActive;

        private OsuModFlashlight? tunnelVisionMod;
        private Container? tunnelVisionContainer;
        private bool wasStopScreenActive = false;
        private bool lastGhostSliders = false;
        private bool lastCsChaos = false;

        public void ApplyToDrawableHitObject(DrawableHitObject drawable)
        {
            tunnelVisionMod?.ApplyToDrawableHitObject(drawable);
            if (!IsCsChaosActive)
            {
                drawable.Scale = Vector2.One;
            }
        }

        public void ApplyToTrack(osu.Framework.Audio.IAdjustableAudioComponent track)
        {
            track.AddAdjustment(osu.Framework.Audio.AdjustableProperty.Tempo, tempoAdjustment);
            track.AddAdjustment(osu.Framework.Audio.AdjustableProperty.Frequency, frequencyAdjustment);
            track.AddAdjustment(osu.Framework.Audio.AdjustableProperty.Balance, balanceAdjustment);
        }

        public void Update(Playfield playfield)
        {
            if (TriggerTapeStop)
            {
                tapeStopTimer.Restart();
                TriggerTapeStop = false;
            }

            float tapeSpeedMultiplier = 1.0f;
            if (tapeStopTimer.IsRunning)
            {
                float tapeMs = (float)tapeStopTimer.Elapsed.TotalMilliseconds;
                if (tapeMs < 1200f)
                {
                    // Decay smoothly from 1.0 down to 0.05
                    tapeSpeedMultiplier = Math.Clamp(1.0f - (tapeMs / 1200f), 0.05f, 1.0f);
                }
                else if (tapeMs < 2000f)
                {
                    // Brief complete stall / silence
                    tapeSpeedMultiplier = 0.05f;
                }
                else if (tapeMs < 3000f)
                {
                    // Ramp back up from 0.05 to 1.0
                    tapeSpeedMultiplier = Math.Clamp(0.05f + ((tapeMs - 2000f) / 1000f), 0.05f, 1.0f);
                }
                else
                {
                    tapeStopTimer.Reset();
                    tapeSpeedMultiplier = 1.0f;
                }
            }

            double reverbFreqMultiplier = 1.0;
            if (IsReverbActive)
            {
                float reverbTime = (float)(playfield.Time.Current / 1000.0);
                if (playfield.Clock.ElapsedFrameTime == 0 || Math.Abs(reverbTime) < 0.001f)
                    reverbTime = Environment.TickCount64 / 1000f;
                // Acoustic reverberation flutter
                reverbFreqMultiplier = 1.0 + Math.Sin(reverbTime * 28.0) * 0.035 + Math.Cos(reverbTime * 14.0) * 0.02;
            }

            if (AdjustPitch)
            {
                frequencyAdjustment.Value = SpeedChange * tapeSpeedMultiplier * reverbFreqMultiplier;
                tempoAdjustment.Value = 1.0;
            }
            else
            {
                tempoAdjustment.Value = SpeedChange * tapeSpeedMultiplier;
                frequencyAdjustment.Value = reverbFreqMultiplier;
            }
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

            if (blackHoleOverlay != null)
            {
                blackHoleOverlay.IsActive = IsBlackHoleActive;
                blackHoleOverlay.Strength = BlackHoleStrength;
            }

            CurrentPlayfield = playfield;

            if (trollOverlay != null)
            {
                if (TriggerTrollBattery)
                {
                    trollOverlay.ShowBatteryAlert();
                    TriggerTrollBattery = false;
                }
                if (TriggerTrollDiscord)
                {
                    trollOverlay.ShowDiscordCall();
                    TriggerTrollDiscord = false;
                }
                if (TriggerTrollDiscordSoundOnly)
                {
                    trollOverlay.PlayDiscordSoundOnly();
                    TriggerTrollDiscordSoundOnly = false;
                }
                if (TriggerTrollBsod)
                {
                    trollOverlay.ShowBsod();
                    TriggerTrollBsod = false;
                }
                if (TriggerTrollDefender)
                {
                    trollOverlay.ShowDefenderAlert();
                    TriggerTrollDefender = false;
                }
                if (TriggerTrollUpdate)
                {
                    trollOverlay.ShowWindowsUpdate();
                    TriggerTrollUpdate = false;
                }
                if (TriggerTrollDonate)
                {
                    trollOverlay.ShowDonation();
                    TriggerTrollDonate = false;
                }
                if (TriggerTrollStickyKeys)
                {
                    trollOverlay.ShowStickyKeys();
                    TriggerTrollStickyKeys = false;
                }
                if (TriggerTrollGlitch)
                {
                    trollOverlay.ShowGlitch();
                    TriggerTrollGlitch = false;
                }
                if (TriggerTrollTelegram)
                {
                    trollOverlay.ShowTelegramCall();
                    TriggerTrollTelegram = false;
                }
                if (TriggerTrollTelegramAudioOnly)
                {
                    trollOverlay.PlayTelegramSoundOnly();
                    TriggerTrollTelegramAudioOnly = false;
                }
                if (TriggerTrollSteam)
                {
                    trollOverlay.ShowSteamNotification();
                    TriggerTrollSteam = false;
                }

                trollOverlay.SetWindowsWatermark(IsWatermarkActive);
                trollOverlay.SetInvertColors(IsInvertColorsActive);
                trollOverlay.SetMosaic(IsMosaicActive);

                if (bufferedPlayfield != null && IsMosaicActive != lastMosaicActive)
                {
                    lastMosaicActive = IsMosaicActive;
                    if (IsMosaicActive)
                    {
                        float scale = Math.Clamp(144f / Math.Max(playfield.DrawHeight, 600f), 0.08f, 0.25f);
                        bufferedPlayfield.FrameBufferScale = new Vector2(scale);
                        bufferedPlayfield.BlurSigma = new Vector2(1.8f);
                    }
                    else
                    {
                        bufferedPlayfield.FrameBufferScale = Vector2.One;
                        bufferedPlayfield.BlurSigma = Vector2.Zero;
                    }
                }
                if (TriggerMouseDisconnect)
                {
                    TrollOverlay.PlayWindowsSound("Windows Hardware Remove.wav");
                    IsMouseDisconnected = true;
                    TriggerMouseDisconnect = false;
                    trollOverlay.ScheduleDelayed(() =>
                    {
                        TrollOverlay.PlayWindowsSound("Windows Hardware Insert.wav");
                        IsMouseDisconnected = false;
                    }, 1800);
                }

                trollOverlay.SetMuffled(IsMuffledAudio);

                bool isStopScreenActive = trollOverlay.IsBsodActive || trollOverlay.IsUpdateActive;

                if (isStopScreenActive && !wasStopScreenActive)
                {
                    IsBsodRunning = true;
                    StopGameplayClock();

                    if (PlayerInstance != null && cachedHudOverlay == null)
                    {
                        var prop = typeof(Player).GetProperty("HUDOverlay", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.Public);
                        if (prop != null)
                            cachedHudOverlay = prop.GetValue(PlayerInstance) as Container;
                    }

                    if (cachedHudOverlay != null)
                    {
                        cachedHudOverlay.ClearTransforms();
                        cachedHudOverlay.Alpha = 0f;
                    }

                    if (GameplayCursorInstance != null)
                    {
                        GameplayCursorInstance.ClearTransforms();
                        GameplayCursorInstance.Alpha = 0f;
                    }

                    HiddenCursorOverlayInstance?.SetHidden(true);
                    wasStopScreenActive = true;
                }
                else if (!isStopScreenActive && wasStopScreenActive)
                {
                    IsBsodRunning = false;
                    if (!IsFreezeActive)
                    {
                        StartGameplayClock();
                    }

                    if (cachedHudOverlay != null)
                    {
                        cachedHudOverlay.ClearTransforms();
                        cachedHudOverlay.Alpha = 1f;
                    }

                    if (GameplayCursorInstance != null)
                    {
                        GameplayCursorInstance.ClearTransforms();
                        GameplayCursorInstance.Alpha = 1f;
                    }

                    HiddenCursorOverlayInstance?.SetHidden(false);
                    wasStopScreenActive = false;
                }
                else if (isStopScreenActive)
                {
                    float stopScreenElapsed = trollOverlay.IsBsodActive ? trollOverlay.BsodElapsed : trollOverlay.UpdateElapsed;
                    float holdDuration = trollOverlay.IsBsodActive ? 3000f : 3500f;
                    const float fadeDuration = 400f;
                    if (stopScreenElapsed > holdDuration)
                    {
                        float progress = Math.Clamp((stopScreenElapsed - holdDuration) / fadeDuration, 0f, 1f);
                        if (cachedHudOverlay != null)
                            cachedHudOverlay.Alpha = progress;
                        if (GameplayCursorInstance != null)
                            GameplayCursorInstance.Alpha = progress;
                    }
                    else
                    {
                        if (cachedHudOverlay != null)
                            cachedHudOverlay.Alpha = 0f;
                        if (GameplayCursorInstance != null)
                            GameplayCursorInstance.Alpha = 0f;
                    }
                }
            }

            if (tunnelVisionContainer != null)
            {
                tunnelVisionContainer.Alpha = IsTunnelVision ? 1f : 0f;
            }

            if (IsGhostSliders)
            {
                foreach (var d in playfield.HitObjectContainer.AliveObjects)
                {
                    if (d is osu.Game.Rulesets.Osu.Objects.Drawables.DrawableSlider slider)
                    {
                        slider.Body.Alpha = 0f;
                        slider.TailCircle.Alpha = 0f;
                    }
                }
                lastGhostSliders = true;
            }
            else if (lastGhostSliders)
            {
                foreach (var d in playfield.HitObjectContainer.AliveObjects)
                {
                    if (d is osu.Game.Rulesets.Osu.Objects.Drawables.DrawableSlider slider)
                    {
                        slider.Body.Alpha = 1f;
                        slider.TailCircle.Alpha = 1f;
                    }
                }
                lastGhostSliders = false;
            }

            if (!IsCsChaosActive && lastCsChaos)
            {
                foreach (var d in playfield.HitObjectContainer.AliveObjects)
                {
                    d.Scale = Vector2.One;
                    if (d is osu.Game.Rulesets.Osu.Objects.Drawables.DrawableSlider s)
                    {
                        if (s.HeadCircle != null) s.HeadCircle.Scale = Vector2.One;
                        if (s.TailCircle != null) s.TailCircle.Scale = Vector2.One;
                    }
                }
                lastCsChaos = false;
            }
            else if (IsCsChaosActive)
            {
                lastCsChaos = true;
            }

            if (IsAudioPanSpin)
            {
                float t = (float)playfield.Clock.CurrentTime / 1000f;
                balanceAdjustment.Value = Math.Sin(t * 4.2);
            }
            else
            {
                balanceAdjustment.Value = 0;
            }

            osu.Game.Beatmaps.FramedBeatmapClock.ExternalAudioOffset = AudioDesyncMilliseconds;

            if (lastChameleonMode != ChameleonMode)
            {
                if (ChameleonMode == ChameleonType.Off)
                {
                    foreach (var d in playfield.HitObjectContainer.AliveObjects)
                    {
                        var method = typeof(osu.Game.Rulesets.Objects.Drawables.DrawableHitObject).GetMethod("UpdateComboColour", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
                        method?.Invoke(d, null);
                    }
                }
                lastChameleonMode = ChameleonMode;
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

            if (playfield.Cursor is OsuCursorContainer osuCursorContainer && osuCursorContainer.ActiveCursor != null)
            {
                if (osuCursorContainer.ActiveCursor.ModScaleAdjust.Value != CursorScaleMultiplier)
                {
                    osuCursorContainer.ActiveCursor.ModScaleAdjust.Value = CursorScaleMultiplier;
                }

                if (IsBusyCursorActive && busyCursorOverlay != null && busyCursorIcon != null)
                {
                    busyCursorOverlay.Alpha = 1f;
                    Vector2 screenPos = osuCursorContainer.ActiveCursor.ToScreenSpace(Vector2.Zero);
                    busyCursorIcon.Position = busyCursorOverlay.ToLocalSpace(screenPos) + new Vector2(8, 8);
                    busyCursorIcon.Rotation += (elapsed / 1000f) * 720f;
                }
                else if (busyCursorOverlay != null)
                {
                    busyCursorOverlay.Alpha = 0f;
                }
            }
            
            // --- Положение, вращение (Пьяная камера, Тряска, Землетрясение, Бочка 360°) и масштаб ---
            float totalRotation = 0f;
            Vector2 totalPosition = Vector2.Zero;

            if (TriggerBarrelRoll)
            {
                barrelRollTimer.Restart();
                TriggerBarrelRoll = false;
            }

            if (barrelRollTimer.IsRunning)
            {
                float rollMs = (float)barrelRollTimer.Elapsed.TotalMilliseconds;
                const float rollDuration = 3500f;
                if (rollMs < rollDuration)
                {
                    float p = rollMs / rollDuration;
                    float smoothP = p * p * (3f - 2f * p); // smoothstep
                    totalRotation += smoothP * 360f;
                }
                else
                {
                    barrelRollTimer.Reset();
                }
            }

            float animTime = (float)(playfield.Time.Current / 1000.0);
            if (playfield.Clock.ElapsedFrameTime == 0 || Math.Abs(animTime) < 0.001f)
                animTime = Environment.TickCount64 / 1000f;

            if (IsDrunkCamera)
            {
                totalRotation += MathF.Sin(animTime * 2.2f) * 16f;
                totalPosition += new Vector2(
                    MathF.Sin(animTime * 1.7f) * 22f,
                    MathF.Cos(animTime * 1.3f) * 14f
                );
            }

            if (IsEarthquakeActive)
            {
                totalRotation += (float)(rnd.NextDouble() * 10 - 5) * EarthquakeStrength;
                totalPosition += new Vector2(
                    (float)(rnd.NextDouble() * 16 - 8) * EarthquakeStrength,
                    (float)(rnd.NextDouble() * 16 - 8) * EarthquakeStrength
                );
            }

            if (IsScreenShake)
            {
                float shakeIntensity = 16f;
                totalRotation += (rnd.NextSingle() * 2f - 1f) * 4f;
                totalPosition += new Vector2(
                    (rnd.NextSingle() * 2f - 1f) * shakeIntensity,
                    (rnd.NextSingle() * 2f - 1f) * shakeIntensity
                );
            }

            if (TriggerFpsThrottle)
            {
                fpsThrottleTimer.Restart();
                lastThrottleSnapshotTime = 0;
                throttledCursorPos = null;
                TriggerFpsThrottle = false;
            }

            if (fpsThrottleTimer.IsRunning)
            {
                float fpsMs = (float)fpsThrottleTimer.Elapsed.TotalMilliseconds;
                if (fpsMs < 3500f)
                {
                    IsFpsThrottleActive = true;
                    double nowTime = Environment.TickCount64;
                    // 15 FPS = 66.6ms frame time
                    if (nowTime - lastThrottleSnapshotTime >= 66.6 || lastThrottleSnapshotTime == 0)
                    {
                        throttledPosition = totalPosition;
                        throttledRotation = totalRotation;
                        throttledStutterOffset = new Vector2(
                            (rnd.NextSingle() * 2f - 1f) * 10f,
                            (rnd.NextSingle() * 2f - 1f) * 10f
                        );
                        if (playfield.Cursor is OsuCursorContainer cursorCont && cursorCont.ActiveCursor != null)
                        {
                            throttledCursorPos = cursorCont.ActiveCursor.Position;
                        }
                        lastThrottleSnapshotTime = nowTime;
                    }

                    totalPosition = throttledPosition + throttledStutterOffset;
                    totalRotation = throttledRotation;

                    if (playfield.Cursor is OsuCursorContainer osuCursor && osuCursor.ActiveCursor != null && throttledCursorPos.HasValue)
                    {
                        osuCursor.ActiveCursor.Position = throttledCursorPos.Value;
                    }
                }
                else
                {
                    IsFpsThrottleActive = false;
                    fpsThrottleTimer.Reset();
                    throttledCursorPos = null;
                    throttledStutterOffset = Vector2.Zero;
                }
            }
            else
            {
                IsFpsThrottleActive = false;
            }

            trollOverlay?.SetFpsThrottle(IsFpsThrottleActive);

            playfield.Rotation = totalRotation;
            playfield.Position = totalPosition;

            float px = PlayfieldScaleX * (IsMirrorPlayfieldX ? -1 : 1);
            float py = PlayfieldScaleY * (IsMirrorPlayfieldY ? -1 : 1);
            Vector2 baseScale = new Vector2(px, py);

            if (IsEarthquakeActive)
            {
                playfield.Scale = baseScale + new Vector2((float)(rnd.NextDouble() * 0.4 - 0.2) * EarthquakeStrength);
            }
            else
            {
                playfield.Scale = baseScale;
            }

            foreach (var drawable in playfield.HitObjectContainer.AliveObjects)
            {
                if (drawable.HitObject is SliderRepeat || drawable.HitObject is SliderTailCircle)
                    continue;

                if (IsCsChaosActive)
                {
                    int hash = drawable.HitObject.StartTime.GetHashCode() ^ drawable.HitObject.GetHashCode();
                    float targetScale = (Math.Abs(hash) % 2 == 0) ? 1.65f : 0.42f;
                    drawable.Scale = new Vector2(targetScale);
                }
                else
                {
                    if (drawable.Scale != Vector2.One)
                        drawable.Scale = Vector2.One;

                    if (drawable is osu.Game.Rulesets.Osu.Objects.Drawables.DrawableSlider slider)
                    {
                        if (slider.HeadCircle != null && slider.HeadCircle.Scale != Vector2.One)
                            slider.HeadCircle.Scale = Vector2.One;
                        if (slider.TailCircle != null && slider.TailCircle.Scale != Vector2.One)
                            slider.TailCircle.Scale = Vector2.One;
                    }
                }

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

                // Чёрная дыра (Гравитация к центру поля 256, 192)
                if (IsBlackHoleActive)
                {
                    Vector2 bhCenter = new Vector2(256, 192);
                    Vector2 toCenter = bhCenter - drawable.Position;
                    float distance = toCenter.Length;
                    if (distance > 1f)
                    {
                        float pullSpeed = (elapsed / 1000f) * 140f * BlackHoleStrength;
                        drawable.Position += toCenter.Normalized() * Math.Min(distance, pullSpeed);
                    }
                }

                // Хамелеон (Подмена цвета нот)
                if (ChameleonMode != ChameleonType.Off)
                {
                    Colour4 targetColor;
                    if (ChameleonMode == ChameleonType.Black)
                        targetColor = Colour4.FromHex("#11111b");
                    else if (ChameleonMode == ChameleonType.Monochrome)
                        targetColor = Colour4.FromHex("#cfd8dc");
                    else // Rainbow
                    {
                        float hue = (float)((playfield.Clock.CurrentTime / 5.0) % 360.0);
                        targetColor = Colour4.FromHSV(hue, 1f, 1f);
                    }

                    drawable.AccentColour.Value = targetColor;

                    foreach (var nested in drawable.NestedHitObjects)
                    {
                        nested.AccentColour.Value = targetColor;
                    }

                    if (drawable is osu.Game.Rulesets.Osu.Skinning.IHasApproachCircle approachObj && approachObj.ApproachCircle != null)
                    {
                        if (!IsHiddenActive)
                            approachObj.ApproachCircle.Colour = targetColor;
                    }
                }
                else
                {
                    if (drawable is osu.Game.Rulesets.Osu.Skinning.IHasApproachCircle approachObj && approachObj.ApproachCircle != null)
                    {
                        if (IsHiddenActive)
                            approachObj.ApproachCircle.Colour = Colour4.Transparent;
                        else
                            approachObj.ApproachCircle.Colour = Colour4.White;
                    }
                }

                foreach (var nested in drawable.NestedHitObjects)
                {
                    if (nested is osu.Game.Rulesets.Osu.Skinning.IHasApproachCircle nestedApproachObj && nestedApproachObj.ApproachCircle != null)
                    {
                        if (IsHiddenActive)
                            nestedApproachObj.ApproachCircle.Colour = Colour4.Transparent;
                        else if (ChameleonMode == ChameleonType.Off)
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
                    
                    StopGameplayClock();

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
                        
                        if (!IsBsodRunning)
                        {
                            StartGameplayClock();
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

        private partial class KeyJamInterceptor : Component, osu.Framework.Input.Bindings.IKeyBindingHandler<OsuAction>
        {
            public bool OnPressed(osu.Framework.Input.Events.KeyBindingPressEvent<OsuAction> e)
            {
                if (JamK1 && e.Action == OsuAction.LeftButton)
                    return true;

                if (JamK2 && e.Action == OsuAction.RightButton)
                    return true;

                return false;
            }

            public void OnReleased(osu.Framework.Input.Events.KeyBindingReleaseEvent<OsuAction> e)
            {
            }
        }

        public partial class BlackHoleOverlay : CompositeDrawable
        {
            public bool IsActive;
            public float Strength = 1.0f;

            private Container vortexContainer = null!;
            private CircularContainer disc = null!;

            public BlackHoleOverlay()
            {
                Origin = Anchor.Centre;
                Anchor = Anchor.TopLeft;
                Position = new Vector2(256, 192);
                Size = new Vector2(160);
            }

            [BackgroundDependencyLoader]
            private void load()
            {
                InternalChildren = new Drawable[]
                {
                    vortexContainer = new Container
                    {
                        RelativeSizeAxes = Axes.Both,
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        Alpha = 0,
                        Children = new Drawable[]
                        {
                            disc = new CircularContainer
                            {
                                RelativeSizeAxes = Axes.Both,
                                Anchor = Anchor.Centre,
                                Origin = Anchor.Centre,
                                Masking = true,
                                BorderThickness = 6,
                                BorderColour = Colour4.FromHex("#9c27b0"),
                                Child = new Box
                                {
                                    RelativeSizeAxes = Axes.Both,
                                    Colour = Colour4.FromHex("#311b92").Opacity(0.35f)
                                }
                            },
                            new CircularContainer
                            {
                                Size = new Vector2(70),
                                Anchor = Anchor.Centre,
                                Origin = Anchor.Centre,
                                Masking = true,
                                BorderThickness = 3,
                                BorderColour = Colour4.FromHex("#ea80fc"),
                                Child = new Box
                                {
                                    RelativeSizeAxes = Axes.Both,
                                    Colour = Colour4.Black
                                }
                            }
                        }
                    }
                };
            }

            protected override void Update()
            {
                base.Update();

                if (IsActive)
                {
                    vortexContainer.FadeTo(0.9f, 250);
                    vortexContainer.Rotation += (float)Clock.ElapsedFrameTime * 0.15f * Strength;
                    float pulse = 1.0f + 0.08f * (float)Math.Sin(Clock.CurrentTime / 150.0);
                    disc.Scale = new Vector2(pulse);
                }
                else
                {
                    vortexContainer.FadeOut(250);
                }
            }
        }
    }
}
