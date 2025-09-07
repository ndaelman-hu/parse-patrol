import cclib
from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field



class CCDataModel(BaseModel):
    aonames: Optional[List[str]] = Field(
        None,
        description="Atomic orbital names. Not normalized; format varies by program.",
        pattern=r"^[A-Za-z0-9_\-]+$"
    )
    aooverlaps: Optional[List] = Field(
        None,
        description="Atomic orbital overlap matrix. Symmetric; needed for population analyses."
    )
    atombasis: Optional[List[List[int]]] = Field(
        None,
        description="Indices of atomic orbitals on each atom. Each sublist contains indices for one atom."
    )
    atomcharges: Optional[Dict[str, List]] = Field(
        None,
        description="Atomic partial charges. Keys are population analysis types (e.g., 'mulliken', 'chelpg').",
        pattern=r"^(mulliken|chelpg|lowdin|hirshfeld)$"
    )
    atomcoords: Optional[List] = Field(
        None,
        description="Atomic coordinates (angstroms). Shape (n, m, 3) for n geometries and m atoms."
    )
    atommasses: Optional[List] = Field(
        None,
        description="Atom masses (daltons). Unified atomic mass units."
    )
    atomnos: Optional[List] = Field(
        None,
        description="Atomic numbers. Number of protons in each atom."
    )
    atomspins: Optional[Dict[str, List]] = Field(
        None,
        description="Atomic spin densities. Keys are population analysis types (e.g., 'mulliken', 'lowdin').",
        pattern=r"^(mulliken|lowdin)$"
    )
    ccenergies: Optional[List] = Field(
        None,
        description="Molecular energies with Coupled-Cluster corrections (eV). Only highest theory level parsed."
    )
    charge: Optional[int] = Field(
        None,
        description="Net charge of the system (units of e)."
    )
    coreelectrons: Optional[List] = Field(
        None,
        description="Number of core electrons in atom pseudopotentials."
    )
    dispersionenergies: Optional[List] = Field(
        None,
        description="Dispersion energy corrections (eV). Only present for empirical models."
    )
    enthalpy: Optional[float] = Field(
        None,
        description="Sum of electronic and thermal enthalpies (hartree/particle)."
    )
    entropy: Optional[float] = Field(
        None,
        description="Entropy (hartree/particle*kelvin)."
    )
    etenergies: Optional[List] = Field(
        None,
        description="Energies of electronic transitions (1/cm). One per excited state."
    )
    etoscs: Optional[List] = Field(
        None,
        description="Oscillator strengths of electronic transitions. One per excited state."
    )
    etdips: Optional[List] = Field(
        None,
        description="Electric transition dipoles of electronic transitions (ebohr)."
    )
    etveldips: Optional[List] = Field(
        None,
        description="Velocity-gauge electric transition dipoles (ebohr)."
    )
    etmagdips: Optional[List] = Field(
        None,
        description="Magnetic transition dipoles (ebohr)."
    )
    etrotats: Optional[List] = Field(
        None,
        description="Rotatory strengths of electronic transitions."
    )
    etsecs: Optional[List] = Field(
        None,
        description="Singly-excited configurations for electronic transitions."
    )
    etsyms: Optional[List[str]] = Field(
        None,
        description="Symmetries of electronic transitions. One per excited state.",
        pattern=r"^[A-Za-z0-9_\-]+$"
    )
    freeenergy: Optional[float] = Field(
        None,
        description="Sum of electronic and thermal free energies (hartree/particle)."
    )
    fonames: Optional[List[str]] = Field(
        None,
        description="Fragment orbital names (ADF specific).",
        pattern=r"^[A-Za-z0-9_\-]+$"
    )
    fooverlaps: Optional[List] = Field(
        None,
        description="Fragment orbital overlap matrix (ADF specific)."
    )
    fragnames: Optional[List[str]] = Field(
        None,
        description="Names of fragments (ADF specific).",
        pattern=r"^[A-Za-z0-9_\-]+$"
    )
    frags: Optional[List[List[int]]] = Field(
        None,
        description="Indices of atoms in a fragment (ADF specific)."
    )
    gbasis: Optional[Any] = Field(
        None,
        description="Gaussian basis functions (PyQuante format)."
    )
    geotargets: Optional[List] = Field(
        None,
        description="Targets for geometry optimization convergence."
    )
    geovalues: Optional[List] = Field(
        None,
        description="Current values for geometry optimization criteria."
    )
    grads: Optional[List] = Field(
        None,
        description="Forces on atoms (negative energy gradient)."
    )
    hessian: Optional[List] = Field(
        None,
        description="Force constant matrix."
    )
    homos: Optional[List] = Field(
        None,
        description="Indexes of highest occupied molecular orbitals (HOMOs)."
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Metadata about the calculation."
    )
    mocoeffs: Optional[List[List]] = Field(
        None,
        description="Molecular orbital coefficients."
    )
    moenergies: Optional[List[List]] = Field(
        None,
        description="Molecular orbital energies (eV)."
    )
    moments: Optional[List] = Field(
        None,
        description="Dipole and higher multipole moments (see docs for order and units)."
    )
    mosyms: Optional[List[List[str]]] = Field(
        None,
        description="Orbital symmetries (normalized labels).",
        pattern=r"^[A-Za-z0-9_\-]+$"
    )
    mpenergies: Optional[List] = Field(
        None,
        description="Møller-Plesset correlation energies."
    )
    mult: Optional[int] = Field(
        None,
        description="Spin multiplicity."
    )
    natom: Optional[int] = Field(
        None,
        description="Number of atoms."
    )
    nbasis: Optional[int] = Field(
        None,
        description="Number of basis functions."
    )
    nmo: Optional[int] = Field(
        None,
        description="Number of molecular orbitals (typically equals nbasis)."
    )
    nmrtensors: Optional[Dict[str, Dict[str, List]]] = Field(
        None,
        description="NMR chemical shielding tensors (keys: total, paramagnetic, diamagnetic)."
    )
    nmrcouplingtensors: Optional[Dict[str, Dict[str, List]]] = Field(
        None,
        description="NMR spin-spin coupling tensors."
    )
    nocoeffs: Optional[List] = Field(
        None,
        description="Natural orbital coefficients."
    )
    nooccnos: Optional[List] = Field(
        None,
        description="Natural orbital occupation numbers."
    )
    nsocoeffs: Optional[List] = Field(
        None,
        description="Natural spin orbital coefficients."
    )
    nsooccnos: Optional[List] = Field(
        None,
        description="Natural spin orbital occupation numbers."
    )
    optdone: Optional[bool] = Field(
        None,
        description="Flags whether an optimization has converged."
    )
    optstatus: Optional[List] = Field(
        None,
        description="Optimization status for each step (bit value notation)."
    )
    polarizabilities: Optional[List] = Field(
        None,
        description="(Dipole) polarizabilities, static or dynamic."
    )
    pressure: Optional[float] = Field(
        None,
        description="Pressure used for Thermochemistry (atm)."
    )
    rotconsts: Optional[List] = Field(
        None,
        description="Rotational constants (GHz)."
    )
    scancoords: Optional[List] = Field(
        None,
        description="Geometries for each scan step."
    )
    scanenergies: Optional[List] = Field(
        None,
        description="Energies at each scan point."
    )
    scannames: Optional[List[str]] = Field(
        None,
        description="Names of scanned parameters.",
        pattern=r"^[A-Za-z0-9_\-]+$"
    )
    scanparm: Optional[List] = Field(
        None,
        description="Values of scanned parameters."
    )
    scfenergies: Optional[List] = Field(
        None,
        description="Converged SCF energies (eV)."
    )
    scftargets: Optional[List] = Field(
        None,
        description="SCF convergence targets."
    )
    scfvalues: Optional[List] = Field(
        None,
        description="Current SCF convergence values."
    )
    temperature: Optional[float] = Field(
        None,
        description="Temperature used for Thermochemistry (kelvin)."
    )
    time: Optional[List] = Field(
        None,
        description="Time in molecular dynamics/trajectories (fs)."
    )
    transprop: Optional[Dict[str, Any]] = Field(
        None,
        description="Absorption/emission spectra."
    )
    vibanharms: Optional[List] = Field(
        None,
        description="Vibrational anharmonicity constants (1/cm)."
    )
    vibdisps: Optional[List] = Field(
        None,
        description="Cartesian displacement vectors (delta angstrom)."
    )
    vibfconsts: Optional[List] = Field(
        None,
        description="Force constants of vibrations (mDyne/angstrom)."
    )
    vibfreqs: Optional[List] = Field(
        None,
        description="Vibrational frequencies (1/cm)."
    )
    vibirs: Optional[List] = Field(
        None,
        description="IR intensities (km/mol)."
    )
    vibramans: Optional[List] = Field(
        None,
        description="Raman activities (A^4/Da)."
    )
    vibrmasses: Optional[List] = Field(
        None,
        description="Reduced masses of vibrations (daltons)."
    )
    vibsyms: Optional[List[str]] = Field(
        None,
        description="Symmetries of vibrations.",
        pattern=r"^[A-Za-z0-9_\-]+$"
    )
    zpve: Optional[float] = Field(
        None,
        description="Zero-point vibrational energy correction (hartree/particle)."
    )


def ccdata_to_model(ccdata: cclib.parser.data.ccData) -> CCDataModel: # type: ignore
    """Convert ccData object to CCDataModel (Pydantic) format.
    
    Args:
        ccdata: Parsed ccData object from cclib
    
    Returns:
        CCDataModel with converted data types for JSON serialization
    """
    result = {}
    for field_name in CCDataModel.model_fields.keys():
        if hasattr(ccdata, field_name):
            value = getattr(ccdata, field_name)
            if value is None:
                continue
            if hasattr(value, 'tolist'):
                result[field_name] = value.tolist()
            elif isinstance(value, dict):
                result[field_name] = {k: v.tolist() if hasattr(v, 'tolist') else v for k, v in value.items()}
            elif isinstance(value, list) and value and hasattr(value[0], 'tolist'):
                result[field_name] = [item.tolist() for item in value]
            else:
                result[field_name] = value
    return CCDataModel(**result)

mcp = FastMCP("CCLib Chemistry Parser")


@mcp.tool()
def parse_file_to_model(filepath: str) -> CCDataModel:
    """Parse chemistry file and return as CCDataModel for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        CCDataModel with parsed data converted for JSON serialization
    """
    ccdata = cclib.io.ccopen(filepath) # type: ignore
    if ccdata is None:
        return CCDataModel()
    ccdata.parse()
    return ccdata_to_model(ccdata)


mcp.run()
