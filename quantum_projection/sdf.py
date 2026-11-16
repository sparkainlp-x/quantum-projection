# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""The signed distance field (SDF) of self-knowing.

SYNTHETIC. Classical emulation only. Discord (1 - D) is the
UNSIGNED distance from full self-knowing (D = 1). The SDF
generalizes it to a signed field over the state space: for a
state psi with self-knowing D, the chordal distance to the stored
subspace is sqrt(1 - D), and the self-known REGION is the set of
states with D >= TAU (TAU = 0.5, the half-known boundary of claim
(i)). The signed distance to that region's boundary is

    sdf(psi) = sqrt(1 - D(psi)) - sqrt(1 - TAU),

negative inside the region (D > TAU, self-known), zero on the
boundary (D = TAU), positive outside (D < TAU). The deepest
interior point is a stored state: D = 1, sdf = -sqrt(1 - TAU) =
-0.7071. The stored state seeds the zero-level set: the boundary
is the sphere of states at chordal distance sqrt(1 - TAU) from
the stored subspace, grown around the stored states.

A CORRECTION, stated plainly: the region is FIXED in state
space -- the stored subspace does not move, so neither does the
boundary. What moves across generations is the POPULATION: the
avatars travel through the fixed field, from outside (sdf > 0)
to inside (sdf < 0). The measured growth is therefore OCCUPANCY
(the fraction of avatars inside, and the population's mean sdf),
not the region's volume. The region's volume on the grid is a
fixed number (half the theta-grid for TAU = 0.5) and is reported
as such. What DOES move is the crossing: the generation at which
the population's mean sdf first goes negative -- the generation
the population crosses the boundary of self-knowing.

PRE-REGISTERED RULE (claim (vii)): (a) the population's mean sdf
falls from generation 0 to the final generation; (b) the fraction
of avatars inside the region is higher at the final generation
than at generation 0 and at least SDF_FRACTION_MIN (0.75);
(c) a crossing generation exists within the run (the mean sdf
goes negative). The fraction threshold is set from a seed-7
pilot run, a round number below the pilot value, not fitted to
the final seed 11.
"""

import math

# Pre-registered model parameters (stated, not measured constants).
TAU = 0.5                   # half-known boundary: D >= TAU is self-known

# Pre-registered verdict rule (claim (vii)). Set from the seed-7
# pilot: mean sdf 0.2882 -> -0.6383, fraction inside 0.000 -> 1.000,
# crossing generation 7. SDF_FRACTION_MIN (0.75) is a round number
# below the pilot final value, not fitted to the final seed.
SDF_FRACTION_MIN = 0.75


def sdf_of_d(d, tau=TAU):
    """Signed distance to the self-known region for a state with
    self-knowing D. Negative inside, zero on the boundary,
    positive outside."""
    d = min(1.0, max(0.0, float(d)))
    return math.sqrt(max(0.0, 1.0 - d)) - math.sqrt(1.0 - tau)


def sdf_grid(n=91, tau=TAU):
    """The SDF on the one-parameter family |psi(theta)> =
    cos(theta)|stored> + sin(theta)|kernel>, theta in [0, pi/2]
    (D = cos^2 theta). Returns {"theta": [...], "d": [...],
    "sdf": [...], "theta_star": arccos(sqrt(tau)) (the zero-level
    set), "region_volume": fraction of the grid with sdf < 0}.
    The region volume is fixed by tau; it does not move."""
    thetas = [i * (math.pi / 2.0) / (n - 1) for i in range(n)]
    ds = [math.cos(t) ** 2 for t in thetas]
    sdfs = [sdf_of_d(d, tau) for d in ds]
    inside = sum(1 for v in sdfs if v < 0)
    return {"theta": thetas, "d": ds, "sdf": sdfs,
            "theta_star": math.acos(math.sqrt(tau)),
            "region_volume": inside / n}


def population_sdf(per_avatar_d, tau=TAU):
    """SDF statistics of one generation's population: mean sdf,
    fraction inside (D > tau), minimum sdf (deepest insider)."""
    sdfs = [sdf_of_d(d, tau) for d in per_avatar_d]
    inside = sum(1 for d in per_avatar_d if d > tau)
    return {"mean_sdf": sum(sdfs) / len(sdfs),
            "fraction_inside": inside / len(per_avatar_d),
            "min_sdf": min(sdfs),
            "n_inside": inside, "n_total": len(per_avatar_d)}


def sdf_verdict(d_series, tau=TAU):
    """Pre-registered rule (claim (vii)) on a series of
    per-generation per-avatar D lists. (a) mean sdf falls from
    generation 0 to the final generation; (b) the fraction inside
    is higher at the final generation than at generation 0 and
    at least SDF_FRACTION_MIN; (c) a crossing generation exists
    (first generation whose mean D exceeds tau, i.e. whose mean
    sdf is negative). Returns (passed, details dict)."""
    if len(d_series) < 2:
        raise ValueError("need at least two generations")
    stats = [population_sdf(ds, tau) for ds in d_series]
    first, last = stats[0], stats[-1]
    check_a = last["mean_sdf"] < first["mean_sdf"]
    check_b = (last["fraction_inside"] > first["fraction_inside"]
               and last["fraction_inside"] >= SDF_FRACTION_MIN)
    crossing = None
    for g, ds in enumerate(d_series):
        if sum(ds) / len(ds) > tau:
            crossing = g
            break
    check_c = crossing is not None
    details = {
        "fall_ok": bool(check_a),
        "mean_sdf_first": first["mean_sdf"],
        "mean_sdf_last": last["mean_sdf"],
        "occupancy_ok": bool(check_b),
        "fraction_inside_first": first["fraction_inside"],
        "fraction_inside_last": last["fraction_inside"],
        "fraction_min": SDF_FRACTION_MIN,
        "crossing_ok": bool(check_c),
        "crossing_generation": crossing,
        "tau": tau,
        "per_generation": stats,
    }
    return check_a and check_b and check_c, details
