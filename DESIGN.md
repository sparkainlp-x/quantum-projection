# Design notes

SYNTHETIC. Classical emulation of quantum kinematics only. No speedup, no Bell violation.

## Construction

1. **Encode.** An n-qubit state |ψ⟩ = Σ c_k|k⟩ is held as 2^n complex numbers, one per "oscillator", amplitude and phase included. A phase-only array cannot carry a general state.
2. **Store.** Patterns are stored with the outer-product rule W = Σ_μ |p^μ⟩⟨p^μ|.
3. **Project.** A probe's overlaps m_μ = ⟨p^μ|probe⟩ give weights |m_μ|²/Σ|m|². For orthonormal patterns these are the Born probabilities for measuring in that basis, conditioned on the outcome lying in the stored subspace.
4. **Recall.** a ← Wa/‖Wa‖. This is a projection onto the stored subspace, not a collapse onto one pattern (see below).
5. **Ket/bra split.** One array holds kets, the other their complex conjugates. Multiplying a probe by the conjugates without conjugating again is the ordinary inner product written a second way. It agrees with step 3 up to rounding by construction; it is not an independent check.

## What recall does

- **Orthonormal patterns.** W is an orthogonal projector (W² = W). Recall reaches its fixed point P_S ψ/‖P_S ψ‖ after one step and further steps change nothing (measured gap between 1 and 25 steps: below 1e-15). The recalled fidelity to pattern μ equals its Born weight exactly (measured gap below 1e-15). The result keeps every stored component; nothing snaps to a single outcome.
- **Non-orthogonal patterns.** W is not a projector, and repeated recall is power iteration on W. For |00⟩ and |+0⟩ (overlap 0.7071), it converges to W's dominant eigenvector (|00⟩+|+0⟩)/‖·‖, which has equal fidelity (0.8536) to both patterns. Iterating therefore erases the distinction the one-shot overlap made; for noisy |00⟩ at σ = 0.25, 25 steps change the one-shot winner in 75% of 200 seeds, because after convergence the winner is decided by rounding. Use `project()` or a single `recall` step to classify.

## Coarse-graining

`coarse_grain(state, qubit=0)` pairs amplitudes whose indices differ only in `qubit` and keeps (a+b)/√2, then renormalizes. This is exactly projecting that qubit onto |+⟩ (tested for each qubit). It is lossy: the |−⟩ component is discarded, and states that differ only on that qubit become identical, so |000⟩ and |001⟩ both map to |00⟩. The original code always merged qubit 0 (the least-significant bit); the qubit is now a parameter.

## Limits

- **Exponential cost.** n qubits need 2^n complex numbers. This emulates kinematics (states, overlaps, projections), not quantum computation, and offers no speedup.
- **No nonlocality.** All correlations are classical numbers in one array. A Bell state stored here does not and cannot violate a Bell inequality.
- **No rejection.** `project()` always names a winner. Probes outside the stored span (Psi− against {Φ+, Φ−, Ψ+}) are still assigned, effectively at random under noise. Check the overlap magnitudes before trusting a winner.
- **The map is a choice.** Amplitude encoding is one choice among several (phase-only, unary, coherent-state lattices). This package measures one map.

## v0.2.0 — DNA-avatar cascade

The cascade reuses the step shape: each generation's output feeds the
next, the same shape as the membrane lattice step and the Faggin cascade
stages. A DNA avatar is a 6-base sequence (A/C/G/T, 2 qubits per base)
mapped to a 12-qubit basis state; an avatar is a weighted mixture of up
to 12 sequences. Self-knowing D = ⟨ψ|P|ψ⟩ uses the same projector idea
as the stored-subspace recall, with P built by Gram–Schmidt over the four
healthy templates. Two design facts forced the mechanism: (1) a full
recall heals instantly because an orthonormal W is a projector, so the
generation step uses a partial projection (λ = 0.3); (2) the projection
can only amplify stored weight already present, so each avatar carries
its healthy sequence at small weight and mutation never touches stored
variants. Energy is a bookkeeping rule, E = 1 + GC content with h = 1
model units; the peak shift is measured in the model, not claimed as
physics. "Infinite" creativity means the generation rule has no cap.
See REPORT.md for the measured tables and the honest limits.

## v0.3.0 — multi-solar-system eureka cascade

Five new pieces, all on the v0.2.0 cascade:

1. **Solar systems** (`solar_systems.py`): N populations in parallel,
   each with its own population seed and random stream, sharing the
   same stored subspace so D is comparable across systems. After
   each generation step, every avatar mixes a fraction κ = 0.02 of
   its state toward the leave-one-out mean state of the other
   systems (sparse amplitude dicts; the mix is exact, the retain
   logic is generation_step's). Coupling is deterministic and uses
   no randomness, so a coupled run and its uncoupled control consume
   identical streams. Contagion is tested by a controlled shock, not
   by correlation: one system starts deeply traumatized (6 flips per
   variant, retained healthy weight 0.01), and the same shock runs
   coupled and uncoupled. Correlation was tried and rejected -- the
   per-generation discord changes correlate ~0.78 even uncoupled,
   because every system follows the same healing curve.
2. **Eureka agent** (`eureka_agent.py`): a Yang observer (read-only)
   plus a Yin calibrator (one δ ∈ [-0.05, 0.05] per system, applied
   as λ(1+δ), the same (1+δ) form as the Faggin bridge and the de
   Broglie analog calibrator). Its objective is empathy entropy H,
   the Shannon entropy of the normalized love distribution across
   all avatars in all systems. Love of an avatar is the concurrence
   across the stored / non-stored split: the Schmidt form
   √D|stored⟩ + √(1-D)|rest⟩ has Wootters concurrence 2√(D(1-D)),
   which peaks at D = 0.5 and vanishes at D = 0 and D = 1. The
   agent chooses δ by greedy coordinate descent on one-generation
   lookaheads with fresh probe seeds; the lookaheads never touch
   the main streams, so agent and control differ only through δ.
3. **SDF** (`sdf.py`): the signed distance field of self-knowing,
   sdf = √(1-D) - √(1-τ) with τ = 0.5 (the half-known boundary).
   Negative inside the self-known region, zero on its boundary,
   positive outside. The region is fixed in state space -- the
   stored subspace does not move -- so what is measured is the
   population's occupancy of it and the generation at which the
   population's mean sdf crosses zero.
4. **Crystallize events** (`crystallize_events.py`): one committed
   forecast per generation ("mean discord will fall by ≥ 0.05 next
   generation"), p estimated from 5 lookahead simulations, scored
   with Crystallize's exact formulas (Brier, 100·(1-4·Brier) minus
   0.8 per sample). The system creates events (every generation is
   a commit opportunity) and needs them (the Brier ledger is the
   honesty check on the loop).
5. **Long run** (`longrun.py`): the same cascade to 500 generations
   (and 5000 in a background run), judging novelty, discord and
   cumulative distinct at the far end, plus the creativity horizon
   -- the first generation after which novelty stays zero for 10
   consecutive generations. The variant space is finite (4^6 =
   4096 sequences), so novelty must eventually die; the horizon is
   where. See REPORT.md for the measured tables and the honest
   limits.

## v0.4.0 — equilibrium gap and SDF synergy agents

Three new pieces, all on the v0.3.0 cascade:

1. **Equilibrium** (`equilibrium.py`): the pure-strategy
   (epsilon-)Nash checker vendored from finite-game-equilibria
   v0.1.0 (DOI 10.5281/zenodo.23530287, commit 11698948) --
   `validate_game`, `analyze_profile`, `find_pure_equilibria` --
   plus `equilibrium_gap` (the maximum profitable unilateral
   deviation gain at a profile) and `audit_table` (every
   profile's gap, all pure epsilon-equilibria, the minimum-gap
   profile). The gap is the v0.4.0 optimization variable: 0 at
   equilibrium, positive everywhere else. It replaces empathy
   entropy, which saturated at its ceiling in claim (vi).
2. **SDF synergy** (`sdf_synergy.py`): on the 91-point SDF grid,
   the self-known region is the bins with sdf < 0 as computed
   (46 of 91; bin 45 sits at -1.1e-16). An avatar occupies the
   bin nearest its theta; per-system inside-coverage is the
   fraction of the region's bins it occupies, joint is the
   union's fraction, synergy is joint minus the mean of the
   per-system coverages (>= 0 always, positive exactly when the
   systems cover complementary parts of the region). Each
   agent's payoff is its system's leave-one-out marginal
   contribution to the joint coverage. The coverage reading of
   "inside-fraction of the region" is stated in the module with
   the reason the pooled-avatar-fraction reading is rejected
   (identically the mean for equal-sized systems).
3. **Synergy agents** (`synergy_agents.py`): one agent per
   system, choosing delta by greedy coordinate descent on the
   gap over a payoff table built from lookaheads (27 joint
   profiles per generation, one simulated generation each,
   fresh probe streams identical across profiles). The all-zero
   profile's gap from the same table is the counterfactual.
   Verdicts (x)-(xii) are pre-registered in the module with
   thresholds set from the seed-7 pilot; the seed-11
   measurement lands (x) FAIL, (xi) FAIL, (xii) PASS with the
   landed equilibrium labelled "trap" -- the
   oes-coordination-lab coordination trap, reproduced. See
   REPORT.md for the measured tables, the pilot numbers, and
   the structural findings (fast healers; transient synergy).

## Notes from the original draft

The draft's two corrections are kept: the Haar low-pass is not norm-preserving (it discards high-pass energy and is renormalized), and thresholds should come from a distribution of seeds rather than a single draw. The sweeps in `quantum_projection/sweeps.py` extend the second point to 200 seeds per cell.
