# Parse Patrol Test Suite

This directory contains comprehensive tests for the Parse Patrol chemistry parsing package, including integration tests that download real computational chemistry files from NOMAD and test parsing functionality.

## Test Categories

### 1. Unit Tests (`test_modular_mcp.py`)
- **Purpose**: Test MCP server initialization and parser configuration
- **Speed**: Fast (< 1 second)
- **Dependencies**: None (tests graceful handling of missing dependencies)
- **Markers**: `unit`

Tests:
- MCP server initialization
- Parser configuration validation
- Individual parser import testing
- Graceful dependency handling

### 2. Integration Tests (`test_nomad_integration.py`) 
- **Purpose**: End-to-end testing with real quantum chemistry files
- **Speed**: Slow (1-5 minutes, downloads files)
- **Dependencies**: `requests`, parser libraries (`cclib`, `iodata`, etc.)
- **Markers**: `integration`, `slow`

Tests:
- NOMAD database search functionality
- File download and extraction
- Parser testing with real QM software output files
- Multi-software workflow validation
- Automatic cleanup of downloaded files

## Supported Quantum Chemistry Software

The integration tests cover files from:

- **Gaussian** (`.log`, `.out`, `.fchk` files)
- **ORCA** (`.out`, `.inp` files)
- **VASP** (`OUTCAR`, `POSCAR`, `CONTCAR` files)
- **Q-Chem** (`.out`, `.in` files)
- **NWChem** (`.out`, `.nw` files)
- **Psi4** (`.out` files)

## Running Tests

### Quick Setup
```bash
# Install test dependencies
uv sync

# Run all tests
uv run pytest

# Run only unit tests (fast)
uv run pytest -m unit

# Run only integration tests
uv run pytest -m integration

# Run without slow download tests
uv run pytest -m "not slow"
```

### Using the Test Runner
```bash
# Quick test (just check dependencies and run a few tests)
uv run python tests/run_nomad_tests.py --quick

# Test specific software 
uv run python tests/run_nomad_tests.py --software Gaussian

# Full test suite (all software, all parsers)
uv run python tests/run_nomad_tests.py
```

### Manual Control
```bash
# Run specific test file
uv run pytest tests/test_nomad_integration.py -v

# Run specific test function
uv run pytest tests/test_nomad_integration.py::test_nomad_search_functionality -v

# Run with detailed output
uv run pytest tests/test_nomad_integration.py -v -s
```

## Test Configuration

### Pytest Markers
- `unit`: Fast unit tests
- `integration`: Tests requiring network access
- `slow`: Tests that download large files (1-5 minutes)

### Environment Variables
None required - tests adapt to available dependencies.

### Dependencies
- **Required**: `pytest`, `requests`
- **Optional**: `cclib`, `qc-iodata`, quantum chemistry parser libraries
- Tests will skip gracefully if dependencies are missing

## Integration Test Workflow

### For Each Supported Software:
1. **Search NOMAD** for computational files from specific QM software
2. **Download** raw files to temporary directory  
3. **Parse** files with compatible parsers (cclib, iodata, gaussian)
4. **Validate** parsed data structure and content
5. **Cleanup** all downloaded files automatically

### File Management:
- Downloads to `.data/[entry_id]/` directory
- Automatic cleanup after each test
- Temporary directories for test isolation
- No permanent files left behind

### Error Handling:
- Graceful skipping if software files not found in NOMAD
- Parser-specific error handling
- Network timeout handling
- Comprehensive cleanup on failures

## Expected Test Results

### Unit Tests
```
✅ test_mcp_server_initialization - MCP server loads correctly
✅ test_parser_config_exists[cclib parser] - Configuration present  
✅ test_individual_parser_imports[cclib] - Parser imports successfully
⚠️  test_individual_parser_imports[iodata] - Skipped (dependency missing)
```

### Integration Tests  
```
✅ test_nomad_search_functionality - NOMAD search works
✅ test_nomad_download_and_parse[Gaussian] - Downloaded and parsed Gaussian files
✅ test_nomad_download_and_parse[ORCA] - Downloaded and parsed ORCA files  
⚠️  test_nomad_download_and_parse[VASP] - Skipped (no VASP files found)
✅ test_nomad_multi_software_workflow - Multi-software workflow successful
```

## Troubleshooting

### Common Issues

**"NOMAD dependencies not available"**
```bash
uv sync  # This will install all dependencies including requests
```

**"No [Software] files found in NOMAD"**
- Expected behavior - NOMAD content varies
- Tests skip gracefully
- Try different formulas or wait for database updates

**"Parser not available"**
```bash
# Install specific parser using optional dependencies
uv sync --cclib  # for cclib parser
# Or install all parsers
uv sync --parsers
```

**Network timeouts**
- Tests include reasonable timeouts (30-120 seconds)
- Check internet connection
- NOMAD servers may be temporarily unavailable

**Permission errors on cleanup**
- Tests create temporary directories
- Ensure write permissions in project directory
- `.data/` directory will be created and cleaned up

### Debug Mode
```bash
# Run with maximum verbosity
uv run pytest tests/test_nomad_integration.py -vv -s --tb=long

# Run single test with debug output
uv run pytest tests/test_nomad_integration.py::test_nomad_search_functionality -vv -s
```

## Contributing

When adding new tests:

1. **Use appropriate markers**: `@pytest.mark.integration`, `@pytest.mark.slow`
2. **Handle missing dependencies gracefully**: Use try/except with `pytest.skip()`
3. **Clean up resources**: Use context managers or proper teardown
4. **Test realistic scenarios**: Use real data when possible
5. **Document expected behavior**: Include docstrings explaining test purpose

### Adding New Software Support
1. Add configuration to `QM_SOFTWARE_CONFIGS` in `test_nomad_integration.py`
2. Specify expected file extensions and compatible parsers
3. Test with `uv run python tests/run_nomad_tests.py --software [NewSoftware]`

## Performance Notes

- **Unit tests**: < 1 second total
- **NOMAD search test**: 5-10 seconds
- **Single software integration test**: 30-120 seconds
- **Full integration suite**: 3-8 minutes

Tests are designed to be robust and handle:
- Network variability
- NOMAD database changes
- Missing optional dependencies
- File format variations
- Parser errors and limitations