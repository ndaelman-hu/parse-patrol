import ase  # pyright: ignore[reportMissingImports]
import ase.io  # pyright: ignore[reportMissingImports]
from typing import Optional, Dict, List, Annotated
from pydantic import BaseModel, Field # pyright: ignore[reportMissingImports]

# Type aliases for constrained arrays
Vector3 = Annotated[List[float], Field(min_length=3, max_length=3)]
Vector6 = Annotated[List[float], Field(min_length=6, max_length=6)]
PBCFlags = Annotated[List[bool], Field(min_length=3, max_length=3)]

class ASEDataModel(BaseModel):
    """A container class for data loaded from (or to be written to) a file using ASE."""

    # Format and metadata information
    source_format: Optional[str] = Field(None, description="Detected file format/software (e.g., 'gaussian', 'vasp', 'orca', 'xyz')")
    source_extension: Optional[str] = Field(None, description="Original file extension or type (e.g., '.fchk', 'POSCAR', '.cube', '.xyz')")
    detected_software: Optional[str] = Field(None, description="Detected quantum chemistry software package")

    # Core structural properties
    natom: Optional[int] = Field(None, description="Number of atoms")
    positions: Optional[List[Vector3]] = Field(None, description="Cartesian coordinates of atoms (Angstrom)")
    scaled_positions: Optional[List[Vector3]] = Field(None, description="Fractional coordinates within unit cell")
    numbers: Optional[List[int]] = Field(None, description="Atomic numbers")
    symbols: Optional[List[str]] = Field(None, description="Chemical element symbols")
    chemical_formula: Optional[str] = Field(None, description="Chemical formula string")
    masses: Optional[List[float]] = Field(None, description="Atomic masses (amu)")
    tags: Optional[List[int]] = Field(None, description="Integer tags for atoms")
    charges: Optional[List[float]] = Field(None, description="Initial atomic charges")
    momenta: Optional[List[Vector3]] = Field(None, description="Momentum vectors")
    velocities: Optional[List[Vector3]] = Field(None, description="Velocity vectors (Angstrom/fs)")

    # Unit cell and periodicity
    cell: Optional[List[Vector3]] = Field(None, description="Unit cell vectors (Angstrom)")
    cell_lengths_and_angles: Optional[Vector6] = Field(None, description="Cell parameters: [a, b, c, alpha, beta, gamma] (Angstrom and degrees)")
    pbc: Optional[PBCFlags] = Field(None, description="Periodic boundary condition flags")
    celldisp: Optional[Vector3] = Field(None, description="Unit cell displacement vectors (Angstrom)")

    # Computational properties (from calculator)
    forces: Optional[List[Vector3]] = Field(None, description="Atomic forces (eV/Angstrom)")
    energy: Optional[float] = Field(None, description="Total potential energy (eV)")
    potential_energies: Optional[List[float]] = Field(None, description="Per-atom potential energies (eV)")
    kinetic_energy: Optional[float] = Field(None, description="Kinetic energy of nuclei (eV)")
    stress: Optional[Vector6] = Field(None, description="Stress tensor (eV/Angstrom^3)")
    stresses: Optional[List[Vector6]] = Field(None, description="Per-atom stress tensors (eV/Angstrom^3)")

    # Magnetic properties
    initial_magnetic_moments: Optional[List[float]] = Field(None, description="Initial magnetic moments (Bohr magneton)")
    magnetic_moments: Optional[List[float]] = Field(None, description="Calculated magnetic moments (Bohr magneton)")
    magnetic_moment: Optional[float] = Field(None, description="Total magnetic moment (Bohr magneton)")

    # Derived properties
    center_of_mass: Optional[Vector3] = Field(None, description="Center of mass (Angstrom)")
    moments_of_inertia: Optional[Vector3] = Field(None, description="Principal moments of inertia (amu*Angstrom^2)")
    angular_momentum: Optional[Vector3] = Field(None, description="Total angular momentum (amu*Angstrom^2/fs)")
    volume: Optional[float] = Field(None, description="Unit cell volume (Angstrom^3)")
    temperature: Optional[float] = Field(None, description="Kinetic temperature (Kelvin)")
    dipole_moment: Optional[Vector3] = Field(None, description="Electric dipole moment (eA)")

    # Additional attributes
    constraints: Optional[List[Dict]] = Field(None, description="Applied constraints as list of dictionaries")
    info: Optional[Dict] = Field(None, description="Dictionary with additional metadata and information")

def ase_to_model(ext_data: ase.Atoms, filepath: str | None = None) -> ASEDataModel:
    """Convert ASE Atoms object to ASEDataModel (Pydantic) format.

    Args:
        ext_data: Parsed Atoms object from ASE
        filepath: Original filepath for metadata extraction

    Returns:
        ASEDataModel with converted data types for JSON serialization
    """
    result = {}

    # Add format metadata if available
    if filepath:
        import os
        basename = os.path.basename(filepath)
        ext = os.path.splitext(filepath)[1].lower() if '.' in basename else None
        result['source_extension'] = ext or basename  # For files without extensions

        # Initialize format variables
        detected_format = None
        detected_software = None

        # === Filename Pattern Matching (highest priority) ===
        basename_lower = basename.lower()

        # VASP files
        if any(x in basename for x in ['POSCAR', 'CONTCAR']):
            detected_format, detected_software = 'vasp', 'VASP'
        elif 'OUTCAR' in basename:
            detected_format, detected_software = 'vasp-out', 'VASP'
        elif 'XDATCAR' in basename:
            detected_format, detected_software = 'vasp-xdatcar', 'VASP'
        elif 'vasp' in basename_lower and '.xml' in basename_lower:
            detected_format, detected_software = 'vasp-xml', 'VASP'
        elif any(x in basename for x in ['CHGCAR', 'LOCPOT']):
            detected_format, detected_software = 'cube', 'VASP'

        # DL_POLY files
        elif basename == 'HISTORY':
            detected_format, detected_software = 'dlp-history', 'DL_POLY'

        # Turbomole files
        elif basename == 'coord':
            detected_format, detected_software = 'turbomole', 'Turbomole'
        elif basename == 'gradient':
            detected_format, detected_software = 'turbomole-gradient', 'Turbomole'

        # ELK files
        elif basename == 'GEOMETRY.OUT':
            detected_format, detected_software = 'elk', 'ELK'

        # Exciting files
        elif basename in ['input.xml', 'INFO.out']:
            detected_format, detected_software = 'exciting', 'exciting'

        # Octopus input
        elif basename == 'inp':
            detected_format, detected_software = 'octopus-in', 'Octopus'

        # GPUMD input
        elif basename == 'xyz.in':
            detected_format, detected_software = 'gpumd', 'GPUMD'

        # ABINIT GSR
        elif 'o_GSR.nc' in basename:
            detected_format, detected_software = 'abinit-gsr', 'ABINIT'

        # CMDFT
        elif 'I_info' in basename:
            detected_format, detected_software = 'cmdft', 'CMDFT'

        # === Extension-Based Detection ===
        elif ext:
            # Quantum Chemistry Software
            if ext in ['.com', '.gjf']:
                detected_format, detected_software = 'gaussian-in', 'Gaussian'
            elif ext == '.log' and 'gaussian' in basename_lower:
                detected_format, detected_software = 'gaussian-out', 'Gaussian'
            elif ext == '.fchk':
                detected_format, detected_software = 'gaussian-out', 'Gaussian'

            # CASTEP formats
            elif ext == '.castep':
                detected_format, detected_software = 'castep-castep', 'CASTEP'
            elif ext == '.cell':
                detected_format, detected_software = 'castep-cell', 'CASTEP'
            elif ext == '.geom':
                detected_format, detected_software = 'castep-geom', 'CASTEP'
            elif ext == '.md':
                detected_format, detected_software = 'castep-md', 'CASTEP'
            elif ext == '.phonon':
                detected_format, detected_software = 'castep-phonon', 'CASTEP'

            # FHI-aims
            elif ext == '.in' and 'aims' in basename_lower:
                detected_format, detected_software = 'aims', 'FHI-aims'

            # Quantum Espresso
            elif ext == '.pwi':
                detected_format, detected_software = 'espresso-in', 'Quantum Espresso'
            elif ext == '.pwo':
                detected_format, detected_software = 'espresso-out', 'Quantum Espresso'
            elif ext == '.out' and ('qe' in basename_lower or 'espresso' in basename_lower):
                detected_format, detected_software = 'espresso-out', 'Quantum Espresso'

            # NWChem
            elif ext == '.nwi':
                detected_format, detected_software = 'nwchem-in', 'NWChem'
            elif ext == '.nwo':
                detected_format, detected_software = 'nwchem-out', 'NWChem'
            elif 'nwchem' in basename_lower:
                detected_format, detected_software = 'nwchem-out', 'NWChem'

            # ORCA
            elif 'orca' in basename_lower:
                detected_format, detected_software = 'orca-output', 'ORCA'

            # CP2K
            elif ext == '.dcd':
                detected_format, detected_software = 'cp2k-dcd', 'CP2K'
            elif ext == '.restart':
                detected_format, detected_software = 'cp2k-restart', 'CP2K'

            # Crystal
            elif ext in ['.f34', '.34']:
                detected_format, detected_software = 'crystal', 'Crystal'

            # GAMESS-US
            elif ext == '.dat' and 'gamess' in basename_lower:
                detected_format, detected_software = 'gamess-us-punch', 'GAMESS-US'

            # DMol3
            elif ext == '.arc':
                detected_format, detected_software = 'dmol-arc', 'DMol3'
            elif ext == '.car':
                detected_format, detected_software = 'dmol-car', 'DMol3'

            # Molecular Dynamics
            elif ext == '.gro':
                detected_format, detected_software = 'gromacs', 'Gromacs'
            elif ext == '.g96':
                detected_format, detected_software = 'gromos', 'Gromos'
            elif ext == '.config':
                detected_format, detected_software = 'dlp4', 'DL_POLY_4'

            # Structure Formats
            elif ext == '.xyz':
                detected_format = 'xyz'
            elif ext == '.cif':
                detected_format = 'cif'
            elif ext == '.pdb':
                detected_format = 'proteindatabank'
            elif ext == '.cube':
                detected_format = 'cube'
            elif ext == '.xsf':
                detected_format = 'xsf'
            elif ext == '.gen':
                detected_format, detected_software = 'gen', 'DFTB+'
            elif ext == '.con':
                detected_format, detected_software = 'eon', 'EON'
            elif ext == '.mol':
                detected_format = 'mol'
            elif ext == '.sdf':
                detected_format = 'sdf'
            elif ext == '.cjson':
                detected_format = 'cjson'
            elif ext == '.xtl':
                detected_format = 'mustem'
            elif ext == '.rmc6f':
                detected_format, detected_software = 'rmc6f', 'RMCProfile'
            elif ext in ['.shelx', '.res']:
                detected_format = 'res'
            elif ext == '.ascii':
                detected_format, detected_software = 'v-sim', 'V_Sim'

            # SIESTA
            elif ext == '.XV' or basename.endswith('.XV'):
                detected_format, detected_software = 'siesta-xv', 'SIESTA'

            # Materials Studio
            elif ext == '.xsd':
                detected_format = 'xsd'
            elif ext == '.xtd':
                detected_format = 'xtd'

            # ASE Native Formats
            elif ext == '.traj':
                detected_format = 'traj'
            elif ext == '.json':
                detected_format = 'json'
            elif ext == '.db':
                detected_format = 'db'

            # Special formats
            elif ext == '.poscar':
                detected_format, detected_software = 'vasp', 'VASP'
            elif ext == '.vtu':
                detected_format = 'vtu'
            elif ext == '.nomad-json':
                detected_format = 'nomad-json'

            # Generic .out or .log files - try to detect software from filename
            elif ext in ['.out', '.log']:
                if 'gaussian' in basename_lower:
                    detected_format, detected_software = 'gaussian-out', 'Gaussian'
                elif 'orca' in basename_lower:
                    detected_format, detected_software = 'orca-output', 'ORCA'
                elif 'nwchem' in basename_lower:
                    detected_format, detected_software = 'nwchem-out', 'NWChem'
                elif 'aims' in basename_lower:
                    detected_format, detected_software = 'aims-output', 'FHI-aims'
                elif 'castep' in basename_lower:
                    detected_format, detected_software = 'castep-castep', 'CASTEP'
                elif 'espresso' in basename_lower or 'qe' in basename_lower:
                    detected_format, detected_software = 'espresso-out', 'Quantum Espresso'
                elif 'gpaw' in basename_lower:
                    detected_format, detected_software = 'gpaw-out', 'GPAW'
                elif 'onetep' in basename_lower:
                    detected_format, detected_software = 'onetep-out', 'ONETEP'
                elif 'qbox' in basename_lower:
                    detected_format, detected_software = 'qbox', 'QBOX'
                elif 'gamess' in basename_lower:
                    detected_format, detected_software = 'gamess-us-out', 'GAMESS-US'
                elif 'abinit' in basename_lower:
                    detected_format, detected_software = 'abinit-out', 'ABINIT'
                elif 'dacapo' in basename_lower:
                    detected_format, detected_software = 'dacapo-text', 'Dacapo'

        result['source_format'] = detected_format
        result['detected_software'] = detected_software

    # Basic property
    result['natom'] = len(ext_data)

    # Define special handling for properties that need custom conversion
    special_properties = {
        'symbols': lambda: ext_data.get_chemical_symbols(),
        'chemical_formula': lambda: ext_data.get_chemical_formula(),
        'scaled_positions': lambda: ext_data.get_scaled_positions(),
        'cell_lengths_and_angles': lambda: ext_data.get_cell_lengths_and_angles(),
        'moments_of_inertia': lambda: ext_data.get_moments_of_inertia(),
        'angular_momentum': lambda: ext_data.get_angular_momentum(),
    }

    # Process special properties with centralized handling
    for field_name, getter in special_properties.items():
        try:
            value = getter()
            if value is not None:
                # Convert numpy arrays to lists
                if hasattr(value, 'tolist'):
                    result[field_name] = value.tolist()
                else:
                    result[field_name] = value if isinstance(value, list) else list(value) if hasattr(value, '__iter__') and not isinstance(value, str) else value
        except:
            pass

    # Special handling for constraints (requires different processing)
    if hasattr(ext_data, 'constraints') and ext_data.constraints:
        result['constraints'] = []
        for constraint in ext_data.constraints:
            if hasattr(constraint, 'todict'):
                result['constraints'].append(constraint.todict())
            else:
                result['constraints'].append({'type': type(constraint).__name__, 'repr': str(constraint)})

    # Iterate through all model fields
    for field_name in ASEDataModel.model_fields.keys():
        if field_name in ['source_format', 'source_extension', 'detected_software', 'natom', 'symbols',
                          'chemical_formula', 'scaled_positions', 'cell_lengths_and_angles',
                          'moments_of_inertia', 'angular_momentum', 'constraints']:
            continue  # Already handled above

        # Try to get the value using get_ method first (ASE convention)
        value = None
        get_method_name = f'get_{field_name}'
        if hasattr(ext_data, get_method_name):
            try:
                value = getattr(ext_data, get_method_name)()
            except:
                # Some get methods might fail if calculator is not attached
                pass

        # Fallback to direct attribute access
        if value is None:
            value = getattr(ext_data, field_name, None)

        if value is None:
            continue

        # Convert numpy arrays and special types to JSON-serializable formats
        if hasattr(value, 'tolist'):
            result[field_name] = value.tolist()
        elif isinstance(value, dict):
            result[field_name] = {k: v.tolist() if hasattr(v, 'tolist') else v for k, v in value.items()}
        elif isinstance(value, list) and value and hasattr(value[0], 'tolist'):
            result[field_name] = [item.tolist() for item in value]
        else:
            result[field_name] = value

    return ASEDataModel(**result)


def ase_parse(filepath: str, format: str | None = None) -> ASEDataModel:
    """Parse chemistry file and return as ASEDataModel for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        ASEDataModel with parsed data converted for JSON serialization
    """
    data = ase.io.read(filepath, format=format)
    return ase_to_model(data, filepath)