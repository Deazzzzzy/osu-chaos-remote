// Copyright (c) ppy Pty Ltd <contact@ppy.sh>. Licensed under the MIT Licence.
// See the LICENCE file in the repository root for full licence text.

using System;
using System.Collections.Generic;
using System.Linq;
using osu.Framework.Allocation;
using osu.Framework.Graphics;
using osu.Framework.Input.Bindings;
using osu.Framework.Input.Events;
using osu.Framework.Input.StateChanges;
using osu.Framework.Lists;
using osu.Framework.Localisation;
using osu.Game.Input.Bindings;
using osu.Game.Localisation;
using osu.Game.Localisation.Osu;
using osu.Game.Rulesets.Osu.Mods;
using osu.Game.Rulesets.Osu.Objects.Drawables;
using osu.Game.Rulesets.Osu.UI;
using osu.Game.Rulesets.UI;
using osuTK;

namespace osu.Game.Rulesets.Osu
{
    public partial class OsuInputManager : RulesetInputManager<OsuAction>
    {
        public SlimReadOnlyListWrapper<OsuAction> PressedActions => KeyBindingContainer.PressedActions;

        /// <summary>
        /// Whether gameplay input buttons should be allowed.
        /// Defaults to <c>true</c>, generally used for mods like Relax which turn off main inputs.
        /// </summary>
        /// <remarks>
        /// Of note, auxiliary inputs like the "smoke" key are left usable.
        /// </remarks>
        public bool AllowGameplayInputs
        {
            get => ((OsuKeyBindingContainer)KeyBindingContainer).AllowGameplayInputs;
            set => ((OsuKeyBindingContainer)KeyBindingContainer).AllowGameplayInputs = value;
        }

        /// <summary>
        /// Whether the user's cursor movement events should be accepted.
        /// Can be used to block only movement while still accepting button input.
        /// </summary>
        public bool AllowUserCursorMovement { get; set; } = true;

        protected override KeyBindingContainer<OsuAction> CreateKeyBindingContainer(RulesetInfo ruleset, int variant, SimultaneousBindingMode unique)
            => new OsuKeyBindingContainer(ruleset, variant, unique);

        public bool CheckScreenSpaceActionPressJudgeable(Vector2 screenSpacePosition) =>
            // This is a very naive but simple approach.
            //
            // Based on user feedback of more nuanced scenarios (where touch doesn't behave as expected),
            // this can be expanded to a more complex implementation, but I'd still want to keep it as simple as we can.
            NonPositionalInputQueue.OfType<DrawableHitCircle.HitReceptor>().Any(c => c.CanBeHit() && c.ReceivePositionalInputAt(screenSpacePosition));

        public OsuInputManager(RulesetInfo ruleset)
            : base(ruleset, 0, SimultaneousBindingMode.Unique)
        {
        }

        [BackgroundDependencyLoader]
        private void load()
        {
            Add(new OsuTouchInputMapper(this) { RelativeSizeAxes = Axes.Both });
        }

        private readonly List<MousePositionRecord> mouseHistory = new List<MousePositionRecord>();
        private Vector2? lastRawMousePosition;
        private bool lastInvertX;
        private bool lastInvertY;

        private Vector2 applyInversion(Vector2 rawPos)
        {
            if (!OsuModChaos.InvertX && !OsuModChaos.InvertY)
                return rawPos;

            Vector2 center = ScreenSpaceDrawQuad.Centre;
            float x = OsuModChaos.InvertX ? (2 * center.X - rawPos.X) : rawPos.X;
            float y = OsuModChaos.InvertY ? (2 * center.Y - rawPos.Y) : rawPos.Y;
            return new Vector2(x, y);
        }

        private readonly struct MousePositionRecord
        {
            public readonly long TimeMs;
            public readonly Vector2 Position;

            public MousePositionRecord(long timeMs, Vector2 position)
            {
                TimeMs = timeMs;
                Position = position;
            }
        }

        private bool isSimulatingInput;
        private readonly Random inputRnd = new Random();
        private bool hadCustomModifier;
        private long lastThrottleInputTime;
        private Vector2? throttledInputPos;

        protected override bool Handle(UIEvent e)
        {
            if (isSimulatingInput)
                return base.Handle(e);

            bool isFpsThrottle = OsuModChaos.IsFpsThrottleActive;
            bool customModifier = OsuModChaos.InputLagMilliseconds > 0
                                  || OsuModChaos.InvertX
                                  || OsuModChaos.InvertY
                                  || isFpsThrottle
                                  || OsuModChaos.IsMouseDisconnected
                                  || OsuModChaos.CursorJitterStrength > 0
                                  || OsuModChaos.IsCircleRepulsion;

            if (e is MouseMoveEvent moveEvent)
            {
                if (!isSimulatingInput && !OsuModChaos.IsMouseDisconnected)
                    lastRawMousePosition = moveEvent.ScreenSpaceMousePosition;

                if (OsuModChaos.InputLagMilliseconds > 0)
                {
                    mouseHistory.Add(new MousePositionRecord(Environment.TickCount64, moveEvent.ScreenSpaceMousePosition));
                    return false;
                }

                if (customModifier)
                    return false;
            }
            else if (e is TouchMoveEvent touchEvent)
            {
                if (!isSimulatingInput && !OsuModChaos.IsMouseDisconnected)
                    lastRawMousePosition = touchEvent.ScreenSpaceTouch.Position;

                if (OsuModChaos.InputLagMilliseconds > 0)
                {
                    mouseHistory.Add(new MousePositionRecord(Environment.TickCount64, touchEvent.ScreenSpaceTouch.Position));
                    return false;
                }

                if (customModifier)
                    return false;
            }

            if ((e is MouseMoveEvent || e is TouchMoveEvent) && !AllowUserCursorMovement) return false;

            return base.Handle(e);
        }

        protected override void Update()
        {
            base.Update();

            float lag = OsuModChaos.InputLagMilliseconds;
            bool invertActive = OsuModChaos.InvertX || OsuModChaos.InvertY;
            bool invertChanged = (lastInvertX != OsuModChaos.InvertX || lastInvertY != OsuModChaos.InvertY);
            lastInvertX = OsuModChaos.InvertX;
            lastInvertY = OsuModChaos.InvertY;

            bool isFpsThrottle = OsuModChaos.IsFpsThrottleActive;
            bool customModifier = lag > 0
                                  || invertActive
                                  || isFpsThrottle
                                  || OsuModChaos.IsMouseDisconnected
                                  || OsuModChaos.CursorJitterStrength > 0
                                  || OsuModChaos.IsCircleRepulsion;

            if (OsuModChaos.IsMouseDisconnected)
            {
                hadCustomModifier = true;
                return;
            }

            if (customModifier)
            {
                hadCustomModifier = true;
                long now = Environment.TickCount64;

                if (lastRawMousePosition.HasValue)
                {
                    if (mouseHistory.Count == 0 || mouseHistory[mouseHistory.Count - 1].TimeMs < now)
                    {
                        mouseHistory.Add(new MousePositionRecord(now, lastRawMousePosition.Value));
                    }
                }

                Vector2 targetPos;

                if (lag > 0)
                {
                    targetPos = getLaggedPosition(lag, now);
                }
                else
                {
                    if (mouseHistory.Count > 0)
                        mouseHistory.Clear();
                    targetPos = lastRawMousePosition ?? ScreenSpaceDrawQuad.Centre;
                }

                targetPos = applyInversion(targetPos);

                if (OsuModChaos.IsCircleRepulsion)
                {
                    targetPos += OsuModChaos.CalculateRepulsionOffset(targetPos);
                }

                if (OsuModChaos.CursorJitterStrength > 0)
                {
                    float j = OsuModChaos.CursorJitterStrength;
                    targetPos += new Vector2(
                        (inputRnd.NextSingle() * 2f - 1f) * j,
                        (inputRnd.NextSingle() * 2f - 1f) * j
                    );
                }

                if (isFpsThrottle)
                {
                    if (now - lastThrottleInputTime >= 66.6 || !throttledInputPos.HasValue)
                    {
                        lastThrottleInputTime = now;
                        throttledInputPos = targetPos;
                    }
                    targetPos = throttledInputPos.Value;
                }
                else
                {
                    throttledInputPos = null;
                }

                isSimulatingInput = true;
                try
                {
                    new MousePositionAbsoluteInput { Position = targetPos }.Apply(CurrentState, this);
                }
                finally
                {
                    isSimulatingInput = false;
                }
            }
            else
            {
                if (hadCustomModifier || mouseHistory.Count > 0 || invertChanged)
                {
                    if (lastRawMousePosition.HasValue)
                    {
                        isSimulatingInput = true;
                        try
                        {
                            new MousePositionAbsoluteInput { Position = lastRawMousePosition.Value }.Apply(CurrentState, this);
                        }
                        finally
                        {
                            isSimulatingInput = false;
                        }
                    }

                    mouseHistory.Clear();
                    hadCustomModifier = false;
                }
            }
        }

        private Vector2 getLaggedPosition(float lag, long now)
        {
            if (mouseHistory.Count == 0)
                return lastRawMousePosition ?? ScreenSpaceDrawQuad.Centre;

            long targetTime = now - (long)lag;

            while (mouseHistory.Count >= 2 && mouseHistory[1].TimeMs <= targetTime)
            {
                mouseHistory.RemoveAt(0);
            }

            if (mouseHistory.Count == 1)
            {
                return mouseHistory[0].Position;
            }

            var p0 = mouseHistory[0];
            var p1 = mouseHistory[1];

            if (p0.TimeMs <= targetTime && targetTime <= p1.TimeMs)
            {
                double duration = p1.TimeMs - p0.TimeMs;
                float t = duration > 0 ? (float)((targetTime - p0.TimeMs) / duration) : 0f;
                return Vector2.Lerp(p0.Position, p1.Position, Math.Clamp(t, 0f, 1f));
            }

            return p0.Position;
        }

        private partial class OsuKeyBindingContainer : RulesetKeyBindingContainer
        {
            private bool allowGameplayInputs = true;

            /// <summary>
            /// Whether gameplay input buttons should be allowed.
            /// Defaults to <c>true</c>, generally used for mods like Relax which turn off main inputs.
            /// </summary>
            /// <remarks>
            /// Of note, auxiliary inputs like the "smoke" key are left usable.
            /// </remarks>
            public bool AllowGameplayInputs
            {
                get => allowGameplayInputs;
                set
                {
                    allowGameplayInputs = value;
                    ReloadMappings();
                }
            }

            public OsuKeyBindingContainer(RulesetInfo ruleset, int variant, SimultaneousBindingMode unique)
                : base(ruleset, variant, unique)
            {
            }

            protected override void ReloadMappings(IQueryable<RealmKeyBinding> realmKeyBindings)
            {
                base.ReloadMappings(realmKeyBindings);

                if (!AllowGameplayInputs)
                    KeyBindings = KeyBindings.Where(static b => b.GetAction<OsuAction>() == OsuAction.Smoke).ToList();
            }
        }
    }

    public enum OsuAction
    {
        [LocalisableDescription(typeof(ActionStrings), nameof(ActionStrings.LeftButton))]
        LeftButton,

        [LocalisableDescription(typeof(ActionStrings), nameof(ActionStrings.RightButton))]
        RightButton,

        [LocalisableDescription(typeof(ActionStrings), nameof(ActionStrings.Smoke))]
        Smoke,

        [LocalisableDescription(typeof(OsuEditorStrings), nameof(OsuEditorStrings.HitCircleTool))]
        EditorHitCircleTool = 10000,

        [LocalisableDescription(typeof(OsuEditorStrings), nameof(OsuEditorStrings.SliderTool))]
        EditorSliderTool,

        [LocalisableDescription(typeof(OsuEditorStrings), nameof(OsuEditorStrings.SpinnerTool))]
        EditorSpinnerTool,

        [LocalisableDescription(typeof(OsuEditorStrings), nameof(OsuEditorStrings.GridFromPointsTool))]
        EditorGridFromPointsTool,

        [LocalisableDescription(typeof(OsuEditorStrings), nameof(OsuEditorStrings.ToggleGridSnap))]
        EditorToggleGridSnap,

        [LocalisableDescription(typeof(EditorStrings), nameof(EditorStrings.ToggleDistanceSnap))]
        EditorToggleDistanceSnap,
    }
}
