"""The canonical target schema the agent must produce, plus scoring helpers.

Modeled on the agent-produced reference outputs already in the repo
(``tests/.data/N5Ib.../h2o_*.csv``): molecular metadata, geometry, energetics,
vibrational, and atomic charges. We keep only directly-extractable, objectively-
scoreable fields (interpretive fields like symmetry label, mode assignment, or
hybridization are out of scope).

**Canonical units** (every arm's task prompt states these, so a mismatch is a
genuine agent unit error, not an ambiguity):

* coordinates  -> Angstrom
* energies     -> Hartree
* frequencies  -> cm^-1
* IR intensity -> km/mol
"""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

# Canonical unit constants, reused by the ground-truth adapters.
EV_PER_HARTREE = 27.211386245988
ANGSTROM_PER_BOHR = 0.529177210903


class Metadata(BaseModel):
    program: Optional[str] = Field(None, description="Simulation program, e.g. 'Gaussian'")
    formula: Optional[str] = Field(None, description="Hill-notation chemical formula, e.g. 'H2O'")
    charge: Optional[int] = Field(None, description="Net charge (e)")
    multiplicity: Optional[int] = Field(None, description="Spin multiplicity")
    n_atoms: Optional[int] = Field(None, description="Number of atoms")


class Geometry(BaseModel):
    elements: Optional[List[str]] = Field(None, description="Element symbols, per atom")
    atomic_numbers: Optional[List[int]] = Field(None, description="Atomic numbers, per atom")
    coords: Optional[List[List[float]]] = Field(None, description="(N,3) Cartesian coords, Angstrom")


class Energetics(BaseModel):
    scf_energy: Optional[float] = Field(None, description="Final SCF/total energy, Hartree")
    zpve: Optional[float] = Field(None, description="Zero-point vibrational energy, Hartree")
    enthalpy: Optional[float] = Field(None, description="Sum of electronic and thermal enthalpies, Hartree")
    free_energy: Optional[float] = Field(None, description="Sum of electronic and thermal free energies, Hartree")


class Vibrational(BaseModel):
    frequencies_cm1: Optional[List[float]] = Field(None, description="Vibrational frequencies, cm^-1")
    ir_intensities: Optional[List[float]] = Field(None, description="IR intensities, km/mol")


class Charges(BaseModel):
    mulliken: Optional[List[float]] = Field(None, description="Mulliken atomic charges, per atom")


class TargetSchema(BaseModel):
    """The goal format the agent is asked to fill from a source file."""

    metadata: Metadata = Field(default_factory=Metadata)  # type: ignore[arg-type]
    geometry: Geometry = Field(default_factory=Geometry)  # type: ignore[arg-type]
    energetics: Energetics = Field(default_factory=Energetics)  # type: ignore[arg-type]
    vibrational: Vibrational = Field(default_factory=Vibrational)  # type: ignore[arg-type]
    charges: Charges = Field(default_factory=Charges)  # type: ignore[arg-type]


# Dotted field paths, grouped by how strictly we score them.
# CORE: a task counts as a success only if every CORE field that ground truth
# provides is reproduced correctly. OPTIONAL fields count toward precision/recall
# but not the pass/fail flag.
CORE_FIELDS = [
    "metadata.n_atoms",
    "geometry.elements",
    "geometry.coords",
    "energetics.scf_energy",
]
OPTIONAL_FIELDS = [
    "metadata.program",
    "metadata.formula",
    "metadata.charge",
    "metadata.multiplicity",
    "geometry.atomic_numbers",
    "energetics.zpve",
    "energetics.enthalpy",
    "energetics.free_energy",
    "vibrational.frequencies_cm1",
    "vibrational.ir_intensities",
    "charges.mulliken",
]
ALL_FIELDS = CORE_FIELDS + OPTIONAL_FIELDS


def get_field(obj: dict, dotted: str):
    """Fetch a dotted field path from a plain dict, returning None if absent."""
    cur = obj
    for part in dotted.split("."):
        if not isinstance(cur, dict) or cur.get(part) is None:
            return None
        cur = cur[part]
    return cur


def schema_json_hint() -> str:
    """A compact JSON skeleton of the target schema for the task prompt."""
    return (
        "{\n"
        '  "metadata": {"program": str, "formula": str (Hill), "charge": int, '
        '"multiplicity": int, "n_atoms": int},\n'
        '  "geometry": {"elements": [str], "atomic_numbers": [int], '
        '"coords": [[x,y,z], ...] (Angstrom)},\n'
        '  "energetics": {"scf_energy": float (Hartree), "zpve": float (Hartree), '
        '"enthalpy": float (Hartree), "free_energy": float (Hartree)},\n'
        '  "vibrational": {"frequencies_cm1": [float], "ir_intensities": [float] (km/mol)},\n'
        '  "charges": {"mulliken": [float]}\n'
        "}"
    )
