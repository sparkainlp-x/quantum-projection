# Changelog

## Unreleased

- Documentation only: added a Provenance statement that says which files are derived from the package received under Mun Seok Lee's name and by how much, that he is not an author of this release and has not endorsed it.

## 0.1.0 (2026-10-21)

- Archived on Zenodo: version DOI [10.5281/zenodo.23530281](https://doi.org/10.5281/zenodo.23530281), concept DOI [10.5281/zenodo.23530280](https://doi.org/10.5281/zenodo.23530280).
- First commit: the package exactly as received (`spec/`).
- Authorship: Jean-François Brisson. Mun Seok Lee is credited in the acknowledgements only.
- Wording: "collapse" is now "projection onto the stored subspace". With orthonormal patterns W is a projector, so recall reaches its fixed point in one step and the recalled fidelity equals the Born weight; both are measured and tested. The default `recall` is now one step (was 25).
- Measured: with non-orthogonal patterns, repeated recall converges to W's dominant eigenvector and loses the one-shot decision (75% of winners change at σ = 0.25).
- Ket/bra split documented as the same inner product; tests now compare complex overlaps, phases included, instead of magnitudes only.
- Single-seed checks replaced by 200-seed sweeps over five σ values for Bell classification, |00⟩ vs |+0⟩ and coarse-grained 3-qubit states, with unstored probes (Ψ−, |01⟩, |001⟩) and Haar-random controls. The "20/20" claim is restated with its seed range.
- Coarse-graining: documented and tested as projecting the merged qubit onto |+⟩; the qubit is now selectable (default 0, the least-significant bit, as before).
- Removed the unused `ry` gate and the unused `n` arguments of `apply_1q` and `apply_cnot`. Added `ValueError` checks for empty pattern lists, length mismatches, zero-norm and non-finite vectors, bad qubit indices and probes orthogonal to every pattern.
- The coarse-grained GHZ check, whose only alternative was a noisy copy of GHZ, is replaced by distinct stored states (W, |000⟩, |+++⟩).
- DESIGN.md: neutral wording in the limits section; headings that overstated the checks replaced by measurements.
- Added a package layout, a CLI that prints the sweeps, 65 pytest tests, CI on Python 3.10 to 3.13, README, CITATION.cff and .zenodo.json.
