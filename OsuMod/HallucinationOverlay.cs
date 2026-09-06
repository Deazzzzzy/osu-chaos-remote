using System;
using osu.Framework.Graphics;
using osu.Framework.Graphics.Containers;
using osu.Game.Rulesets.UI;
using osu.Game.Rulesets.Osu.Skinning;
using osu.Game.Rulesets.Osu.Skinning.Default;
using osu.Game.Skinning;
using osuTK;
using osuTK.Graphics;
using osu.Framework.Bindables;
using osu.Game.Graphics;
using osu.Game.Audio;
using osu.Framework.Allocation;
using osu.Framework.Audio;

namespace osu.Game.Rulesets.Osu.Mods
{
    public partial class HallucinationOverlay : Container
    {
        public HallucinationOverlay()
        {
            RelativeSizeAxes = Axes.Both;
            Anchor = Anchor.TopLeft;
            Origin = Anchor.TopLeft;
        }

        public Playfield Playfield { get; set; }

        public void SpawnFakeNote(Vector2 position, float scale, double preempt, Color4 color)
        {
            var fakeNote = new FakeNote(position, scale, preempt, color, Clock.CurrentTime);
            Add(fakeNote);
        }

        public void ScheduleAction(Action action)
        {
            Schedule(action);
        }

        private partial class FakeNote : osu.Game.Rulesets.Osu.Objects.Drawables.DrawableHitCircle
        {
            public FakeNote(Vector2 position, float scale, double preempt, Color4 color, double currentTime)
                : base(new osu.Game.Rulesets.Osu.Objects.HitCircle 
                { 
                    Position = position,
                    TimePreempt = preempt,
                    StartTime = currentTime + preempt,
                    HitWindows = new osu.Game.Rulesets.Osu.Scoring.OsuHitWindows(),
                    Scale = scale
                })
            {
                HitObject.HitWindows.SetDifficulty(5); // Prevent 0-range HitWindows which might cause issues
                AccentColour.Value = color;
            }

            protected override void LoadComplete()
            {
                base.LoadComplete();
                
                // Trigger scale update since we bypass the object pool (which normally triggers this on Apply)
                float currentScale = HitObject.Scale;
                HitObject.Scale = currentScale == 1.0f ? 1.0001f : 1.0f;
                HitObject.Scale = currentScale;

                // Make unclickable
                if (HitArea != null)
                    HitArea.Alpha = 0;

                // Fake note naturally fades out after preemptTime
                using (BeginDelayedSequence(HitObject.TimePreempt))
                {
                    this.FadeOut(100).Expire();
                }
            }

        }
    }
}
