# Robot sounds and mixing notes

## Included

- **Beeping Robot or Machine**, Jofae: [original sound and CC0 licence](https://freesound.org/people/Jofae/sounds/363251/). The site includes the public MP3 preview as `assets/audio/robot-beeps-jofae.mp3`. Source metadata is in `assets/audio/sources.json`. It plays softly on an explicit discovery start.
- **Original interface tones**, generated in Web Audio by `pages/learn/sounds.js`: scan, pickup, connection, dodge, success. They are project-authored tones, with no external samples. The wrong-match sound is gentle; it is not an alarm or punishment.

## Additional researched choices

[Mixkit's robot collection](https://mixkit.co/free-sound-effects/robot/) includes positive notifications, short machine activations and mechanical movement sounds. Its [sound-effect licence](https://mixkit.co/license/#sfxFree) governs their use. These are suggestions; no Mixkit files have been copied into the public source repository. Review redistribution terms before including external samples in source code.

[Pixabay's robot collection](https://pixabay.com/sound-effects/search/robots/) includes robot motor and electronic character sounds. None are included in the project; check the individual asset and licence before using one.

## Sound direction

- Startup: one friendly chirp, no looping robot chatter.
- Inspecting a sensor: short, quiet scanning notes.
- A component lands: a small connection ping.
- Wrong match: a soft descending wobble while the target dodges sideways.
- Correct match: two bright but quiet notes.
- Completed practice: a short rising three-note celebration.
- Speech remains the main sound. Avoid background music during explanations. The “Sounds” control mutes effects while leaving narration available.
