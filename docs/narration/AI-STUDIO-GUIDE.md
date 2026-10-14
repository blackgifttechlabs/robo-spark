# Sparks narration: Google AI Studio production guide

Research checked on 14 October 2026. Start at [AI Studio speech generation](https://aistudio.google.com/generate-speech).

Current [Google speech documentation](https://ai.google.dev/gemini-api/docs/speech-generation) lists Gemini 3.8 TTS. Its delivery instructions belong in `speech_metadata.style`; brief human vocalizations use angle brackets inside the transcript, such as `<chuckles>`, `<gasp>` and `<short pause>`. Do not put robot beeps in the speech transcript: those are separate effects.

Earlier TTS models used prompt directions and bracket tags. The script studio includes both versions. Use the format appropriate to the model in your account; tags are directions, not a guarantee of identical performance. Check the first clip before generating the rest. [Earlier API guide](https://ai.google.dev/gemini-api/docs/generate-content/speech-generation).

## Voice identity — copy into your voice/style instructions

```text
A warm, playful robot companion speaking to children aged 8–12. Clear conversational English, gentle curiosity, a friendly smile and light comic timing. About 125–140 words per minute. Small natural breaths and thoughtful pauses. Never shout. Treat a wrong guess as a chance to discover. Keep the voice and accent consistent across clips.
```

Suggested starting voice: Puck. Choose another if you prefer; retain it for every file. For the current API, the production helper uses the selected voice and style as separate configuration. In AI Studio, use the delivery/style controls available for your selected model. If a control is absent, consult that model's prompting guide before pasting directions into the transcript.

## Generate roughly two-minute batches

1. Open the website's `narration.html` creator studio.
2. Copy the voice style once. Choose your model and keep the same voice.
3. Choose “Two-minute recording batches”. Copy one complete batch. Its paragraphs retain the separate component explanations.
4. Copy one batch transcript, generate it, and listen. The speaker should explain clearly, with light natural expression, rather than reading vocal tags aloud.
5. Download WAV audio and give it the exact batch filename shown on the card.
6. Bring back the full recording for speech alignment and cutting. After cutting, import all the resulting component files together. Imported clips remain in this browser and this website origin.
7. Reopen the lesson and test the component, captions and transition into the next clip. Cut excessive leading or trailing silence from the generated file.

There are 28 lesson clips and 70 component scripts, grouped into 11 approximately two-minute recording batches. See `TWO-MINUTE-BATCHES.md`. Files in this folder also contain copy-ready transcripts. `narration-pack.zip` contains the complete script collection.

## Performance direction

Sparks is curious, gentle and a little amused by small discoveries. Use chuckles for a small joke, a gasp for a discovery, and pauses before a prediction. Keep those moments brief. Never laugh at a learner's mistake. The scripts vary expression while leaving enough space to understand the idea. Use normal spoken emphasis for key terms such as “complete loop” and “input”; avoid a theatrical voice on every sentence.

## Publication and synchronization

Local imports are useful for auditioning. To share a finished voice with everyone, copy generated files into `assets/audio/narration/`, then run:

```sh
python3 scripts/index-narration.py
```

The generated manifest maps clip IDs to public file paths. No Google key is needed in the browser. Do not add a key to site code.

Playback treats each component explanation as one clip. A recorded clip's `currentTime / duration` drives part movement, seeking and connection progress. The active caption displays that clip's clean spoken text; it changes at clip boundaries, rather than pretending to be a word-timed transcript. Pause freezes narration and movement together. Replay resets the assembly. Navigating away cancels playback; switching to practice also stops narration. The effects occur at matching stage boundaries and can be muted independently.

The preview can use the browser's device voice, which does not reproduce the expressive AI tags. Where a device voice is unavailable, it uses a clearly labelled caption preview. Device preview timing is approximate; recorded audio uses its own playback clock. AI recordings have not been generated automatically because no Google API key or account was provided.

## Optional batch generation

`scripts/generate-narration.py` sends the separate clips to the currently documented Gemini TTS endpoint. Set `GEMINI_API_KEY` securely in your terminal environment. Generate a whole recording with `--batch basics-batch-01`, then align and cut it. You can also audition one component with `--clip CLIP_ID`. It can incur Google API usage charges, so it is not run by the site.

## Cutting a batch from its actual speech

The [stable-ts project](https://github.com/jianfch/stable-ts) supports aligning known text to recorded speech. The cutter can use that alignment to propose component boundaries, then export the clips at sample boundaries. Alignment estimates must be listened to and reviewed; they are not assumed exact merely because a model produced timestamps.

```sh
python3 scripts/split-narration.py recording.wav --batch basics-batch-01 --review-only
# After reviewing/editing the proposed boundary JSON:
python3 scripts/split-narration.py recording.wav --batch basics-batch-01 --cuts assets/audio/narration/basics-batch-01-cutpoints.json
python3 scripts/index-narration.py
```

The optional aligner requires `stable-ts` and a Whisper model in a separate Python environment. They are not downloaded automatically by the website. The cutter also accepts reviewed timestamps directly, so there is no need to install an aligner when the cutpoints are known. The script refuses mismatched turns, missing cutpoints or overlapping segments instead of guessing equal-length divisions. No final narration has been cut yet because the generated recordings have not been supplied.
