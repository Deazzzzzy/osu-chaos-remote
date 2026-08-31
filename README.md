# osu! Chaos Remote

[Русская версия](README.ru.md)

A custom fun mod for **osu!lazer** that allows a second person (e.g., a streamer's chat or a friend) to interactively manipulate the gameplay in real-time. The mod communicates with a Python-based Control Panel via a TCP socket, enabling dynamic control over the game's difficulty and UI.

## Features

- **Wind / Gravity**: Push notes across the screen with adjustable strength and direction.
- **Magnet**: Force notes to repel from the player's cursor dynamically.
- **Earthquake**: Induce screen shake across the entire UI and playfield.
- **Flashbang**: Temporarily blind the player with a white screen flash.
- **Hidden**: Toggle the standard "Hidden" mode (invisible approach circles) on and off mid-game.
- **Blackout (Time Freeze)**: Freeze the game state for 5 seconds while the song continues playing.
- **Kiss**: Spawn a massive visual distraction in the middle of the screen.
- **Fake Miss**: Play a fake miss sound and animation to bait the player.
- **Playfield & UI Distortion**: Shrink, stretch, or squash the game interface and playfield on the X and Y axes independently.
- **Mirror Mode**: Flip the playfield or the UI horizontally and vertically.

## Installation

### 1. Control Panel (Python)
The Control Panel requires Python 3. No external dependencies are required, as it uses the built-in `tkinter` for the GUI and `socket` for networking.

1. Navigate to the `ControlPanel/` directory.
2. Run the application:
```cmd
python main.py
```

### 2. osu! Mod (C#)
Since osu!lazer does not currently support loading third-party mods as external plugins, this mod must be compiled directly into the game's source code.

1. Clone the official [osu! source code](https://github.com/ppy/osu).
2. Copy `OsuModChaos.cs` from the `OsuMod/` folder in this repository into `osu/osu.Game.Rulesets.Osu/Mods/`.
3. Open `osu.Game.Rulesets.Osu/OsuRuleset.cs` and register the mod by adding `new OsuModChaos()` to the `GetModsFor()` method (e.g., under `ModType.Fun` or `ModType.Conversion`).
4. Build and run the `osu.Desktop` project.

## How it Works
When the mod is selected and active in-game, it initializes a local TCP server listening on port `2826`. The Python Control Panel connects to `127.0.0.1:2826` and sends plain-text commands (e.g., `WIND_ON`, `EARTHQUAKE_STRENGTH:1.5`, `FLASHBANG`). The mod parses these incoming commands and dynamically overrides the `DrawableHitObject` transforms and playfield properties in real-time.
