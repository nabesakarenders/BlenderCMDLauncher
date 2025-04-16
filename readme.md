
# Blender CMD Launcher

A small portable application to launch Blender in 'headless' mode for rendering single frames or animations without the overhead of the viewport. Will try to also estimate the total remaining time when rendering animations.

## IMPORTANT

Swapped to Nuitka to hopefully prevent issues with anti-virus flagging. It doesn't get flagged on my PC by Windows Defender or Bitdefender, but some still seem flag it. I don't have the money to sign such a small app so you can download the release or clone this repo and `pip install -r requirements.txt` and then `python app.py`.

## Installation

Grab from the releases page and place somewhere memorable. The app is portable and so does not need to be installed. It will place a small `ini` file next to the application after first launch to remember your chosen Blender path.

## Known Issues

- "Time Remaining" features are calculated by parsing Blender's output during rendering. I've made it as robust as I can but issues are possible.
    
## Roadmap

- UI Cleanup and pretty-fication
- May be useful for more of the options to be remembered, instead of just the default Blender EXE path
- Warnings about options that cannot be specified from the UI and are taken from the Blend File
- Soon™

## Changelog

- v0.1.0
    - Initial release
- v0.1.1
    - Font fixes
    - remaining time fixes
- v0.2.0
    - Nearly a year later!
    - Swap to Nuitka for building
    - Add Final Completion Time Estimation for animation rendering
    - Change Render button to Cancel button while rendering
    - Lock fields when rendering
    - Code improvements 