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

## Notes from the original draft

The draft's two corrections are kept: the Haar low-pass is not norm-preserving (it discards high-pass energy and is renormalized), and thresholds should come from a distribution of seeds rather than a single draw. The sweeps in `quantum_projection/sweeps.py` extend the second point to 200 seeds per cell.
