# Model and scientific interpretation

## 1. Attenuation and mixing

The ideal free-field spherical model uses local intensity proportional to the inverse square of distance. Pressure amplitude is proportional to the square root of intensity, giving amplitude proportional to inverse distance [R1]. The emitted total acoustic power does not decrease when a microphone moves away; local intensity does.

With source amplitude defined at reference distance d₀ = 1 metre:

**Aᵢⱼ = d₀ / dᵢⱼ**, and **xᵢ(t) = Σⱼ Aᵢⱼ sⱼ(t)**.

Rows of A correspond to microphones; columns correspond to speakers. The sum describes what a microphone receives. Positions in the YAML configuration determine all distances and gains; rows and columns are not normalized independently.

The code uses samples as rows and channels as columns:

```python
observations = sources @ mixing.T
```

The mixture is instantaneous, linear, and noiseless. Drawn wave ribbons are explanatory artwork, not propagation delays in the numerical model. Reverberation, echoes, source directivity, and real speech are outside this model.

## 2. The blind problem

If A is known, square, and invertible, the ideal separator is W = A⁻¹. With more microphones and full column rank, a left inverse such as the pseudoinverse is an ideal noiseless reference. A poorly conditioned matrix can amplify errors even if its rank is full.

In blind source separation, A and the source signals are unknown. ICA seeks statistically independent components, not maximum-variance directions. Classical identifiability relies on additional assumptions, including independent sources, sufficient observable dimensions, and at most one Gaussian source. Order, sign, and scale remain ambiguous [R2–R4].

`fit_ica` receives only observations. After estimation, `align_for_display` uses known simulator sources to match components and align their signs and scales for comparison. This evaluation step is not part of blind estimation. Accordingly, the project does not claim that ICA recovers calibrated distances or physical source amplitudes.

## 3. Why each projected trajectory is a mixing line

With two microphones, write the source columns as:

**a₁ = (A₁₁, A₂₁)ᵀ**, **a₂ = (A₁₂, A₂₂)ᵀ**.

When only source j is active:

**x(t) = aⱼ sⱼ(t)**.

Every microphone pair is therefore a scalar multiple of the same column. For nonzero A₁ⱼ, eliminating sⱼ gives:

**x₂ = (A₂ⱼ / A₁ⱼ) x₁**.

This is the line shown in the animation. Positive and negative source amplitudes trace both sides of the origin. No line-fitting algorithm or hand-selected direction is involved: both the points and the reference direction come from the same matrix column.

### Projection is not separation

The default 3D path is **(x₁(t), x₂(t), t)**. The floor projection is **(x₁(t), x₂(t), 0)**. The function `flatten_points` changes only the third coordinate, even partway through the animation. It does not change either microphone measurement.

Each source is projected separately. A real sample is highlighted in the moving path, its floor projection, and the second view. The connecting arrow ends at that same sample, not at an arbitrary point on the line. Vertical guides and same-colored line labels make the relationship visible. The camera then turns overhead without changing any data.

The two panels show identical floor samples and identical column directions before the coordinate-change phase begins. That later phase changes the right panel with an interpolated linear coordinate map whose endpoint is W = A⁻¹. At the endpoint, W a₁ and W a₂ are the two canonical source directions. This is not orthogonal projection onto a₁ and a₂; mixing columns need not be perpendicular.

### Three-microphone alternative

`config/third_microphone.yml` draws **(x₁, x₂, x₃)** instead. Projection shows the first two coordinates. ICA still receives the three measurements. The ideal coordinate-change panel uses the first two rows of A, so that subsystem must have rank two.

## 4. Simultaneous sources, PCA, and ICA

In scene 2, the white dashed directions are computed by PCA on the two displayed microphone coordinates. They are orthogonal maximum-variance directions. The colored estimated directions are the columns of the ICA mixing estimate, displayed in the same microphone plane [R3–R5]. They are not the rows of the unmixing matrix; mixing directions and coordinate-extraction functionals have different meanings.

The default source sinusoids have different integer cycle counts over the sampling window and nearly zero sample correlation. The program checks the configured correlation bound. This is not a proof of statistical independence, nor a general guarantee that any pair of sinusoids can be separated. The alternating-source segment illustrates geometry; ICA is fitted to the later simultaneous-source dataset.

## 5. Three sources reduced to two components

Scene 3 keeps three sources and three microphone channels but requests two ICA components. FastICA's whitening step reduces the observation space to two principal dimensions before seeking independent components [R3]. A separate PCA fit supplies the retained plane drawn for explanation.

The default amplitudes are 5, 1, and 1. Source variances are approximately 12.5, 0.5, and 0.5. The two weaker mixing directions are close enough that their distinguishing direction contributes very little variance. Losing that dimension preserves almost all variance but prevents full recovery of both weak sources.

The observed result is a well-recovered dominant source and a second component containing both weaker sources. Its estimated mixing direction lies between their directions in this configuration. It is not a universal behavior of ICA. A full three-component control is computed in the diagnostics, but numerical control results and setup details are not placed on screen.

Colored points in the 3D plot are source contributions expressed in microphone coordinates. Gray points are their sum, which is what the estimator receives. The inset uses normalized directions to make the weak-source geometry visible; it is not a second fit. The lower source traces share an amplitude scale.

Generate the numerical matrices, correlations, retained variance, and direction angles with `python run.py inspect --output output/diagnostics.json`. This report is excluded from version control. Changing geometry, amplitudes, frequencies, or the seed may change this result; use `inspect` and the tests to check the modified configuration.

## 6. Identical source signals

When s₁(t) = s₂(t) = s(t), the observations satisfy:

**x(t) = (a₁ + a₂) s(t)**.

The displayed floor data occupy one line even when A itself is invertible. The observation matrix has rank one, so the code does not fit a two-component ICA model to it. A common waveform can be described, but the blind observations do not identify two independent source signals or their separate mixing columns.

## 7. Sonification

Optional audio uses a fixed frequency multiplier to make the illustrative low-frequency signals audible. The first two microphone mixtures are written to stereo channels. Source-activity timing in scene 2 is shared with the visual timeline. Global normalization prevents clipping while preserving relative gains.

This is sonification, not voice, narration, a physical room recording, or cycle-for-cycle audio at the plotted frequency. Scene 3 is intentionally silent because its 3D dataset has no playback time.

## References

Reference identifiers [R1]–[R6] are listed in `REFERENCES.md`. Numerical claims about the supplied configuration can be reproduced with `python run.py inspect` and `pytest -q`.
