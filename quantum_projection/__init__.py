"""quantum_projection: SYNTHETIC classical emulation of quantum kinematics.

Amplitude-encoded statevectors in a complex outer-product memory,
overlap-based projection, and lossy Haar coarse-graining. Standard
library only. No speedup, no Bell violation.
"""

from .membrane import HolographicMembrane, KetBraPair, coarse_grain, overlap
from .qsim import (bell_phi_minus, bell_phi_plus, bell_psi_minus, bell_psi_plus,
                   fidelity, ghz, inner, noisy, normalize, plus_product,
                   random_state, w_state, zero)

__version__ = "0.1.0"
__all__ = [
    "HolographicMembrane", "KetBraPair", "coarse_grain", "overlap",
    "bell_phi_plus", "bell_phi_minus", "bell_psi_plus", "bell_psi_minus",
    "fidelity", "ghz", "inner", "noisy", "normalize", "plus_product",
    "random_state", "w_state", "zero", "__version__",
]
