# osu! Chaos Remote

A custom fun mod for **osu!lazer** that allows a second person (or a streamer's chat) to interactively mess with the gameplay in real-time! The mod communicates with a Python Control Panel over a TCP socket.

## Features
- 💨 **Wind / Gravity**: Push the notes across the screen with adjustable strength and direction.
- 🧲 **Magnet**: Push notes away from the player's cursor.
- 💥 **Earthquake**: Shake the entire UI and playfield.
- 🙈 **Flashbang**: Temporarily blind the player with a white screen flash.
- 🕶️ **Hidden**: Toggle the standard "Hidden" mode (invisible approach circles) on and off mid-game.
- 🛑 **Blackout (Time Freeze)**: Freeze the game for 5 seconds (notes stop, but the song continues).
- 💋 **Kiss**: Spawns a massive distraction in the middle of the screen.
- ❌ **Fake Miss**: Plays the miss sound and animation to bait the player.
- 🔍 **Playfield & UI Distortion**: Shrink, stretch, or squash the game interface and playfield on X/Y axes.
- 🪞 **Mirror Mode**: Flip the playfield or the UI horizontally and vertically.

## Installation

### 1. Control Panel (Python)
The Control Panel requires Python to be installed. No external pip libraries are required (it uses the built-in `tkinter` and `socket`).
1. Navigate to the `ControlPanel/` folder.
2. Run `main.py` using Python:
```cmd
python main.py
```

### 2. osu! Mod (C#)
Because osu!lazer does not support loading third-party mods as plugins yet, you must compile this mod directly into the game source.
1. Clone the [osu! source code](https://github.com/ppy/osu).
2. Copy `OsuModChaos.cs` from the `OsuMod/` folder in this repository into `osu/osu.Game.Rulesets.Osu/Mods/`.
3. Open `osu.Game.Rulesets.Osu/OsuRuleset.cs` and add `new OsuModChaos()` to the `GetModsFor()` method (under `ModType.Fun` or `ModType.Conversion`).
4. Build the `osu.Desktop` project.

## How it works
When the mod is active in-game, it starts a local TCP server on port `2826`. The Python control panel connects to `127.0.0.1:2826` and sends simple text commands (like `WIND_ON`, `EARTHQUAKE_STRENGTH:1.5`, `FLASHBANG`). The mod reads these commands and overrides the `DrawableHitObject` properties dynamically!
