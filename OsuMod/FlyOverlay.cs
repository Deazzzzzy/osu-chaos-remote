using System;
using System.Collections.Generic;
using osu.Framework.Graphics;
using osu.Framework.Graphics.Containers;
using osu.Framework.Graphics.Shapes;
using osu.Framework.Utils;
using osu.Game.Rulesets.Osu.Objects.Drawables;
using osu.Game.Rulesets.UI;
using osuTK;

namespace osu.Game.Rulesets.Osu.Mods
{
    public partial class FlyOverlay : CompositeDrawable
    {
        private readonly Container flyContainer;
        private readonly Container leftWing;
        private readonly Container rightWing;
        private readonly Random rnd = new Random();

        public bool IsActive { get; set; }

        private Vector2 currentPos = new Vector2(400, 300);
        private Vector2 targetPos = new Vector2(400, 300);
        private float flySpeed = 450f;
        private double nextDecisionTime;
        private bool isFlying;
        private float wingAngle;

        public FlyOverlay()
        {
            RelativeSizeAxes = Axes.Both;
            Depth = float.MinValue + 15;
            AlwaysPresent = true;
            Alpha = 0;

            InternalChild = flyContainer = new Container
            {
                Size = new Vector2(26, 26),
                Origin = Anchor.Centre,
                Position = currentPos,
                Children = new Drawable[]
                {
                    // Shadow
                    new Circle
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        Size = new Vector2(10, 16),
                        Position = new Vector2(3, 4),
                        Colour = Colour4.Black.Opacity(0.35f),
                    },
                    // Left Wing
                    leftWing = new Container
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.BottomRight,
                        Size = new Vector2(9, 15),
                        Position = new Vector2(-1, -1),
                        Rotation = -20,
                        Child = new Circle
                        {
                            RelativeSizeAxes = Axes.Both,
                            Colour = Colour4.White.Opacity(0.55f)
                        }
                    },
                    // Right Wing
                    rightWing = new Container
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.BottomLeft,
                        Size = new Vector2(9, 15),
                        Position = new Vector2(1, -1),
                        Rotation = 20,
                        Child = new Circle
                        {
                            RelativeSizeAxes = Axes.Both,
                            Colour = Colour4.White.Opacity(0.55f)
                        }
                    },
                    // Fly Body
                    new Circle
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        Size = new Vector2(8, 14),
                        Colour = Colour4.FromHex("#1a1a1a"),
                    },
                    // Thorax / stripe
                    new Circle
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        Size = new Vector2(9, 7),
                        Position = new Vector2(0, -1),
                        Colour = Colour4.FromHex("#2d2d2d"),
                    },
                    // Head
                    new Circle
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        Size = new Vector2(7, 6),
                        Position = new Vector2(0, -6),
                        Colour = Colour4.FromHex("#111111"),
                    },
                    // Red eyes
                    new Circle
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        Size = new Vector2(2.5f, 2.5f),
                        Position = new Vector2(-2.5f, -7f),
                        Colour = Colour4.FromHex("#aa1111"),
                    },
                    new Circle
                    {
                        Anchor = Anchor.Centre,
                        Origin = Anchor.Centre,
                        Size = new Vector2(2.5f, 2.5f),
                        Position = new Vector2(2.5f, -7f),
                        Colour = Colour4.FromHex("#aa1111"),
                    }
                }
            };
        }

        public void UpdateFly(Playfield? playfield, Vector2? screenCursorPos)
        {
            if (!IsActive)
            {
                if (Alpha > 0)
                    this.FadeOut(200);
                return;
            }

            if (Alpha < 1)
                this.FadeIn(200);

            double now = Environment.TickCount64;

            // Cursor spook reaction
            if (screenCursorPos.HasValue)
            {
                Vector2 localCursor = ToLocalSpace(screenCursorPos.Value);
                float distToCursor = Vector2.Distance(currentPos, localCursor);
                if (distToCursor < 80f)
                {
                    // Escape!
                    targetPos = new Vector2(
                        (float)rnd.NextDouble() * Math.Max(DrawWidth - 100, 400) + 50,
                        (float)rnd.NextDouble() * Math.Max(DrawHeight - 100, 300) + 50
                    );
                    isFlying = true;
                    flySpeed = 650f; // Panic flight speed
                    nextDecisionTime = now + rnd.Next(1500, 3000);
                }
            }

            if (now >= nextDecisionTime)
            {
                decideNextMove(playfield);
            }

            // Move fly towards targetPos
            float dt = (float)Math.Clamp(Time.Elapsed / 1000.0, 0.0, 0.1);
            if (dt > 0)
            {
                Vector2 diff = targetPos - currentPos;
                float dist = diff.Length;

                if (dist > 3f)
                {
                    isFlying = dist > 40f;
                    Vector2 dir = diff / dist;
                    float step = Math.Min(dist, (isFlying ? flySpeed : 80f) * dt);
                    currentPos += dir * step;

                    // Rotate towards movement direction
                    float targetAngle = MathHelper.RadiansToDegrees((float)Math.Atan2(dir.Y, dir.X)) + 90f;
                    flyContainer.Rotation = (float)Interpolation.Damp(flyContainer.Rotation, targetAngle, 0.95, dt);
                }
                else
                {
                    isFlying = false;
                }
            }

            flyContainer.Position = currentPos;

            // Wing flutter
            if (isFlying)
            {
                wingAngle += (float)(dt * 4500f);
                float flutter = (float)Math.Sin(wingAngle) * 35f;
                leftWing.Rotation = -20f - Math.Abs(flutter);
                rightWing.Rotation = 20f + Math.Abs(flutter);
            }
            else
            {
                // Occasional sitting twitch
                float twitch = (float)Math.Sin(now * 0.015) * 8f;
                leftWing.Rotation = -20f + twitch;
                rightWing.Rotation = 20f - twitch;
            }
        }

        private void decideNextMove(Playfield? playfield)
        {
            double now = Environment.TickCount64;

            // 60% chance to target an active note if available
            bool targetedNote = false;
            if (playfield?.HitObjectContainer != null && rnd.NextDouble() < 0.6)
            {
                foreach (var obj in playfield.HitObjectContainer.AliveObjects)
                {
                    if (obj is DrawableOsuHitObject dHit && dHit.HitObject != null)
                    {
                        Vector2 noteScreen = dHit.ToScreenSpace(Vector2.Zero);
                        targetPos = ToLocalSpace(noteScreen);
                        targetedNote = true;
                        break;
                    }
                }
            }

            if (!targetedNote)
            {
                // Random position on screen
                targetPos = new Vector2(
                    (float)rnd.NextDouble() * Math.Max(DrawWidth - 100, 500) + 50,
                    (float)rnd.NextDouble() * Math.Max(DrawHeight - 100, 400) + 50
                );
            }

            isFlying = Vector2.Distance(currentPos, targetPos) > 40f;
            flySpeed = isFlying ? (float)rnd.Next(380, 520) : 70f;
            nextDecisionTime = now + rnd.Next(1400, 3200);
        }
    }
}
