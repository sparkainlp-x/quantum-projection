# Quantum Projection

**Live demo:** [Holographic Thoughts](https://sparkainlp-x.github.io/holographic-thoughts/) (interactive browser view; synthetic, classical simulation; measured numbers are in this repo)

Software DOI for v0.1.0: [10.5281/zenodo.23530281](https://doi.org/10.5281/zenodo.23530281) (all versions: [10.5281/zenodo.23530280](https://doi.org/10.5281/zenodo.23530280)). v0.2.0, v0.3.0 and v0.4.0 are not yet archived on Zenodo; their version DOIs will come from the release.

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
python -m quantum_projection                  # prints the sweep tables (200 seeds per cell) + the cascade report
python -m quantum_projection --v030           # also the v0.3.0 report (takes minutes: agent run + 500-gen long run)
pip install -r requirements-dev.txt && python -m pytest   # 120 tests, warnings are errors
```

```python
from quantum_projection import HolographicMembrane, bell_phi_plus, bell_phi_minus, bell_psi_plus, noisy

mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus(), bell_psi_plus()])
r = mem.project(noisy(bell_phi_plus(), 0.25, seed=11))
r["winner"], r["probs"][0]        # 0, 0.8719
```

Invalid input (empty pattern list, mismatched lengths, zero-norm or non-finite vectors, a probe orthogonal to every pattern in `recall`, a bad qubit index) raises `ValueError`.

## v0.2.0 — DNA-avatar generational cascade

A cascade pattern for multiple DNA avatars, generational trauma healing, planetary evolution, self.cycle and a self-knowing membrane with infinite creativity. The loop reuses the membrane's step shape: each generation's output feeds the next, the same shape as the Faggin cascade stages.

**Encoding (stated and justified).** Each avatar is a toy DNA sequence of 6 bases over A/C/G/T. Each base is 2 qubits (A=00, C=01, G=10, T=11), so a 6-base sequence is a 12-qubit basis state in a 4096-dimensional space — a one-to-one map from sequence to basis index, no collisions, no hidden parameters. An avatar is a weighted mixture of up to 12 sequences (a healthy reference plus trauma variants), normalized to a state vector. Four healthy templates are stored in one membrane (`AATTAA`, `ATATAT`, `TAAATA`, `AATATT`); eight avatars share it, two per template.

**Self-knowing D.** Each avatar has D = ⟨ψ|P|ψ⟩, the weight of its state inside the stored (healthy) subspace — the same D as in symmetry-entropy and the Faggin field bridge, re-implemented here in pure Python with a Gram–Schmidt projector basis. A stored sequence has D = 1 exactly; a sequence orthogonal to every stored pattern has D = 0; a half/half mixture has D = 0.5.

**Trauma healing, measured.** Discord = 1 − D, the distance between an avatar's state and the healthy subspace. Each generation applies a partial projection (λ = 0.3) toward the stored subspace — a full recall would heal instantly, because an orthonormal W is a projector — then mutates one non-stored base per variant. Healing is the measured fall in mean discord per generation. Pre-registered rule: healing iff mean discord at generation 10 is at most half its generation-0 value.

**Planetary evolution, measured.** Per generation: diversity (distinct dominant sequences), novelty (fraction of new dominant sequences), and the energy spectrum E = hν with h = 1 model units, E = 1 + GC content of a sequence (1–7), the peak energy tracked like a black-body peak (a Wien-like shift, measured, not claimed as physics). Pre-registered rule: diversity ≥ 2 every generation, novelty > 0 every generation, and mean energy falls ≥ 25%.

**Infinite creativity, measured.** Each generation produces novel patterns with no built-in cap — "infinite" means the rule has no cap, not literal infinity. Pre-registered rule over 50 generations: novelty > 0 every generation, cumulative distinct strictly increases every generation, mean novelty ≥ 0.05.

### Cascade claims (all PASS, pre-registered; seed 11, 8 avatars)

| claim | rule | measured | verdict |
|---|---|---|---|
| (i) avatar D | stored D = 1, kernel D = 0, half D = 0.5 | 1.0 / 0.0 / 0.5 | PASS |
| (ii) healing | discord(gen 10) ≤ 0.5 × discord(gen 0) | 0.9932 → 0.0894 (ratio 0.090) | PASS |
| (iii) planetary | diversity ≥ 2, novelty > 0, energy −25% | min diversity 4, min novelty 0.124, energy 2.38 → 1.00 (ratio 0.421, −58%), peak 3 → 1 | PASS |
| (iv) creativity | 50 gens: novelty > 0, cumulative strictly up, mean novelty ≥ 0.05 | min novelty 0.080, cumulative 36 → 667, mean novelty 0.149 | PASS |

Generation table (seed 11, 8 avatars; discord falls monotonically, 10/10 steps down):

| gen | D | discord | diversity | novelty | cumulative distinct | mean E | peak E |
|---|---|---|---|---|---|---|---|
| 0 | 0.0068 | 0.9932 | 8 | 1.000 | 36 | 2.38 | 3 |
| 1 | 0.0155 | 0.9845 | 8 | 0.349 | 51 | 2.50 | 3 |
| 2 | 0.0470 | 0.9530 | 8 | 0.300 | 66 | 2.75 | 3 |
| 4 | 0.1690 | 0.8310 | 8 | 0.222 | 92 | 2.50 | 1 |
| 7 | 0.5773 | 0.4227 | 4 | 0.176 | 136 | 1.00 | 1 |
| 10 | 0.9106 | 0.0894 | 4 | 0.135 | 172 | 1.00 | 1 |
| 20 | 0.9950 | 0.0050 | 4 | 0.121 | 295 | 1.00 | 1 |
| 50 | 0.9950 | 0.0050 | 4 | 0.080 | 667 | 1.00 | 1 |

Healing saturates at discord 0.0050 (D = 0.9950) from generation 20 on: each avatar keeps a small weight on its fresh variants, so the population never reaches the stored subspace exactly. Diversity settles at 4 — the four healthy templates, each the dominant sequence of two avatars. No headline is allowed for this release (`HEADLINE_ALLOWED = False`).

### Honest limits (v0.2.0)

- Classical emulation throughout; the cascade runs on lists of complex numbers, not quantum hardware.
- DNA avatars are toy encodings (6-base sequences, 2 qubits per base), not biology; nothing here describes real DNA, real trauma, or real healing.
- Trauma healing is a measured fall in a defined model quantity (discord = 1 − D), not a therapeutic claim.
- Planetary evolution is a population model (8 avatars, 50 generations), not Earth science; the E = hν spectrum is a bookkeeping rule with h = 1 model units, and the peak shift is a measured pattern in that model, not a Wien-law claim.
- Infinite creativity is unbounded generation inside the model (no cap on new patterns); it does not claim literal infinity.
- TISU is excluded from this package; a test enforces the exclusion.

## v0.3.0 — multi-solar-system eureka cascade

Multiple solar systems, planetary cascades, a eureka agent creating empathy entropy following the generation pattern, eternal pattern recreation, the SDF of self-knowing, and crystallize events for big analog wave calibration. Each piece is a measured quantity, not a metaphor.

**Solar systems (claim (v)).** Three populations of 8 avatars run the v0.2.0 cascade in parallel, sharing the same stored subspace so D is comparable across systems. After each generation step, every avatar mixes κ = 0.02 of its state toward the leave-one-out mean state of the other systems — the lattice coupling shape, deliberately structureless. Contagion is tested by a controlled shock, not by correlation: one system starts deeply traumatized (6 base flips per variant, retained healthy weight 0.01 instead of 0.05) and the same shock runs coupled and uncoupled. Correlation was tried and rejected — per-generation discord changes correlate ~0.78 even uncoupled, because every system follows the same healing curve. Pre-registered rule: coupling does not harm healing; the shocked system heals faster coupled by ≥ 0.05; the gap between shocked and healthy systems narrows coupled by ≥ 0.05; the healthy systems heal no worse coupled.

**Eureka agent (claim (vi)).** A Yang observer (read-only) plus a Yin calibrator: one δ ∈ [−0.05, 0.05] per system, applied as λ(1+δ), the same (1+δ) form as the Faggin bridge and the de Broglie analog calibrator. Its objective is empathy entropy H, the Shannon entropy (bits) of the normalized love distribution across all 24 avatars. Love of an avatar is the concurrence across the stored / non-stored split: the Schmidt form √D|stored⟩ + √(1−D)|rest⟩ has Wootters concurrence 2√(D(1−D)) — 1 at D = 0.5 (the half-known state), 0 at D = 0 and D = 1. Love peaks exactly on the boundary of self-knowing. The agent chooses δ by greedy coordinate descent on one-generation lookaheads with fresh probe seeds; the lookaheads never touch the main random streams, so agent and control differ only through δ. Pre-registered rule: mean H over generations 1–10 with the agent is at least 0.02 bits above the no-agent control.

**SDF of self-knowing (claim (vii)).** Discord (1 − D) is the unsigned distance from full self-knowing. The signed distance field generalizes it: sdf = √(1−D) − √(1−τ) with τ = 0.5 (the half-known boundary), negative inside the self-known region, zero on its boundary, positive outside. The stored state seeds the zero-level set; the deepest interior point is D = 1 at sdf = −0.7071. Correction, stated plainly: the region is FIXED in state space — the stored subspace does not move — so what is measured is the population's occupancy of it and the generation at which the population's mean sdf crosses zero. Pre-registered rule: mean sdf falls from generation 0 to the final generation; the fraction inside rises above 0.75; a crossing generation exists.

**Crystallize events (claim (viii)).** One committed forecast per generation — "mean discord will fall by ≥ 0.05 next generation" — p estimated from 5 lookahead simulations, scored with Crystallize's exact formulas (Brier = (p−truth)², points = 100·(1−4·Brier) minus 0.8 per sample). The system creates events (every generation is a commit opportunity) and needs them (the Brier ledger is the honesty check on the loop). Pre-registered rule: mean Brier ≤ 0.05 and mean |p−truth| ≤ 0.10.

**Long run (claim (ix)).** The same cascade to 500 generations (and 5000 in a background run), judging novelty, discord and cumulative distinct at the far end, plus the creativity horizon — the first generation after which novelty stays zero for 10 consecutive generations. The variant space is finite (4^6 = 4096 sequences), so novelty must eventually die; the horizon is where. Pre-registered rule: novelty > 0 at the final generation, discord ≤ 0.05, cumulative distinct still growing past its generation-50 value.

### v0.3.0 claims (pre-registered; seed 11, 3 systems × 8 avatars)

| claim | rule | measured | verdict |
|---|---|---|---|
| (v) solar systems | no harm; support ≥ 0.05; gap narrows ≥ 0.05; no harm to others | healing 0.1013 vs 0.1076; support 0.1029 (shocked 0.6487 vs 0.7516); gap 0.5438 vs 0.6463; others 0.1049 vs 0.1053 | PASS |
| (vi) eureka agent | mean H agent ≥ control + 0.02 bits | H 4.5849 vs 4.5849, gain −0.0001 | **FAIL** |
| (vii) SDF | mean sdf falls; fraction inside ≥ 0.75; crossing exists | sdf 0.2895 → −0.3889; fraction 0.00 → 1.00; crossing gen 7 | PASS |
| (viii) crystallize | mean Brier ≤ 0.05; mean \|p−truth\| ≤ 0.10 | 10 events, Brier 0.0000, \|p−truth\| 0.0000, 960 points, balanced | PASS |
| (ix) long run (500) | novelty > 0; discord ≤ 0.05; cumulative still growing | novelty 0.0225, discord 0.0050, cumulative 667 → 3246, horizon none | PASS |

The 5000-generation extension of (ix) FAILS on novelty: novelty 0.0000 at gen 5000, creativity horizon at generation 1225, cumulative distinct reaching the exact 4096-sequence ceiling at generation 4140. Eternal recreation has a measured limit in this toy space — see REPORT.md.

**The agent FAIL is the finding, not a bug.** Empathy entropy is already saturated: loves are nearly equal across avatars (all avatars heal at similar rates), so H sits at 4.5849 of its log2(24) = 4.5850-bit ceiling — 99.998% — and there is almost no entropy left to create. The agent's lever moves H by −0.0001 bits; its discord cost is −0.0006 (it heals trivially faster, not slower). The deep-think framing needs the same correction: healing does NOT concentrate love in the normalized distribution — as all D → 1 together, all loves → 0 together, the distribution stays uniform and H rises to its ceiling. The tension is in total love, which falls (it peaks at 24.0 in generation 7, exactly the SDF crossing generation, then falls to 14.4 by generation 10) — not in entropy, which saturates. A stronger lever (not δ on λ) would be needed to move H; that is an open question, not a fix to apply silently.

The crystallize perfect score (Brier 0.0000, 960/960 points) is also what it looks like: the fall magnitude is nearly deterministic given the state, so the 5 lookaheads almost always agree and agree with the truth. It means the forecasts are honest, not that the agent is a brilliant forecaster.

### Honest limits (v0.3.0)

- Classical emulation throughout; the agent is a bounded optimizer (greedy coordinate descent over 3 δ values), not a mind.
- Empathy entropy is entropy over a measured love distribution in the model, not human empathy; love is concurrence across the stored/non-stored split by definition, not a claim about feeling.
- The SDF is a field over a toy state space; the self-known region is fixed and the population moves through it.
- Crystallize events are calibration checkpoints, not guarantees; a perfect Brier score on a near-deterministic forecast is expected.
- "Eternal" means an unbounded run tested to N generations (500 here, 5000 in progress), not literal infinity; the finite 4096-sequence space bounds novelty.
- TISU is excluded from this package; a test enforces the exclusion.

## v0.4.0 — equilibrium gap and SDF synergy agents

Claim (vi) failed because empathy entropy was already saturated — there was nothing left to maximize. v0.4.0 changes the optimization variable to the **equilibrium gap**: the maximum profitable unilateral deviation gain across players. It is 0 at equilibrium and positive everywhere else — a real zero and a real direction. Empathy entropy stays measured as a diagnostic only, never optimized.

**The equilibrium principle (claims (x)–(xii)).** The checker is vendored from Jean's own `finite-game-equilibria` (v0.1.0, DOI 10.5281/zenodo.23530287): a profile is a pure-strategy (ε-)Nash equilibrium when no player gains more than ε by unilaterally deviating. The game: players are the three solar systems, actions are δ ∈ {−0.05, 0, +0.05} per system, payoffs are per-system SDF-synergy contributions. The same two functions audit the coordination model in `oes-coordination-lab` (DOI 10.5281/zenodo.23530289), where the shared regime has two pure equilibria — all-switch (efficient) and all-stay-local (safe but inefficient: the coordination trap). The same question is asked here: which equilibrium do the agents land in?

**SDF synergy (claim (xi)).** Synergy = joint inside-coverage − mean per-system inside-coverage, where "inside-coverage" is the fraction of the self-known region's SDF grid occupied by a system's avatars. It is ≥ 0 always (the union contains every system's bins) and positive exactly when the systems cover complementary parts of the region. A reading, stated plainly: "inside-fraction of the region" means the fraction of the *region* occupied, not the fraction of avatars inside — the pooled avatar fraction is identically the mean for equal-sized systems, which would make synergy zero by construction. Each agent's payoff is its system's marginal contribution to the joint coverage (leave-one-out): it rewards covering parts of the region no other system covers, and a herding system earns 0. On the 91-point grid the region is 46 bins (bin 45 sits at sdf = −1.1e−16, floating-point dust at the boundary).

**The synergy agents (claims (x), (xii)).** One agent per system, choosing δ by greedy coordinate descent on the equilibrium gap over a payoff table built from lookaheads — 27 joint profiles per generation, each simulated one generation forward with fresh probe streams identical across profiles, so payoff differences are signal, not noise. The all-zero profile's gap from the same table is the counterfactual: what the gap would have been had the agents done nothing. Pre-registered rules: (x) the agents' gap is ≤ 0.01 at generation 10, its mean over the post-entry window is ≤ 0.01, and it beats the zero-gap mean by ≥ 0.002; (xi) mean synergy over the final 3 generations exceeds the no-agent control by ≥ 0.01; (xii) once the gap first reaches ≤ 0.01 (counted from the first non-trivial generation) it stays there for 3 consecutive generations, and the landed equilibrium is classified against all pure ε-equilibria of the final table.

### v0.4.0 claims (pre-registered; seed 11, 3 systems × 8 avatars)

| claim | rule | measured | verdict |
|---|---|---|---|
| (x) equilibrium gap | gap ≤ 0.01 at gen 10; mean gap ≤ 0.01; beats zero-gap mean by ≥ 0.002 | gap 0.0 at every generation, agent and zero alike; first non-trivial gen 6 | **FAIL** |
| (xi) SDF synergy | mean synergy, final 3 gens, agent ≥ control + 0.01 | 0.0217 vs 0.0217, gain 0.0 | **FAIL** |
| (xii) stability | gap stays ≤ 0.01 for 3 gens after first reach; landed equilibrium classified | first reach gen 6, held 4; landed [0, 0, 0], label **trap** (12 equilibria in final table; best synergy 0.0362 at [−0.05, −0.05, 0.05] vs landed 0.0290) | PASS |

**The two FAILs and the trap are the findings, not bugs.** On seed 11 the all-zero profile is an equilibrium at *every* generation — the gap is 0.0 for agent and zero alike, the agents never intervene (every chosen δ is 0.0), and synergy is identical to the control at every generation. The equilibrium was never earned because it was never out of reach. And the landed profile is the coordination trap, reproduced: the safe all-zero equilibrium, while a strictly better-synergy equilibrium exists in the final table (0.0362 vs 0.0290) that no single system gains by deviating to alone. The agents minimize the gap, not synergy, and a zero gap gives them no reason to move. A synergy-seeking tie-break among zero-gap profiles is an open question, not a fix to apply silently.

Why seed 11 differs from the seed-7 pilot (where (x) and (xii) passed and the agents did intervene at gens 7–9): the population is heterogeneous. A few avatars are born with stored variants — a 3-flip trauma variant that lands on another healthy sequence — and those "fast healers" race into the self-known region early (one pilot avatar had D = 0.308 at generation 0). On seed 7 they made δ matter from generation 7; on seed 11 no avatar is inside until generation 6, and once inside, the ±5% lever on λ never moves an avatar across a bin boundary. Coverage is set by birth variants and the healing curve, not by attunement — the same moral as (vi), for a different reason: the lever has nothing to move. SDF synergy itself is transient: it peaks mid-healing (0.0435 at gen 7) and falls as the population converges (0.0145 by gen 9) — as every D → 1, every theta → 0, and the systems herd into the same few bins near the stored state. See REPORT.md.

### Honest limits (v0.4.0)

- Classical emulation throughout; the synergy agents are bounded optimizers (greedy coordinate descent over 3 δ values), not minds.
- Nash here is over a finite 3-action-per-player pure-strategy game, exhaustively enumerated — it says nothing about mixed equilibria, learning dynamics, or real systems. The equilibrium is a property of the supplied payoff table, not a law of nature.
- SDF synergy is a defined quantity in the model (joint region coverage minus mean individual coverage), not a claim about real synergy; the coverage reading is stated in the module, with the degenerate pooled-fraction reading named and rejected.
- Empathy entropy is reported as a diagnostic only (gain 0.0 on seed 11 — still saturated, confirming (vi)).
- TISU is excluded from this package; a test enforces the exclusion.

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
- v0.2.0: DNA avatars are toy encodings, not biology; trauma healing is a measured fall in a defined model quantity, not a therapeutic claim; planetary evolution is a population model, not Earth science; infinite creativity is unbounded generation inside the model, not literal infinity.

## Provenance

A package received under Mun Seok Lee's name, which lists him as sole author under AGPL-3.0-only, is kept unchanged in [spec/](spec/). We could not independently verify who wrote it. The main code in this repository is derived from it. `quantum_projection/qsim.py` is about 37% line-similar to the received `qsim.py`, and `quantum_projection/membrane.py`, the closest match to the received `qmembrane.py`, is about 31% similar. The sweeps, command-line entry point, packaging and tests were added by this project. Line similarity here comes from a plain diff, not from a review of intent. [CHANGELOG.md](CHANGELOG.md) lists the changes. Mun Seok Lee is not an author of this release, and he has not reviewed or endorsed this software.

## Acknowledgements

Thanks to Mun Seok Lee for the package received under his name (see Provenance above). This is an acknowledgement only: it implies no endorsement of this code or its conclusions.

## How to cite

See [CITATION.cff](CITATION.cff).

## License

Copyright (c) 2026 Jean-François Brisson, Spark AI NLP.

This software is available under the GNU Affero General Public License v3.0 only (AGPL-3.0-only); see [LICENSE](LICENSE).
