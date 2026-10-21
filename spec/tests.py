"""Tests for quantum-projection. Run: python tests.py"""

from qsim import (zero, apply_1q, apply_cnot, H, X, bell_phi_plus,
                  bell_phi_minus, noisy, normalize, fidelity)
from qmembrane import HolographicMembrane, KetBraPair, coarse_grain, overlap

SQRT1_2 = 2 ** -0.5


def test_gates():
    plus = apply_1q(zero(1), 1, 0, H)
    assert abs(plus[0] - SQRT1_2) < 1e-12 and abs(plus[1] - SQRT1_2) < 1e-12
    one = apply_1q(zero(1), 1, 0, X)
    assert abs(one[1] - 1) < 1e-12
    bell = bell_phi_plus()
    assert abs(bell[0] - SQRT1_2) < 1e-12 and abs(bell[3] - SQRT1_2) < 1e-12
    assert abs(bell[1]) < 1e-12 and abs(bell[2]) < 1e-12


def test_orthonormal_projection_exact():
    mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus()])
    r = mem.project(bell_phi_minus())
    assert r["winner"] == 1
    assert abs(abs(r["overlaps"][1]) - 1.0) < 1e-12
    assert abs(r["overlaps"][0]) < 1e-12
    assert abs(sum(r["probs"]) - 1.0) < 1e-12


def test_noisy_recall_fidelity():
    mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus()])
    fids = []
    for seed in range(5):
        probe = noisy(bell_phi_plus(), 0.15, seed=seed)
        final, winner, _ = mem.recall(probe)
        assert winner == 0  # correct pattern chosen, every draw
        fids.append(fidelity(final, bell_phi_plus()))
    assert sum(fids) / len(fids) > 0.90


def test_ket_bra_matches_direct():
    kets = [bell_phi_plus(), bell_phi_minus()]
    pair = KetBraPair(kets)
    mem = HolographicMembrane(kets)
    probe = noisy(bell_phi_plus(), 0.15, seed=8)
    r1, r2 = pair.project(probe), mem.project(probe)
    assert r1["winner"] == r2["winner"]
    for a, b in zip(r1["overlaps"], r2["overlaps"]):
        assert abs(abs(a) - abs(b)) < 1e-12


def test_coarse_grain_norm_and_recall():
    from qsim import ghz
    g = ghz(3)
    cg = coarse_grain(g)
    assert len(cg) == 4
    assert abs(sum(abs(c) ** 2 for c in cg) - 1.0) < 1e-12
    mem = HolographicMembrane([cg])
    r = mem.project(coarse_grain(noisy(g, 0.2, seed=4)))
    assert abs(r["overlaps"][0]) > 0.85


def test_probs_sum_to_one():
    mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus(),
                               noisy(bell_phi_plus(), 0.5, seed=1)])
    r = mem.project(noisy(bell_phi_plus(), 0.3, seed=2))
    assert abs(sum(r["probs"]) - 1.0) < 1e-12


if __name__ == "__main__":
    for name, fn in sorted(
            [(k, v) for k, v in globals().items() if k.startswith("test_")]):
        fn()
        print(f"PASS {name}")
    print("all tests passed")
