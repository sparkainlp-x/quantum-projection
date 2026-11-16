# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the infinite-creativity rules."""

from quantum_projection import creativity_run, creativity_verdict


def _recs(novelty, cumulative):
    return [{"novelty": n, "cumulative_distinct": c}
            for n, c in zip(novelty, cumulative)]


def test_creativity_verdict_logic():
    ok, det = creativity_verdict(_recs([1.0, 0.2, 0.1], [10, 12, 15]))
    assert ok is True
    assert det["mean_novelty"] == (0.2 + 0.1) / 2
    # Zero novelty breach
    ok, _ = creativity_verdict(_recs([1.0, 0.0, 0.1], [10, 12, 15]))
    assert ok is False
    # Non-increasing cumulative breach
    ok, _ = creativity_verdict(_recs([1.0, 0.2, 0.1], [10, 12, 12]))
    assert ok is False
    # Mean novelty floor breach
    ok, _ = creativity_verdict(_recs([1.0, 0.01, 0.01], [10, 12, 15]))
    assert ok is False


def test_creativity_passes_on_a_short_run():
    # Short run (10 generations) for speed; the full 50-generation
    # verdict is covered by test_unified.py.
    res = creativity_run(generations=10)
    assert res["passed"], res["details"]
    assert res["details"]["min_novelty"] > 0
    assert res["details"]["mean_novelty"] >= 0.05
