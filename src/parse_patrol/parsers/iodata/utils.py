import iodata as iodata_package
from typing import Optional, Dict, List
from pydantic import BaseModel, Field # pyright: ignore[reportMissingImports]


class IODataCubeModel(BaseModel):
    """The volumetric data from a cube (or similar) file."""

    origin: List[float] = Field(description="A 3D vector with the origin of the axes frame.")
    axes: List[List[float]] = Field(description="A (3, 3) array where each row represents the spacing between two neighboring grid points along the first, second and third axis, respectively.")
    data: List[List[List[float]]] = Field(description="A (K, L, M) array of data on a uniform grid.")
    shape: List[int] = Field(description="Shape of the rectangular grid.")


class IODataModel(BaseModel):
    """A container class for data loaded from (or to be written to) a file."""
    
    # Format and metadata information
    source_format: Optional[str] = Field(None, description="Detected file format/software (e.g., 'gaussian', 'vasp', 'orca')")
    source_extension: Optional[str] = Field(None, description="Original file extension or type (e.g., '.fchk', 'POSCAR', '.cube')")
    detected_software: Optional[str] = Field(None, description="Detected quantum chemistry software package")

    atcharges: Optional[Dict[str, List[float]]] = Field(None, description="A dictionary where keys are names of charge definitions and values are arrays with atomic charges (size N).")
    atcoords: Optional[List[List[float]]] = Field(None, description="A (N, 3) float array with Cartesian coordinates of the atoms.")
    atcorenums: Optional[List[float]] = Field(None, description="A (N,) float array with pseudo-potential core charges. The matrix elements corresponding to ghost atoms are zero.")
    atffparams: Optional[dict] = Field(None, description="A dictionary with arrays of atomic force field parameters (typically non-bonded). Keys include 'charges', 'vdw_radii', 'sigmas', 'epsilons', 'alphas' (atomic polarizabilities), 'c6s', 'c8s', 'c10s', 'buck_as', 'buck_bs', 'lj_as', 'core_charges', 'valence_charges', 'valence_widths', etc. Not all of them have to be present, depending on the use case.")
    atfrozen: Optional[List[bool]] = Field(None, description="A (N,) bool array with frozen atoms. (All atoms are free if this attribute is not set.)")
    atgradient: Optional[List[List[float]]] = Field(None, description="A (N, 3) float array with the first derivatives of the energy w.r.t. Cartesian atomic displacements.")
    athessian: Optional[List[List[float]]] = Field(None, description="A (3*N, 3*N) array containing the energy Hessian w.r.t Cartesian atomic displacements.")
    atmasses: Optional[List[float]] = Field(None, description="A (N,) float array with atomic masses.")
    atnums: Optional[List[int]] = Field(None, description="A (N,) int vector with the atomic numbers.")
    basisdef: Optional[str] = Field(None, description="A basis set definition, i.e. a dictionary whose keys are symbols (of chemical elements), atomic numbers (similar to previous, str to make distinction with following) or an atom index (integer referring to a specific atom in a molecule). The format of the values is to be decided when implementing a load function for basis set definitions.")
    bonds: Optional[List[int]] = Field(None, description="An (nbond, 3) array with the list of covalent bonds. Each row represents one bond and consists of three integers: first atom index (starting from zero), second atom index & an optional bond type. Numerical values of bond types are defined in ``iodata.periodic``.")
    cellvecs: Optional[List[float]] = Field(None, description="A (NP, 3) array with (real-space) cell vectors describing periodic boundary conditions. A single vector corresponds to a 1D cell, e.g. for a wire. Two vectors describe a 2D cell, e.g. for a membrane. Three vectors describe a 3D cell, e.g. a crystalline solid.")
    charge: Optional[float] = Field(None, description="The net charge of the system. When possible, this is derived from atcorenums and nelec.")
    core_energy: Optional[float] = Field(None, description="The Hartree-Fock energy due to the core orbitals.")
    cube: Optional[IODataCubeModel] = Field(None, description="An instance of Cube, describing the volumetric data from a cube (or similar) file. Common sources: Gaussian .cube files, VASP CHGCAR/LOCPOT files, or other volumetric density data.")
    energy: Optional[float] = Field(None, description="The total energy (electronic + nn) in Hartree. Available from most QM software output files (.log, .out, .fchk files).")
    extcharges: Optional[List[float]] = Field(None, description="Array with values of external charges, with shape (nextcharge, 4). First three columns for Cartesian X, Y and Z coordinates, last column for the actual charge. Used in QM/MM calculations.")
    extra: Optional[dict] = Field(None, description="A dictionary with additional data loaded from a file. Any data which cannot be assigned to the other attributes belongs here. It may be decided in future to move some of the results from this dictionary to IOData attributes, with a more final name.")
    g_rot: Optional[float] = Field(None, description="The rotational symmetry number of the molecule.")
    lot: Optional[str] = Field(None, description="The level of theory used to compute the orbitals (and other properties).")
    # mo: Optional[MolecularOrbitals] = Field(None, description="The molecular orbitals.")
    moments: Optional[dict] = Field(None, description="A dictionary with electrostatic multipole moments. Keys are (angmom, kind) tuples where angmom is an integer for the angular momentum and kind is 'c' for Cartesian or 'p' for pure functions (only for angmom >= 2). The corresponding values are 1D numpy arrays. The order of the components of the multipole moments follows the HORTON2_CONVENTIONS defined in :py:mod:`iodata.basis`.")
    nelec: Optional[float] = Field(None, description="The number of electrons.")
    # obasis: Optional[MolecularBasis] = Field(None, description="An OrderedDict containing parameters to instantiate a GOBasis class.")
    obasis_name: Optional[str] = Field(None, description="A name or DOI describing the basis set used for the orbitals in the mo attribute (if defined). The name should be consistent with those defined the `Basis Set Exchange <www.basissetexchange.org>`_.")
    one_ints: Optional[dict] = Field(None, description="Dictionary where keys are names and values are numpy arrays with one-body operators, typically integrals of a one-body operator with a pair of (Gaussian) basis functions. Names can start with ``olp`` (overlap), ``kin`` (kinetic energy), ``na`` (nuclear attraction), ``core`` (core hamiltonian), etc., or ``one`` (general one-electron integral). When relevant, these names must have a suffix ``_ao`` or ``_mo`` to clarify in which basis the integrals are computed. ``_ao`` is used to denote integrals in a non-orthogonal (atomic orbital) basis. ``_mo`` is used to denote an orthogonal (molecular orbital) basis. For the overlap integrals, this suffix can be omitted because it is only useful to compute them in the atomic-orbital basis.")
    one_rdms: Optional[dict] = Field(None, description="Dictionary where keys are names and values are one-particle density matrices. Names can be ``scf``, ``post_scf``, ``scf_spin``, ``post_scf_spin``. When relevant, these names must have a suffix ``_ao`` or ``_mo`` to clarify in which basis the RDMs are computed. ``_ao`` is used to denote a non-orthogonal (atomic orbital) basis. ``_mo`` is used to denote an orthogonal (molecular orbital) basis. For the SCF RDMs, this suffix can be omitted because it is only useful to compute them in the atomic-orbital basis.")
    run_type: Optional[str] = Field(None, description="The type of calculation that lead to the results stored in IOData, which must be one of the following: 'energy', 'energy_force', 'opt', 'scan', 'freq' or None.")
    spinpol: Optional[float] = Field(None, description="The spin polarization. When molecular orbitals are present, spinpol cannot be set and is derived as ``abs(nalpha - nbeta)``. When no molecular orbitals are present, this attribute can be set.")
    title: Optional[str] = Field(None, description="A suitable name for the data.")
    two_ints: Optional[dict] = Field(None, description="Dictionary where keys are names and values are numpy arrays with two-body operators, typically integrals of two-body operator with four of (Gaussian) basis functions. Names can start with ``er`` (electron repulsion) or ``two`` (general pairswise interaction). When relevant, these names must have a suffix ``_ao`` or ``_mo`` to clarify in which basis the integrals are computed.  See ``one_ints`` for more details. Array indexes are in physicists' notation.")
    two_rdms: Optional[dict] = Field(None, description="Dictionary where keys are names and values are two-particle density matrices. Names can be ``post_scf`` or ``post_scf_spin``. When relevant, these names must have a suffix ``_ao`` or ``_mo`` to clarify in which basis the RDMs are computed. See ``one_rdms`` for more details. Array indexes are in physicists' notation.")


def iodata_to_model(ext_data: iodata_package.IOData, filepath: Optional[str] = None) -> IODataModel: # pyright: ignore[reportAttributeAccessIssue]
    """Convert IOData object to IODataModel (Pydantic) format.
    
    Args:
        ext_data: Parsed iodata object from IOData
        filepath: Original filepath for metadata extraction
    
    Returns:
        IODataModel with converted data types for JSON serialization
    """
    result = {}
    
    # Add format metadata if available
    if filepath:
        import os
        basename = os.path.basename(filepath)
        ext = os.path.splitext(filepath)[1] if '.' in basename else None
        result['source_extension'] = ext or basename  # For VASP files without extensions
        
        # Detect software based on file patterns
        if ext in ['.fchk', '.log', '.out', '.gjf', '.com'] or 'gaussian' in filepath.lower():
            result['detected_software'] = 'Gaussian'
            result['source_format'] = 'gaussian'
        elif 'POSCAR' in basename or 'CONTCAR' in basename or 'OUTCAR' in basename or 'CHGCAR' in basename:
            result['detected_software'] = 'VASP'
            result['source_format'] = 'vasp'
        elif ext == '.cube' or '.cube' in basename:
            result['source_format'] = 'cube'
        elif ext in ['.xyz']:
            result['source_format'] = 'xyz'
        elif 'orca' in filepath.lower():
            result['detected_software'] = 'ORCA'
            result['source_format'] = 'orca'
        else:
            result['detected_software'] = None
            result['source_format'] = None
    
    for field_name in IODataModel.model_fields.keys():
        if field_name in ['source_format', 'source_extension', 'detected_software']:
            continue  # Already handled above
            
        value = getattr(ext_data, field_name, None)
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
    return IODataModel(**result)


def iodata_parse(filepath: str) -> IODataModel:
    """Parse chemistry file and return as IODataModel for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        IODataModel with parsed data converted for JSON serialization
    """
    data = iodata_package.load_one(filepath) # pyright: ignore[reportAttributeAccessIssue]
    return iodata_to_model(data, filepath)