# Revision 1.1

## English and shorter captions

- English is the default and fallback language. The caption catalog is `locales/en.yml`.
- Documentation is in English, and the previous Spanish caption file is removed.
- Persistent subtitles, configuration details, signal-generation formulas, correlation reports, full-rank control metrics, and repeated explanatory paragraphs are removed from the animation.
- Variance labels remain only in the third scene, where the variance contrast is part of the explanation.
- The numeric mixing matrix has direct speaker-column and microphone-row labels.

## Explicit projection in scene 2

- Each source is projected separately, keeping its source color.
- Faint original trajectories, vertical guides, highlighted samples, and cross-view arrows connect the 3D observations to their exact floor points.
- Each projected line is identified with its mixing-matrix column and slope.
- The camera turns overhead to show identical directions in both panels.
- The coordinate-change animation follows this comparison rather than occurring during the projection.
- The second scene lasts 66 seconds; the full sequence lasts 156 seconds.
- Audio and visual source-activity timing share one timeline.
- Regression tests check coordinate preservation, line collinearity, point-to-point correspondence, identical panel data, and the distinction between projection and unmixing.

The numerical source model, default device positions, and scientific interpretation are unchanged.
