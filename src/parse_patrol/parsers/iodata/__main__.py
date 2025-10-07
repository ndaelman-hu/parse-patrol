from mcp.server.fastmcp import FastMCP  # pyright: ignore[reportMissingImports]
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger # pyright: ignore[reportMissingImports]
from .utils import iodata_parse, IODataModel

configure_logging("INFO")
logger = get_logger(__name__)

mcp = FastMCP("IOData Chemistry Parser")


@mcp.resource("iodata://documentation")
async def iodata_documentation() -> str:
    """Comprehensive documentation for IOData parser capabilities.
    
    Returns detailed information about supported file formats, 
    data types, and usage patterns for the IOData library.
    """
    return """
# IOData Chemistry Parser Documentation

## Overview
IOData is a Python library for reading, writing, and converting computational chemistry file formats. 
It provides a unified interface to work with molecular data from various quantum chemistry and molecular modeling software packages.

## Supported File Formats (30+ formats)

### Quantum Chemistry Software Output Files:

#### **Gaussian Formats:**
- **.log, .out** - Output files with SCF energies, geometries, frequencies
- **.fchk** - Formatted checkpoint files (comprehensive data)
- **.gjf, .com** - Input files (geometry, basis sets, keywords)
- **.chk** - Binary checkpoint files (use `formchk` to convert)

#### **ORCA Formats:**
- **.out** - Output files with energies, gradients, properties
- **.inp** - Input files
- **.gbw** - Binary wavefunction files
- **.densities** - Electron density files

#### **VASP Formats:**
- **POSCAR, CONTCAR** - Structure files
- **OUTCAR** - Detailed output with forces, stresses
- **CHGCAR, AECCAR** - Charge density files
- **LOCPOT** - Local potential files
- **WAVECAR** - Wavefunction files

#### **Q-Chem Formats:**
- **.out** - Output files
- **.in** - Input files

#### **MOLPRO Formats:**
- **.out** - Output files with energies and properties
- **.inp** - Input files

#### **NWChem Formats:**
- **.out** - Output files
- **.nw** - Input files

#### **GAMESS Formats:**
- **.out, .log** - Output files
- **.inp** - Input files

#### **CP2K Formats:**
- **.out** - Output files
- **.inp** - Input files

#### **FHI-AIMS:**
- **.out** - Output files

#### **MOPAC:**
- **.out** - Output files
- **.mop** - Input files

#### **PSI4:**
- **.out** - Output files

### Coordinate and Structure Files:

#### **Standard Molecular Formats:**
- **.xyz** - Cartesian coordinates (simple format)
- **.mol, .sdf** - MOL/SDF molecular data files
- **.pdb** - Protein Data Bank format
- **.mol2** - Tripos MOL2 format
- **.cml** - Chemical Markup Language

#### **Simulation Formats:**
- **.gro** - GROMACS coordinate files
- **.crd** - CHARMM coordinate files

### Wavefunction and Density Files:

#### **Volumetric Data:**
- **.cube, .cub** - Gaussian cube format (volumetric data)
- **.dx** - OpenDX format for volumetric data

#### **Basis Set and Orbital Data:**
- **.molden, .molden.input** - Molden molecular orbital format
- **.mkl** - Molekel format
- **.wfn, .wfx** - Wavefunction files (AIMPAC format)
- **.mwfn** - Multiwfn format

#### **Integral Files:**
- **.fcidump, *FCIDUMP*** - Molpro FCIDUMP integral files
- Supports: one- and two-electron integrals, core energies

Format Detection:
IOData uses filename patterns and content analysis for format detection.
Many formats don't require specific extensions (e.g., VASP files).

## Usage Patterns

### Basic File Loading:
```python
# Load any supported format
data = iodata_parse("calculation.fchk")
print(f"Molecule has {len(data.atnums)} atoms")
print(f"Total energy: {data.energy} hartree")
```

### Multi-Format Workflows:
```python
# Read Gaussian, analyze with Python, write to different format
gaussian_data = iodata_parse("gaussian.fchk")
orca_data = iodata_parse("orca.out")  
xyz_coords = iodata_parse("structure.xyz")
```

### Volumetric Data Analysis:
```python
# Work with electron density from cube files
cube_data = iodata_parse("density.cube")
if cube_data.cube:
    print(f"Grid shape: {cube_data.cube.shape}")
    print(f"Grid spacing: {cube_data.cube.axes}")
```

### Property Extraction:
```python
# Extract various molecular properties
data = iodata_parse("calculation.out")
if data.atcharges:
    print("Available charge schemes:", list(data.atcharges.keys()))
if data.moments:
    print("Available multipole moments:", list(data.moments.keys()))
```

## Best Practices

### 1. **Error Handling**
Always check if properties exist before using them:
```python
if data.energy is not None:
    print(f"Energy: {data.energy}")
if data.cube is not None:
    analyze_volumetric_data(data.cube)
```

### 2. **Format Selection**
- **FCHK** files for comprehensive Gaussian data
- **Cube** files for volumetric analysis
- **XYZ** files for simple coordinate handling
- **Molden** files for orbital visualization

### 3. **Memory Considerations**
- Large cube files may require streaming
- Consider data compression for storage

### 4. **Unit Awareness**
- Coordinates are in Angstroms
- Energies are in Hartree (atomic units)
- Check documentation for specific property units

## Integration with Other Tools

### Visualization:
- Compatible with molecular viewers (VMD, PyMOL, etc.)
- Direct integration with plotting libraries
- Support for orbital and density visualization

### Analysis Libraries:
- Integration with NumPy for numerical analysis
- Compatible with SciPy for advanced calculations
- Works with pandas for data manipulation

### Quantum Chemistry Packages:
- Can generate input files for various software
- Supports basis set exchange formats
- Compatible with electronic structure analysis tools

## Limitations and Notes

### Format-Specific Limitations:
- Some binary formats not supported (use converted versions)
- Certain package-specific features may not be extracted
- Large files may have memory limitations

### Data Completeness:
- Not all properties available in all formats
- Some formats are read-only or write-only

### Performance Considerations:
- Large volumetric files may be slow to load
- Memory usage scales with molecular system size

IOData provides a comprehensive, flexible foundation for computational chemistry data handling.
"""


@mcp.tool()
async def iodata_parse_file_to_model(filepath: str) -> IODataModel:
    """Parse chemistry file and return as IODataModel for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        IODataModel with parsed data converted for JSON serialization
    """
    
    return iodata_parse(filepath)


@mcp.tool()
async def iodata_test_prompt(
    query: str = "Parse the file and extract molecular properties"
) -> str:
    """Generate a prompt for parsing chemistry files using IOData.
    
    Args:
        query: Custom query for the prompt
        
    Returns:
        A formatted prompt string for testing
    """
    return f"""
You are working with computational chemistry files. {query}

Available IOData parser can handle:
- Gaussian (.log, .fchk, .gjf files)
- ORCA (.out files) 
- VASP (POSCAR, OUTCAR files)
- Cube files (.cube)
- XYZ coordinate files (.xyz)
- And 25+ other formats

Use iodata_parse_file_to_model(filepath) to parse any supported chemistry file.
"""


if __name__ == "__main__":
    mcp.run()