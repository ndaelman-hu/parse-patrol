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

TODO
"""


@mcp.tool()
async def ase_parse_file_to_model(filepath: str) -> ASEDataModel:
    """Parse chemistry file and return as ASEDataModel for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        ASEDataModel with parsed data converted for JSON serialization
    """
    
    return ase_parse(filepath)


@mcp.tool()
async def ase_test_prompt(
    query: str = "Parse the file and extract molecular properties"
) -> str:
    """Generate a prompt for parsing chemistry files using ASEData.
    
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