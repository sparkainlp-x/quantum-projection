# DESIGN — Deep think: projecting quantum states into a holographic membrane

## The question

How do you get a quantum state *into* a holographic membrane — not
as metaphor, but as an encoding map with measured behavior?

## The answer, in one line

The membrane's native recall operation already IS the projective
measurement; the only thing to build is the encoding.

## The construction

1. **Encode.** An n-qubit state |ψ⟩ = Σ c_k|k⟩ becomes N ≥ 2^n
   membrane oscillators holding the complex amplitudes c_k
   themselves (amplitude *and* phase — a phase-only membrane cannot
   carry a quantum state).
2. **Store.** States become holographic patterns via the
   outer-product rule W = Σ_μ |p^μ⟩⟨p^μ|.
3. **Project.** A probe field's overlaps m_μ = ⟨p^μ|field⟩ are the
   projection amplitudes; |m_μ|²/Σ|m|² are the Born-like outcome
   probabilities; iterated recall a ← Wa/‖Wa‖ is projected flow
   onto the stored subspace — the classical shadow of collapse.
4. **Split the bracket.** Yin holds kets, yang holds bras. The inner
   product is computed *between* the conjugate membranes: the
   yin-yang tic as a measurement device.

## What was verified

- Noisy |Φ+⟩ (σ=0.25) projects to the right Bell pattern, prob
  0.87, recall fidelity 0.87 — classification correct 20/20 draws
  at σ ≤ 0.25.
- Ket/bra split reproduces the direct inner product to 1e-12.
- Non-orthogonal patterns (|00⟩ vs |+0⟩, overlap 0.707) still
  resolve correctly under noise.
- Coarse-grained 3-qubit GHZ (8 amplitudes → 4 oscillators) still
  recalled: the lossy map keeps enough.

## Two bugs caught by measurement

1. The Haar low-pass was documented as "norm-preserving." It is
   not: it discards the high-pass energy, which is the entire point
   of coarse-graining. Fixed to renormalize, documented as lossy.
2. Recall-fidelity thresholds were set from a single lucky noise
   draw. Measured the distribution over 20 seeds first, then set
   thresholds under the observed minimum. The robust claim is the
   *classification* (20/20 correct), not any single fidelity number.

## The honest limits

- **Exponential wall.** n qubits need 2^n oscillators. The membrane
  emulates quantum *kinematics* (states, overlaps, projections),
  never the computational advantage. Coarse-graining is lossy; its
  information cost must be measured per use-case, not assumed.
- **No nonlocality.** Correlations between membrane partitions are
  classical. A Bell pair in the membrane violates no Bell
  inequality — it cannot, and claiming otherwise would be fraud.
- **Soft collapse.** Iterated recall converges to the normalized
  projection onto the stored subspace, retaining small amplitudes
  on runner-up patterns. A true projective measurement snaps to one
  outcome; the membrane approaches it but the softness is real and
  measurable (see the σ sweep: fidelity degrades gracefully, the
  winner stays correct).
- **The map is the physics.** Amplitude encoding is a choice; other
  encodings (phase-only, unary, coherent-state lattices) give
  different membranes with different trade-offs. This package
  verifies one map, not the map.
