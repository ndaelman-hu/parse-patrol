"""Build reference (ground-truth) target-schema answers from parser output.

Each parser exposes its data in its own field names and *its own units*
(cclib: eV + Angstrom; ASE: eV + Angstrom; iodata: Hartree + Bohr; custom
Gaussian: Hartree + Angstrom). The adapters below canonicalize everything to the
target schema's units (Angstrom, Hartree, cm^-1, km/mol) so the reference is
directly comparable to whatever the agent produces — and so that a units mismatch
in the agent's output is a real error, not an artifact.

We reuse the actual parse functions from ``parse_patrol`` (not a reimplementation),
so the ground truth is exactly what a correct use of the tools would yield.
"""

from __future__ import annotations

import collections
from typing import Any, Callable, Dict, List, Optional

from ase.data import chemical_symbols

from agent_study.target_schema import ANGSTROM_PER_BOHR, EV_PER_HARTREE


def _symbols(atomic_numbers: Optional[List[int]]) -> Optional[List[str]]:
    if not atomic_numbers:
        return None
    return [chemical_symbols[int(z)] for z in atomic_numbers]


def _hill_formula(atomic_numbers: Optional[List[int]]) -> Optional[str]:
    if not atomic_numbers:
        return None
    counts = collections.Counter(chemical_symbols[int(z)] for z in atomic_numbers)
    order: List[str] = []
    if "C" in counts:
        order.append("C")
        if "H" in counts:
            order.append("H")
    order += sorted(s for s in counts if s not in order)
    return "".join(s + (str(counts[s]) if counts[s] > 1 else "") for s in order)


def _last_geometry(atomcoords: Any) -> Optional[List[List[float]]]:
    """cclib stores coords as (nsteps, natom, 3); take the final step."""
    if not atomcoords:
        return None
    first = atomcoords[0]
    if isinstance(first, list) and first and isinstance(first[0], list):
        return [list(map(float, row)) for row in atomcoords[-1]]  # trajectory
    return [list(map(float, row)) for row in atomcoords]  # already (natom, 3)


def _scale_coords(coords: Optional[List[List[float]]], factor: float) -> Optional[List[List[float]]]:
    if coords is None:
        return None
    return [[c * factor for c in row] for row in coords]


def _floats(values: Any) -> Optional[List[float]]:
    if not values:
        return None
    return [float(v) for v in values]


def _prune(d: Dict[str, Any]) -> Dict[str, Any]:
    """Drop None-valued leaves and now-empty groups so the reference only asserts
    fields that were actually extracted."""
    out: Dict[str, Any] = {}
    for group, fields in d.items():
        kept = {k: v for k, v in fields.items() if v is not None}
        if kept:
            out[group] = kept
    return out


def _from_cclib(m: Any) -> Dict[str, Any]:
    atomic_numbers = [int(z) for z in m.atomnos] if m.atomnos else None
    scf = m.scfenergies[-1] / EV_PER_HARTREE if m.scfenergies else None  # cclib: eV
    mulliken = None
    if m.atomcharges and isinstance(m.atomcharges, dict):
        mulliken = _floats(m.atomcharges.get("mulliken"))
    return {
        "metadata": {"formula": _hill_formula(atomic_numbers), "charge": m.charge,
                     "multiplicity": m.mult, "n_atoms": m.natom},
        "geometry": {"elements": _symbols(atomic_numbers), "atomic_numbers": atomic_numbers,
                     "coords": _last_geometry(m.atomcoords)},  # cclib: Angstrom
        "energetics": {"scf_energy": scf, "zpve": m.zpve, "enthalpy": m.enthalpy,
                       "free_energy": m.freeenergy},  # cclib thermo: Hartree
        "vibrational": {"frequencies_cm1": _floats(m.vibfreqs), "ir_intensities": _floats(m.vibirs)},
        "charges": {"mulliken": mulliken},
    }


def _from_ase(m: Any) -> Dict[str, Any]:
    atomic_numbers = [int(z) for z in m.numbers] if m.numbers else None
    energy = m.energy / EV_PER_HARTREE if m.energy is not None else None  # ASE: eV
    return {
        "metadata": {"formula": m.chemical_formula or _hill_formula(atomic_numbers),
                     "n_atoms": m.natom},
        "geometry": {"elements": list(m.symbols) if m.symbols else _symbols(atomic_numbers),
                     "atomic_numbers": atomic_numbers,
                     "coords": _last_geometry(m.positions)},  # ASE: Angstrom
        "energetics": {"scf_energy": energy},
        "vibrational": {},
        "charges": {},
    }


def _from_gaussian(m: Any) -> Dict[str, Any]:
    atomic_numbers = [int(z) for z in m.atomnos] if m.atomnos else None
    scf = m.final_energy if m.final_energy is not None else (m.scfenergies[-1] if m.scfenergies else None)
    return {
        "metadata": {"program": "Gaussian", "formula": _hill_formula(atomic_numbers),
                     "charge": m.charge, "multiplicity": m.mult, "n_atoms": m.natom},
        "geometry": {"elements": _symbols(atomic_numbers), "atomic_numbers": atomic_numbers,
                     "coords": _last_geometry(m.atomcoords)},  # Gaussian: Angstrom
        "energetics": {"scf_energy": scf, "zpve": m.zpve,  # Gaussian: Hartree
                       "enthalpy": m.sum_electronic_and_thermal_enthalpies,
                       "free_energy": m.sum_electronic_and_thermal_free_energies},
        "vibrational": {"frequencies_cm1": _floats(m.vibfreqs), "ir_intensities": _floats(m.vibirs)},
        "charges": {},
    }


def _from_iodata(m: Any) -> Dict[str, Any]:
    atomic_numbers = [int(z) for z in m.atnums] if m.atnums else None
    charge = int(round(m.charge)) if m.charge is not None else None
    return {
        "metadata": {"formula": _hill_formula(atomic_numbers), "charge": charge,
                     "n_atoms": len(atomic_numbers) if atomic_numbers else None},
        "geometry": {"elements": _symbols(atomic_numbers), "atomic_numbers": atomic_numbers,
                     "coords": _scale_coords(_last_geometry(m.atcoords), ANGSTROM_PER_BOHR)},  # iodata: Bohr
        "energetics": {"scf_energy": m.energy},  # iodata: Hartree
        "vibrational": {},
        "charges": {},
    }


_ADAPTERS: Dict[str, Callable[[Any], Dict[str, Any]]] = {
    "cclib": _from_cclib,
    "ase": _from_ase,
    "gaussian": _from_gaussian,
    "iodata": _from_iodata,
}

_PARSE_FNS: Dict[str, tuple] = {
    "cclib": ("parse_patrol.parsers.cclib.utils", "cclib_parse"),
    "ase": ("parse_patrol.parsers.ase.utils", "ase_parse"),
    "gaussian": ("parse_patrol.parsers.gaussian.utils", "gaussian_parse"),
    "iodata": ("parse_patrol.parsers.iodata.utils", "iodata_parse"),
}


def extract(parser: str, filepath: str) -> Optional[Dict[str, Any]]:
    """Parse ``filepath`` with ``parser`` and adapt to the target schema.

    Returns a pruned dict (only extracted fields), or None if the parser fails or
    yields no atomic structure.
    """
    import importlib

    mod, fn = _PARSE_FNS[parser]
    parse = getattr(importlib.import_module(mod), fn)
    try:
        model = parse(filepath)
    except BaseException:
        return None
    adapted = _prune(_ADAPTERS[parser](model))
    geom = adapted.get("geometry", {})
    if not (geom.get("coords") and geom.get("elements")):
        return None  # no usable structure -> not a valid reference
    return adapted


def _richness(ref: Dict[str, Any]) -> int:
    return sum(len(v) for v in ref.values() if isinstance(v, dict))


def _merge(into: Dict[str, Any], src: Dict[str, Any]) -> None:
    """Union src into `into`: fill missing fields; prefer the longer value for
    list-valued fields (a richer extraction of the same quantity)."""
    for group, fields in src.items():
        dst = into.setdefault(group, {})
        for k, v in fields.items():
            if v is None:
                continue
            cur = dst.get(k)
            if cur is None:
                dst[k] = v
            elif isinstance(v, list) and isinstance(cur, list) and len(v) > len(cur):
                dst[k] = v


def union_reference(filepath: str, candidate_parsers: List[str],
                    program: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Reference = union of every succeeding parser's extraction (not one parser).

    A single parser is a *lower bound* on extractable fields — one gets geometry,
    another gets energy/charges — so scoring against one parser mislabels the
    agent's extra correct fields as hallucinations. Merging fixes that. ``program``
    (known from the dataset) is stamped in, since most adapters don't set it.
    Returns None if no parser yields a usable structure.
    """
    merged: Dict[str, Any] = {}
    used: List[str] = []
    for parser in candidate_parsers:
        ref = extract(parser, filepath)
        if ref is not None:
            _merge(merged, ref)
            used.append(parser)
    if not merged.get("geometry", {}).get("coords"):
        return None
    if program:
        merged.setdefault("metadata", {})["program"] = program
    merged["_reference_parsers"] = used
    return merged
