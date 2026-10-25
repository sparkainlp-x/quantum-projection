# Quantum Projection

**Live demo:** [Holographic Thoughts](https://sparkainlp-x.github.io/holographic-thoughts/) (interactive browser view; synthetic, classical simulation; measured numbers are in this repo)

Software DOI for v0.1.0: [10.5281/zenodo.23530281](https://doi.org/10.5281/zenodo.23530281) (all versions: [10.5281/zenodo.23530280](https://doi.org/10.5281/zenodo.23530280)).

A small, standard-library Python package that stores amplitude-encoded statevectors in a complex outer-product memory and projects probe states onto the stored subspace.

**SYNTHETIC.** This is a classical emulation of quantum kinematics only. n qubits cost 2^n complex numbers, so there is no speedup, and all correlations are classical, so there is no Bell violation. Every number below is measured in this repo with seeded pseudo-random noise; none is hardware data.

## What it does

- `HolographicMembrane(patterns).project(probe)` returns the complex overlaps ⟨p^μ|probe⟩, the normalized weights |m_μ|²/Σ|m|² and the arg-max pattern.
- `recall(probe, steps)` iterates a ← Wa/‖Wa‖ with W = Σ|p^μ⟩⟨p^μ|. This is a **projection onto the stored subspace**, not a collapse:
  - with orthonormal patterns, W is a projector, so recall reaches its fixed point after one step and the recalled fidelity to each pattern equals its Born weight;
  - with non-orthogonal patterns, repeated steps drift to W's dominant eigenvector, which is a mix of the patterns (see the measurements).
- `KetBraPair` computes the same overlaps from stored conjugates. It is the direct inner product written a second way; tests compare the complex values, phases included.
- `coarse_grain(state, qubit=0)` merges one qubit by a pairwise Haar low-pass. This equals projecting that qubit onto |+⟩ and renormalizing, and it is lossy.

## Quick start

```bash
python -m quantum_projection                  # prints the sweep tables (200 seeds per cell)
pip install -r requirements-dev.txt && python -m pytest   # 65 tests, warnings are errors
```

```python
from quantum_projection import HolographicMembrane, bell_phi_plus, bell_phi_minus, bell_psi_plus, noisy

mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus(), bell_psi_plus()])
r = mem.project(noisy(bell_phi_plus(), 0.25, seed=11))
r["winner"], r["probs"][0]        # 0, 0.8719
```

Invalid input (empty pattern list, mismatched lengths, zero-norm or non-finite vectors, a probe orthogonal to every pattern in `recall`, a bad qubit index) raises `ValueError`.

## Measured in this repo

Accuracy is the fraction of 200 seeds where the arg-max pattern is the true one. σ is the standard deviation of the complex Gaussian noise added to each real and imaginary part before renormalizing. For probes that are not stored, the cell shows how many of the 200 seeds went to each stored pattern.

**Bell states.** Stored: Φ+, Φ−, Ψ+.

| probe | σ=0.1 | σ=0.25 | σ=0.5 | σ=0.75 | σ=1.0 |
|---|---|---|---|---|---|
| Φ+ | 1.000 | 0.985 | 0.695 | 0.510 | 0.535 |
| Φ− | 1.000 | 0.990 | 0.720 | 0.525 | 0.480 |
| Ψ+ | 1.000 | 0.975 | 0.730 | 0.570 | 0.495 |
| Ψ− (not stored) | 71/68/61 | 64/63/73 | 71/67/62 | 65/58/77 | 62/71/67 |
| \|01⟩ (not stored) | 0/0/200 | 12/11/177 | 37/45/118 | 52/56/92 | 60/57/83 |

- 200 Haar-random 2-qubit states split 62/66/72; mean top weight 0.613.
- Largest gap between recalled fidelity and Born weight: 5.6e-16. Largest gap between 1-step and 25-step recall: 6.1e-16.
- The original draft reported 20/20 correct at σ ≤ 0.25. That reproduces for Φ+ with seeds 0 to 19; over 200 seeds the rate at σ = 0.25 is 0.975 to 0.990.

**Non-orthogonal patterns.** Stored: |00⟩ and |+0⟩, overlap 0.7071.

| probe | σ=0.1 | σ=0.25 | σ=0.5 | σ=0.75 | σ=1.0 |
|---|---|---|---|---|---|
| \|00⟩ | 1.000 | 0.895 | 0.750 | 0.660 | 0.550 |
| \|+0⟩ | 1.000 | 0.950 | 0.760 | 0.645 | 0.550 |

Recall of a clean |00⟩:

| steps | F(\|00⟩) | F(\|+0⟩) | F(dominant eigenvector) |
|---|---|---|---|
| 1 | 0.9000 | 0.8000 | 0.9950 |
| 2 | 0.8621 | 0.8448 | 0.9999 |
| 5 | 0.8536 | 0.8535 | 1.0000 |
| 25 | 0.8536 | 0.8536 | 1.0000 |

Iterating erases the distinction: for noisy |00⟩ at σ = 0.25, 25-step recall changes the one-shot winner in 75% of 200 seeds. Classify with `project()` or a single step.

**Coarse-grained 3 qubits to 2 (merge qubit 0).** Stored: GHZ, W, |000⟩, |+++⟩, each coarse-grained.

| probe | σ=0.1 | σ=0.25 | σ=0.5 | σ=0.75 | σ=1.0 |
|---|---|---|---|---|---|
| GHZ | 0.995 | 0.665 | 0.375 | 0.335 | 0.335 |
| W | 0.950 | 0.690 | 0.385 | 0.350 | 0.265 |
| \|000⟩ | 1.000 | 0.760 | 0.545 | 0.375 | 0.330 |
| \|+++⟩ | 0.990 | 0.790 | 0.480 | 0.300 | 0.255 |
| \|001⟩ (not stored) | 0/0/200/0 | 17/16/161/6 | 45/30/95/30 | 50/40/81/29 | 56/41/67/36 |

- After coarse-graining the stored patterns overlap heavily (W and |+++⟩: 0.866; GHZ and |000⟩: 0.707), which is why accuracy falls faster than in the Bell case.
- |001⟩ becomes identical to |000⟩ once qubit 0 is merged, so it is always assigned to |000⟩.
- 200 Haar-random 3-qubit states split 45/60/51/44.

## Limits

- No speedup, no Bell violation, no hardware: SYNTHETIC classical emulation only.
- `project()` never rejects a probe. A state outside the stored span is still assigned to some pattern; check the overlap magnitudes.
- Coarse-graining is lossy by construction, and its cost depends on the states in use.
- Amplitude encoding is one choice of map. See [DESIGN.md](DESIGN.md).

## Provenance

A package received under Mun Seok Lee's name, which lists him as sole author under AGPL-3.0-only, is kept unchanged in [spec/](spec/). We could not independently verify who wrote it. The main code in this repository is derived from it. `quantum_projection/qsim.py` is about 37% line-similar to the received `qsim.py`, and `quantum_projection/membrane.py`, the closest match to the received `qmembrane.py`, is about 31% similar. The sweeps, command-line entry point, packaging and tests were added by this project. Line similarity here comes from a plain diff, not from a review of intent. [CHANGELOG.md](CHANGELOG.md) lists the changes. Mun Seok Lee is not an author of this release, and he has not reviewed or endorsed this software.

## Acknowledgements

Thanks to Mun Seok Lee for the package received under his name (see Provenance above). This is an acknowledgement only: it implies no endorsement of this code or its conclusions.

## How to cite

See [CITATION.cff](CITATION.cff).

## License

Copyright (c) 2026 Jean-François Brisson, Spark AI NLP.

This software is available under the GNU Affero General Public License v3.0 only (AGPL-3.0-only); see [LICENSE](LICENSE).
