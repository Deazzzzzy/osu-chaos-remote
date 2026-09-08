using System;
using System.Collections.Generic;
using System.IO;
using osu.Framework.Allocation;
using osu.Framework.Graphics;
using osu.Framework.Graphics.Containers;
using osu.Framework.Graphics.Rendering;
using osu.Framework.Graphics.Sprites;
using osu.Framework.Graphics.Textures;
using osuTK;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;

namespace osu.Game.Rulesets.Osu.Mods
{
    public partial class BusyCursorDrawable : CompositeDrawable
    {
        private Sprite sprite = null!;
        private SpriteIcon? fallbackIcon;
        private readonly List<Texture> frames = new List<Texture>();
        private const int frame_duration_ms = 50; // 20 FPS (Windows standard cursor rate)

        public BusyCursorDrawable()
        {
            Origin = Anchor.Centre;
            Size = new Vector2(34, 34);
        }

        [BackgroundDependencyLoader]
        private void load(IRenderer renderer)
        {
            InternalChild = sprite = new Sprite
            {
                RelativeSizeAxes = Axes.Both,
                FillMode = FillMode.Fit,
                Origin = Anchor.Centre,
                Anchor = Anchor.Centre,
            };

            loadAniFrames(renderer);

            if (frames.Count == 0)
            {
                AddInternal(fallbackIcon = new SpriteIcon
                {
                    Origin = Anchor.Centre,
                    Anchor = Anchor.Centre,
                    Icon = FontAwesome.Solid.CircleNotch,
                    Size = new Vector2(30),
                    Colour = Colour4.FromHex("#00a2ed")
                });
            }
        }

        private void loadAniFrames(IRenderer renderer)
        {
            string primaryPath = @"C:\Windows\Cursors\aero_busy.ani";
            string fallbackLocal = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "aero_busy.ani");
            string modsFolder = @"C:\Users\dizzy\Downloads\Osu_Debuffs\osu\osu.Game.Rulesets.Osu\Mods\aero_busy.ani";

            string? targetPath = null;
            if (File.Exists(primaryPath))
                targetPath = primaryPath;
            else if (File.Exists(modsFolder))
                targetPath = modsFolder;
            else if (File.Exists(fallbackLocal))
                targetPath = fallbackLocal;

            if (targetPath == null)
                return;

            try
            {
                byte[] data = File.ReadAllBytes(targetPath);
                var rawFrames = parseAni(data);

                foreach (var (w, h, bgra) in rawFrames)
                {
                    var image = new Image<Rgba32>(w, h);
                    for (int y = 0; y < h; y++)
                    {
                        int dibRow = h - 1 - y;
                        int rowOffset = dibRow * w * 4;
                        for (int x = 0; x < w; x++)
                        {
                            int p = rowOffset + x * 4;
                            byte b = bgra[p];
                            byte g = bgra[p + 1];
                            byte r = bgra[p + 2];
                            byte a = bgra[p + 3];
                            image[x, y] = new Rgba32(r, g, b, a);
                        }
                    }

                    var tex = renderer.CreateTexture(w, h);
                    tex.SetData(new TextureUpload(image));
                    frames.Add(tex);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"[BusyCursorDrawable] Error loading ani: {ex}");
            }
        }

        private static List<(int width, int height, byte[] bgra)> parseAni(byte[] data)
        {
            var list = new List<(int, int, byte[])>();
            if (data.Length < 16) return list;
            if (data[0] != (byte)'R' || data[1] != (byte)'I' || data[2] != (byte)'F' || data[3] != (byte)'F') return list;
            if (data[8] != (byte)'A' || data[9] != (byte)'C' || data[10] != (byte)'O' || data[11] != (byte)'N') return list;

            int idx = 12;
            while (idx + 8 <= data.Length)
            {
                string chunkId = System.Text.Encoding.ASCII.GetString(data, idx, 4);
                int chunkSize = BitConverter.ToInt32(data, idx + 4);
                if (chunkSize < 0 || idx + 8 + chunkSize > data.Length) break;

                if (chunkId == "LIST" && chunkSize >= 4)
                {
                    string listType = System.Text.Encoding.ASCII.GetString(data, idx + 8, 4);
                    if (listType == "fram")
                    {
                        int subIdx = idx + 12;
                        int endSub = idx + 8 + chunkSize;
                        while (subIdx + 8 <= endSub)
                        {
                            string subId = System.Text.Encoding.ASCII.GetString(data, subIdx, 4);
                            int subSz = BitConverter.ToInt32(data, subIdx + 4);
                            if (subSz < 0 || subIdx + 8 + subSz > endSub) break;

                            if (subId == "icon" && subSz >= 22)
                            {
                                int curStart = subIdx + 8;
                                int bWidth = data[curStart + 6];
                                int bHeight = data[curStart + 7];
                                int w = bWidth == 0 ? 256 : bWidth;
                                int h = bHeight == 0 ? 256 : bHeight;
                                int imgOffset = BitConverter.ToInt32(data, curStart + 18);

                                int pixelOffset = curStart + imgOffset + 40;
                                int byteCount = w * h * 4;
                                if (pixelOffset + byteCount <= curStart + subSz)
                                {
                                    byte[] bgra = new byte[byteCount];
                                    Buffer.BlockCopy(data, pixelOffset, bgra, 0, byteCount);
                                    list.Add((w, h, bgra));
                                }
                            }
                            subIdx += 8 + subSz + (subSz % 2);
                        }
                    }
                }
                idx += 8 + chunkSize + (chunkSize % 2);
            }
            return list;
        }

        protected override void Update()
        {
            base.Update();

            if (frames.Count > 0)
            {
                int index = (int)((Environment.TickCount64 / frame_duration_ms) % frames.Count);
                if (index >= 0 && index < frames.Count)
                    sprite.Texture = frames[index];
            }
            else if (fallbackIcon != null)
            {
                fallbackIcon.Rotation += (float)(Time.Elapsed / 1000.0) * 720f;
            }
        }
    }
}
