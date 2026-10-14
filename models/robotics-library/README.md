# Reusable robotics models in Blender

Open `robotics-library.blend`. Its starting scene shows the 20 components together. Use the scene menu in the top right to select any `Component • …` or `Project • …` scene. Middle mouse orbits; Numpad 0 toggles the inspection camera.

All 20 components are native editable meshes, curves and text, with materials and separately named subparts. Each `PART • …` collection is marked as a Blender asset. The 24 project assemblies reuse these collections through collection instances. Editing a source collection in the master updates its instances throughout that file. Move or rotate an instance to position a whole component. To edit a source, select its Component scene. To create independent editable geometry from an instance, use Object > Apply > Make Instances Real.

`components/` contains 20 standalone Blender files. `projects/` contains all 24 standalone project files, including their component dependencies. These standalone files are portable snapshots; edits do not automatically sync between separate files. Append a `PART • …` collection from the master to reuse it in another Blender file, or link it if you want external updates. Add this directory under Preferences > File Paths > Asset Libraries to browse the marked collections.

Geometry coordinates are millimetres. Blender’s unit scale is 0.001. `manifest.json` records the nominal size assumptions, reference images and components used in each project. Supplementary props model the parts needed by the projects beyond the 20-component list, such as displays, moisture probes, lamps, a Bluetooth module and rails.

## Accuracy

The source pictures were generated illustrations. Models reconstruct their appearance with common module proportions, including HC-SR04, SG90, TT, Uno-style, L298N, DHT11 and NEMA17 forms. They are **not exact manufacturer CAD**. The pictures do not provide measured dimensions, hidden geometry, tolerances or a unique product revision. Board holes, pin layouts, circuitry and project props contain approximations. Wires illustrate connections and are not validated wiring diagrams. Projects are visual learning assemblies, not electrically simulated or certified working circuits. The servo sweep is a choreographed animation.

For exact replicas, provide the manufacturer and revision of each part, mechanical drawings or measured dimensions, and photographs from multiple sides. Use these models for visual learning and scene assembly; do not use their geometry to manufacture mating parts.

## Rebuild and preview

- `blender --python build_library.py` builds components and projects in stages in the visible Blender window. It yields to the UI between stages and saves after completion.
- `blender -b --python build_library.py` rebuilds without a visible window.
- `OCIO="$PWD/models/robotics-library/preview-color.ocio" blender -b --python models/robotics-library/validate_and_preview.py` checks files and shared assets, fixes mesh normals, and creates Blender-rendered previews.

`progress.json` and `live-build.log` report the live build. `validation.json` reports structural checks. `previews/` contains actual Blender renders, not the original reference illustrations.

## Web assembly playback

`blender -b --python models/robotics-library/export_web.py` exports all 24 project assemblies into `assets/assemblies/` as GLB models. Each model preserves separate assembly groups with numbered stages. `mission.html?topic=PROJECT_ID` loads the exported model and assembles these groups with play, pause, replay, seek and speed controls. The original Blender geometry stays editable; the browser exports bake curves and modifiers into meshes for playback.

To refresh web models after editing the Blender library, add `-- --force` to the export command. Existing exports are otherwise reused. The local `preview-color.ocio` supplies a basic display transform because this machine’s Blender installation lacks its usual color configuration. Use the `OCIO` environment variable shown above when rendering here.
