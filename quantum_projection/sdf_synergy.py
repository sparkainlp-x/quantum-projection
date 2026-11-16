# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""SDF synergy: what the solar systems cover together that no
one of them covers alone.

SYNTHETIC. Classical emulation only. SDF synergy is a defined
quantity in this model, not a claim about real synergy.

DEFINITION, stated before measuring. The v0.3.0 SDF puts every
avatar at an angle theta = arccos(sqrt(D)) on the one-parameter
family |psi(theta)> = cos(theta)|stored> + sin(theta)|kernel>,
theta in [0, pi/2]; the self-known REGION is the set of states
with D > TAU (TAU = 0.5), i.e. theta < pi/4. On the 91-point
grid of sdf_grid, the region is the 45 bins with sdf < 0.

An avatar occupies the grid bin nearest its theta. A system's
INSIDE-COVERAGE is the fraction of the region's bins occupied
by at least one of its avatars; the JOINT inside-coverage is
the fraction occupied by the union over all systems. SDF
synergy is

    synergy = joint_coverage - mean(per-system coverage).

It is >= 0 always (the union contains every system's bins, so
the joint coverage is at least the largest per-system coverage,
hence at least the mean), and 0 exactly when every system
covers the same bins. It is positive when the systems cover
COMPLEMENTARY parts of the self-known region: together they
span more of it than any one of them, or than their average.

FLOATING-POINT NOTE. On the 91-point grid the region is the
bins with sdf < 0 as computed: 46 of 91, because the boundary
bin 45 sits at sdf = -1.1e-16 (floating-point dust at
theta = pi/4). The region is defined by the computed grid, so
every coverage fraction in this module uses the same 46 bins;
the one-bin difference from the ideal 45 is immaterial to
synergy, which is a difference of coverages.

A READING, stated plainly. "Inside-fraction of the self-known
region" is read here as the fraction of the REGION that is
occupied, not the fraction of avatars inside it: the pooled
avatar fraction is identically the mean of the per-system
fractions when all systems have the same size, so that reading
makes synergy zero by construction and the game degenerate.
The coverage reading keeps the joint-minus-mean shape of the
definition and is non-degenerate: it measures complementary
occupation of the self-known region.

PAYOFFS. Each synergy agent's payoff is its system's MARGINAL
contribution to the joint inside-coverage (leave-one-out, the
same shape as the v0.3.0 coupling): payoff_s = joint(all) -
joint(all except s). It is >= 0 (removing a system cannot grow
the union) and it rewards a system for covering parts of the
region no other system covers. A system that herds -- covering
only bins others already cover -- earns 0.
"""

import math

from .sdf import TAU, sdf_grid

# Pre-registered model parameters (stated, not measured constants).
SDF_GRID_N = 91              # grid points of the SDF theta family
SYNERGY_SYSTEMS = 3          # solar systems in the registered run
SYNERGY_AVATARS = 8          # avatars per system (same as v0.2.0)


def region_bins(n=SDF_GRID_N, tau=TAU):
    """Grid indices inside the self-known region (sdf < 0).
    Fixed by tau; the region does not move (v0.3.0 correction)."""
    grid = sdf_grid(n=n, tau=tau)
    return frozenset(i for i, v in enumerate(grid["sdf"]) if v < 0)


def theta_of_d(d):
    """Angle of a state with self-knowing D on the SDF family:
    D = cos^2(theta), so theta = arccos(sqrt(D))."""
    d = min(1.0, max(0.0, float(d)))
    return math.acos(math.sqrt(d))


def bin_of_theta(theta, n=SDF_GRID_N):
    """Nearest grid bin of an angle theta in [0, pi/2]."""
    theta = min(math.pi / 2.0, max(0.0, float(theta)))
    return int(round(theta / (math.pi / 2.0) * (n - 1)))


def coverage_bins(per_avatar_d, n=SDF_GRID_N):
    """The set of grid bins occupied by a population (one bin per
    avatar, by its D)."""
    return frozenset(bin_of_theta(theta_of_d(d), n)
                     for d in per_avatar_d)


def region_coverage(per_system_ds, n=SDF_GRID_N, tau=TAU):
    """SDF synergy of one generation's population.

    per_system_ds: a list (one per system) of per-avatar D lists.
    Returns {"per_system": [...], "joint": float, "synergy":
    float, "region_size": int, ...}. per_system[i] is system i's
    inside-coverage; joint is the union's inside-coverage;
    synergy = joint - mean(per_system), always >= 0 (up to
    float rounding)."""
    region = region_bins(n=n, tau=tau)
    size = len(region)
    per_system_bins = [coverage_bins(ds, n) for ds in per_system_ds]
    per_system = [len(b & region) / size for b in per_system_bins]
    joint_bins = frozenset().union(*per_system_bins) if per_system_bins else frozenset()
    joint = len(joint_bins & region) / size
    mean = sum(per_system) / len(per_system) if per_system else 0.0
    return {
        "per_system": per_system,
        "joint": joint,
        "synergy": joint - mean,
        "region_size": size,
        "per_system_bins": per_system_bins,
        "joint_bins": joint_bins,
    }


def marginal_contribution(per_system_bins, system, n=SDF_GRID_N,
                          tau=TAU):
    """System `system`'s marginal contribution to the joint
    inside-coverage: joint(all) - joint(all except `system`).
    Always >= 0. The payoff of a synergy agent."""
    region = region_bins(n=n, tau=tau)
    size = len(region)
    joint_all = frozenset().union(*per_system_bins) if per_system_bins else frozenset()
    others = [b for i, b in enumerate(per_system_bins) if i != system]
    joint_others = frozenset().union(*others) if others else frozenset()
    return (len(joint_all & region) - len(joint_others & region)) / size


def synergy_series_from_records(records):
    """Per-generation synergy from run_solar_systems records:
    records[g] is a list of per-system records carrying
    per_avatar_d. Returns a list of region_coverage dicts."""
    out = []
    for recs in records:
        per_system_ds = [r["per_avatar_d"] for r in recs]
        out.append(region_coverage(per_system_ds))
    return out
