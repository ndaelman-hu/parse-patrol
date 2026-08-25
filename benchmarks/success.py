"""Field-level success criteria for each parser's output model.

All parser models use ``Optional`` fields, so a parser that silently fails to
understand a file returns a near-empty model *without raising*. Merely checking
"no exception" therefore overcounts success. We instead inspect the fields that
actually carry scientific content.

Two graded signals, uniform across parsers so they are comparable:

* ``has_structure`` -- the parser extracted an atomic system (atoms + coordinates).
  This is the *primary* success criterion: it means the parser genuinely
  understood the file rather than returning an empty shell.
* ``has_energy`` -- the parser additionally extracted a total/SCF energy. A
  stricter, richer bar reported alongside the primary one.

Each criterion is keyed to the real fields of the corresponding Pydantic model
(see ``src/parse_patrol/parsers/<name>/utils.py``).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict


@dataclass(frozen=True)
class Verdict:
    has_structure: bool
    has_energy: bool

    @property
    def success(self) -> bool:
        """Primary success: a structure was extracted."""
        return self.has_structure


def _nonempty(value: Any) -> bool:
    """True if a model field carries data (non-None, and non-empty if sized)."""
    if value is None:
        return False
    if isinstance(value, (list, tuple, dict, str)):
        return len(value) > 0
    return True


def _ase_verdict(m: Any) -> Verdict:
    structure = bool(m.natom) and (_nonempty(m.positions) or _nonempty(m.scaled_positions))
    energy = m.energy is not None
    return Verdict(structure, energy)


def _cclib_verdict(m: Any) -> Verdict:
    structure = _nonempty(m.atomcoords) or (_nonempty(m.atomnos) and bool(m.natom))
    energy = any(_nonempty(getattr(m, f)) for f in ("scfenergies", "moenergies", "ccenergies", "mpenergies"))
    return Verdict(structure, energy)


def _gaussian_verdict(m: Any) -> Verdict:
    structure = _nonempty(m.atomcoords) and _nonempty(m.atomnos)
    energy = (m.final_energy is not None) or _nonempty(m.scfenergies)
    return Verdict(structure, energy)


def _iodata_verdict(m: Any) -> Verdict:
    structure = _nonempty(m.atnums) and _nonempty(m.atcoords)
    energy = m.energy is not None
    return Verdict(structure, energy)


VERDICTS: Dict[str, Callable[[Any], Verdict]] = {
    "ase": _ase_verdict,
    "cclib": _cclib_verdict,
    "gaussian": _gaussian_verdict,
    "iodata": _iodata_verdict,
}


def evaluate(parser: str, model: Any) -> Verdict:
    """Return the success Verdict for a parsed model produced by ``parser``."""
    return VERDICTS[parser](model)
