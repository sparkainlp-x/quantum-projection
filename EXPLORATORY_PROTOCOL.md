# Exploratory input-dependent ZZ feature-map protocol

**Status:** prospective and explicitly exploratory. This is a protocol for a
possible later study, not a preregistration, result, or performance claim. No
input-dependent accuracy search is part of this PR. An equivalent or negative
result is valid.

## Question and encoding

Compare a fixed input-dependent ZZ statevector feature map with classical
representations on small, synthetic classification tasks. The comparison asks
whether this particular representation changes performance under a controlled
classifier and equal tuning budgets; it does not test quantum hardware or
quantum advantage.

For a feature vector \(x\in\mathbb R^d\), fit each feature's affine scaling on
the training split only, map it to \(\hat x_i\in[-1,1]\), and use the unique
unordered edges of a fixed ring, with \(n=d\) for the candidate small-qubit
tasks. A candidate map is

\[
|\phi(x)\rangle =
\left(\prod_{(i,j)\in E}RZZ_{ij}(\gamma\hat x_i\hat x_j)\right)
\left(\prod_i RY_i(\beta\hat x_i)\right)H^{\otimes n}|0^n\rangle,
\qquad
K_{\rm ZZ}(x,z)=|\langle\phi(x)|\phi(z)\rangle|^2.
\]

Products are applied right-to-left; all selected \(\beta,\gamma\), graph and
scaling choices must be frozen before held-out scoring. The ring is a
prospective candidate, not an asserted optimal map.

## Synthetic data, splits, and replicate unit

Use only generated data in this study. Candidate generators, defined before
running it, are:

1. **Linear:** independent coordinates uniform on \([-1,1]\), labeled by a
   fixed nonzero linear separator.
2. **Parity/XOR:** coordinates uniform on \([-1,1]\), labeled by the parity of
   their signs.
3. **Radial:** coordinates uniform on \([-1,1]\), labeled by whether squared
   Euclidean radius exceeds a fixed, declared threshold.

Any label-flip mechanism and rate must be declared in the run configuration;
do not tune them against test outcomes. Each generator has disjoint
training, calibration, and test examples. No example, duplicate, or
perturbation of an example may cross a split. Keep feature scaling and any
learned preprocessing fit on training data only.

The independent replicate is a newly generated dataset instance with its own
recorded seed, not a row, query, qubit, or repeated optimization from the same
dataset. Determine and record the replicate count and split sizes before
confirmatory scoring, using a justified compute or power plan; this protocol
does not invent a sample size. Do not extend the run because an interim result
looks favorable.

Include a label-control run that permutes labels within each split while
preserving each split's class counts, using separate recorded seeds. Label
controls are negative controls, not extra model-selection data.

## Representations and implementation-equivalence control

All representations use the same examples and classifier:

- **Raw:** training-standardized original features with the linear kernel.
- **Classical pairwise/trigonometric:** a training-standardized explicit
  vector \([\,\hat x_i,\hat x_i\hat x_j,\sin(\pi\hat x_i),\cos(\pi\hat
  x_i),\sin(\pi\hat x_i\hat x_j),\cos(\pi\hat x_i\hat x_j)\,]\) over
  coordinates and all unordered pairs, with its dot-product kernel.
- **Input-dependent ZZ:** the statevector fidelity kernel \(K_{\rm ZZ}\)
  above.

Use one kernel-ridge classifier with labels coded \(\{-1,+1\}\) and the same
declared regularization candidate grid, fitting procedure, and number of
tuning candidates for each representation. Choose hyperparameters using
training-only cross-validation; equalize and report the tuning budget,
including failed candidates.

Separately compute \(K_{\rm ZZ}\) by an exact classical statevector calculation
of the same encoded states and compare every kernel entry with the
implementation under a fixed numerical tolerance. This is an
**implementation-equivalence control**, not a competitive baseline and not
evidence of a quantum advantage. The code in this repository is classical
statevector emulation.

## Noise, calibration, and held-out evaluation

The primary noisy-data condition perturbs each classical input before any
representation is computed. Materialize each realized perturbed example once
and reuse it across raw, engineered, and statevector representations. Do not
regenerate noise per representation or add noise after a shared unitary in a
way that breaks a paired comparison. If a separate statevector/readout
perturbation is explored, label it as a different condition and report its
placement and seed; it is not hardware noise.

Fit models and choose hyperparameters using training data only. Use calibration
data only for any prespecified score calibration or refusal threshold. Freeze
preprocessing, encoding, classifier, hyperparameters, and threshold before
opening test scores. Score the test split once for the frozen pipeline.

The primary metric is **balanced accuracy**. If the application requires
refusal, define the score and risk ceiling before the run, select the
largest-coverage threshold meeting that ceiling on calibration data only, and
report both test coverage (fraction accepted) and selective balanced
accuracy/error. Do not compare a refusing model's accepted-only accuracy
without coverage.

## Analysis and decision rules

The prospective meaningful-effect margin is **+0.02 absolute balanced
accuracy** for the ZZ representation over a competitive classical
representation. This is a decision threshold, not an expected effect. Report
per-replicate paired differences, their mean and median, and a 95% confidence
interval obtained by resampling independent dataset replicates (not individual
rows as if independent). State the interval method and all replicate outcomes.
A result below the margin, an interval spanning zero, or equivalence is not a
success claim.

Name one primary generator and one primary competitive contrast before
scoring. Treat other generators, metrics, and pairwise contrasts as secondary;
report all of them and use Holm adjustment within the declared secondary
comparison family. Do not select a favorable generator, metric, replicate, or
baseline after inspecting test results. Report label-control results and the
exact classical-kernel equivalence error alongside the performance analysis.

## Scope and citations

Havlíček et al. introduce quantum-enhanced feature spaces for supervised
learning and report demonstrations on selected data and quantum hardware;
that work does not establish a general advantage for this package or this
proposed experiment. Thanasilp et al. analyze exponential concentration in
quantum kernel methods and its consequences for learning under the studied
settings; it is a caution about feature-map/kernel design, not evidence about
the results of this prospective protocol.

- Havlíček et al., “Supervised learning with quantum-enhanced feature spaces,”
  *Nature* (2019), https://doi.org/10.1038/s41586-019-0980-2.
- Thanasilp et al., “Exponential concentration in quantum kernel methods,”
  *Nature Communications* (2024),
  https://doi.org/10.1038/s41467-024-49287-w.
- IBM's `RZZGate` reference documents the gate definition and matrix, not a
  claim about this package:
  https://quantum.cloud.ibm.com/docs/api/qiskit/qiskit.circuit.library.RZZGate.
