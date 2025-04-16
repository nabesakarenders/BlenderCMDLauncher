
# Blender CMD Launcher

A small portable application to launch Blender in 'headless' mode for rendering single frames or animations without the overhead of the viewport. Will try to also estimate the total remaining time when rendering animations.

## IMPORTANT

The exe is currently being flagged by some anti-virus programs (like Windows Defender) because... I have no idea. The app is literally just a single python file and PyQt6. Probably PyInstaller being flagged because reasons. Either trust it or don't, I'll do what I can to resolve the false positives when I have time.

## Installation

Grab from the releases page and place somewhere memorable. The app is portable and so does not need to be installed. It will place a small `ini` file next to the application after first launch to remember your chosen Blender path.

## Known Issues

- "Time Remaining" features are calculated by parsing Blender's output during rendering. I've made it as robust as I can but issues are possible.
    
## Roadmap

- UI Cleanup and pretty-fication
- May be useful for more of the options to be remembered, instead of just the default Blender EXE path
- Warnings about options that cannot be specified from the UI and are taken from the Blend File
- Soon™

