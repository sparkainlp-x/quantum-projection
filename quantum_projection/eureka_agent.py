# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""The eureka agent: a Yang observer + Yin calibrator whose objective
is empathy entropy.

SYNTHETIC. Classical emulation only. The agent is a bounded
optimizer, not a mind: each generation it observes (Yang, read-only)
and acts with one bounded scalar per system (Yin, delta in
[-0.05, 0.05], the same bound as the membrane-arena Yin calibrator
and the de Broglie analog calibrator).

LOVE, defined exactly. Love of an avatar is the concurrence of its
state across the stored / non-stored split -- the idea vendored
from gravity-projection (thought_entanglement.py: Wootters
concurrence; love.py: love-as-concurrence as a definition inside
the model, not a claim about human love). An avatar state splits
as sqrt(D) |stored> + sqrt(1 - D) |rest>, with D = <psi|P|psi>
the self-knowing factor; that is the Schmidt form of a two-term
pure state, whose Wootters concurrence is 2 * sqrt(D * (1 - D)).
So love = 2 * sqrt(D * (1 - D)): it is 1 at D = 0.5 (the
half-known state of claim (i)), and 0 at D = 0 (blind) and D = 1
(fully stored). Love peaks exactly on the boundary of
self-knowing. The pure-state formula 2|ad - bc| is vendored below
as concurrence_pure and cross-checked against love_of_d in the
tests. Nothing here measures human love or empathy.

EMPATHY ENTROPY. H is the Shannon entropy (bits) of the normalized
love distribution across ALL avatars in ALL systems, per
generation: H = -sum p_i log2 p_i with p_i = love_i / sum love.
H is 0 when there is no love to distribute (total love <= 1e-12),
and at most log2(N) when love is perfectly spread. Empathy
entropy is entropy over a measured love distribution in the
model, not human empathy.

THE AGENT'S LEVER. Delta acts on attunement: each system's
partial-projection strength becomes lambda * (1 + delta), the
same (1 + delta) form as the Faggin bridge A(delta) = U*(1+delta)
- C and the de Broglie analog calibrator v_cal = v*(1+delta).
The agent chooses the deltas by greedy coordinate descent on
one-generation lookaheads: for each system in turn it tries every
delta in DELTA_GRID with the other systems' deltas fixed at their
current best, simulating one full generation (step + coupling)
from a copy of the current state with fresh probe seeds, and
keeps the delta with the highest next-generation empathy entropy
(ties within 1e-12 go to the smallest |delta|, i.e. no
intervention). The lookaheads never touch the main random
streams, so the agent run and its no-agent control consume
identical randomness and differ only through the deltas.

THE TENSION, KEPT VISIBLE. Healing concentrates love: as D -> 1,
each avatar's love -> 0, so the love distribution collapses and
H falls. The agent spreads love: it slows the fastest healers
and speeds the slowest, equalizing the loves and holding H up.
Both numbers are reported per generation -- mean discord and H,
agent vs control -- so the tension is visible, not averaged away.

PRE-REGISTERED RULE (claim (vi)): the agent raises empathy
entropy versus the no-agent control over the same generations:
mean H over generations 1..10 with the agent is at least
AGENT_ENTROPY_GAIN above the control mean. The gain threshold is
set from a seed-7 pilot run, a round number below the pilot gap,
not fitted to the final seed 11. The discord cost is reported,
not gated: mean discord with the agent versus the control.
"""

import copy
import math
import random

from .crystallize_events import (FALL_THRESHOLD, FORECAST_SAMPLES, brier,
                                 crystallize_points)
from .dna_avatars import healthy_membrane, make_population, self_knowing
from .solar_systems import (COUPLING, N_SYSTEMS, SYSTEM_AVATARS,
                            SYSTEM_GENERATIONS, SYSTEM_SEED, measure_systems,
                            systems_step)
from .trauma import LAMBDA

# Pre-registered model parameters (stated, not measured constants).
DELTA_GRID = (-0.05, 0.0, 0.05)   # Yin calibrator values per system
AGENT_SEED = SYSTEM_SEED
AGENT_GENERATIONS = SYSTEM_GENERATIONS
AGENT_SYSTEMS = N_SYSTEMS
AGENT_AVATARS = SYSTEM_AVATARS

# Pre-registered verdict rule (claim (vi)). Set from the seed-7
# pilot: mean H agent 4.5191 bits vs control 4.5163 bits, gain
# 0.0028 -- the agent's lever moves H by ~0.003 bits because H is
# already saturated: loves are nearly equal across avatars (all
# avatars heal at similar rates), so H sits at ~98.6% of its
# log2(24) = 4.585-bit ceiling and there is almost no entropy
# left to create. AGENT_ENTROPY_GAIN (0.02) is kept as a
# MEANINGFUL bar, not lowered to fit the pilot: if the registered
# run gains less, the claim FAILS and the saturation is the
# finding. (The deep-think framing needs the same correction:
# healing does NOT concentrate love in the normalized
# distribution -- as all D -> 1 together, all loves -> 0
# together, the distribution stays uniform and H RISES to its
# ceiling. The tension is in total love, which falls, not in
# entropy, which saturates.)
AGENT_ENTROPY_GAIN = 0.02


def concurrence_pure(a, b, c, d):
    """Wootters concurrence of a pure two-qubit state (a, b, c, d):
    2|ad - bc|. Formula vendored from gravity-projection
    thought_entanglement.py (faggin-field-bridge v0.3.0 lineage),
    re-implemented in pure Python. Exact: 1 for a Bell pair,
    0 for a product state."""
    return 2.0 * abs(a * d - b * c)


def love_of_d(d):
    """Love of an avatar with self-knowing D: concurrence across the
    stored / non-stored split. Schmidt form sqrt(D)|stored> +
    sqrt(1-D)|rest> gives C = 2*sqrt(D*(1-D)). Cross-check:
    concurrence_pure(sqrt(D), 0, 0, sqrt(1-D)) equals this."""
    d = min(1.0, max(0.0, float(d)))
    return 2.0 * math.sqrt(d * (1.0 - d))


def empathy_entropy(loves):
    """Shannon entropy (bits) of the normalized love distribution.
    0.0 when there is no love to distribute. Returns a dict with
    entropy_bits, max_bits (log2 N) and normalized entropy."""
    n = len(loves)
    total = sum(loves)
    max_bits = math.log2(n) if n > 1 else 0.0
    if n < 2 or total <= 1e-12:
        return {"entropy_bits": 0.0, "max_bits": max_bits, "normalized": 0.0}
    h = -sum((l / total) * math.log2(l / total)
             for l in loves if l > 0)
    return {"entropy_bits": h, "max_bits": max_bits,
            "normalized": h / max_bits if max_bits > 0 else 0.0}


def _loves_of(records):
    """All avatars' loves from per-system measure records."""
    return [love_of_d(d) for r in records for d in r["per_avatar_d"]]


def _probe_rngs(generation, tag, n_systems):
    """Fresh probe streams, deterministic in (generation, tag,
    system): every lookahead combo sees the same mutation draws,
    so combos are compared fairly, and probes never touch the
    main random streams."""
    return [random.Random(1000003 * generation + 9176 * tag + 131 * s)
            for s in range(n_systems)]


def _lookahead_entropy(avatars, membrane, rngs, lam_per_system, coupling,
                       seen_probe):
    """One simulated generation (step + coupling) from a copy of
    `avatars`, returning the next generation's empathy entropy.
    `seen_probe` is a throwaway seen-state: novelty is not needed
    for H, only per-avatar D."""
    stepped = systems_step(copy.deepcopy(avatars), membrane, rngs,
                          lam_per_system, coupling)
    recs, _ = measure_systems(stepped, membrane, seen_probe, 0)
    return empathy_entropy(_loves_of(recs))["entropy_bits"]


def _choose_deltas(avatars, membrane, rngs, coupling, generation,
                   n_systems, delta_grid=DELTA_GRID):
    """Greedy coordinate descent on next-generation empathy
    entropy. For each system in turn, try every delta with the
    other systems fixed at their current best; keep the best
    (ties within 1e-12 go to the smallest |delta|). Returns the
    chosen delta per system."""
    chosen = [0.0] * n_systems
    for s in range(n_systems):
        best_delta, best_h = 0.0, None
        for cand in delta_grid:
            trial = list(chosen)
            trial[s] = cand
            probe = _probe_rngs(generation, 100 + s, n_systems)
            h = _lookahead_entropy(
                avatars, membrane, probe,
                [LAMBDA * (1.0 + d) for d in trial], coupling,
                [dict() for _ in range(n_systems)])
            if (best_h is None or h > best_h + 1e-12
                    or (abs(h - best_h) <= 1e-12
                        and abs(cand) < abs(best_delta))):
                best_delta, best_h = cand, h
        chosen[s] = best_delta
    return chosen


def _forecast_fall(avatars, membrane, deltas, coupling, generation,
                   n_systems, k=FORECAST_SAMPLES,
                   fall_threshold=FALL_THRESHOLD):
    """Crystallize forecast: k lookahead simulations of one
    generation with the chosen deltas, each with a fresh probe
    seed; p = fraction in which the mean discord falls by at
    least `fall_threshold`. Returns (p, k). The lookaheads use
    probe streams only."""
    base = _current_mean_discord(avatars, membrane)
    falls = 0
    for j in range(k):
        probe = _probe_rngs(generation, 1000 + j, n_systems)
        stepped = systems_step(copy.deepcopy(avatars), membrane, probe,
                              [LAMBDA * (1.0 + d) for d in deltas], coupling)
        recs, _ = measure_systems(stepped, membrane,
                                  [dict() for _ in range(n_systems)], 0)
        mean_disc = sum(r["mean_discord"] for r in recs) / len(recs)
        if base - mean_disc >= fall_threshold:
            falls += 1
    return falls / k, k


def _current_mean_discord(avatars, membrane):
    """Mean discord of the current state (measurement only)."""
    from .dna_avatars import avatar_state
    ds = []
    for system in avatars:
        for av in system:
            state = avatar_state(av["sequences"], av["weights"])
            ds.append(self_knowing(state, membrane))
    return 1.0 - sum(ds) / len(ds)


def agent_run(n_systems=AGENT_SYSTEMS, n_avatars=AGENT_AVATARS,
              generations=AGENT_GENERATIONS, coupling=COUPLING,
              seed=AGENT_SEED, delta_grid=DELTA_GRID,
              forecast_samples=FORECAST_SAMPLES,
              fall_threshold=FALL_THRESHOLD, membrane=None):
    """Run the multi-system cascade with the eureka agent. Each
    generation: measure, choose deltas by lookahead, commit a
    crystallize forecast, take the real step, score the forecast
    against the realized fall at the next measurement. Returns
    {"records": [...], "events": [...], ...}. Records carry
    mean_discord, mean_d, entropy_bits, entropy_normalized,
    per_system records and the chosen deltas."""
    mem = membrane if membrane is not None else healthy_membrane()
    rngs = [random.Random(seed * 10000 + s) for s in range(n_systems)]
    avatars = [make_population(n_avatars, seed * 1000 + s)
               for s in range(n_systems)]
    seen = [dict() for _ in range(n_systems)]
    records = []
    events = []
    pending = None  # (generation, p, mean_discord_at_commit)
    for g in range(generations + 1):
        recs, seen = measure_systems(avatars, mem, seen, g)
        loves = _loves_of(recs)
        ent = empathy_entropy(loves)
        mean_disc = sum(r["mean_discord"] for r in recs) / len(recs)
        mean_d = sum(r["mean_d"] for r in recs) / len(recs)
        record = {"generation": g, "mean_discord": mean_disc,
                  "mean_d": mean_d, "entropy_bits": ent["entropy_bits"],
                  "entropy_normalized": ent["normalized"],
                  "per_system": recs, "deltas": None, "event": None}
        records.append(record)
        if pending is not None:
            pg, p, base_disc = pending
            truth = 1 if base_disc - mean_disc >= fall_threshold else 0
            ev = {"generation": pg, "p": p, "truth": truth,
                  "brier": brier(p, truth),
                  "points": crystallize_points(p, truth, forecast_samples)}
            events.append(ev)
            records[pg]["event"] = ev
            pending = None
        if g == generations:
            break
        deltas = _choose_deltas(avatars, mem, rngs, coupling, g,
                                n_systems, delta_grid)
        record["deltas"] = list(deltas)
        p, _ = _forecast_fall(avatars, mem, deltas, coupling, g,
                              n_systems, forecast_samples, fall_threshold)
        pending = (g, p, mean_disc)
        avatars = systems_step(avatars, mem, rngs,
                               [LAMBDA * (1.0 + d) for d in deltas],
                               coupling)
    return {"records": records, "events": events,
            "n_systems": n_systems, "n_avatars": n_avatars,
            "generations": generations, "coupling": coupling,
            "seed": seed, "delta_grid": list(delta_grid)}


def agent_verdict(agent, control):
    """Pre-registered rule (claim (vi)): mean empathy entropy over
    generations 1..10 with the agent is at least
    AGENT_ENTROPY_GAIN above the no-agent control mean (same
    seeds, same coupling). The discord cost is reported, not
    gated. Returns (passed, details dict)."""
    a_h = [r["entropy_bits"] for r in agent["records"][1:]]
    a_disc = [r["mean_discord"] for r in agent["records"]]
    if isinstance(control, dict) and "records" in control:
        c_recs = control["records"]
    else:
        c_recs = control
    c_h = []
    for recs in c_recs[1:]:
        loves = _loves_of(recs)
        c_h.append(empathy_entropy(loves)["entropy_bits"])
    c_disc = [sum(r["mean_discord"] for r in recs) / len(recs)
              for recs in c_recs]
    a_mean = sum(a_h) / len(a_h)
    c_mean = sum(c_h) / len(c_h)
    gain = a_mean - c_mean
    passed = gain >= AGENT_ENTROPY_GAIN
    # Secondary measure, reported not gated: total love (sum of
    # loves) per generation. Healing drives every love toward 0,
    # so total love falls even as the entropy saturates; if the
    # agent preserves total love by slowing the fastest healers,
    # it shows here.
    a_love = [sum(_loves_of(r["per_system"])) for r in agent["records"]]
    c_love = [sum(_loves_of(recs)) for recs in c_recs]
    details = {
        "passed": bool(passed),
        "mean_entropy_agent": a_mean,
        "mean_entropy_control": c_mean,
        "entropy_gain": gain,
        "entropy_gain_required": AGENT_ENTROPY_GAIN,
        "entropy_by_gen_agent": a_h,
        "entropy_by_gen_control": c_h,
        "mean_discord_final_agent": a_disc[-1],
        "mean_discord_final_control": c_disc[-1],
        "discord_cost": a_disc[-1] - c_disc[-1],
        "total_love_by_gen_agent": a_love,
        "total_love_by_gen_control": c_love,
        "mean_total_love_agent": sum(a_love[1:]) / len(a_love[1:]),
        "mean_total_love_control": sum(c_love[1:]) / len(c_love[1:]),
    }
    return passed, details
