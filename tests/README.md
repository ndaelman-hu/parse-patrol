# Parse Patrol Test Suite

## Testing

Testing is done in multiple ways to ensure both functionality and MCP server behavior:

### Automated Unit Tests

Run the comprehensive test suite using pytest:

```bash
# Run all tests with verbose output
uv run python -m pytest tests/ -v

# Run specific test file
uv run python -m pytest tests/test_modular_mcp.py -v

# Run tests with coverage
uv sync --dev  # ensures pytest-cov is installed
uv run pytest tests/ --cov=parse_patrol
```

The test suite includes:

- **MCP Server Initialization**: Tests that the unified MCP server loads correctly
- **Parser Configuration**: Parametrized tests ensuring each parser has proper configuration
- **Runtime Import Tests**: Validates that parsers work with their dependencies (gracefully skips if dependencies missing)
- **Minimal Dependency Tests**: Tests core MCP functionality without optional parser dependencies

(`test_modular_mcp.py`)

- **Purpose**: Test MCP server initialization and parser configuration
- **Speed**: Fast (< 1 second)
- **Dependencies**: None (tests graceful handling of missing dependencies)
- **Markers**: `unit`

Tests:

- MCP server initialization
- Parser configuration validation
- Individual parser import testing
- Graceful dependency handling

#### Expected Test Results

```text
✅ test_mcp_server_initialization - MCP server loads correctly
✅ test_parser_config_exists[cclib parser] - Configuration present  
✅ test_individual_parser_imports[cclib] - Parser imports successfully
⚠️  test_individual_parser_imports[iodata] - Skipped (dependency missing)
```

### Continuous Integration

GitHub Actions automatically runs tests on all pushes and pull requests:

- **Multi-Python Testing**: Tests run on Python 3.9, 3.10, 3.11, and 3.12
- **Code Quality**: Linting with ruff and optional type checking with mypy
- **Coverage Reporting**: Test coverage is tracked and reported via Codecov

The CI ensures that:

- All tests pass across supported Python versions
- Code follows consistent formatting and style
- Dependencies install correctly with `uv`
- Both minimal and full installation scenarios work(`test_nomad_integration.py`)

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

#### Expected Test Results

```text
✅ test_nomad_search_functionality - NOMAD search works
✅ test_nomad_download_and_parse[Gaussian] - Downloaded and parsed Gaussian files
✅ test_nomad_download_and_parse[ORCA] - Downloaded and parsed ORCA files  
⚠️  test_nomad_download_and_parse[VASP] - Skipped (no VASP files found)
✅ test_nomad_multi_software_workflow - Multi-software workflow successful
```

### Agent Pipeline Testing

Test end-to-end workflows:

- The agent attempts to generate pipeline scripts using the MCP tools
- Successful cases are stored in `.pipelines/scripts/`
- Input data for processing is found in `.pipelines/data/`
- Schema definitions and documentation resources are available in `.resources/`

This directory contains comprehensive tests for the Parse Patrol chemistry parsing package, including integration tests that download real computational chemistry files from NOMAD and test parsing functionality.

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

# Run without slow download tests
uv run pytest -m "not slow"

# Run a specific file
# at maximal verbosity
# and with log messages (atm only INFO channel)
uv run pytest tests/test_nomad_integration.py -vv -s --tb=long --log-cli-level=INFO
```

Or use the test interfaces:

```bash
# Test specific software 
uv run python tests/run_nomad_tests.py --software Gaussian
```

### Pytest Markers

- `unit`: Fast unit tests
- `integration`: Tests requiring network access
- `slow`: Tests that download large files (1-5 minutes)

## Integration Test Workflow

### For Each Supported Software

1. **Search NOMAD** for computational files from specific QM software
2. **Download** raw files to temporary directory  
3. **Parse** files with compatible parsers
4. **Validate** parsed data structure and content
5. **Cleanup** all downloaded files automatically

### File Management

- Downloads to `.data/[entry_id]/` directory
- Automatic cleanup after each test
- Temporary directories for test isolation
- No permanent files left behind

### Error Handling

- Skip if software files not found in NOMAD
- Parser-specific error handling
- Network timeout handling
- Comprehensive cleanup on failures

## Troubleshooting

**"NOMAD dependencies not available":**

Install all dependencies.
Afterwards, you can choose a more specific setup (see general `README.md`).

```bash
# install features
uv sync --all
# install all parsers
uv sync --parsers
```

**"No [Software] files found in NOMAD"**

- Expected behavior
- NOMAD content varies
- Tests skip gracefully
- Try different formulas or wait for database updates

**Network timeouts:**

- Tests include reasonable timeouts (30-120 seconds)
- Check internet connection
- NOMAD servers may be temporarily unavailable

**Permission errors on cleanup:**

- Tests create temporary directories
- Ensure write permissions in project directory
- `.data/` directory will be created and cleaned up

## Manual Testing with MCP Inspector (experimental)

MCP primitives can be tested using [MCP instructor](https://github.com/modelcontextprotocol/inspector).
This instructor is limited to a single server at a time, and separate servers should be tested individually.

```bash
# Test the unified server (recommended)
uv run mcp dev -m parse_patrol

# Test individual parsers  
uv run mcp dev -m parse_patrol.parsers.cclib
uv run mcp dev -m parse_patrol.databases.nomad
```

Then open up the URL link appearing in the terminal in the browser, in case the inspector does not appear automatically.

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
