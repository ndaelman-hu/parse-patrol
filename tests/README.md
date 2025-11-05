# Parse Patrol Test Suite

## Unit Tests

Run the comprehensive test suite using `pytest`:

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
- **Runtime Import Tests**: Validates that parsers work with their dependencies (gracefully skips if dependencies missing)
- NOMAD database search functionality
- File download and extraction
- NOMAD `pydantic` schema

Note that actual testing of the parsers and their semantics is relegated to development projects for each instance.

### Pytest Markers

- `unit`: Fast unit tests
- `integration`: Tests requiring network access
- `slow`: Tests that download large files (1-5 minutes)

Many of these markers indicated expected performance:

- **Unit tests**: < 1 second total
- **NOMAD search test**: 5-10 seconds

### File Management

- Downloads to `.data/[entry_id]/` directory
- Automatic cleanup after each test

### Error Handling

- Skip if software files not found in NOMAD
- Network timeout handling
- Comprehensive cleanup on failures

### Continuous Integration

GitHub Actions automatically runs all tests on pushes to a pull request:

- Tests run on Python 3.12
<!-- - **Code Quality**: Linting with `ruff` and optional type checking with `mypy` -->
- Test coverage is tracked and reported via Codecov

## Manually Running Tests

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

All queries and downloads have been verified.
While the contents of NOMAD-lab is dynamic, the number of hits should only grow.
This implies that tests with an expected empty return value could auto-deprecate after time.

Regardless, visit [the NOMAD-lab website](https://nomad-lab.eu/nomad-lab/) directly and try the same query there.

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
