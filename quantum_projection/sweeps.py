"""Multi-seed sweeps behind the numbers in the README.

SYNTHETIC. Every number is a measurement of this classical emulation
with seeded pseudo-random noise; nothing here is hardware data.
"""

from .membrane import HolographicMembrane, coarse_grain
from .qsim import (H, apply_1q, basis, bell_phi_minus, bell_phi_plus,
                   bell_psi_minus, bell_psi_plus, fidelity, ghz, noisy,
                   normalize, plus_product, random_state, w_state, zero)

SIGMAS = (0.1, 0.25, 0.5, 0.75, 1.0)
SEEDS = 200


def _seed(*parts):
    s = 0
    for p in parts:
        s = s * 1000003 + int(p)
    return s


def _accuracy(mem, truths, transform, sigmas, seeds, tag):
    """truths: list of (name, state, expected_index or None)."""
    table = {}
    for si, sigma in enumerate(sigmas):
        for ti, (name, state, want) in enumerate(truths):
            counts = [0] * len(mem.patterns)
            for s in range(seeds):
                probe = transform(noisy(state, sigma, _seed(tag, si, ti, s)))
                counts[mem.project(probe)["winner"]] += 1
            table[(name, sigma)] = {
                "counts": counts,
                "accuracy": None if want is None else counts[want] / seeds,
            }
    return table


def _random_controls(mem, n, transform, seeds, tag):
    maxw = []
    counts = [0] * len(mem.patterns)
    for s in range(seeds):
        r = mem.project(transform(random_state(n, _seed(tag, s))))
        maxw.append(max(r["probs"]))
        counts[r["winner"]] += 1
    return {"counts": counts, "mean_max_weight": sum(maxw) / seeds,
            "min_max_weight": min(maxw)}


def bell_sweep(sigmas=SIGMAS, seeds=SEEDS):
    names = ["Phi+", "Phi-", "Psi+"]
    mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus(), bell_psi_plus()])
    truths = [("Phi+", bell_phi_plus(), 0), ("Phi-", bell_phi_minus(), 1),
              ("Psi+", bell_psi_plus(), 2),
              ("Psi- (not stored)", bell_psi_minus(), None),
              ("|01> (not stored)", basis(2, 1), None)]
    table = _accuracy(mem, truths, lambda v: v, sigmas, seeds, 1)
    # Orthonormal patterns: one recall step is the fixed point and the
    # recalled fidelity equals the Born weight.
    born_gap = step_gap = 0.0
    for s in range(seeds):
        probe = noisy(bell_phi_plus(), 0.25, _seed(9, s))
        w = mem.project(probe)["probs"][0]
        one, _, _ = mem.recall(probe, steps=1)
        many, _, _ = mem.recall(probe, steps=25)
        born_gap = max(born_gap, abs(fidelity(one, bell_phi_plus()) - w))
        step_gap = max(step_gap, max(abs(x - y) for x, y in zip(one, many)))
    return {"patterns": names, "table": table,
            "controls_random": _random_controls(mem, 2, lambda v: v, seeds, 2),
            "max_born_vs_fidelity_gap": born_gap,
            "max_one_vs_25_step_gap": step_gap}


def plus0():
    return normalize(apply_1q(zero(2), 1, H))


def nonorthogonal_sweep(sigmas=SIGMAS, seeds=SEEDS):
    p0, p1 = zero(2), plus0()
    mem = HolographicMembrane([p0, p1])
    truths = [("|00>", p0, 0), ("|+0>", p1, 1)]
    table = _accuracy(mem, truths, lambda v: v, sigmas, seeds, 3)
    # Iteration with non-orthogonal patterns: power iteration on W.
    # Dominant eigenvector of W for two patterns with real positive overlap
    # is (p0 + p1)/||p0 + p1||.
    dom = normalize([a + b for a, b in zip(p0, p1)])
    iteration = []
    for steps in (1, 2, 5, 25):
        a, win, _ = mem.recall(p0, steps=steps)
        iteration.append({"steps": steps, "fid_to_00": fidelity(a, p0),
                          "fid_to_plus0": fidelity(a, p1),
                          "fid_to_dominant_eigvec": fidelity(a, dom),
                          "winner": win})
    # How often does long recall flip the one-shot decision?
    flips = 0
    for s in range(seeds):
        probe = noisy(p0, 0.25, _seed(4, s))
        if mem.project(probe)["winner"] != mem.recall(probe, steps=25)[1]:
            flips += 1
    return {"patterns": ["|00>", "|+0>"], "table": table,
            "pattern_overlap": abs(sum(a.conjugate() * b for a, b in zip(p0, p1))),
            "iteration_from_clean_00": iteration,
            "recall25_flips_at_sigma_0.25": flips / seeds}


def ghz_sweep(sigmas=SIGMAS, seeds=SEEDS, qubit=0):
    names = ["GHZ", "W", "|000>", "|+++>"]
    states = [ghz(3), w_state(3), zero(3), plus_product(3)]
    cg = lambda v: coarse_grain(v, qubit)  # noqa: E731
    mem = HolographicMembrane([cg(s) for s in states])
    truths = [(n, s, i) for i, (n, s) in enumerate(zip(names, states))]
    truths.append(("|001> (not stored)", basis(3, 1 << qubit), None))
    table = _accuracy(mem, truths, cg, sigmas, seeds, 5)
    return {"patterns": names, "table": table,
            "controls_random": _random_controls(mem, 3, cg, seeds, 6),
            "stored_overlaps": [[abs(sum(a.conjugate() * b for a, b in zip(x, y)))
                                 for y in mem.patterns] for x in mem.patterns]}


def _fmt_table(res):
    sig = sorted({k[1] for k in res["table"]})
    rows = []
    names = list(dict.fromkeys(k[0] for k in res["table"]))
    rows.append("| probe | " + " | ".join(f"sigma={s}" for s in sig) + " |")
    rows.append("|---|" + "---|" * len(sig))
    for n in names:
        cells = []
        for s in sig:
            e = res["table"][(n, s)]
            if e["accuracy"] is None:
                cells.append("/".join(str(c) for c in e["counts"]))
            else:
                cells.append(f"{e['accuracy']:.3f}")
        rows.append(f"| {n} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def report(seeds=SEEDS):
    out = []
    b = bell_sweep(seeds=seeds)
    out.append(f"Bell: stored {b['patterns']}; accuracy over {seeds} seeds "
               "(unstored probes: winner counts per stored pattern)")
    out.append(_fmt_table(b))
    c = b["controls_random"]
    out.append(f"random 2-qubit states: winner counts {c['counts']}, "
               f"mean max weight {c['mean_max_weight']:.3f}, min {c['min_max_weight']:.3f}")
    out.append(f"max |recalled fidelity - Born weight| = {b['max_born_vs_fidelity_gap']:.2e}; "
               f"max |1-step - 25-step| = {b['max_one_vs_25_step_gap']:.2e}")
    n = nonorthogonal_sweep(seeds=seeds)
    out.append(f"\nNon-orthogonal: stored {n['patterns']}, overlap {n['pattern_overlap']:.4f}")
    out.append(_fmt_table(n))
    for it in n["iteration_from_clean_00"]:
        out.append(f"recall of clean |00>, {it['steps']:>2} steps: F(|00>)={it['fid_to_00']:.4f} "
                   f"F(|+0>)={it['fid_to_plus0']:.4f} F(dominant)={it['fid_to_dominant_eigvec']:.4f} "
                   f"winner={n['patterns'][it['winner']]}")
    out.append(f"25-step recall changes the one-shot winner (sigma=0.25): "
               f"{n['recall25_flips_at_sigma_0.25']:.3f}")
    g = ghz_sweep(seeds=seeds)
    out.append(f"\nCoarse-grained 3 qubits -> 2 (merge qubit 0): stored {g['patterns']}")
    out.append(_fmt_table(g))
    c = g["controls_random"]
    out.append(f"random 3-qubit states: winner counts {c['counts']}, "
               f"mean max weight {c['mean_max_weight']:.3f}")
    out.append("stored-pattern overlaps after coarse-graining:")
    for name, row in zip(g["patterns"], g["stored_overlaps"]):
        out.append(f"  {name:6s} " + " ".join(f"{x:.3f}" for x in row))
    return "\n".join(out)
