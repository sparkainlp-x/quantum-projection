# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the planetary-evolution measurements and rules."""

from quantum_projection import (planetary_run, planetary_verdict,
                                run_cascade)


def _recs(diversity, novelty, mean_energy, peak_energy=None):
    if peak_energy is None:
        peak_energy = [3] * len(diversity)
    return [{"diversity": d, "novelty": n, "mean_energy": e, "peak_energy": p}
            for d, n, e, p in zip(diversity, novelty, mean_energy, peak_energy)]


def test_planetary_verdict_logic():
    ok, det = planetary_verdict(_recs([8, 8, 4], [1.0, 0.2, 0.15],
                                      [3.0, 2.0, 2.0], [3, 2, 1]))
    assert ok is True
    assert det["energy_ratio"] == 2.0 / 3.0
    assert det["peak_energy_first"] == 3
    assert det["peak_energy_last"] == 1
    # Diversity floor breach
    ok, _ = planetary_verdict(_recs([8, 1, 4], [1.0, 0.2, 0.15],
                                    [3.0, 2.0, 2.0]))
    assert ok is False
    # Zero novelty breach
    ok, _ = planetary_verdict(_recs([8, 8, 4], [1.0, 0.0, 0.15],
                                    [3.0, 2.0, 2.0]))
    assert ok is False
    # Energy must fall by >= 25%
    ok, _ = planetary_verdict(_recs([8, 8, 4], [1.0, 0.2, 0.15],
                                    [3.0, 2.0, 2.4]))
    assert ok is False


def test_planetary_passes_on_the_registered_run():
    res = planetary_run()
    assert res["passed"], res["details"]
    assert res["details"]["min_diversity"] >= 2
    assert res["details"]["energy_ratio"] < 0.75
    assert res["details"]["peak_energy_first"] > res["details"]["peak_energy_last"]


def test_records_carry_the_spectrum():
    recs = run_cascade(n_avatars=3, generations=2, seed=5)
    for r in recs:
        assert 1.0 <= r["mean_energy"] <= 7.0
        assert 1 <= r["peak_energy"] <= 7
        assert r["diversity"] >= 1
        assert 0.0 <= r["novelty"] <= 1.0
