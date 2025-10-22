"""
Core CCLib parsing functionality for direct Python usage.
This module provides sync functions that can be imported and used directly.
"""

import cclib
from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field # pyright: ignore[reportMissingImports]


class CCDataModel(BaseModel):
    """Pydantic model for CCLib parsed data."""
    class Config:
        validate_assignment = True
    
    # Format and metadata information
    source_format: Optional[str] = Field(None, description="Detected file format/software (e.g., 'gaussian', 'orca', 'qchem')")
    source_version: Optional[str] = Field(None, description="Software version if detected (e.g., 'Gaussian 16', 'ORCA 5.0')")
    file_extension: Optional[str] = Field(None, description="Original file extension (e.g., '.log', '.out', '.fchk')")
    
    aonames: Optional[List[str]] = Field(None, description="Atomic orbital names (list of strings)")
    aooverlaps: Optional[List] = Field(None, description="Atomic orbital overlap matrix (array of rank 2)")
    atombasis: Optional[List[List[int]]] = Field(None, description="Indices of atomic orbitals on each atom (list of lists)")
    atomcharges: Optional[Dict[str, List]] = Field(None, description="Atomic partial charges (dict of arrays of rank 1)")
    atomcoords: Optional[List] = Field(None, description="Atom coordinates (angstroms, array of rank 3)")
    atommasses: Optional[List] = Field(None, description="Atom masses (daltons, array of rank 1)")
    atomnos: Optional[List] = Field(None, description="Atomic numbers (array of rank 1)")
    atomspins: Optional[Dict[str, List]] = Field(None, description="Atomic spin densities (dict of arrays of rank 1)")
    ccenergies: Optional[List] = Field(None, description="Molecular energies with Coupled-Cluster corrections (eV, array of rank 2)")
    charge: Optional[int] = Field(None, description="Net charge of the system (integer)")
    coreelectrons: Optional[List] = Field(None, description="Number of core electrons in atom pseudopotentials (array of rank 1)")
    dispersionenergies: Optional[List] = Field(None, description="Dispersion energy corrections (eV, array of rank 1)")
    enthalpy: Optional[float] = Field(None, description="Sum of electronic and thermal enthalpies (hartree/particle, float)")
    entropy: Optional[float] = Field(None, description="Entropy (hartree/particle*kelvin, float)")
    etenergies: Optional[List] = Field(None, description="Energies of electronic transitions (1/cm, array of rank 1)")
    etoscs: Optional[List] = Field(None, description="Oscillator strengths of electronic transitions (array of rank 1)")
    etdips: Optional[List] = Field(None, description="Electric transition dipoles of electronic transitions (ebohr, array of rank 2)")
    etveldips: Optional[List] = Field(None, description="Velocity-gauge electric transition dipoles of electronic transitions (ebohr, array of rank 2)")
    etmagdips: Optional[List] = Field(None, description="Magnetic transition dipoles of electronic transitions (ebohr, array of rank 2)")
    etrotats: Optional[List] = Field(None, description="Rotatory strengths of electronic transitions (array of rank 1)")
    etsecs: Optional[List] = Field(None, description="Singly-excited configurations for electronic transitions (list of lists)")
    etsyms: Optional[List[str]] = Field(None, description="Symmetries of electronic transitions (list of strings)")
    freeenergy: Optional[float] = Field(None, description="Sum of electronic and thermal free energies (hartree/particle, float)")
    fonames: Optional[List[str]] = Field(None, description="Fragment orbital names (list of strings)")
    fooverlaps: Optional[List] = Field(None, description="Fragment orbital overlap matrix (array of rank 2)")
    fragnames: Optional[List[str]] = Field(None, description="Names of fragments (list of strings)")
    frags: Optional[List[List[int]]] = Field(None, description="Indices of atoms in a fragment (list of lists)")
    gbasis: Optional[Any] = Field(None, description="Coefficients and exponents of Gaussian basis functions (PyQuante format)")
    geotargets: Optional[List] = Field(None, description="Targets for convergence of geometry optimization (array of rank 1)")
    geovalues: Optional[List] = Field(None, description="Current values for convergence of geometry optimization (array of rank 1)")
    grads: Optional[List] = Field(None, description="Current values of forces (gradients) in geometry optimization (array of rank 3)")
    hessian: Optional[List] = Field(None, description="Elements of the force constant matrix (array of rank 1)")
    homos: Optional[List] = Field(None, description="Molecular orbital indices of HOMO(s) (array of rank 1)")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Various metadata about the package and computation (dict)")
    mocoeffs: Optional[List[List]] = Field(None, description="Molecular orbital coefficients (list of arrays of rank 2)")
    moenergies: Optional[List[List]] = Field(None, description="Molecular orbital energies (eV, list of arrays of rank 1)")
    moments: Optional[List] = Field(None, description="Molecular multipole moments (a.u., list of arrays)")
    mosyms: Optional[List[List[str]]] = Field(None, description="Orbital symmetries (list of lists)")
    mpenergies: Optional[List] = Field(None, description="Molecular electronic energies with Møller-Plesset corrections (eV, array of rank 2)")
    mult: Optional[int] = Field(None, description="Multiplicity of the system (integer)")
    natom: Optional[int] = Field(None, description="Number of atoms (integer)")
    nbasis: Optional[int] = Field(None, description="Number of basis functions (integer)")
    nmo: Optional[int] = Field(None, description="Number of molecular orbitals (integer)")
    nmrtensors: Optional[Dict[str, Dict[str, List]]] = Field(None, description="Nuclear magnetic resonance chemical shielding tensors (dict of dicts of array of rank 2)")
    nmrcouplingtensors: Optional[Dict[str, Dict[str, List]]] = Field(None, description="Nuclear magnetic resonance spin-spin coupling tensors (dict of dicts of array of rank 2)")
    nocoeffs: Optional[List] = Field(None, description="Natural orbital coefficients (array of rank 2)")
    nooccnos: Optional[List] = Field(None, description="Natural orbital occupation numbers (array of rank 1)")
    nsocoeffs: Optional[List] = Field(None, description="Natural spin orbital coefficients (list of array of rank 2)")
    nsooccnos: Optional[List] = Field(None, description="Natural spin orbital occupation numbers (list of array of rank 1)")
    optdone: Optional[bool] = Field(None, description="Flags whether an optimization has converged (Boolean)")
    optstatus: Optional[List] = Field(None, description="Optimization status for each set of atomic coordinates (array of rank 1)")
    polarizabilities: Optional[List] = Field(None, description="(Dipole) polarizabilities, static or dynamic (list of arrays of rank 2)")
    pressure: Optional[float] = Field(None, description="Pressure used for Thermochemistry (atm, float)")
    rotconsts: Optional[List] = Field(None, description="Rotational constants (GHz, array of rank 2)")
    scancoords: Optional[List] = Field(None, description="Geometries of each scan step (angstroms, array of rank 3)")
    scanenergies: Optional[List] = Field(None, description="Energies of potential energy surface (list)")
    scannames: Optional[List[str]] = Field(None, description="Names of variables scanned (list of strings)")
    scanparm: Optional[List] = Field(None, description="Values of parameters in potential energy surface (list of tuples)")
    scfenergies: Optional[List] = Field(None, description="Molecular electronic energies after SCF (Hartree-Fock, DFT) (eV, array of rank 1). Available from all QM software output files (.log, .out, .fchk)")
    scftargets: Optional[List] = Field(None, description="Targets for convergence of the SCF (array of rank 2)")
    scfvalues: Optional[List] = Field(None, description="Current values for convergence of the SCF (list of arrays of rank 2)")
    temperature: Optional[float] = Field(None, description="Temperature used for Thermochemistry (kelvin, float)")
    time: Optional[List] = Field(None, description="Time in molecular dynamics and other trajectories (fs, array of rank 1)")
    transprop: Optional[Dict[str, Any]] = Field(None, description="All absorption and emission spectra (dictionary)")
    vibanharms: Optional[List] = Field(None, description="Vibrational anharmonicity constants (1/cm, array of rank 2)")
    vibdisps: Optional[List] = Field(None, description="Cartesian displacement vectors (delta angstrom, array of rank 3)")
    vibfconsts: Optional[List] = Field(None, description="Force constants of vibrations (mDyne/angstrom, array of rank 1)")
    vibfreqs: Optional[List] = Field(None, description="Vibrational frequencies (1/cm, array of rank 1)")
    vibirs: Optional[List] = Field(None, description="IR intensities (km/mol, array of rank 1)")
    vibramans: Optional[List] = Field(None, description="Raman activities (A^4/Da, array of rank 1)")
    vibrmasses: Optional[List] = Field(None, description="Reduced masses of vibrations (daltons, array of rank 1)")
    vibsyms: Optional[List[str]] = Field(None, description="Symmetries of vibrations (list of strings)")
    zpve: Optional[float] = Field(None, description="Zero-point vibrational energy correction (hartree/particle, float)")


def ccdata_to_model(ccdata: cclib.parser.data.ccData, filepath: str = None) -> CCDataModel:  # type: ignore
    """Convert ccData object to CCDataModel (Pydantic) format.
    
    Args:
        ccdata: Parsed ccData object from cclib
        filepath: Original filepath for metadata extraction
    
    Returns:
        CCDataModel with converted data types for JSON serialization
    """
    result = {}
    
    # Add format metadata if available
    if filepath:
        import os
        result['file_extension'] = os.path.splitext(filepath)[1] if '.' in os.path.basename(filepath) else None
    
    # Extract software information from metadata if available
    if hasattr(ccdata, 'metadata') and ccdata.metadata:
        package_info = ccdata.metadata.get('package', '')
        if package_info:
            result['source_format'] = package_info.lower()
            result['source_version'] = ccdata.metadata.get('package_version', '')
    
    for field_name in CCDataModel.model_fields.keys():
        if field_name in ['source_format', 'source_version', 'file_extension']:
            continue  # Already handled above
            
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


def cclib_parse(filepath: str) -> CCDataModel:
    """Parse chemistry file using cclib and return as CCDataModel.
    
    This is the core sync function for direct usage in production code.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        CCDataModel with parsed data converted for JSON serialization
        
    Raises:
        FileNotFoundError: If file cannot be opened
        ValueError: If file cannot be parsed
    """
    filereader = cclib.io.ccopen(filepath)  # type: ignore
    if filereader is None:
        raise FileNotFoundError(f"File not found or unsupported format: {filepath}")
    
    ccdata = filereader.parse()
    if ccdata is None:
        raise ValueError(f"Failed to parse file: {filepath}")
        
    return ccdata_to_model(ccdata, filepath)


