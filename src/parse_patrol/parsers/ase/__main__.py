from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger # pyright: ignore[reportMissingImports]
from .utils import ase_parse, ASEDataModel

configure_logging("INFO")
logger = get_logger(__name__)

mcp = FastMCP("ASE Chemistry Parser")


@mcp.resource("ase://documentation")
async def ase_documentation() -> str:
    """Comprehensive documentation for ASE parser capabilities.

    Returns detailed information about supported file formats,
    data types, and usage patterns for the ASE library.
    """
    return """
# ASE Chemistry Parser Documentation

## Overview
ASE (Atomic Simulation Environment) is a Python library for working with atoms.
It provides tools for setting up, manipulating, running, visualizing and analyzing atomistic simulations.
This parser leverages ASE's extensive I/O capabilities to read 80+ file formats.

## Supported File Formats (80+)

### Quantum Chemistry Software:
- **VASP** - POSCAR, CONTCAR, OUTCAR, XDATCAR, vasprun.xml
- **Gaussian** - .com, .gjf (input), .log, .fchk (output)
- **ORCA** - output files
- **NWChem** - .nwi (input), .nwo (output)
- **Quantum Espresso** - .pwi (input), .pwo, .out (output)
- **CASTEP** - .castep, .cell, .geom, .md, .phonon
- **FHI-aims** - .in (input), output files
- **CP2K** - .dcd, .restart
- **ABINIT** - GSR files, input/output
- **Crystal** - .f34, .34
- **GAMESS-US** - .dat (punch files)
- **GPAW** - output files, .gpw
- **ONETEP** - input/output
- **Octopus** - inp (input)
- **SIESTA** - .XV files, STRUCT
- **Turbomole** - coord, gradient
- **ELK** - GEOMETRY.OUT
- **Exciting** - input.xml, INFO.out
- **QBOX** - output files
- **Dacapo** - text output

### Molecular Dynamics:
- **LAMMPS** - data files, dump files (text/binary)
- **Gromacs** - .gro
- **Gromos** - .g96
- **DL_POLY** - HISTORY, .config
- **AMBER** - NetCDF trajectories
- **GPUMD** - xyz.in
- **DMol3** - .arc, .car, incoor

### Structure Formats:
- **XYZ** - .xyz (standard and extended)
- **CIF** - .cif (Crystallographic Information File)
- **PDB** - .pdb (Protein Data Bank)
- **CUBE** - .cube (Gaussian cube files)
- **XSF** - XCrySDen Structure File
- **GEN** - DFTB+ format
- **MOL** - MDL Molfile
- **SDF** - Structure Data File
- **Chemical JSON** - .cjson
- **Materials Studio** - .xsd, .xtd
- **RMCProfile** - .rmc6f
- **SHELX** - .shelx, .res
- **V_Sim** - .ascii
- **muSTEM** - .xtl

### ASE Native Formats:
- **Trajectory** - .traj (ASE trajectory)
- **JSON** - .json (ASE JSON database)
- **Database** - .db (SQLite database)
- **Bundle** - Bundle trajectory format

### Visualization:
- **VTK** - .vti, .vtu
- **X3D** - X3D format
- **HTML** - X3DOM HTML

## Data Model (41 Fields)

### Metadata (3 fields):
- `source_format` - Detected file format
- `source_extension` - File extension
- `detected_software` - Software package name

### Core Structural (11 fields):
- `natom` - Number of atoms
- `positions` - Cartesian coordinates (Nx3, Angstrom)
- `scaled_positions` - Fractional coordinates (Nx3)
- `numbers` - Atomic numbers (N)
- `symbols` - Chemical symbols (N)
- `chemical_formula` - Formula string
- `masses` - Atomic masses (N, amu)
- `tags` - Integer tags (N)
- `charges` - Atomic charges (N)
- `momenta` - Momentum vectors (Nx3)
- `velocities` - Velocity vectors (Nx3, Angstrom/fs)

### Unit Cell & Periodicity (4 fields):
- `cell` - Unit cell vectors (3x3, Angstrom)
- `cell_lengths_and_angles` - [a,b,c,α,β,γ] (6)
- `pbc` - Periodic flags (3, boolean)
- `celldisp` - Cell displacement (3, Angstrom)

### Computational (6 fields, calculator-dependent):
- `forces` - Atomic forces (Nx3, eV/Angstrom)
- `energy` - Total potential energy (eV)
- `potential_energies` - Per-atom energies (N, eV)
- `kinetic_energy` - Kinetic energy (eV)
- `stress` - Stress tensor (6, eV/Angstrom³)
- `stresses` - Per-atom stresses (Nx6, eV/Angstrom³)

### Magnetic (3 fields):
- `initial_magnetic_moments` - Initial moments (N, Bohr magneton)
- `magnetic_moments` - Calculated moments (N, Bohr magneton)
- `magnetic_moment` - Total moment (Bohr magneton)

### Derived (6 fields):
- `center_of_mass` - COM position (3, Angstrom)
- `moments_of_inertia` - Principal moments (3, amu·Angstrom²)
- `angular_momentum` - Total angular momentum (3, amu·Angstrom²/fs)
- `volume` - Unit cell volume (Angstrom³)
- `temperature` - Kinetic temperature (Kelvin)
- `dipole_moment` - Electric dipole (3, eA)

### Additional (2 fields):
- `constraints` - Applied constraints (list of dicts)
- `info` - Metadata dictionary

## Type Validation

All vector and tensor fields are validated using Pydantic constraints:
- **Vector3**: Lists of exactly 3 floats
- **Vector6**: Lists of exactly 6 floats (stress tensors, cell params)
- **PBCFlags**: Lists of exactly 3 booleans

## Best Practices

1. **Format Detection**: ASE auto-detects most formats, but you can specify: `ase_parse_file_to_model(filepath, format='vasp')`
2. **Calculator Properties**: Forces, energy, stress require a calculator attachment
3. **Periodic Systems**: Use `scaled_positions` for fractional coordinates
4. **Large Files**: ASE handles trajectories efficiently
5. **Compressed Files**: ASE supports .gz, .bz2, .xz compression

## Limitations

- Binary Gaussian .chk files not supported (use .fchk)
- Some calculator-specific properties may not be available
- Format detection may require file content inspection
- Very specialized formats may need explicit format specification

## Extensibility

ASE is modular - users can add custom calculators and I/O formats through plugins, potentially supporting more formats than listed here.

Use `ase_parse_file_to_model(filepath)` to parse any supported chemistry file.
"""


@mcp.tool()
async def ase_parse_file_to_model(filepath: str, format: str | None = None) -> ASEDataModel:
    """Parse chemistry file and return as ASEDataModel for JSON serialization.

    Args:
        filepath: Path to chemistry output file
        format: Optional format hint for ASE (e.g., 'vasp', 'xyz', 'cif')

    Returns:
        ASEDataModel with parsed data converted for JSON serialization

    Raises:
        FileNotFoundError: If file cannot be opened or is an unsupported format
        ValueError: If file parsing fails
    """
    logger.info("Parsing file: %s%s", filepath, f" (format: {format})" if format else "")
    try:
        return ase_parse(filepath, format=format)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Failed to parse file: %s", e)
        raise


@mcp.prompt()
async def ase_test_prompt(
    query: str = "Parse the file and extract molecular properties"
) -> str:
    """Generate a prompt for parsing chemistry files using ASE.

    Args:
        query: Custom query for the prompt

    Returns:
        A formatted prompt string for testing
    """
    return f"""
You are working with computational chemistry files. {query}

Available ASE parser can handle:

Category 1: Python-Based Calculators (Native ASE Integration)

    Abacus - Plane-wave DFT code
    ALIGNN - Machine learning potential
    AMS - Amsterdam Modeling Suite
    Asap - Classical potential molecular dynamics
    BigDFT - Wavelet-based DFT code
    CHGNet - Machine learning potential
    DeePMD-kit - Deep learning molecular dynamics
    DFTD3 - Grimme's DFT-D3 dispersion correction
    DFTD4 - Grimme's DFT-D4 dispersion correction
    DFTK - Density Functional Toolkit
    EquiFormerV2 - Machine learning potential
    FLEUR - All-electron DFT code
    GPAW - Grid-based DFT code (Python)
    Hotbit - Tight-binding code
    M3GNet - Materials 3-body Graph Network
    MACE - Machine learning potential
    OrbModels - Orbital-based models
    SevenNet - Machine learning potential
    TBLite - Light tight-binding framework
    XTB - Extended tight-binding methods

Category 2: External Codes with Python Wrappers

    ABINIT - Plane-wave DFT code
    AMBER - Molecular dynamics for biomolecules
    CASTEP - Plane-wave DFT code
    CP2K - Quantum chemistry and solid state physics
    deMon2k - Auxiliary DFT code
    DFTB+ - Density Functional Tight Binding
    ELK - All-electron full-potential linearized augmented-plane wave code
    EXCITING - All-electron DFT code
    FHI-aims - All-electron DFT code
    GAUSSIAN - Quantum chemistry package
    Gromacs - Molecular dynamics
    LAMMPS - Large-scale Atomic/Molecular Massively Parallel Simulator
    MOPAC - Semi-empirical quantum chemistry
    NWChem - Computational chemistry package
    Octopus - Real-space DFT code
    ONETEP - Linear-scaling DFT
    PLUMED - Free energy calculations
    Psi4 - Open-source quantum chemistry
    Q-Chem - Quantum chemistry package
    Quantum ESPRESSO - Plane-wave DFT suite
    SIESTA - Linear-scaling DFT
    TURBOMOLE - Quantum chemistry package
    VASP - Vienna Ab initio Simulation Package

Category 3: Pure Python Implementations (Built-in)

    EMT - Effective Medium Theory potential
    EAM - Embedded Atom Method
    Lennard-Jones - Classical potential
    Morse - Morse potential
    Tersoff - Tersoff potential
    HarmonicCalculator - Harmonic oscillator

Category 4: Meta-Calculators (Calculator Wrappers)

    CheckpointCalculator - Saves calculation checkpoints
    FiniteDifferenceCalculator - Numerical derivatives
    LoggingCalculator - Logs calculator calls
    LinearCombinationCalculator - Combines multiple calculators
    MixedCalculator - Different calculators for different atoms
    SumCalculator - Sums energies from multiple calculators
    AverageCalculator - Averages results
    SocketIOCalculator - Client-server calculator interface
    EIQMMM - Embedded QM/MM
    SimpleQMMM - Simple QM/MM partitioning

You can check which calculators are available on your system by running:
`ase info --calculators`

Use `ase_parse_file_to_model(filepath)` to parse any supported chemistry file.
"""


if __name__ == "__main__":
    mcp.run()