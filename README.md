# osu! Chaos Remote

[Русская версия](README.ru.md)

A fun interactive mod for **osu!lazer** that allows a second person (such as stream chat, friends, or donors) to intervene in the gameplay in real time. The mod communicates with a Python-based graphical control panel over a local TCP socket, allowing dynamic control over game physics, cursor behavior, notes, audio sync, and sudden troll events.

---

## 🎮 Features & Debuffs

### 1. Cursor & Controls
- **Hardware-Level Input Lag**: True cursor input buffering in milliseconds.
- **Hidden Cursor**: Completely hide the player's cursor during gameplay.
- **Schizophrenia (Fake Cursors)**: Spawn duplicate cursor copies with trails (mirrored, lagging, swarm).
- **Cursor Scaling**: Resize cursor from tiny (0.1x) to gigantic (5.0x).
- **Invert Controls**: Flip cursor coordinates horizontally (X) and vertically (Y).
- **Key Jam**: Block Left (K1) or Right (K2) keys to force single-tap play.

### 2. Playfield & Note Physics
- **Wind / Gravity**: Blow notes across the screen with configurable strength and direction (0°–360°).
- **Magnet**: Dynamically repel notes away from the player's cursor.
- **Black Hole**: A singularity vortex at screen center (256, 192) pulling notes inward.
- **Chameleon Notes**: Override combo colors of notes, sliders, and approach circles (Stealth Black, Rainbow Disco, Monochrome).

### 3. Screen Distortion & Audio
- **Audio Desync**: Shift the audio track timing relative to notes (-300ms to +300ms).
- **Earthquake**: Shake the playfield and HUD dynamically.
- **Scale Distortion**: Compress or stretch playfield and HUD along X and Y axes.
- **Mirroring**: Flip playfield or HUD horizontally and vertically.

### 4. Sudden Events & Trolling
- **Low Battery 5% 🔋**: Windows toast alert with warning sound.
- **Discord Incoming Call 📞**: Discord call popup with avatar, wobble effect, and accept/decline buttons.
- **Blue Screen of Death (BSOD) 💻**: Fullscreen Windows BSOD (`CRITICAL_PROCESS_DIED`, `osu!.exe`) with critical stop chime for 3 seconds.
- **Windows Defender Threat 🛡️**: Windows Security alert toast warning about malware.
- **Blackout (Time Freeze)**: Stop all hit objects for 5 seconds while audio continues playing.
- **Flashbang 💥**: Fullscreen blinding white flash with gradual fade out.
- **Kiss 💋 & Fake Miss ❌**: Distracting visual overlays and fake combo break sounds.
- **Hallucination Radar**: Clickable radar in the control panel to spawn fake notes on demand.

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
2. Copy the mod source files from `OsuMod/` into `osu/osu.Game.Rulesets.Osu/Mods/`:
   - `OsuModChaos.cs`
   - `TrollOverlay.cs`
   - `FakeCursorOverlay.cs`
   - `HiddenCursorOverlay.cs`
   - `HallucinationOverlay.cs`
   - `call_calling.mp3`
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
The mod listens on TCP port **9000** (`127.0.0.1:9000`). The Python Control Panel sends plain text commands (e.g. `TROLL:BSOD`, `BLACK_HOLE_ON`, `INPUT_LAG:150`), and the game applies them immediately in the active session.
