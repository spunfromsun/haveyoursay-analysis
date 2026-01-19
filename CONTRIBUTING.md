# Contributing to haveyoursay-analysis

Thank you for your interest in contributing! This project is designed to make EU "Have Your Say" feedback and attachment data more accessible and analyzable.

## Development Setup

1. Clone the repo and install in editable mode:
   ```bash
   pip install -e ".[dev]"
   ```

2. Run tests:
   ```bash
   pytest tests/ -v
   ```

3. Lint and type check:
   ```bash
   ruff check src/ tests/
   mypy src/
   ```

## Workflow

- Fork the repo and create a feature branch
- Make your changes; write tests
- Ensure CI passes (GitHub Actions)
- Submit a pull request with a clear description

## Code Style

- Follow PEP 8
- Use type hints where possible
- Keep functions focused and testable
- Document public API with docstrings

## Reporting Issues

- Use GitHub Issues for bugs and feature requests
- Provide minimal reproducible examples
- Include EC API publicationId and error messages

## Questions?

Open a discussion or issue and we'll respond as soon as possible.
