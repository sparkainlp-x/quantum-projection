# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the long run (v0.3.0). Fast sizes only; the registered
500-generation measurement runs in unified.v030_claims, not here."""

from quantum_projection.longrun import creativity_horizon, long_run


def test_creativity_horizon_found():
    records = [{"novelty": 0.1}] * 5 + [{"novelty": 0.0}] * 12
    assert creativity_horizon(records, window=10) == 5


def test_creativity_horizon_not_reached():
    records = [{"novelty": 0.1}] * 20
    assert creativity_horizon(records, window=10) is None
    records = [{"novelty": 0.1}] * 5 + [{"novelty": 0.0}] * 9
    assert creativity_horizon(records, window=10) is None


def test_long_run_small_structure():
    res = long_run(n_avatars=2, generations=5, seed=7)
    assert len(res["records"]) == 6
    assert isinstance(res["passed"], bool)
    for key in ("novelty_final", "discord_final",
                "cumulative_distinct_final", "cumulative_distinct_gen50",
                "creativity_horizon", "generations", "seed"):
        assert key in res["details"]
    # Gen 50 does not exist in a 5-generation run: the gen-50
    # comparison reads the last record. (The registered 500-gen
    # run has a real generation 50.)
    assert res["details"]["cumulative_distinct_gen50"] == \
        res["records"][5]["cumulative_distinct"]
