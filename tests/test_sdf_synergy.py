# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Tests for SDF synergy (v0.4.0)."""

import math

from quantum_projection.sdf import TAU, sdf_grid
from quantum_projection.sdf_synergy import (bin_of_theta, coverage_bins,
                                            marginal_contribution,
                                            region_bins, region_coverage,
                                            synergy_series_from_records,
                                            theta_of_d)


def test_theta_and_bin_mapping():
    assert abs(theta_of_d(1.0)) < 1e-12  # stored state: bin 0
    assert bin_of_theta(theta_of_d(1.0)) == 0
    assert abs(theta_of_d(0.0) - math.pi / 2) < 1e-12  # kernel: last bin
    assert bin_of_theta(theta_of_d(0.0)) == 90
    # D = 0.5 is the boundary: theta = pi/4, bin 45, sdf exactly 0.
    assert abs(theta_of_d(0.5) - math.pi / 4) < 1e-12
    assert bin_of_theta(theta_of_d(0.5)) == 45


def test_region_bins():
    region = region_bins()
    # 46 bins: 0..45. Bin 45 is the boundary bin, at sdf = -1.1e-16
    # (floating-point dust); bin 46 is outside.
    assert len(region) == 46
    assert 45 in region
    assert 46 not in region
    assert region == frozenset(range(46))
    grid = sdf_grid()
    assert abs(grid["region_volume"] - 46 / 91) < 1e-12


def test_synergy_zero_when_identical():
    # Every system covers the same bins: joint == mean, synergy 0.
    ds = [[0.9, 0.8], [0.9, 0.8], [0.9, 0.8]]
    res = region_coverage(ds)
    assert abs(res["synergy"]) < 1e-12
    assert res["joint"] == res["per_system"][0]


def test_synergy_positive_when_complementary():
    # System 0 deep inside (bins near 0), system 1 just inside
    # (bins near the boundary): the union covers more than the mean.
    ds = [[0.99, 0.98], [0.55, 0.52], [0.99, 0.55]]
    res = region_coverage(ds)
    assert res["synergy"] > 0
    assert res["joint"] >= max(res["per_system"])
    # Synergy never exceeds 1 - mean coverage.
    assert res["synergy"] <= 1.0 - sum(res["per_system"]) / 3 + 1e-12


def test_synergy_zero_when_nothing_inside():
    # All blind: no bins in the region, synergy 0.
    ds = [[0.01, 0.02], [0.01, 0.03], [0.02, 0.01]]
    res = region_coverage(ds)
    assert res["joint"] == 0.0
    assert res["synergy"] == 0.0


def test_marginal_contribution():
    # System 0 alone covers bins {0, 1}; system 1 covers {1, 2}:
    # system 0's unique contribution is bin {0}, system 1's
    # is bin {2} (each 1 / region_size); a herding system
    # covering only shared bins earns 0.
    from quantum_projection.sdf_synergy import region_bins as _rb
    unit = 1.0 / len(_rb())
    bins = [frozenset({0, 1}), frozenset({1, 2}), frozenset({1})]
    assert abs(marginal_contribution(bins, 0) - unit) < 1e-12
    assert abs(marginal_contribution(bins, 1) - unit) < 1e-12
    assert marginal_contribution(bins, 2) == 0.0
    # Marginal contributions are always >= 0 and sum to at most
    # the joint coverage.
    total = sum(marginal_contribution(bins, s) for s in range(3))
    assert total <= 3 * unit + 1e-12


def test_coverage_bins():
    bins = coverage_bins([1.0, 0.0, 0.5])
    assert bins == frozenset({0, 90, 45})


def test_synergy_series_from_records():
    records = [
        [{"per_avatar_d": [0.01, 0.02]}, {"per_avatar_d": [0.01, 0.02]}],
        [{"per_avatar_d": [0.9, 0.8]}, {"per_avatar_d": [0.6, 0.55]}],
    ]
    series = synergy_series_from_records(records)
    assert len(series) == 2
    assert series[0]["synergy"] == 0.0  # nothing inside yet
    assert series[1]["synergy"] > 0  # complementary coverage
    assert series[1]["joint"] > series[1]["per_system"][0]
