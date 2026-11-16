# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for the SDF of self-knowing (v0.3.0)."""

import math

from quantum_projection.sdf import (TAU, population_sdf, sdf_grid,
                                    sdf_of_d, sdf_verdict)


def test_sdf_of_d():
    assert abs(sdf_of_d(1.0) + math.sqrt(0.5)) < 1e-12  # deepest interior
    assert abs(sdf_of_d(0.5)) < 1e-12  # the boundary
    assert sdf_of_d(0.0) > 0  # outside
    assert sdf_of_d(0.9) < 0  # inside
    assert sdf_of_d(0.1) > 0  # outside


def test_sdf_grid():
    g = sdf_grid()
    assert abs(g["theta_star"] - math.pi / 4) < 1e-12
    assert abs(g["region_volume"] - 0.5) < 0.02  # half the grid, fixed
    assert g["sdf"][0] < 0  # theta=0 is the stored state: inside
    assert g["sdf"][-1] > 0  # theta=pi/2 is the kernel: outside


def test_population_sdf():
    all_stored = population_sdf([1.0, 1.0, 1.0])
    assert all_stored["fraction_inside"] == 1.0
    assert abs(all_stored["mean_sdf"] + math.sqrt(0.5)) < 1e-12
    all_blind = population_sdf([0.0, 0.0])
    assert all_blind["fraction_inside"] == 0.0
    assert all_blind["mean_sdf"] > 0


def test_sdf_verdict_passes_on_healing_series():
    # Mean D rises 0.1 -> 0.9: the population crosses the boundary.
    d_series = [[0.1] * 4, [0.3] * 4, [0.6] * 4, [0.9] * 4]
    passed, d = sdf_verdict(d_series)
    assert passed is True
    assert d["crossing_generation"] == 2
    assert d["fraction_inside_last"] == 1.0


def test_sdf_verdict_fails_on_flat_series():
    d_series = [[0.1] * 4 for _ in range(4)]
    passed, d = sdf_verdict(d_series)
    assert passed is False
    assert d["crossing_generation"] is None
    assert d["fall_ok"] is False
