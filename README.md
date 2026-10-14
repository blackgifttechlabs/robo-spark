# Robo Sparks

A robotics learning website for children, with a landing page, a dedicated learning studio, six beginner lessons, a 70-part Blender library and 24 project assembly views.

## Preview locally

```sh
python3 -m http.server 8765 --bind 127.0.0.1
```

Open:

- `http://127.0.0.1:8765/` — landing page.
- `http://127.0.0.1:8765/learn.html` — animated lessons and practice mode.
- `http://127.0.0.1:8765/learn.html?lesson=parts-library` — inspect and hear about the parts.
- `http://127.0.0.1:8765/narration.html` — voice production studio.

## Lessons

“Start here” introduces parts before projects. Children can watch components turn and move into place, follow captions, pause/replay and play an individual explanation. Practice supports dragging or tapping a component into its role, gentle sideways dodges for wrong matches, and connecting the placed parts. Progress is saved in the browser.

Recorded narration controls animation timing through the audio playback clock. Until recordings are added, the site offers device speech where available, or an explicitly labelled caption preview. Expressive AI voices are not pre-generated.

## Two-minute voice recordings

The creator studio groups the 28 lesson clips and 70 component scripts into 11 approximately two-minute batches. Copy a complete batch into Google AI Studio. Download the audio with the matching batch filename. Speech alignment and reviewed cutpoints separate it into component files; the player then uses those clips for synchronization.

See [the production guide](docs/narration/AI-STUDIO-GUIDE.md), [batch scripts](docs/narration/TWO-MINUTE-BATCHES.md) and [sound credits](docs/narration/SOUND-SOURCES.md).

For published voices, put the finished component clips in `assets/audio/narration/` and run:

```sh
python3 scripts/index-narration.py
```

For production, credentials belong in a terminal environment, never in site source. The browser does not call Google TTS or require a Google key. Local recording imports are stored only in that browser and website origin.

## Blender library

Open `models/robotics-kit/robotics-kit.blend`. The kit contains 70 reusable assets, 70 standalone Blender files, 70 web exports and rendered previews. Choose `BROWSE • …` scenes to inspect categories. These are representative educational models with approximate dimensions. Assembly and practice connections show ideas, not validated physical wiring diagrams.

See [the kit guide](models/robotics-kit/README.md) and [all-part preview](models/robotics-kit/previews/contact-sheet.jpg).
