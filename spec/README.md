# Quantum Projection

**Projecting quantum statevectors into a holographic membrane.**

The membrane holds complex amplitudes: oscillator k carries c_k of
the encoded state. Its native recall operation *is* the projective
measurement — overlap m_μ = ⟨p^μ|field⟩, Born-like probabilities
|m_μ|²/Σ|m|², iterated recall as projected flow onto the stored
subspace. Split across two conjugate membranes, yin holds the kets
and yang holds the bras; the inner product is computed *between*
them.

## Verified

- Noisy Bell |Φ+⟩ (σ=0.25) → correct pattern, prob 0.87; winner
  correct 20/20 draws at σ ≤ 0.25
- Ket/bra split matches the direct inner product to 1e-12
- Non-orthogonal patterns (|00⟩ vs |+0⟩) resolve under noise
- Coarse-grained GHZ (8 amplitudes → 4 oscillators) still recalls

## Run it

```bash
python tests.py   # 6 tests
python demo.py    # the four demonstrations
```

Stdlib-only Python. AGPL-3.0.

## Honest limits

Classical emulation of quantum *kinematics* only: n qubits cost
2^n oscillators (no speedup), correlations are classical (no Bell
violation possible), coarse-graining is lossy by construction, and
recall is a soft collapse. Full account in `DESIGN.md`.
