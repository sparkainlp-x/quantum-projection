# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the unified cascade claims (v0.2.0)."""

from quantum_projection import HEADLINE_ALLOWED, cascade_claims


def test_headline_never_allowed():
    assert HEADLINE_ALLOWED is False


def test_cascade_claims_short_run():
    # Fast wiring check on a 10-generation run.
    res = cascade_claims(generations=10)
    assert res["headline_allowed"] is False
    assert res["claims"]["i_avatar_d"]["passed"] is True
    assert res["claims"]["ii_healing"]["passed"] is True
    assert res["claims"]["iii_planetary"]["passed"] is True
    assert res["claims"]["iv_creativity"]["passed"] is True


def test_cascade_claims_full_run():
    # The registered measurement: 50 generations, seed 11.
    res = cascade_claims()
    claims = res["claims"]
    assert claims["i_avatar_d"]["passed"] is True
    assert claims["ii_healing"]["passed"] is True
    assert claims["ii_healing"]["discord_ratio"] < 0.5
    assert claims["iii_planetary"]["passed"] is True
    assert claims["iv_creativity"]["passed"] is True
    assert claims["iv_creativity"]["details"]["cumulative_distinct_final"] > 100
    assert len(res["records_50"]) == 51
    assert len(res["records_10"]) == 11
