"""Demo: quantum statevectors projected into a holographic membrane.

1. Bell-state projective measurement: store |Phi+>, |Phi->, |Psi+>;
   probe with a noisy |Phi+>; the membrane picks the right pattern
   with Born-like probabilities and recalls it with high fidelity.
2. Ket/bra split: the same projection computed BETWEEN two conjugate
   membranes (yin = kets, yang = bras).
3. Non-orthogonal patterns: |00> vs |+0> (overlap 1/sqrt(2)).
4. Coarse-graining: 3-qubit GHZ (8 amplitudes) -> 4-oscillator
   membrane, still recalled correctly.
Run: python demo.py
"""

from qsim import (bell_phi_plus, bell_phi_minus, bell_psi_plus, ghz,
                  noisy, zero, apply_1q, H, fidelity, normalize)
from qmembrane import HolographicMembrane, KetBraPair, coarse_grain


def show(name, res, names):
    print(f"  {name}")
    for n_, m, p in zip(names, res["overlaps"], res["probs"]):
        print(f"    <{n_:5s}|probe> = {abs(m):.4f}   prob = {p:.4f}")
    print(f"    winner: {names[res['winner']]}")


print("== 1. Bell-state projection ==")
names = ["Phi+", "Phi-", "Psi+"]
mem = HolographicMembrane([bell_phi_plus(), bell_phi_minus(), bell_psi_plus()])
probe = noisy(bell_phi_plus(), 0.25, seed=11)
res = mem.project(probe)
show("noisy |Phi+> (sigma=0.25) projected:", res, names)
final, winner, _ = mem.recall(probe)
print(f"  recall winner: {names[winner]}, "
      f"fidelity to true |Phi+>: {fidelity(final, bell_phi_plus()):.4f}")
ok1 = winner == 0

print("\n== 2. ket/bra split across two membranes ==")
pair = KetBraPair([bell_phi_plus(), bell_phi_minus(), bell_psi_plus()])
res2 = pair.project(probe)
show("same probe, bracket via yang (bras):", res2, names)
ok2 = res2["winner"] == 0 and \
    abs(abs(res2["overlaps"][0]) - abs(res["overlaps"][0])) < 1e-9

print("\n== 3. non-orthogonal patterns: |00> vs |+0> ==")
plus0 = normalize(apply_1q(zero(2), 2, 1, H))  # (|00> + |10>)/sqrt2
mem3 = HolographicMembrane([zero(2), plus0])
probe3 = noisy(zero(2), 0.20, seed=5)
res3 = mem3.project(probe3)
print(f"  <00|probe> = {abs(res3['overlaps'][0]):.4f}, "
      f"<+0|probe> = {abs(res3['overlaps'][1]):.4f} "
      f"(true pattern overlap = {abs(sum(a.conjugate()*b for a, b in zip(zero(2), plus0))):.4f})")
print(f"  winner: {'|00>' if res3['winner'] == 0 else '|+0>'}")
ok3 = res3["winner"] == 0

print("\n== 4. coarse-grained GHZ: 8 amplitudes -> 4 oscillators ==")
g = ghz(3)
mem4 = HolographicMembrane([coarse_grain(g),
                            coarse_grain(noisy(g, 0.6, seed=3))])
probe4 = coarse_grain(noisy(g, 0.25, seed=9))
res4 = mem4.project(probe4)
print(f"  <GHZ|probe> = {abs(res4['overlaps'][0]):.4f}, "
      f"<noisy-GHZ-template|probe> = {abs(res4['overlaps'][1]):.4f}")
print(f"  winner: {'GHZ' if res4['winner'] == 0 else 'template'}")
ok4 = res4["winner"] == 0

print("\nRESULT:", "PASS -- projections resolve the right pattern, "
      "ket/bra split matches, coarse membrane still recalls"
      if all([ok1, ok2, ok3, ok4]) else "FAIL")
raise SystemExit(0 if all([ok1, ok2, ok3, ok4]) else 1)
