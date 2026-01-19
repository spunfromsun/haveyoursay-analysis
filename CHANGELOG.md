# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial CLI with `fetch`, `download`, and `organize` commands
- Robust feedback API parsing (handles both `content` and `_embedded.feedback` structures)
- Attachment downloading with retry logic (backoff)
- Organizing files by `userType` (NGO, TRADE_UNION, OTHER, etc.)
- CSV export for feedback and attachment metadata
- GitHub Actions CI for linting and testing
- MIT license
- Editable package installation support

## [0.1.0] - 2025-01-XX

### Added
- Project scaffold with modern Python packaging (pyproject.toml, src layout)
- API client for EU "Have Your Say" feedback endpoint
- File download and organization utilities
- Basic test suite (smoke tests)
