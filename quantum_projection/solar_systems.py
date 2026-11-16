# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 Jean-Francois Brisson (Spark AI NLP)
"""Multiple solar systems: N populations running the v0.2.0 cascade in
parallel, with a bounded coupling between systems.

SYNTHETIC. Classical emulation only. A "solar system" is a population
of DNA avatars evolving under the self-cycle (trauma.py); the systems
share the same stored (healthy) subspace, so D and discord are
comparable across systems. "Planetary" is a population model, not
astronomy: no orbits, no gravity, no claim about real planets.

Coupling (the lattice shape): after each generation step, every
avatar mixes a small fraction COUPLING (0.02) of its state toward
the leave-one-out mean state of the OTHER systems. The value 0.02
is the same order as the membrane-arena-3x3 lattice coupling
(0.02, measured safe there); it is a stated choice, not a measured
constant. The mix is a linear blend of state vectors, the same
shape as the lattice interaction (coupling x (other - rho)), with
the fidelity factor replaced by the fixed fraction: the coupling
here is deliberately structureless, so any synchronization it
produces is measured, not built in. Coupling is deterministic and
uses no randomness, so a coupled run and its uncoupled control
consume identical random streams and differ only through the mix.

Contagion is measured, not assumed, by a controlled shock: one
system starts with deeper trauma (SHOCK_FLIPS base flips per
variant, retained healthy weight SHOCK_SEED_WEIGHT instead of
0.05), so it heals slower. The same shock runs coupled and
uncoupled, same seeds. What spreads through the coupling is then
a causal question, not a correlation. Claim (v) has four checks:
(a) coupling does not harm healing on the unshocked run;
(b) support -- the shocked system heals faster coupled than
uncoupled; (c) convergence -- the gap between the shocked system
and the healthy ones narrows coupled; (d) no spread of harm --
the healthy systems heal no worse coupled than uncoupled. The
naive correlation check was tried and rejected: per-generation discord CHANGES correlate
~0.78 even uncoupled, because every system follows the same
healing curve, so correlation measures the shared trend, not the
coupling. And the spread-of-harm direction does NOT occur: the
coupling transfers healed weight preferentially to the laggard,
so the shocked system gains ~0.10 while the healthy ones lose
nothing. That asymmetry is the measured finding.
"""

import math
import random

from .dna_avatars import (HEALTHY_SEQUENCES, MAX_VARIANTS, avatar_state,
                          dominant_sequence, energy_of, healthy_membrane,
                          index_to_sequence, make_population, sequence_index,
                          self_knowing, trauma_variant)
from .trauma import LAMBDA, RETAIN_THRESHOLD, generation_step

# Pre-registered model parameters (stated, not measured constants).
COUPLING = 0.02             # mix fraction per generation toward other systems
N_SYSTEMS = 3               # solar systems in the registered run
SYSTEM_AVATARS = 8          # avatars per system (same as v0.2.0)
SYSTEM_GENERATIONS = 10     # generations in the registered run
SYSTEM_SEED = 11            # independent of the pilot seed (7)
SHOCK_FLIPS = 6             # base flips per variant in the shocked system
SHOCK_SEED_WEIGHT = 0.01    # retained healthy weight in the shocked system

# Pre-registered verdict rules (claim (v)). Set from the seed-7 pilot:
# unshocked mean final discord 0.0872 coupled vs 0.0980 uncoupled;
# shocked system 0 final discord 0.5553 coupled vs 0.6515 uncoupled
# (support 0.096); gap shocked-vs-others 0.4662 coupled vs 0.5553
# uncoupled (narrowing 0.089); healthy others 0.0891 coupled vs
# 0.0962 uncoupled. Thresholds are round numbers below the pilot
# margins, not fitted to the final seed.
CONTAGION_DISCORD_TOL = 0.02
SUPPORT_MARGIN = 0.05
CONVERGENCE_MARGIN = 0.05
OTHERS_TOL = 0.02


def avatar_state_dict(avatar):
    """An avatar's state as a sparse amplitude dict {basis index:
    amplitude}. Exact: avatar_state is a superposition of basis
    states, so the dict holds the same amplitudes (normalized)."""
    out = {}
    for s, w in zip(avatar["sequences"], avatar["weights"]):
        i = sequence_index(s)
        out[i] = out.get(i, 0.0) + w
    norm = math.sqrt(sum(abs(v) ** 2 for v in out.values()))
    return {i: v / norm for i, v in out.items()}


def _dict_norm(d):
    return math.sqrt(sum(abs(v) ** 2 for v in d.values()))


def _mean_dicts(dicts):
    """Mean state of a list of sparse state dicts."""
    out = {}
    n = len(dicts)
    for d in dicts:
        for i, v in d.items():
            out[i] = out.get(i, 0.0) + v / n
    return out


def _mix_dicts(a, b, kappa):
    """normalize((1 - kappa) * a + kappa * b) as a sparse dict."""
    out = {i: (1.0 - kappa) * v for i, v in a.items()}
    for i, v in b.items():
        out[i] = out.get(i, 0.0) + kappa * v
    n = _dict_norm(out)
    return {i: v / n for i, v in out.items()}


def state_dict_to_avatar(d):
    """Retain logic of generation_step, applied to a sparse state
    dict: keep |amplitude|^2 > RETAIN_THRESHOLD, top MAX_VARIANTS,
    weights = |amplitude| renormalized. The healthy reference is
    stable here too: the mix never invents stored weight, it only
    redistributes amplitude already present."""
    items = sorted(((abs(v), i) for i, v in d.items()
                    if abs(v) ** 2 > RETAIN_THRESHOLD),
                   reverse=True)[:MAX_VARIANTS]
    total = sum(w * w for w, _ in items)
    return {"sequences": [index_to_sequence(i) for _, i in items],
            "weights": [w / math.sqrt(total) for w, _ in items]}


def couple_systems(avatars_by_system, kappa=COUPLING):
    """One coupling pass: every avatar mixes `kappa` toward the
    leave-one-out mean state of the OTHER systems. Deterministic;
    uses no randomness. With one system there is nothing to couple
    to and the avatars pass through unchanged."""
    if len(avatars_by_system) < 2 or kappa <= 0:
        return avatars_by_system
    system_means = [_mean_dicts([avatar_state_dict(av) for av in avatars])
                    for avatars in avatars_by_system]
    out = []
    for s, avatars in enumerate(avatars_by_system):
        others = [m for j, m in enumerate(system_means) if j != s]
        mean_other = _mean_dicts(others)
        out.append([state_dict_to_avatar(
            _mix_dicts(avatar_state_dict(av), mean_other, kappa))
            for av in avatars])
    return out


def systems_step(avatars_by_system, membrane, rngs, lam_per_system,
                 kappa=COUPLING):
    """One generation for all systems: the v0.2.0 partial-projection
    step per avatar (each system at its own lambda), then the
    coupling pass."""
    stepped = [[generation_step(av, membrane, lam_per_system[s], rngs[s])
                for av in avatars]
               for s, avatars in enumerate(avatars_by_system)]
    return couple_systems(stepped, kappa)


def measure_systems(avatars_by_system, membrane, seen_by_system, g):
    """Per-system records for generation `g`, same definitions as
    trauma.run_cascade's record block (mean D, mean discord,
    per-avatar D, diversity, novelty, cumulative distinct, mean
    energy, peak energy). `seen_by_system` is a list of dicts
    (variant -> first-seen generation), updated in place; it is
    what makes novelty per-system. Returns (records, seen)."""
    records = []
    for s, avatars in enumerate(avatars_by_system):
        seen = seen_by_system[s]
        ds, energies, dominants = [], [], []
        current_variants = set()
        for av in avatars:
            state = avatar_state(av["sequences"], av["weights"])
            ds.append(self_knowing(state, membrane))
            dom = dominant_sequence(av["sequences"], av["weights"])
            dominants.append(dom)
            energies.append(energy_of(dom))
            current_variants.update(av["sequences"])
        for v in current_variants:
            if v not in seen:
                seen[v] = g
        new_this_gen = sum(1 for v in current_variants if seen[v] == g)
        records.append({
            "system": s,
            "generation": g,
            "mean_d": sum(ds) / len(ds),
            "mean_discord": 1.0 - sum(ds) / len(ds),
            "per_avatar_d": list(ds),
            "diversity": len(set(dominants)),
            "novelty": new_this_gen / max(1, len(current_variants)),
            "cumulative_distinct": len(seen),
            "mean_energy": sum(energies) / len(energies),
            "peak_energy": max(set(energies), key=energies.count),
        })
    return records, seen_by_system


def make_shocked_avatar(healthy, rng):
    """A deeper-trauma avatar: SHOCK_FLIPS base flips per variant and
    a retained healthy weight of SHOCK_SEED_WEIGHT (0.01) instead of
    0.05, so there is less healthy weight for the projection to
    amplify and the avatar heals slower. Same shape as make_avatar,
    same variant weights otherwise."""
    from .dna_avatars import VARIANT_WEIGHTS
    variants = [healthy] + [trauma_variant(healthy, rng, nflips=SHOCK_FLIPS)
                            for _ in VARIANT_WEIGHTS]
    return {"sequences": list(variants),
            "weights": [SHOCK_SEED_WEIGHT] + list(VARIANT_WEIGHTS)}


def make_shocked_population(n_avatars, seed):
    """A shocked system: every avatar deeply traumatized."""
    rng = random.Random(seed)
    return [make_shocked_avatar(HEALTHY_SEQUENCES[m % len(HEALTHY_SEQUENCES)], rng)
            for m in range(n_avatars)]


def run_solar_systems(n_systems=N_SYSTEMS, n_avatars=SYSTEM_AVATARS,
                      generations=SYSTEM_GENERATIONS, coupling=COUPLING,
                      seed=SYSTEM_SEED, membrane=None, shocked_system=None):
    """Run N systems in parallel for `generations` steps. Each system
    gets its own population seed (seed*1000 + s) and its own random
    stream (seed*10000 + s), so systems are independent except for
    the coupling. If `shocked_system` is an index, that system starts
    deeply traumatized (make_shocked_population). Returns {"records":
    [per-generation list of per-system records], ...}. With
    coupling=0 this is the uncoupled control: same seeds, same
    streams, no mix."""
    mem = membrane if membrane is not None else healthy_membrane()
    rngs = [random.Random(seed * 10000 + s) for s in range(n_systems)]
    avatars = []
    for s in range(n_systems):
        if s == shocked_system:
            avatars.append(make_shocked_population(n_avatars, seed * 1000 + s))
        else:
            avatars.append(make_population(n_avatars, seed * 1000 + s))
    seen = [dict() for _ in range(n_systems)]
    records = []
    for g in range(generations + 1):
        recs, seen = measure_systems(avatars, mem, seen, g)
        records.append(recs)
        if g == generations:
            break
        avatars = systems_step(avatars, mem, rngs,
                               [LAMBDA] * n_systems, coupling)
    return {"records": records, "n_systems": n_systems,
            "n_avatars": n_avatars, "generations": generations,
            "coupling": coupling, "seed": seed,
            "shocked_system": shocked_system}


def _mean(xs):
    return sum(xs) / len(xs)


def contagion_verdict(coupled, uncoupled, shocked_coupled,
                      shocked_uncoupled, shocked_system=0):
    """Pre-registered rule (claim (v)). Four checks, all must hold:
    (a) coupling does not harm healing on the unshocked run;
    (b) support: the shocked system heals faster coupled than
    uncoupled, by at least SUPPORT_MARGIN;
    (c) convergence: the gap between the shocked system and the
    healthy ones narrows coupled by at least CONVERGENCE_MARGIN;
    (d) no spread of harm: the healthy systems heal no worse
    coupled than uncoupled (within OTHERS_TOL).
    Returns (passed, details dict)."""
    c_mean = _mean([r["mean_discord"] for r in coupled["records"][-1]])
    u_mean = _mean([r["mean_discord"] for r in uncoupled["records"][-1]])
    check_a = c_mean <= u_mean + CONTAGION_DISCORD_TOL

    s = shocked_system
    sc_shocked = shocked_coupled["records"][-1][s]["mean_discord"]
    su_shocked = shocked_uncoupled["records"][-1][s]["mean_discord"]
    check_b = sc_shocked <= su_shocked - SUPPORT_MARGIN

    others = [i for i in range(shocked_coupled["n_systems"]) if i != s]
    sc_others = _mean([shocked_coupled["records"][-1][i]["mean_discord"]
                       for i in others])
    su_others = _mean([shocked_uncoupled["records"][-1][i]["mean_discord"]
                       for i in others])
    check_c = (sc_shocked - sc_others) <= (su_shocked - su_others) - CONVERGENCE_MARGIN
    check_d = sc_others <= su_others + OTHERS_TOL

    details = {
        "healing_ok": bool(check_a),
        "mean_final_discord_coupled": c_mean,
        "mean_final_discord_uncoupled": u_mean,
        "discord_tol": CONTAGION_DISCORD_TOL,
        "support_ok": bool(check_b),
        "shocked_final_discord_coupled": sc_shocked,
        "shocked_final_discord_uncoupled": su_shocked,
        "support_margin": SUPPORT_MARGIN,
        "support_gain": su_shocked - sc_shocked,
        "convergence_ok": bool(check_c),
        "gap_coupled": sc_shocked - sc_others,
        "gap_uncoupled": su_shocked - su_others,
        "convergence_margin": CONVERGENCE_MARGIN,
        "no_harm_ok": bool(check_d),
        "others_final_discord_coupled": sc_others,
        "others_final_discord_uncoupled": su_others,
        "others_tol": OTHERS_TOL,
    }
    return check_a and check_b and check_c and check_d, details
