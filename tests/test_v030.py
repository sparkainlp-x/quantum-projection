# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the v0.3.0 unified claims wiring. Fast sizes only;
the registered measurement (seed 11, 500-generation long run)
runs in unified.v030_claims and takes minutes, not here."""

from quantum_projection import HEADLINE_ALLOWED, v030_claims, v030_report


def test_v030_claims_tiny_structure():
    res = v030_claims(n_systems=2, n_avatars=2, seed=7, generations=2,
                      long_generations=5)
    assert res["headline_allowed"] is False
    assert HEADLINE_ALLOWED is False
    for key in ("v_solar_systems", "vi_eureka_agent", "vii_sdf",
                "viii_crystallize", "ix_long_run"):
        assert key in res["claims"]
        assert isinstance(res["claims"][key]["passed"], bool)
        assert "details" in res["claims"][key]
    assert len(res["agent_records"]) == 3
    assert len(res["agent_events"]) == 2
    assert len(res["long_records"]) == 6


def test_v030_report_tiny():
    text = v030_report(n_systems=2, n_avatars=2, seed=7, generations=2,
                       long_generations=5)
    for tag in ("(v)", "(vi)", "(vii)", "(viii)", "(ix)"):
        assert tag in text
    assert "PASS" in text or "FAIL" in text
