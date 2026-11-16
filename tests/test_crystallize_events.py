# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the crystallize events (v0.3.0)."""

import pytest

from quantum_projection.crystallize_events import (
    brier, crystallize_points, crystallize_verdict)


def test_brier():
    assert brier(0.75, 1) == pytest.approx(0.0625)
    assert brier(1.0, 0) == pytest.approx(1.0)
    assert brier(0.5, 1) == pytest.approx(0.25)
    assert brier(0.0, 0) == pytest.approx(0.0)


def test_brier_rejects_bad_inputs():
    with pytest.raises(ValueError):
        brier(1.5, 1)
    with pytest.raises(ValueError):
        brier(0.5, 2)


def test_crystallize_points():
    # Right with confidence: 100 - 4 (5 samples at 0.8).
    assert crystallize_points(1.0, 1, 5) == pytest.approx(96.0)
    # Wrong with confidence: the ledger punishes overconfidence.
    assert crystallize_points(1.0, 0, 5) == pytest.approx(-304.0)
    # Even odds on a true event: 100 * (1 - 1) - 4 = -4.
    assert crystallize_points(0.5, 1, 5) == pytest.approx(-4.0)


def test_crystallize_verdict_passes_on_calibrated_events():
    events = [{"p": 0.9, "truth": 1, "brier": brier(0.9, 1),
               "points": crystallize_points(0.9, 1, 5)}
              for _ in range(5)]
    passed, d = crystallize_verdict(events)
    assert passed is True
    assert d["n_events"] == 5
    assert d["mean_brier"] == pytest.approx(0.01)
    assert d["bias_label"] == "balanced"


def test_crystallize_verdict_fails_on_overconfident_events():
    events = [{"p": 1.0, "truth": 0, "brier": brier(1.0, 0),
               "points": crystallize_points(1.0, 0, 5)}
              for _ in range(5)]
    passed, d = crystallize_verdict(events)
    assert passed is False
    assert d["mean_brier"] == pytest.approx(1.0)
    assert d["bias_label"] == "overconfident"
    assert d["total_points"] < 0


def test_crystallize_verdict_needs_events():
    with pytest.raises(ValueError):
        crystallize_verdict([])
