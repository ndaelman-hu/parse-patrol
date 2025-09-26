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
# Handle optional dependencies gracefully
__version__ = "0.1.0"
__all__ = []

# Parser configuration: (module_path, function_name, model_name, parser_name)
PARSERS = [
    (".parsers.cclib.utils", "cclib_parse", "CCDataModel", "cclib"),
    (".parsers.gaussian.utils", "gaussian_parse", "CustomGaussianDataModel", "gaussian"),
    (".parsers.iodata.utils", "iodata_parse", "IODataModel", "iodata"),
]

# Import available parsers
_available_parsers = []
for module_path, func_name, model_name, parser_name in PARSERS:
    try:
        module = __import__(f"parse_patrol{module_path}", fromlist=[func_name, model_name])
        func = getattr(module, func_name)
        model = getattr(module, model_name)
        
        # Add to globals and __all__
        globals()[func_name] = func
        globals()[model_name] = model
        __all__.extend([func_name, model_name])
        _available_parsers.append(parser_name)
    except ImportError:
        pass

def available_parsers():
    """Return a list of available parsers based on installed dependencies."""
    return _available_parsers.copy()

__all__.append("available_parsers")