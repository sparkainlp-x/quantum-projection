# Design notes

SYNTHETIC. Classical emulation of quantum kinematics only. No speedup, no Bell violation.

## Construction

1. **Encode.** An n-qubit state |ψ⟩ = Σ c_k|k⟩ is held as 2^n complex numbers, one per "oscillator", amplitude and phase included. A phase-only array cannot carry a general state.
2. **Store.** Patterns are stored with the outer-product rule W = Σ_μ |p^μ⟩⟨p^μ|.
3. **Project.** A probe's overlaps m_μ = ⟨p^μ|probe⟩ give weights |m_μ|²/Σ|m|². For orthonormal patterns these are the Born probabilities for measuring in that basis, conditioned on the outcome lying in the stored subspace.
4. **Recall.** a ← Wa/‖Wa‖. This is a projection onto the stored subspace, not a collapse onto one pattern (see below).
5. **Ket/bra split.** One array holds kets, the other their complex conjugates. Multiplying a probe by the conjugates without conjugating again is the ordinary inner product written a second way. It agrees with step 3 up to rounding by construction; it is not an independent check.

## Statevector order and ZZ rotations

The statevector entry at integer index \(k\) is the amplitude of
\(|q_{n-1}\ldots q_1q_0\rangle\), where bit \(q\) is
\((k \mathbin{\gg} q)\mathbin{\&}1\). Thus qubit 0 is the least-significant
bit and the rightmost tensor factor. For example, the two-qubit vector order is
\((|00\rangle, |01\rangle, |10\rangle, |11\rangle)\), with qubit 0 on the
right.

`rz(theta)` returns
\(\operatorname{diag}(e^{-i\theta/2},e^{+i\theta/2})\). `apply_rzz(state,
q0, q1, theta)` applies
\[
RZZ(\theta)=e^{-i\theta(Z\otimes Z)/2}.
\]
It multiplies an amplitude by \(e^{-i\theta/2}\) when the selected bits are
equal and \(e^{+i\theta/2}\) when they differ. This agrees with the matrix
definition in [IBM's RZZGate reference](https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.RZZGate).
The direct statevector operation checks for a finite real angle, distinct
integer qubit indices, and a finite numeric vector of power-of-two length. It
rejects boolean/string angles, does not mutate or normalize its input, and
accepts unnormalized finite vectors as ordinary linear-algebra inputs.

The fixed shared-unitary control has a no-free-improvement invariant. If the
same unitary \(U\) is applied to every normalized stored pattern and query,
\(\langle Up^\mu|Uq\rangle=\langle p^\mu|q\rangle\); complex overlaps,
fidelities, normalized recognition weights, and non-tied winners are
unchanged. With transformed patterns,
\[
W'=\sum_\mu |Up^\mu\rangle\langle Up^\mu|=U W U^\dagger.
\]
Consequently, recall of \(Uq\) under \(W'\) follows the \(U\)-transformed
trajectory of recall of \(q\) under \(W\), with the same winners away from
numerical ties. This is equivariance, not a recognition gain. A diagonal ZZ
layer alone also preserves computational-basis probabilities; interference
with later gates can convert the phases into different readout probabilities.

Exact amplitude equality is kept distinct from equivalence up to global
phase: for example, \(RZZ(2\pi)=-I\), so the output amplitudes are the
negatives of the input even though the physical pure state is equivalent.
The existing first-maximum convention remains in force: exact winner ties
select the first pattern. A query orthogonal to every stored pattern keeps
all-zero weights and also reports winner 0; `recall` still raises for such a
query.

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

No experiment in this repository is a test of quantum advantage. The possible
input-dependent ZZ study is described as exploratory in
[`EXPLORATORY_PROTOCOL.md`](EXPLORATORY_PROTOCOL.md); it has not been run.
Relevant prior work has distinct scopes: Havlíček et al. introduced and
demonstrated quantum-enhanced feature spaces for selected supervised-learning
tasks ([Nature, 2019](https://doi.org/10.1038/s41586-019-0980-2)), while
Thanasilp et al. analyzed exponential concentration in quantum kernel methods
under their studied settings ([Nature Communications, 2024](https://doi.org/10.1038/s41467-024-49287-w)).
Neither establishes a performance result for this classical emulator.

## Notes from the original draft

The draft's two corrections are kept: the Haar low-pass is not norm-preserving (it discards high-pass energy and is renormalized), and thresholds should come from a distribution of seeds rather than a single draw. The sweeps in `quantum_projection/sweeps.py` extend the second point to 200 seeds per cell.
