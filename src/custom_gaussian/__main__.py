from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple
import re

from pydantic import BaseModel, Field
import periodictable
from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]


class CustomGaussianDataModel(BaseModel):
    # Common job info
    route: Optional[str] = Field(None, description="Gaussian route section (from .gjf or inferred)")
    title: Optional[str] = Field(None, description="Title section (from .gjf if present)")
    charge: Optional[int] = Field(None, description="Net charge")
    mult: Optional[int] = Field(None, description="Multiplicity")
    natom: Optional[int] = Field(None, description="Number of atoms")

    # Geometry
    atomnos: Optional[List[int]] = Field(None, description="Atomic numbers")
    atomcoords: Optional[List[List[float]]] = Field(None, description="Final geometry (angstroms)")

    # Energies & thermochemistry (Hartree unless noted)
    scfenergies: Optional[List[float]] = Field(None, description="SCF energies encountered (Hartree)")
    final_energy: Optional[float] = Field(None, description="Final SCF energy (Hartree)")
    zpve: Optional[float] = Field(None, description="Zero-point vibrational energy (Hartree/particle)")
    sum_electronic_and_zero_point: Optional[float] = Field(None, description="Sum of electronic and zero-point energies (Hartree)")
    sum_electronic_and_thermal_energies: Optional[float] = Field(None, description="Sum of electronic and thermal energies (Hartree)")
    sum_electronic_and_thermal_enthalpies: Optional[float] = Field(None, description="Sum of electronic and thermal enthalpies (Hartree)")
    sum_electronic_and_thermal_free_energies: Optional[float] = Field(None, description="Sum of electronic and thermal free energies (Hartree)")
    temperature: Optional[float] = Field(None, description="Thermochemistry temperature (K)")

    # Vibrations
    vibfreqs: Optional[List[float]] = Field(None, description="Vibrational frequencies (cm^-1)")
    vibirs: Optional[List[float]] = Field(None, description="IR intensities (km/mol)")
    vibrmasses: Optional[List[float]] = Field(None, description="Reduced masses (amu)")
    # vibdisps omitted for now due to complexity; can be added later

    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


mcp = FastMCP("Custom Gaussian Parser")


_float_re = r"[-+]?\d+(?:\.\d*)?(?:[DEde][+-]?\d+)?"
_re_charge_mult = re.compile(r"Charge\s*=\s*(-?\d+)\s+Multiplicity\s*=\s*(\d+)")
_re_scf_done = re.compile(r"SCF Done:\s+E\([^\)]+\)\s*=\s*(" + _float_re + r")")
_re_zpve = re.compile(r"Zero-point vibrational energy\s+(" + _float_re + r")")
_re_sum_zpe = re.compile(r"Sum of electronic and zero-point Energies=\s*(" + _float_re + r")")
_re_sum_therm_e = re.compile(r"Sum of electronic and thermal Energies=\s*(" + _float_re + r")")
_re_sum_therm_h = re.compile(r"Sum of electronic and thermal Enthalpies=\s*(" + _float_re + r")")
_re_sum_therm_g = re.compile(r"Sum of electronic and thermal Free Energies=\s*(" + _float_re + r")")
_re_temperature = re.compile(r"Temperature\s+(" + _float_re + r")")
_re_freqs = re.compile(r"Frequencies --\s*(.*)")
_re_ir = re.compile(r"IR Inten\s+--\s*(.*)")
_re_redmasses = re.compile(r"Red\.?\s*masses\s+--\s*(.*)", re.IGNORECASE)

# Standard orientation block headers in Gaussian logs
_re_std_orient_header = re.compile(r"^\s*Standard orientation:\s*$")
_re_orient_divider = re.compile(r"^\s*-{2,}\s*$")
# Columns: Center  Atomic  Atomic  Coordinates (Angstroms)
#          Number  Number   Type      X           Y           Z


def _safe_float(s: str) -> float:
    # Gaussian sometimes uses D for exponent
    return float(s.replace("D", "E").replace("d", "e"))


def _parse_last_standard_orientation(lines: List[str]) -> Tuple[Optional[List[int]], Optional[List[List[float]]]]:
    atomnos: List[int] = []
    coords: List[List[float]] = []

    i = 0
    last_block_start = -1
    while i < len(lines):
        if _re_std_orient_header.match(lines[i]):
            last_block_start = i
        i += 1

    if last_block_start == -1:
        return None, None

    i = last_block_start
    # Skip header line + two header rows (column headers + divider)
    # Find the first divider after the header line, then the next line after it is header, then another divider.
    # Practically, Gaussian prints:
    # Standard orientation:
    # ---------------------------------------------------------------------
    # Center     Atomic      Atomic             Coordinates (Angstroms)
    # Number     Number       Type             X           Y           Z
    # ---------------------------------------------------------------------
    # ... data ...
    # ---------------------------------------------------------------------
    # So skip until we hit the second divider, then read until the next divider.
    # Move to first divider
    while i < len(lines) and not _re_orient_divider.match(lines[i]):
        i += 1
    # Skip first divider and two header rows and second divider
    i += 1  # divider
    i += 2  # two header rows
    if i < len(lines) and _re_orient_divider.match(lines[i]):
        i += 1  # second divider

    # Now read data until next divider
    while i < len(lines) and not _re_orient_divider.match(lines[i]):
        parts = lines[i].split()
        if len(parts) >= 6:
            try:
                an = int(parts[1])
                x = float(parts[3])
                y = float(parts[4])
                z = float(parts[5])
                atomnos.append(an)
                coords.append([x, y, z])
            except ValueError as e:
                print(f"Error parsing geometry line '{lines[i]}': {e}")
        i += 1

    if not atomnos:
        return None, None
    return atomnos, coords


def _parse_log_or_out(path: Path) -> CustomGaussianDataModel:
    text = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    charge: Optional[int] = None
    mult: Optional[int] = None
    scfenergies: List[float] = []
    final_energy: Optional[float] = None
    zpve: Optional[float] = None
    sum_e_zpe: Optional[float] = None
    sum_e_therm: Optional[float] = None
    sum_h_therm: Optional[float] = None
    sum_g_therm: Optional[float] = None
    temperature: Optional[float] = None

    vibfreqs: List[float] = []
    vibirs: List[float] = []
    vibrmasses: List[float] = []

    for line in text:
        if charge is None or mult is None:
            m = _re_charge_mult.search(line)
            if m:
                charge = int(m.group(1))
                mult = int(m.group(2))
                continue

        m = _re_scf_done.search(line)
        if m:
            e = _safe_float(m.group(1))
            scfenergies.append(e)
            final_energy = e
            continue

        if zpve is None:
            m = _re_zpve.search(line)
            if m:
                zpve = _safe_float(m.group(1))
                continue

        if sum_e_zpe is None:
            m = _re_sum_zpe.search(line)
            if m:
                sum_e_zpe = _safe_float(m.group(1))
                continue

        if sum_e_therm is None:
            m = _re_sum_therm_e.search(line)
            if m:
                sum_e_therm = _safe_float(m.group(1))
                continue

        if sum_h_therm is None:
            m = _re_sum_therm_h.search(line)
            if m:
                sum_h_therm = _safe_float(m.group(1))
                continue

        if sum_g_therm is None:
            m = _re_sum_therm_g.search(line)
            if m:
                sum_g_therm = _safe_float(m.group(1))
                continue

        if temperature is None:
            m = _re_temperature.search(line)
            if m:
                try:
                    temperature = _safe_float(m.group(1))
                except Exception:
                    pass

        m = _re_freqs.search(line)
        if m:
            try:
                vibfreqs.extend([_safe_float(x) for x in m.group(1).split()])
            except Exception:
                pass
            continue

        m = _re_ir.search(line)
        if m:
            try:
                vibirs.extend([_safe_float(x) for x in m.group(1).split()])
            except Exception:
                pass
            continue

        m = _re_redmasses.search(line)
        if m:
            try:
                vibrmasses.extend([_safe_float(x) for x in m.group(1).split()])
            except Exception:
                pass
            continue

    atomnos, coords = _parse_last_standard_orientation(text)
    natom = len(atomnos) if atomnos else None

    return CustomGaussianDataModel(
        charge=charge,
        mult=mult,
        natom=natom,
        atomnos=atomnos,
        atomcoords=coords,
        scfenergies=scfenergies or None,
        final_energy=final_energy,
        zpve=zpve,
        sum_electronic_and_zero_point=sum_e_zpe,
        sum_electronic_and_thermal_energies=sum_e_therm,
        sum_electronic_and_thermal_enthalpies=sum_h_therm,
        sum_electronic_and_thermal_free_energies=sum_g_therm,
        temperature=temperature,
        vibfreqs=vibfreqs or None,
        vibirs=vibirs or None,
        vibrmasses=vibrmasses or None,
        metadata={"source": str(path), "parser": "gaussian-log"},
    )


def _parse_gjf(path: Path) -> CustomGaussianDataModel:
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()

    # Gaussian input format:
    # (Link0 commands, optional)
    # # route line(s)
    #
    # title
    #
    # charge mult
    # geometry...
    route_lines: List[str] = []
    title: Optional[str] = None
    charge: Optional[int] = None
    mult: Optional[int] = None
    atomnos: List[int] = []
    coords: List[List[float]] = []

    i = 0
    # Skip Link0 lines (start with %)
    while i < len(lines) and lines[i].strip().startswith("%"):
        i += 1

    # Route section starts with '#'
    while i < len(lines) and lines[i].strip().startswith("#"):
        route_lines.append(lines[i].strip())
        i += 1

    # Skip blank line
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # Title
    if i < len(lines):
        title = lines[i].rstrip()
        i += 1

    # Skip blank line
    while i < len(lines) and lines[i].strip() == "":
        i += 1

    # Charge and multiplicity
    if i < len(lines):
        parts = lines[i].split()
        if len(parts) >= 2:
            try:
                charge = int(parts[0])
                mult = int(parts[1])
            except Exception:
                pass
        i += 1

    # Geometry block until blank line or section break
    # Configurable or extensible set of lattice vector identifiers to ignore in geometry
    # Gaussian may use "Tv", "Tv1", "Tv2", "Tv3", "Tv4", etc. for lattice vectors in periodic jobs.
    # You can extend this list as needed.
    lattice_vector_prefixes = ("Tv", "Tv1", "Tv2", "Tv3", "Tv4", "Tv5", "Tv6")
    periodic = set(lattice_vector_prefixes)
    # Use periodictable for comprehensive element mapping
    try:
        element_to_Z = {el.symbol: el.number for el in periodictable.elements if el.number}
    except ImportError:
        # Fallback minimal mapping if periodictable is not installed
        element_to_Z: Dict[str, int] = {
            "H": 1, "He": 2,
            "Li": 3, "Be": 4, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "Ne": 10,
            "Na": 11, "Mg": 12, "Al": 13, "Si": 14, "P": 15, "S": 16, "Cl": 17, "Ar": 18,
            "K": 19, "Ca": 20, "Sc": 21, "Ti": 22, "V": 23, "Cr": 24, "Mn": 25, "Fe": 26,
            "Co": 27, "Ni": 28, "Cu": 29, "Zn": 30, "Ga": 31, "Ge": 32, "As": 33, "Se": 34,
            "Br": 35, "Kr": 36, "Rb": 37, "Sr": 38, "Y": 39, "Zr": 40, "Nb": 41, "Mo": 42,
            "Tc": 43, "Ru": 44, "Rh": 45, "Pd": 46, "Ag": 47, "Cd": 48, "In": 49, "Sn": 50,
            "Sb": 51, "Te": 52, "I": 53, "Xe": 54,
        }

    while i < len(lines) and lines[i].strip() != "":
        parts = lines[i].split()
        if parts and parts[0] not in periodic and not parts[0].startswith("-"):
            symbol = parts[0]
            if symbol in element_to_Z and len(parts) >= 4:
                try:
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    atomnos.append(element_to_Z[symbol])
                    coords.append([x, y, z])
                except Exception:
                    pass
        i += 1

    natom = len(atomnos) if atomnos else None
    route = " ".join(route_lines) if route_lines else None

    return CustomGaussianDataModel(
        route=route,
        title=title,
        charge=charge,
        mult=mult,
        natom=natom,
        atomnos=atomnos or None,
        atomcoords=coords or None,
        metadata={"source": str(path), "parser": "gaussian-gjf"},
    )


def _parse_fchk(path: Path) -> CustomGaussianDataModel:
    # Minimal extraction: atomic numbers and coordinates if present.
    # Note: Formatted checkpoint keys:
    #  - Atomic numbers: "Atomic numbers"
    #  - Current cartesian coordinates: "Current cartesian coordinates"
    # Values may be in blocks over multiple lines.
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    atomnos: List[int] = []
    coords: List[float] = []

    def read_block(start_idx: int) -> Tuple[int, List[str]]:
        """
        Reads a block of lines from the input, starting at the given index, until a line matching the FCHK file header pattern is encountered.

        Args:
            start_idx (int): The index in the lines list to start reading from.

        Returns:
            Tuple[int, List[str]]: A tuple containing the index of the next header line and a list of string values collected from the block.

        Notes:
            The function uses a regular expression to detect FCHK file headers, which are lines that typically start with a label, followed by whitespace, a type indicator ('I', 'R', or 'L'), and a count (e.g., "Atomic numbers           I   N=Natom").
            The regex pattern used is: ^[A-Za-z].*\s+[IRL]\s+\d+
            - ^[A-Za-z] : Line starts with a letter (header label)
            - .*\s+     : Followed by any characters and at least one whitespace
            - [IRL]     : Followed by a single character indicating type (I: integer, R: real, L: logical)
            - \s+       : At least one whitespace
            - \d+       : One or more digits (count)
            Consider moving this regex to the module level for consistency with other patterns.
        """
        # Reads subsequent lines until a line matching the header regex is found:
        # i.e., a line that looks like "<Label>  <Type>  <Count>" (e.g., "Atomic numbers           I   N=Natom")
        vals: List[str] = []
        i = start_idx
        header_re = re.compile(r"^[A-Za-z].*\s+[IRL]\s+\d+")
        while i < len(lines):
            if header_re.match(lines[i]):
                break
            vals.extend(lines[i].split())
            i += 1
        return i, vals

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("Atomic numbers"):
            # Example: "Atomic numbers           I   N=Natom"
            i += 1
            i, vals = read_block(i)
            try:
                atomnos = [int(v) for v in vals]
            except Exception:
                atomnos = []
            continue
        if line.startswith("Current cartesian coordinates"):
            # Example: "Current cartesian coordinates    R   N=3*Natom"
            i += 1
            i, vals = read_block(i)
            try:
                floats = [float(v) for v in vals]
                coords = floats
            except Exception:
                coords = []
            continue
        i += 1

    natom = len(atomnos) if atomnos else None
    coord_triplets: Optional[List[List[float]]] = None
    if natom and len(coords) >= 3 * natom:
        coord_triplets = [coords[j:j+3] for j in range(0, 3 * natom, 3)]

    return CustomGaussianDataModel(
        natom=natom,
        atomnos=atomnos or None,
        atomcoords=coord_triplets or None,
        metadata={"source": str(path), "parser": "gaussian-fchk"},
    )


@mcp.tool()
def gauss_parse_file_to_model(filepath: str) -> CustomGaussianDataModel:
    """
    Parse a Gaussian file (.log/.out, .gjf/.com, .fchk) and return a CustomGaussianDataModel.

    - .log/.out: Extracts charge/multiplicity, last geometry, SCF energies, basic thermochemistry, vibrational frequencies/IR.
    - .gjf/.com: Extracts route, title, charge/multiplicity, and geometry.
    - .fchk: Extracts atomic numbers and coordinates.
    - .chk (binary): Not supported; convert with 'formchk' first.

    Args:
        filepath: Path to Gaussian file.

    Returns:
        CustomGaussianDataModel with parsed contents.
    """
    path = Path(filepath)
    if not path.exists():
        return CustomGaussianDataModel(metadata={"error": f"File not found: {filepath}"})

    ext = path.suffix.lower()

    if ext in {".log", ".out"}:
        return _parse_log_or_out(path)

    if ext in {".gjf", ".com"}:
        return _parse_gjf(path)

    if ext == ".fchk":
        return _parse_fchk(path)

    if ext == ".chk":
        return CustomGaussianDataModel(
            metadata={
                "source": str(path),
                "warning": "Binary .chk not supported. Convert to .fchk using: formchk input.chk output.fchk"
            }
        )

    return CustomGaussianDataModel(metadata={"source": str(path), "warning": f"Unrecognized extension: {ext}"})


mcp.run()