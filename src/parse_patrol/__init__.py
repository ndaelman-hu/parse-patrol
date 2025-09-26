"""
Parse Patrol - Dual-Mode Chemistry Parsing Package

This package provides computational chemistry parsing tools in dual modes:

## MCP Discovery Mode
LLMs can discover and experiment with tools through MCP protocol, including:
- Parser tools: cclib, gaussian, iodata 
- Database tools: NOMAD materials database search and download

## Direct Import Mode  
Developers can install the package and import parser functions directly:

```python
from parse_patrol import cclib_parse, gaussian_parse, iodata_parse

# Parse chemistry files directly
cclib_result = cclib_parse("output.log")
gaussian_result = gaussian_parse("calculation.out") 
iodata_result = iodata_parse("data.xyz")
```

Note: Database tools (NOMAD) are only available via MCP for discovery/experimentation.
"""

# Import parser functions only (not database tools)
from .parsers.cclib.utils import cclib_parse, CCDataModel
from .parsers.gaussian.utils import gaussian_parse, CustomGaussianDataModel  
from .parsers.iodata.utils import iodata_parse, IODataModel

__version__ = "0.1.0"
__all__ = [
    # Parser functions
    "cclib_parse",
    "gaussian_parse", 
    "iodata_parse",
    # Data models
    "CCDataModel",
    "CustomGaussianDataModel",
    "IODataModel",
]