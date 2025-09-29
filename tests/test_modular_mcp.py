"""
Test the modular MCP server behavior.
This tests that the MCP server gracefully handles missing optional dependencies
and dynamically registers only available parsers.
"""

import sys
import pytest  # pyright: ignore[reportMissingImports]


# Test configurations - moved to top for easy maintenance
PARSER_TEST_CONFIGS = [
    ("cclib parser", "parse_patrol.parsers.cclib.__main__", "cclib_parse_file_to_model"),
    ("gaussian parser", "parse_patrol.parsers.gaussian.__main__", "gauss_parse_file_to_model"),
    ("iodata parser", "parse_patrol.parsers.iodata.__main__", "iodata_parse_file_to_model"),
    ("NOMAD database", "parse_patrol.databases.nomad.__main__", "search_nomad_entries"),
]


def test_mcp_server_initialization():
    """Test MCP server loads successfully and basic structure is correct.
    
    This test validates the core MCP server setup:
    - MCP server object is created with correct name
    - Parser configuration list exists and is properly structured
    
    NOTE: This tests the basic server initialization, not individual parser configs.
    Individual parser configs are tested separately with parametrize.
    """
    # Add src to path for imports
    import os
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Import and initialize MCP server (parsers register automatically)
    from parse_patrol.__main__ import mcp
    
    # Test that MCP server was created successfully
    assert mcp is not None
    assert mcp.name == "Parse Patrol - Unified Chemistry Parser"
    
    # Test that we can access the parser configs (shows modular design works)
    from parse_patrol.__main__ import parser_configs
    assert len(parser_configs) > 0
    assert isinstance(parser_configs, list)
    # Individual parser configs are tested in test_parser_config_exists


@pytest.mark.parametrize(
        "expected_parser_name",
        [config[0] for config in PARSER_TEST_CONFIGS]
    )
def test_parser_config_exists(expected_parser_name):
    """Test that each expected parser has a configuration entry.
    
    This test validates STATIC CONFIGURATION for individual parsers:
    - Each parser has an entry in the parser_configs list
    - The configuration has the expected name
    
    NOTE: This tests configuration PRESENCE, not functionality.
    The config can exist even if the parser's dependencies are missing.
    """
    import os
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    from parse_patrol.__main__ import parser_configs
    assert any(config["name"] == expected_parser_name for config in parser_configs), \
           f"Parser config for '{expected_parser_name}' not found"


@pytest.mark.parametrize("parser_name,module_path,function_name", PARSER_TEST_CONFIGS)
def test_individual_parser_imports(parser_name, module_path, function_name):
    """Test importing individual parsers to ensure they work at RUNTIME.
    
    This test validates ACTUAL FUNCTIONALITY for each parser:
    - Parser module can be imported successfully
    - Required dependencies are available (cclib, iodata, etc.)
    - Expected functions exist and are callable
    
    NOTE: This tests RUNTIME functionality, not just configuration.
    This test will fail/skip if dependencies are missing, even if 
    the parser configuration exists and is correct.
    
    Contrast with test_parser_config_exists which only tests static config.
    """
    import os
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    try:
        module = __import__(module_path, fromlist=[function_name])
        func = getattr(module, function_name)
        assert callable(func)
        print(f"✓ {parser_name} imports successfully")
    except ImportError as e:
        print(f"⚠ {parser_name} not available: {e}")
        pytest.skip(f"Skipping {parser_name} test due to missing dependencies")


def test_mcp_server_without_optional_deps():
    """Test MCP server core functionality without parser dependencies."""
    import os
    src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Test that we can at least import the MCP framework
    from mcp.server.fastmcp import FastMCP # pyright: ignore[reportMissingImports]
    
    # Create a minimal MCP server
    minimal_mcp = FastMCP("Minimal Parse Patrol")
    assert minimal_mcp is not None
    assert minimal_mcp.name == "Minimal Parse Patrol"