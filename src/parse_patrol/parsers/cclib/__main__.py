from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]
from mcp.server.fastmcp.utilities.logging import configure_logging, get_logger # pyright: ignore[reportMissingImports]
from .utils import cclib_parse, CCDataModel

configure_logging("INFO")
logger = get_logger(__name__)


mcp = FastMCP("CCLib Chemistry Parser")


@mcp.resource("cclib://documentation")
async def cclib_documentation() -> str:
    """Comprehensive documentation for cclib parser capabilities.
    
    Returns detailed information about supported quantum chemistry software,
    file formats, and data types that can be parsed by cclib.
    """
    return """
# CCLib Chemistry Parser Documentation

## Overview
CCLib is an open source library for parsing and interpreting results from computational chemistry packages. 
It provides a consistent interface to extract data from quantum chemistry calculation output files.

## Supported Quantum Chemistry Software (cclib v1.8+)

### Major Packages:
- **ADF (versions 2007, 2013)** - Amsterdam Density Functional program
- **DALTON (versions 2013, 2015)** - Molecular electronic structure calculations
- **Gaussian (versions 09, 16)** - Widely used quantum chemistry package
- **ORCA (versions 4.1, 4.2, 5.0)** - Modern quantum chemistry package
- **NWChem (versions 6.0, 6.1, 6.5, 6.6, 6.8, 7.0)** - Open source computational chemistry
- **Psi4 (versions 1.2.1, 1.3.1, 1.7)** - Open source quantum chemistry
- **Q-Chem (versions 5.1, 5.4, 6.0)** - Commercial quantum chemistry package
- **Turbomole (versions 5.9, 7.2, 7.4, 7.5)** - Quantum chemistry package

### GAMESS Family:
- **GAMESS (US) (versions 2017, 2018)** - General Atomic and Molecular Electronic Structure System
- **GAMESS-UK (versions 7.0, 8.0)** - UK version of GAMESS
- **Firefly (version 8.0)** - formerly known as PC GAMESS

### Specialized Packages:
- **Jaguar (versions 7.0, 8.3)** - Schrödinger's quantum chemistry package
- **Molcas (version 18.0)** - Multiconfigurational quantum chemistry
- **Molpro (versions 2006, 2012)** - Quantum chemistry package for correlated methods
- **MOPAC (version 2016)** - Semiempirical quantum chemistry methods
- **NBO (version 7.0)** - Natural Bond Orbital analysis

### Legacy Support:
- **Psi3 (version 3.4)** - Older version of Psi (regression testing only)

Note: Output files from newer versions may still work even if not explicitly tested.

## Supported File Extensions

CCLib automatically detects file format based on content, not extension. Common extensions include:

### Standard Output Files:
- **.out** - Standard output files (most common across all packages)
- **.log** - Log files from calculations
- **.dat** - Data files (especially GAMESS)

### Specialized Formats:
- **.fchk** - Gaussian formatted checkpoint files
- **.punch** - GAMESS punch files
- **.xyz** - XYZ coordinate files (when containing calculation data)
- **.xml** - XML structured output files
- **.json** - JSON structured output files
- **No extension** - Many packages create output files without extensions

### Format Detection:
CCLib uses intelligent content-based detection, so the actual file extension doesn't matter. 
The parser examines the file content to determine the appropriate format and software.

## Best Practices

1. **File Validation**: Always check if specific properties exist before using them
2. **Error Handling**: Wrap parsing calls in try-catch blocks for production code
3. **Memory Management**: Large trajectory files may require streaming approaches
4. **Version Compatibility**: Test with your specific software versions for best results

## Limitations

- Some very old file formats may not be supported
- Binary file formats (like Gaussian .chk files) are not supported - use formatted versions (.fchk)
- Very large files may have memory limitations
- Some package-specific features may not be extracted

This comprehensive coverage makes cclib an excellent choice for computational chemistry data extraction and analysis workflows.
"""


@mcp.tool()
async def cclib_parse_file_to_model(filepath: str) -> CCDataModel:
    """Parse chemistry file and return as CCDataModel for JSON serialization.
    
    Args:
        filepath: Path to chemistry output file
    
    Returns:
        CCDataModel with parsed data converted for JSON serialization
    """
    logger.info("Parsing file: %s ...", filepath)
    try:
        return cclib_parse(filepath)
    except (FileNotFoundError, ValueError) as e:
        logger.error("Failed to parse file: %s", e)
        return CCDataModel()


@mcp.prompt()
async def cclib_test_prompt(
    file_description: str, output_format: str = "a CCDataModel for JSON serialization"
) -> str:
    """Generate a prompt for parsing chemistry files using cclib.
    
    Args:
        file_description: Description of the file to be parsed
        output_format: Desired output format (default: CCDataModel)
    
    Returns:
        Formatted prompt string for the MCP client
    """

    return f"""
    Use `cclib_parse_file_to_model`
    to parse the file with description {file_description}
    and return the data as {output_format}.
    """

if __name__ == "__main__":
    mcp.run()
