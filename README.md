# osu! Chaos Remote

[Русская версия](README.ru.md)

A fun interactive mod for **osu!lazer** that allows a second person (such as stream chat, friends, or donors) to intervene in the gameplay in real time. The mod communicates with a Python-based graphical control panel over a local TCP socket, allowing dynamic control over game physics, cursor behavior, notes, audio filters, and sudden troll events.

---

## 🎮 Features & Debuffs

### 1. Cursor & Controls
- **⏳ Windows Busy Cursor**: Animated rotating blue circular spinner attached to the cursor tip, obscuring exact hit aiming.
- **🔌 Mouse Disconnect (1.8s)**: Plays Windows device disconnect chime, completely locks cursor movement for 1.8s, then plays device connect chime.
- **🧲 Note Repulsion**: Cursor is physically repelled when getting close to active circles and sliders (130px radius).
- **🫨 Shaky Hands (Jitter)**: High-frequency cursor vibration simulating adrenaline tremor (customizable strength slider).
- **👥 Army of Clones**: Spawns 9 fake trailing/orbiting cursors with staggered delays and offsets.
- **Hardware-Level Input Lag**: True cursor input buffering in milliseconds (0 to 500 ms).
- **Hidden Cursor**: Completely hide the player's cursor during gameplay (leaving only the trail).
- **Schizophrenia (Fake Cursors)**: Mirrored copies (X, Y, X+Y), lagging swarm.
- **Cursor Scaling**: Resize cursor from tiny (0.1x) to gigantic (5.0x).
- **Invert Controls**: Flip cursor coordinates horizontally (X) and vertically (Y).
- **Key Jam**: Block Left (K1) or Right (K2) keys to force single-tap play.

### 2. Screen Distortion & Camera
- **🌀 Barrel Roll (360°)**: Smooth cinematic 360-degree rotation of the entire playfield over 3.5 seconds.
- **⏱️ Slideshow / 15 FPS Throttle**: Quantize playfield update rate to 15 frames per second (66.6ms frame steps) for 3.5 seconds.
- **🎯 Gigantic vs Micro Notes (CS Chaos)**: Alternating notes become huge (1.65x) or microscopic (0.42x).
- **🔲 144p Mosaic Effect**: Fullscreen low-resolution compression mosaic block overlay.
- **🌗 Invert Colors (Negative)**: Additive inverted lighting overlay flipping scene contrast.
- **🍾 Drunk Camera**: Smooth sinusoidal rolling and rotation of the playfield (±15°) creating a dizzy motion sickness effect.
- **🌋 Screen Shake (Earthquake)**: High-frequency playfield offsets up to ±25px.
- **🔦 Tunnel Vision**: Darkens the entire screen except for a circular spotlight around the player's cursor.
- **👻 Ghost Sliders**: Slider bodies become completely invisible (only heads and tails remain visible).
- **Scale Distortion**: Compress or stretch playfield and HUD along X and Y axes.
- **Mirroring**: Flip playfield or HUD horizontally and vertically.
- **Hidden Blindness**: Force notes to fade out after appearing.

### 3. Audio Havoc
- **🛑 Vinyl / Tape Stop**: Smooth speed and pitch drop to zero over 1.2s, brief silence, then smooth recovery back to normal.
- **⛪ Cathedral Echo (Reverb)**: Acoustic flutter and frequency oscillation simulating a massive hollow cathedral.
- **🌊 Underwater Audio (Low-Pass Filter)**: Cuts frequencies above 380 Hz — the song sounds submerged under deep water.
- **🎧 8D Panorama (Audio Spin)**: Continuous sinusoidal panning between Left and Right audio channels.
- **Audio Desync**: Shift the audio track timing relative to notes (-300ms to +300ms).
- **Time Rate**: Adjust gameplay speed with optional pitch shift (chipmunk effect).

### 4. Sudden Events & Trolling
- **📱 Telegram Call from «Мамуля ❤️»**: Realistic Telegram desktop call toast with audio `telegram-zvonok-pk.mp3` and answer/decline buttons (or audio-only mode).
- **💬 Steam Message Toast**: Bottom-right dark Steam notification popup with `steam-.mp3` sound ("Friend: Can you lend me $2 for shawarma?").
- **🪟 Windows Activation Watermark**: Translucent Windows watermark in the bottom-right ("Activate Windows: Go to Settings to activate Windows").
- **🔄 Windows Update Screen (3.5s)**: Fullscreen black update screen with spinning dots ("Working on updates 67%..."), stops gameplay clock, hides HUD and cursor.
- **💰 Papich Donation Alert (5 000 ₽)**: Top sliding stream alert with coins, avatar, and message: «Папич — 5 000 ₽: "Удали игру и не позорься"» with cash register chime.
- **⌨️ Sticky Keys Dialog**: Authentic Windows Sticky Keys confirmation dialog with exclamation beep.
- **⚡ GPU Artifacts / Matrix Glitch**: Sliced RGB horizontal displacement strips with Windows hardware failure sound.
- **💻 Blue Screen of Death (BSOD)**: Fullscreen Windows BSOD (`CRITICAL_PROCESS_DIED`, `osu!.exe`) with clock stop for 3 seconds.
- **📞 Discord Incoming Call**: Realistic Discord popup with avatar, vibration, and accept/decline buttons (or audio-only mode).
- **💬 Discord & Steam Audio-Only Notifications**: Authentic Discord message ping (`discord-notification.mp3`) and voice connected (`connected.mp3`) sounds, plus Steam message sound (`steam-.mp3`) without showing on-screen overlays.
- **🎯 Dynamic Mouse Sensitivity Slider**: Real-time cursor sensitivity scaling from 0.10x to 4.00x with presets and instant reset, supporting both Raw Input and graphic tablets.
- **🔋 Low Battery 5%**: Windows toast notification with system sound.
- **🛡️ Windows Defender Threat**: System malware alert toast.
- **⏳ Blackout (Time Freeze)**: Freeze hit objects for 5 seconds while audio keeps playing.
- **💥 Flashbang**: Fullscreen blinding white flash with gradual fade out.
- **💋 Kiss & ❌ Fake Miss**: Distracting visual overlays and fake combo break sound effects.
- **🎯 Hallucination Radar**: Clickable radar in the control panel to spawn fake notes on demand.

---

## 🚀 Installation & Setup

### 1. Control Panel (Python)
Requires Python 3. Uses standard libraries (`tkinter` and `socket`), no external packages needed.

```powershell
cd ControlPanel
python main.py
```

### 2. osu! Mod (C#)
1. Clone the [osu!lazer repository](https://github.com/ppy/osu).
2. Copy the mod source files from `OsuMod/`:
   - Into `osu/osu.Game.Rulesets.Osu/Mods/`:
     - `OsuModChaos.cs`
     - `TrollOverlay.cs`
     - `FakeCursorOverlay.cs`
     - `HiddenCursorOverlay.cs`
     - `HallucinationOverlay.cs`
     - `call_calling.mp3`
   - Into `osu/osu.Game.Rulesets.Osu/`:
     - `OsuInputManager.cs` (contains hooks for slippery cursor physics, note repulsion, jitter, and mouse lock)
3. Register the mod in `osu.Game.Rulesets.Osu/OsuRuleset.cs` within `GetModsFor()`:
   ```csharp
   new OsuModChaos(),
   ```
4. Build and run:
   ```powershell
   dotnet run --project osu.Desktop/osu.Desktop.csproj -c Debug
   ```

---

## 📡 Network Protocol
The mod listens on TCP port **9000** (`127.0.0.1:9000`). The Python Control Panel sends plain text commands (e.g. `TROLL:UPDATE`, `SLIPPERY_ON`, `REPULSION_ON`, `MUFFLED_ON`), and the game applies them immediately in the active session.
