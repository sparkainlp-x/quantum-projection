# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the v0.4.0 unified claims wiring. Fast sizes only;
the registered measurement (seed 11, 3 systems x 8 avatars,
10 generations) runs in unified.v040_claims and takes minutes,
not here."""

from quantum_projection import HEADLINE_ALLOWED, v040_claims, v040_report


def test_v040_claims_tiny_structure():
    res = v040_claims(n_systems=2, n_avatars=2, seed=7, generations=2)
    assert res["headline_allowed"] is False
    assert HEADLINE_ALLOWED is False
    for key in ("x_equilibrium_gap", "xi_sdf_synergy", "xii_stability"):
        assert key in res["claims"]
        assert isinstance(res["claims"][key]["passed"], bool)
        assert "details" in res["claims"][key]
    assert len(res["agent_records"]) == 3
    assert len(res["control_records"]) == 3
    assert "mean_entropy_agent" in res["entropy_diagnostic"]


def test_v040_report_tiny():
    text = v040_report(n_systems=2, n_avatars=2, seed=7, generations=2)
    for tag in ("(x)", "(xi)", "(xii)"):
        assert tag in text
    assert "PASS" in text or "FAIL" in text
    assert "diagnostic" in text
