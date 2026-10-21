"""python -m quantum_projection [--seeds N]: print the measured sweep tables."""

import argparse

from .sweeps import SEEDS, report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="quantum-projection",
                                 description="SYNTHETIC classical emulation; prints measured sweeps.")
    ap.add_argument("--seeds", type=int, default=SEEDS)
    args = ap.parse_args(argv)
    if args.seeds < 1:
        ap.error("--seeds must be >= 1")
    print("SYNTHETIC: classical emulation of quantum kinematics only. "
          "No speedup, no Bell violation.\n")
    print(report(seeds=args.seeds))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
