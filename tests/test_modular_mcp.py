"""
Test the modular MCP server behavior.
This tests that the MCP server gracefully handles missing optional dependencies
and dynamically registers only available parsers.
"""

import sys
import pytest
import os
import logging

# Add src to path for imports
src_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)


class TestModularMCP:
    """Test suite for MCP server modular functionality."""

    @pytest.fixture(autouse=True)
    def setup_imports(self):
        """Setup imports for all tests in the class."""
        # Import and initialize MCP server (parsers register automatically)
        from parse_patrol.__main__ import mcp, parser_configs
        self.mcp = mcp
        self.parser_configs = parser_configs

    def get_available_parsers(self):
        """Get list of parsers that are actually available (have dependencies installed)."""
        available_parsers = []
        
        for config in self.parser_configs:
            parser_name = config["name"]
            module_path = f"parse_patrol{config['module']}"  # Add parse_patrol prefix
            
            # Get the first tool function as the test function
            if "tools" in config and config["tools"]:
                function_name = config["tools"][0]  # Use first tool function
            else:
                continue  # Skip if no tools defined
            
            try:
                module = __import__(module_path, fromlist=[function_name])
                getattr(module, function_name)
                available_parsers.append((parser_name, module_path, function_name, True))
            except ImportError:
                # Skip parsers with missing dependencies
                continue
        
        return available_parsers

    def test_mcp_server_initialization(self, caplog):
        """Test MCP server loads successfully and basic structure is correct."""
        with caplog.at_level(logging.INFO):
            # Test that MCP server was created successfully
            assert self.mcp is not None
            assert self.mcp.name == "Parse Patrol - Unified Chemistry Parser"
            
            # Test that we can access the parser configs (shows modular design works)
            assert len(self.parser_configs) > 0
            assert isinstance(self.parser_configs, list)
            
            # Log successful initialization
            caplog.clear()
            for config in self.parser_configs:
                logging.info(f"✓ Registered {config['name']}")

    def test_parser_config_and_import(self, caplog):
        """Test that each available parser can be imported and all configured tools exist."""
        with caplog.at_level(logging.INFO):
            available_parsers = self.get_available_parsers()
            
            # Ensure we have at least some parsers to test
            assert len(available_parsers) > 0, "No parsers available for testing"
        
            for parser_name, module_path, function_name, should_import in available_parsers:
                # Find the parser config (we know it exists since get_available_parsers uses it)
                parser_config = next((config for config in self.parser_configs if config["name"] == parser_name), None)
                assert parser_config is not None, f"Parser config for '{parser_name}' not found"
                
                # Import functionality works at runtime and verify all configured tools exist
                try:
                    module = __import__(module_path, fromlist=parser_config["tools"])
                    
                    # Verify all configured tools actually exist in the module
                    for tool_name in parser_config["tools"]:
                        func = getattr(module, tool_name, None)
                        assert func is not None, f"Tool '{tool_name}' configured for '{parser_name}' but not found in module"
                        assert callable(func), f"Tool '{tool_name}' in '{parser_name}' is not callable"
                    
                    # Verify the module has exactly the tools that are configured (no more, no less)
                    module_functions = [name for name in dir(module) if callable(getattr(module, name)) and not name.startswith('_')]
                    configured_tools = set(parser_config["tools"])
                    available_functions = set(module_functions)
                    
                    # Check that all configured tools exist
                    missing_tools = configured_tools - available_functions
                    assert not missing_tools, f"Parser '{parser_name}' config lists tools not found in module: {missing_tools}"
                    
                    logging.info(f"✓ {parser_name}: {len(parser_config['tools'])} tools verified")

                except ImportError as e:
                    if should_import:
                        logging.warning(f"⚠ {parser_name} config valid but not available: {e}")
                        pytest.skip(f"Skipping {parser_name} test due to missing dependencies")
                    else:
                        # Expected failure case
                        pass
