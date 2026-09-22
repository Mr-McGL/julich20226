# Blind source separation with ICA

Four configurable Python animations on a black background. The on-screen text, source code, configuration comments, and documentation are in English.

## Run

From the project directory:

```bash
conda env create -f conda/environment.yml
conda activate ica-animation
python run.py render --scene all --preset full
```

The result is `output/ica_animation.mp4`: **156 seconds**, at **1920 × 1080 and 30 fps**. No LaTeX, GPU, downloaded icons, or package installation is needed. FFmpeg is included in the Conda environment.

Render one scene or a faster preview:

```bash
python run.py render --scene 2 --preset preview --output output/scene_2.mp4
python run.py render --scene 2 --preset draft --duration-scale 0.25 --output output/quick.mp4
```

Existing videos are protected; add `--overwrite` to replace them.

## Generate previews

Videos, stills, metadata, and numerical diagnostics are generated outputs and
are excluded from version control, including the original outputs in `examples/`.
The project draws its illustrations in code and requires no input image assets.
Generate local previews in the ignored `output/` directory:

```bash
python run.py render --scene all --preset preview --fps 15 --audio --output output/preview.mp4
python run.py stills --scene all --preset preview
python run.py inspect --output output/diagnostics.json
```

Local validation reports and the original distribution's generated checksum
inventory (`manifest.sha256.json`) are also ignored.

## Scenes

| Scene | Duration | What happens |
|---|---:|---|
| 1 | 32 s | Speakers and microphones; distance attenuation; weighted sums; the mixing matrix; undoing the mixture. |
| 2 | 66 s | Alternating sources; separate projection of each trajectory; matching mixing lines; a top-view camera rotation; a coordinate change; simultaneous sources; PCA and ICA. |
| 3 | 34 s | Three sources and three microphones, but only two retained components; the dominant source and a residual mixture. |
| 4 | 24 s | Identical source signals collapse onto a single observable direction. |

### Reading the second scene

A colored trajectory is lowered onto `z = 0` while its original position remains faintly visible. Vertical guides connect the observations to the plane. A highlighted sample and a colored arrow identify **the very same point** in the right-hand view. The projected observations form the line of the corresponding column of the mixing matrix.

After each source has been projected separately, the camera turns overhead. Both panels now show the same two mixing lines, with the same colors, labels, samples, and coordinate scales. **Only then** does the right panel change to source coordinates through the ideal inverse. This separates two different operations visually: dropping the time coordinate and undoing the mixing.

In the simultaneous-source section, dashed white directions belong to PCA; colored directions are estimated by ICA. Colored source traces remain visible below the plots. During the final comparison, dashed white traces show the recovered signals.

## Configuration

Edit `config/default.yml`. Device positions are read from the `speakers` and `microphones` lists for each scene, using `position: [x, y]` in metres. Signal settings, colors, camera angles, scene durations, and export presets are also configurable.

Caption text is in `src/ica_animation/locales/en.yml`. Signal-generation details and numerical diagnostics stay in the documentation and diagnostic files rather than appearing on screen.

A separate configuration can override selected values:

```yaml
extends: default.yml
scenes:
  '2':
    duration: 75.0
    speakers:
      - {id: S1, position: [-3.2, 1.0]}
      - {id: S2, position: [3.0, -1.4]}
    microphones:
      - {id: M1, position: [-1.8, -0.5]}
      - {id: M2, position: [1.8, 0.7]}
```

Save this as `config/custom.yml` and run:

```bash
python run.py render --config config/custom.yml --scene 2 --output output/custom.mp4
```

Mappings merge recursively; lists are replaced in full. Preserve device identifiers when the same device should move between scenes. Scene 1 allows one to six speakers and microphones; additional speakers require matching frequencies, phases, amplitudes, and colors. Scenes 2–4 keep their teaching-specific dimensions.

The source projection, overhead view, coordinate change, and audio timing of scene 2 share the timeline in `src/ica_animation/timeline.py`.

### Optional third microphone

The default third axis in scene 2 is **time**, because there are two microphones. The supplied alternative uses three actual microphone measurements:

```bash
python run.py render --config config/third_microphone.yml --scene 2 --output output/three_microphones.mp4
```

In that variant, projecting onto `z = 0` shows the first two microphones while ICA still receives all three. The inverse demonstration uses the first two microphones, which must form an invertible two-by-two subsystem.

## Other commands

Add audible sonification of the first two microphones:

```bash
python run.py render --scene all --preset preview --audio --output output/with_audio.mp4
```

The audio is illustrative, not narration or recorded speech. Its frequencies are raised into the audible range. Scene 3 has no playback time and stays silent. Without `--audio`, exports are silent.

Generate stills or a specific scene position:

```bash
python run.py stills --scene all --preset full
python run.py stills --scene 2 --progress 0.558 --output output/top_view
```

Open the interactive viewer:

```bash
python run.py play --scene all --preset preview
```

Space pauses/resumes, Left/Right seek by two seconds, R restarts, and Escape closes the window. The viewer requires a desktop; video and still exports work without one.

Generate a small GIF, inspect the numerical model, or run the tests:

```bash
python run.py render --scene 4 --preset draft --duration-scale 0.3 --output output/identical.gif
python run.py inspect --output output/diagnostics.json
pytest -q
```

Large GIF exports are rejected to avoid excessive memory use. MP4 is the intended format for full-length exports. All layouts use a 16:9 aspect ratio.

Optional package installation:

```bash
python -m pip install -e .
ica-animation render --scene all --preset full
```

Commands assume the project root is the working directory. From another directory, supply an explicit `--config` path.

## Project layout

```text
ica_animation_project/
  conda/environment.yml
  config/default.yml
  config/third_microphone.yml
  src/ica_animation/
    config.py
    model.py
    graphics.py
    projection.py
    scenes.py
    timeline.py
    render.py
    audio.py
    cli.py
    locales/en.yml
  tests/
  scripts/
  docs/SCIENCE.md
  docs/REFERENCES.md
  docs/VALIDATION.md
  docs/CHANGES.md
  run.py
  pyproject.toml
```

## Scientific scope

This is a linear, instantaneous, noiseless teaching model, not a room-acoustics or speech-separation simulator. PCA directions maximize variance; ICA directions do not. In scene 3, dimensionality reduction discards information before two ICA components are estimated. The intermediate residual direction is a result of this particular configuration, not a general rule of ICA.

FastICA only receives microphone observations. The known source signals are used after estimation to align component order, sign, and scale for display. See `docs/SCIENCE.md` for the model, assumptions, and interpretation, and `docs/VALIDATION.md` for the checks actually performed.
