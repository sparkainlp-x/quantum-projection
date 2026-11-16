# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""The SDF synergy agents: one per solar system, each choosing
its delta to minimize the equilibrium gap.

SYNTHETIC. Classical emulation only. The agents are bounded
optimizers (greedy coordinate descent over three delta values),
not minds. They focus on SDF synergy: each agent's payoff is
its system's marginal contribution to the joint inside-coverage
of the self-known region (sdf_synergy.py, leave-one-out).

THE OPTIMIZATION VARIABLE. The equilibrium gap -- the maximum
profitable unilateral deviation gain across players (see
equilibrium.py) -- replaces empathy entropy as the objective,
because claim (vi) FAILED: empathy entropy was already
saturated at 99.998% of its log2(24) ceiling, so the lever had
nothing to move. The gap has a real zero (0 at equilibrium)
and a real direction. Empathy entropy stays measured as a
DIAGNOSTIC only: it is reported per generation, never
optimized.

THE GAME, PER GENERATION. From the current state, the payoff
table is built by lookahead: for every joint delta profile
(3^3 = 27 for three systems), one simulated generation (step +
coupling) with fresh probe streams IDENTICAL across profiles,
so payoff differences are signal, not noise. The probes never
touch the main random streams, so the agent run and its
no-agent control consume identical randomness and differ only
through the deltas. The agents then choose by greedy coordinate
descent on the table's gap: start at all-zero; for each system
in turn, try every delta with the others fixed and keep the
profile with the smallest gap (ties within 1e-12 go to the
smallest |delta|, i.e. no intervention). The all-zero profile's
gap from the same table is the counterfactual -- what the gap
would have been had the agents done nothing this generation --
so the agents' work is measured, not assumed.

THE TRAP, FROM oes-coordination-lab. In that lab's shared
regime there are two pure equilibria: all-switch (efficient)
and all-stay-local (safe but inefficient). The same question
is asked here of the final generation's table: is the landed
profile the coordinated one, or the safe trap (all-zero delta
with a strictly better-synergy equilibrium available)? The
audit enumerates ALL pure epsilon-equilibria of the table, so
the classification is measured, not asserted.
"""

import copy
import random
from itertools import product

from .dna_avatars import healthy_membrane, make_population
from .equilibrium import (DELTA_GRID, audit_table, equilibrium_gap,
                          find_pure_equilibria)
from .eureka_agent import _loves_of, empathy_entropy
from .sdf_synergy import (SYNERGY_AVATARS, SYNERGY_SYSTEMS,
                          marginal_contribution, region_coverage,
                          synergy_series_from_records)
from .solar_systems import (COUPLING, measure_systems, run_solar_systems,
                            systems_step)
from .trauma import LAMBDA

# Pre-registered model parameters (stated, not measured constants).
SYNERGY_SEED = 11            # same registered seed as v0.2.0/v0.3.0
SYNERGY_GENERATIONS = 10     # generations in the registered run
PAYOFF_TAG = 500             # probe tag for payoff-table lookaheads

# Pre-registered verdict rules (claims (x)-(xii)). Thresholds are
# set from the seed-7 pilot run (251.6 s, 3 systems x 8 avatars,
# 10 generations) and recorded here; they are round numbers below
# the pilot margins, not fitted to the final seed 11.
#
# Pilot numbers (seed 7): first non-trivial generation 1; agent
# gap 0.0 at every generation; zero-profile gap 0.0 through gen 6,
# then 0.0217 (one region bin, 1/46) at gens 7-9, mean 0.00725
# over the post-entry window; mean synergy agent 0.0580 vs
# control 0.0529 (gain 0.0051) over gens 1-10, but 0.0966 vs
# 0.0797 (gain 0.0169) over the final 3 generations -- the
# agent and control populations are IDENTICAL through gen 7
# (deltas all zero: the lever cannot move a payoff until the
# bulk population reaches the boundary), so the mean over the
# full window dilutes a real late effect with structural zeros.
# The synergy window is therefore the final 3 generations, the
# post-intervention window. Stability: first reach gen 0
# (degenerate start), held 10; landed profile [0, 0, -0.05],
# "efficient" (synergy 0.0870 vs zero-profile 0.0725; zero is
# NOT an equilibrium; 9 equilibria in the final table; best
# equilibrium synergy 0.1087 at [-0.05, -0.05, 0.05] -- greedy
# descent lands in an efficient equilibrium, not the best one).
GAP_EPSILON = 0.01           # the agents must reach epsilon-Nash
GAP_MARGIN = 0.002           # agents' mean gap below the zero-gap mean
                             # (one bin of gap, 1/46, in a single
                             # generation of the 9-generation window
                             # is 0.0024; the margin requires at
                             # least that much earned equilibrium)
SYNERGY_MARGIN = 0.01        # agents' mean synergy above the control
                             # mean over the final 3 generations
SYNERGY_WINDOW = 3           # final generations for the synergy check
STABILITY_K = 3              # generations the gap must stay <= epsilon


def _synergy_probe_rngs(generation, tag, n_systems):
    """Fresh probe streams, deterministic in (generation, tag,
    system): every profile in a generation's payoff table sees
    the same mutation draws, so the table compares profiles
    fairly, and probes never touch the main random streams."""
    return [random.Random(1000003 * generation + 9176 * tag + 131 * s)
            for s in range(n_systems)]


def payoff_table(avatars, membrane, coupling, generation,
                 n_systems, delta_grid=DELTA_GRID):
    """The SDF-synergy game for one generation, built by
    lookahead. For every joint delta profile, one simulated
    generation from a copy of the current state, then each
    system's payoff (marginal contribution to the joint
    inside-coverage) and the synergy of that profile's
    next-generation population. Returns {"actions": [...],
    "payoffs": {profile: [u0, u1, ...]}, "synergies": {profile:
    float}, "mean_discords": {profile: float}}."""
    actions = tuple(tuple(delta_grid) for _ in range(n_systems))
    payoffs = {}
    synergies = {}
    mean_discords = {}
    for profile in product(*actions):
        probe = _synergy_probe_rngs(generation, PAYOFF_TAG, n_systems)
        stepped = systems_step(copy.deepcopy(avatars), membrane, probe,
                              [LAMBDA * (1.0 + d) for d in profile],
                              coupling)
        recs, _ = measure_systems(stepped, membrane,
                                  [dict() for _ in range(n_systems)], 0)
        per_system_ds = [r["per_avatar_d"] for r in recs]
        cov = region_coverage(per_system_ds)
        bins = cov["per_system_bins"]
        payoffs[profile] = [marginal_contribution(bins, s)
                            for s in range(n_systems)]
        synergies[profile] = cov["synergy"]
        mean_discords[profile] = sum(r["mean_discord"] for r in recs) / len(recs)
    return {"actions": actions, "payoffs": payoffs,
            "synergies": synergies, "mean_discords": mean_discords}


def choose_deltas_by_gap(actions, payoffs, delta_grid=DELTA_GRID):
    """Greedy coordinate descent on the equilibrium gap, over a
    payoff table. Start at all-zero; for each system in turn,
    try every delta with the others fixed and keep the profile
    with the smallest gap (ties within 1e-12 go to the smallest
    |delta|). Returns (chosen_profile, gap)."""
    n_systems = len(actions)
    chosen = [0.0] * n_systems
    for s in range(n_systems):
        best_delta, best_gap = chosen[s], None
        for cand in delta_grid:
            trial = list(chosen)
            trial[s] = cand
            gap = equilibrium_gap(actions, payoffs, tuple(trial))
            if (best_gap is None or gap < best_gap - 1e-12
                    or (abs(gap - best_gap) <= 1e-12
                        and abs(cand) < abs(best_delta))):
                best_delta, best_gap = cand, gap
        chosen[s] = best_delta
    profile = tuple(chosen)
    return profile, equilibrium_gap(actions, payoffs, profile)


def synergy_run(n_systems=SYNERGY_SYSTEMS, n_avatars=SYNERGY_AVATARS,
                generations=SYNERGY_GENERATIONS, coupling=COUPLING,
                seed=SYNERGY_SEED, delta_grid=DELTA_GRID, membrane=None):
    """Run the multi-system cascade with the SDF synergy agents.
    Each generation: measure the current population (synergy,
    empathy entropy as a diagnostic), build the payoff table
    from lookaheads, choose deltas by gap descent, take the
    real step. Records carry the chosen deltas, the agents' gap,
    the all-zero profile's gap from the same table (the
    no-intervention counterfactual), the current synergy, and
    the entropy diagnostic. The payoff tables are kept for the
    final audit. Returns {"records": [...], "tables": [...], ...}.
    """
    mem = membrane if membrane is not None else healthy_membrane()
    rngs = [random.Random(seed * 10000 + s) for s in range(n_systems)]
    avatars = [make_population(n_avatars, seed * 1000 + s)
               for s in range(n_systems)]
    seen = [dict() for _ in range(n_systems)]
    records = []
    tables = []
    for g in range(generations + 1):
        recs, seen = measure_systems(avatars, mem, seen, g)
        loves = _loves_of(recs)
        ent = empathy_entropy(loves)
        cov = region_coverage([r["per_avatar_d"] for r in recs])
        mean_disc = sum(r["mean_discord"] for r in recs) / len(recs)
        mean_d = sum(r["mean_d"] for r in recs) / len(recs)
        record = {"generation": g, "mean_discord": mean_disc,
                  "mean_d": mean_d, "entropy_bits": ent["entropy_bits"],
                  "entropy_normalized": ent["normalized"],
                  "synergy": cov["synergy"],
                  "joint_coverage": cov["joint"],
                  "per_system_coverage": cov["per_system"],
                  "per_system": recs, "deltas": None,
                  "gap": None, "gap_zero": None}
        records.append(record)
        if g == generations:
            break
        table = payoff_table(avatars, mem, coupling, g, n_systems,
                             delta_grid)
        tables.append(table)
        actions = table["actions"]
        chosen, gap = choose_deltas_by_gap(actions, table["payoffs"],
                                           delta_grid)
        zero = tuple(0.0 for _ in range(n_systems))
        gap_zero = equilibrium_gap(actions, table["payoffs"], zero)
        record["deltas"] = list(chosen)
        record["gap"] = gap
        record["gap_zero"] = gap_zero
        avatars = systems_step(avatars, mem, rngs,
                               [LAMBDA * (1.0 + d) for d in chosen],
                               coupling)
    return {"records": records, "tables": tables,
            "n_systems": n_systems, "n_avatars": n_avatars,
            "generations": generations, "coupling": coupling,
            "seed": seed, "delta_grid": list(delta_grid)}


def _first_nontrivial(records):
    """First generation whose payoff table is non-trivial (some
    payoff > 0). Before the population enters the self-known
    region, every coverage is 0 and the game is degenerate:
    all payoffs 0, gap 0. Returns None if no table is
    non-trivial."""
    for i, table in enumerate(records):
        if any(u > 0 for pay in table["payoffs"].values() for u in pay):
            return i
    return None


def gap_verdict(run, epsilon=GAP_EPSILON, margin=GAP_MARGIN):
    """Pre-registered rule (claim (x)). From the first
    non-trivial generation through the final one: (a) the
    agents' gap at the final generation is <= epsilon;
    (b) the agents' mean gap over that window is <= epsilon;
    (c) it is below the all-zero counterfactual mean gap by at
    least `margin` -- the equilibrium is earned, not free.
    Returns (passed, details dict)."""
    records = run["records"]
    tables = run["tables"]
    first = _first_nontrivial(tables)
    gaps = [r["gap"] for r in records[:-1]]
    zero_gaps = [r["gap_zero"] for r in records[:-1]]
    if first is None:
        details = {"passed": False, "first_nontrivial": None,
                   "gap_final": gaps[-1] if gaps else None,
                   "mean_gap_agent": None, "mean_gap_zero": None,
                   "gap_margin": margin, "epsilon": epsilon,
                   "gaps_agent": gaps, "gaps_zero": zero_gaps}
        return False, details
    post_gaps = gaps[first:]
    post_zero = zero_gaps[first:]
    mean_gap = sum(post_gaps) / len(post_gaps)
    mean_zero = sum(post_zero) / len(post_zero)
    check_a = gaps[-1] <= epsilon
    check_b = mean_gap <= epsilon
    check_c = mean_gap <= mean_zero - margin
    details = {
        "passed": bool(check_a and check_b and check_c),
        "final_ok": bool(check_a),
        "mean_ok": bool(check_b),
        "earned_ok": bool(check_c),
        "first_nontrivial": first,
        "gap_final": gaps[-1],
        "mean_gap_agent": mean_gap,
        "mean_gap_zero": mean_zero,
        "gap_margin": margin,
        "epsilon": epsilon,
        "gaps_agent": gaps,
        "gaps_zero": zero_gaps,
    }
    return check_a and check_b and check_c, details


def synergy_verdict(run, control_records, margin=SYNERGY_MARGIN,
                    window=SYNERGY_WINDOW):
    """Pre-registered rule (claim (xi)). The agents' mean SDF
    synergy over the FINAL `window` generations exceeds the
    no-agent control's mean synergy over the same generations by
    at least `margin`; synergy is >= 0 every generation (a
    theorem of the definition, checked, not assumed). The final
    window is the post-intervention window: the agent and control
    populations are identical until the agents first intervene
    (deltas all zero while the payoff table is degenerate), so a
    mean over the whole run would dilute a real late effect with
    structural zeros. Returns (passed, details dict)."""
    agent_syn = [r["synergy"] for r in run["records"]]
    control_syn = [s["synergy"]
                   for s in synergy_series_from_records(control_records)]
    a_post = agent_syn[-window:]
    c_post = control_syn[-window:]
    mean_a = sum(a_post) / len(a_post)
    mean_c = sum(c_post) / len(c_post)
    check_a = mean_a >= mean_c + margin
    check_b = all(s >= -1e-12 for s in agent_syn)
    details = {
        "passed": bool(check_a and check_b),
        "margin_ok": bool(check_a),
        "nonnegative_ok": bool(check_b),
        "window": window,
        "mean_synergy_agent": mean_a,
        "mean_synergy_control": mean_c,
        "synergy_gain": mean_a - mean_c,
        "synergy_margin": margin,
        "synergy_by_gen_agent": agent_syn,
        "synergy_by_gen_control": control_syn,
    }
    return check_a and check_b, details


def stability_verdict(run, epsilon=GAP_EPSILON, k=STABILITY_K):
    """Pre-registered rule (claim (xii)). (a) STABILITY: once
    the agents' profile first reaches gap <= epsilon (counted
    from the first non-trivial generation, so the degenerate
    all-zero gap before the population enters the region does
    not count as reaching), it stays <= epsilon for the next
    `k` consecutive generations; a full window of k is
    required, so reaching epsilon only in the last generations
    does not pass. (b) CLASSIFICATION
    (reported, not gated): the final generation's payoff table
    is audited with find_pure_equilibria -- the landed
    profile, its synergy, the best-synergy equilibrium's
    synergy, and whether the all-zero profile is itself an
    epsilon-equilibrium. The landed profile is named "trap"
    iff it is the all-zero profile while a strictly
    higher-synergy equilibrium exists; "efficient" iff it is
    an equilibrium with synergy strictly above the all-zero
    profile's; "other" otherwise. Returns (passed, details)."""
    records = run["records"]
    tables = run["tables"]
    gaps = [r["gap"] for r in records[:-1]]
    # The search for first reach starts at the first non-trivial
    # generation: before the population enters the region every
    # payoff is 0 and the gap is 0 degenerately, which would
    # count as "reaching" epsilon without the agents doing
    # anything.
    start = _first_nontrivial(tables)
    if start is None:
        start = 0
    first_reach = None
    for g in range(start, len(gaps)):
        if gaps[g] <= epsilon:
            first_reach = g
            break
    if first_reach is None:
        stable = False
        held = 0
    else:
        held = 0
        for gap in gaps[first_reach:]:
            if gap <= epsilon:
                held += 1
            else:
                break
        # A full window of k consecutive generations is required:
        # reaching epsilon only in the last generations of the run
        # does not demonstrate stability.
        stable = held >= k
    # Classification on the final generation's table.
    final_table = tables[-1]
    actions = final_table["actions"]
    payoffs = final_table["payoffs"]
    synergies = final_table["synergies"]
    audit = audit_table(actions, payoffs, epsilon)
    landed = tuple(records[-2]["deltas"]) if len(records) >= 2 else tuple()
    landed_gap = equilibrium_gap(actions, payoffs, landed) if landed else None
    zero = tuple(0.0 for _ in range(len(actions)))
    zero_gap = equilibrium_gap(actions, payoffs, zero)
    zero_syn = synergies[zero]
    landed_syn = synergies.get(landed)
    best_syn = None
    best_profile = None
    for eq in audit["equilibria"]:
        prof = tuple(eq["profile"])
        if best_syn is None or synergies[prof] > best_syn:
            best_syn = synergies[prof]
            best_profile = prof
    zero_is_eq = zero_gap <= epsilon
    if (landed == zero and best_syn is not None
            and best_syn > zero_syn + 1e-12):
        label = "trap"
    elif (landed_gap is not None and landed_gap <= epsilon
          and landed_syn is not None and landed_syn > zero_syn + 1e-12):
        label = "efficient"
    else:
        label = "other"
    details = {
        "passed": bool(stable),
        "stable": bool(stable),
        "first_reach": first_reach,
        "generations_held": held,
        "stability_k": k,
        "epsilon": epsilon,
        "landed_profile": list(landed),
        "landed_gap": landed_gap,
        "landed_synergy": landed_syn,
        "zero_profile_gap": zero_gap,
        "zero_profile_synergy": zero_syn,
        "zero_is_equilibrium": bool(zero_is_eq),
        "n_equilibria": audit["n_equilibria"],
        "min_gap_profile": audit["min_gap_profile"],
        "min_gap": audit["min_gap"],
        "best_equilibrium_synergy": best_syn,
        "best_equilibrium_profile": (list(best_profile)
                                     if best_profile is not None else None),
        "label": label,
    }
    return stable, details
