using System;
using System.Collections.Generic;
using osu.Framework.Graphics;
using osu.Framework.Graphics.Containers;
using osu.Game.Rulesets.Osu.UI.Cursor;
using osu.Game.Rulesets.UI;
using osuTK;

namespace osu.Game.Rulesets.Osu.Mods
{
    public partial class FakeCursorOverlay : Container
    {
        private GameplayCursorContainer realCursor;
        private string currentMode = "OFF";

        private List<FakeCursorContainer> fakeCursors = new List<FakeCursorContainer>();

        public FakeCursorOverlay(GameplayCursorContainer cursor)
        {
            this.realCursor = cursor;
            RelativeSizeAxes = Axes.Both;
        }

        public void SetMode(string mode)
        {
            if (currentMode == mode) return;
            currentMode = mode;
            
            ClearCursors();

            if (mode == "OFF") return;

            // Spawn cursors depending on mode
            if (mode == "MIRROR_X" || mode == "MIRROR_Y" || mode == "MIRROR_XY")
            {
                var fake = new FakeCursorContainer(realCursor, mode);
                fakeCursors.Add(fake);
                Add(fake);
            }
            else if (mode == "SWARM")
            {
                // Spawn a few delayed/offset cursors
                for (int i = 0; i < 3; i++)
                {
                    var fake = new FakeCursorContainer(realCursor, "SWARM_" + i);
                    fakeCursors.Add(fake);
                    Add(fake);
                }
            }
            else if (mode == "ARMY" || mode == "CLONES")
            {
                for (int i = 0; i < 9; i++)
                {
                    var fake = new FakeCursorContainer(realCursor, "ARMY_" + i);
                    fakeCursors.Add(fake);
                    Add(fake);
                }
            }
        }

        private void ClearCursors()
        {
            foreach (var cursor in fakeCursors)
            {
                cursor.Expire();
            }
            fakeCursors.Clear();
        }
    }

    public partial class FakeCursorContainer : OsuCursorContainer
    {
        private GameplayCursorContainer realCursor;
        private string mode;
        private Vector2 currentPos;

        // For swarm mode
        private Queue<Vector2> posHistory = new Queue<Vector2>();
        private int delayFrames = 0;
        private Vector2 swarmOffset = Vector2.Zero;

        public FakeCursorContainer(GameplayCursorContainer realCursor, string mode)
        {
            this.realCursor = realCursor;
            this.mode = mode;

            if (mode == "SWARM_0") { delayFrames = 5; swarmOffset = new Vector2(30, 30); }
            if (mode == "SWARM_1") { delayFrames = 15; swarmOffset = new Vector2(-30, 20); }
            if (mode == "SWARM_2") { delayFrames = 25; swarmOffset = new Vector2(10, -40); }

            if (mode.StartsWith("ARMY_"))
            {
                int idx = int.Parse(mode.Substring(5));
                delayFrames = (idx + 1) * 3;
                float angle = idx * (MathF.PI * 2f / 9f);
                float dist = 24f + (idx % 3) * 14f;
                swarmOffset = new Vector2(MathF.Cos(angle) * dist, MathF.Sin(angle) * dist);
            }
        }

        protected override void Update()
        {
            base.Update();

            if (realCursor?.ActiveCursor == null) return;

            if (realCursor.ActiveCursor is OsuCursor realOsuCursor && ActiveCursor != null)
            {
                if (ActiveCursor.ModScaleAdjust.Value != realOsuCursor.ModScaleAdjust.Value)
                    ActiveCursor.ModScaleAdjust.Value = realOsuCursor.ModScaleAdjust.Value;
            }

            Vector2 realPos = realCursor.ActiveCursor.Position;
            Vector2 newPos = realPos;

            // Assuming Playfield space (512x384)
            if (mode == "MIRROR_X")
            {
                newPos.X = 512 - realPos.X;
            }
            else if (mode == "MIRROR_Y")
            {
                newPos.Y = 384 - realPos.Y;
            }
            else if (mode == "MIRROR_XY")
            {
                newPos.X = 512 - realPos.X;
                newPos.Y = 384 - realPos.Y;
            }
            else if (mode.StartsWith("SWARM") || mode.StartsWith("ARMY"))
            {
                posHistory.Enqueue(realPos);
                if (posHistory.Count > delayFrames)
                {
                    newPos = posHistory.Dequeue() + swarmOffset;
                }
                else
                {
                    newPos = realPos; // While filling history
                }
            }

            currentPos = newPos;
            ActiveCursor.Position = currentPos;
        }
    }
}
