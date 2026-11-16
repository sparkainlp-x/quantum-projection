"""python -m quantum_projection [--seeds N] [--v030]: print the measured sweep tables."""

import argparse

from .sweeps import SEEDS, report
from .unified import cascade_report, v030_report, v040_report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="quantum-projection",
                                 description="SYNTHETIC classical emulation; prints measured sweeps.")
    ap.add_argument("--seeds", type=int, default=SEEDS)
    ap.add_argument("--v030", action="store_true",
                    help="also print the v0.3.0 multi-system eureka "
                         "cascade report (takes minutes: the agent run "
                         "and the 500-generation long run)")
    ap.add_argument("--v040", action="store_true",
                    help="also print the v0.4.0 SDF synergy agents "
                         "report (takes minutes: 27 lookaheads per "
                         "generation for the payoff tables)")
    args = ap.parse_args(argv)
    if args.seeds < 1:
        ap.error("--seeds must be >= 1")
    print("SYNTHETIC: classical emulation of quantum kinematics only. "
          "No speedup, no Bell violation.\n")
    print(report(seeds=args.seeds))
    print("\n" + cascade_report())
    if args.v030:
        print("\n" + v030_report())
    if args.v040:
        print("\n" + v040_report())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
