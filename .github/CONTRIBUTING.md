# Contributing to Intangible Asset Valuation

Thank you for your interest in contributing! This guide helps ensure a smooth process.

## Code of Conduct

This project follows the [Python Code of Conduct](https://www.python.org/psf/conduct/).

## How to Contribute

### Reporting Bugs

1. Check the [issue tracker](https://github.com/simonmak-ascent/intangible-valuation/issues) for existing reports
2. Use the bug report template when creating a new issue
3. Include: Python version, OS, library version, and a minimal reproducible example

### Suggesting Enhancements

1. Check existing issues and discussions
2. Use the feature request template
3. Describe the use case and expected behavior

### Pull Requests

1. Fork the repository and create your branch from `main`
2. Install dev dependencies: `pip install -e ".[dev]"`
3. Make your changes
4. Add tests for new functionality
5. Ensure all checks pass:
   ```bash
   ruff check .
   mypy src/
   pytest --cov=src
   ```
6. Update documentation if needed
7. Submit your pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/intangible-valuation.git
cd intangible-valuation

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest --cov=src --cov-report=term-missing

# Lint and type check
ruff check .
mypy src/
```

## Coding Standards

- **TypeScript**: N/A — this is a Python project
- **Python**: 3.11+ with type annotations
- **Style**: Follow [PEP 8](https://peps.python.org/pep-0008/) (enforced by ruff)
- **Types**: Use type annotations on all public functions (enforced by mypy)
- **Docstrings**: Google style for all public functions and classes
- **Tests**: One test file per module, tests verify against textbook example values

## Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` new feature
- `fix:` bug fix
- `docs:` documentation changes
- `chore:` maintenance tasks
- `test:` test additions or changes
- `refactor:` code refactoring

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
