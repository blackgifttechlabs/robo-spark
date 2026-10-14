# Robo Sparks: 70-part Blender kit

Open `robotics-kit.blend`. The starting scene displays all 70 parts. Choose a `KIT • …` scene in Blender's scene selector to inspect one of the 50 new parts; `Component • …` scenes contain the 20 earlier parts. Middle mouse orbits; Numpad 0 toggles the inspection camera.

Every part is an editable `PART • …` collection marked as a Blender asset. Components have individually named geometry, curves, text and materials. Overview and `BROWSE • …` category scenes reuse collection instances. Geometry coordinates are millimetres, with unit scale 0.001. These are representative educational models with approximate proportions, rather than manufacturer CAD or electrically validated assemblies.

## Files

- `robotics-kit.blend`: complete master including the original scenes.
- `components/`: all 70 standalone Blender scenes and marked asset collections, with updated camera framing. The original library is preserved in `../robotics-library/`.
- `web/`: 70 GLB exports with baked mesh geometry, materials and named subparts. Curves and lettering are actual exported geometry.
- `previews/`: 70 individual Blender renders and an overview.
- `manifest.json`: part IDs, explanations, categories and file locations.
- `robot-recipes.json`: 20 suggested robot builds with required library parts. These are planning recipes, not completed robot assemblies or wiring instructions.
- `validation.json`: structural and web-export checks.

Append a `PART • …` collection from the master to reuse a part. Link it when future source changes should propagate. Separate standalone files are snapshots and do not automatically sync with the master.

## Reference provenance

The original 20 models retain their earlier generated-reference provenance. New components use common recognisable hardware forms and authored mechanisms. The following official references informed the board families; hidden details, revisions, footprints and dimensions are not exact replicas:

- Nano: https://docs.arduino.cc/resources/datasheets/A000005-datasheet.pdf
- micro:bit: https://tech.microbit.org/docs/hardware/assets/Microbit_V2_Assembly.pdf
- Servo driver: https://learn.adafruit.com/16-channel-pwm-servo-driver/downloads

## Reproduce

The live build loads the earlier master, adds one new part per timer tick, and saves to this folder:

```sh
OCIO="$PWD/models/robotics-library/preview-color.ocio" blender models/robotics-library/robotics-library.blend --python models/robotics-kit/build_kit.py
```

Validate, export and render from the completed kit:

```sh
OCIO="$PWD/models/robotics-library/preview-color.ocio" blender -b --python models/robotics-kit/validate_export.py
```

The originals are preserved. The kit does not yet change the website or its curriculum.
