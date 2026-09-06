using System;
using osu.Framework.Graphics;
using osu.Game.Rulesets.UI;

namespace osu.Game.Rulesets.Osu.Mods
{
    public partial class HiddenCursorOverlay : Component
    {
        private GameplayCursorContainer realCursor;
        private bool isHidden = false;

        public HiddenCursorOverlay(GameplayCursorContainer cursor)
        {
            this.realCursor = cursor;
        }

        public void SetHidden(bool hidden)
        {
            isHidden = hidden;
            
            if (realCursor?.ActiveCursor != null)
            {
                if (!isHidden)
                {
                    realCursor.ActiveCursor.Alpha = 1;
                }
            }
        }

        protected override void Update()
        {
            base.Update();

            if (isHidden && realCursor?.ActiveCursor != null)
            {
                realCursor.ActiveCursor.Alpha = 0;
            }
        }
    }
}
