# haveyoursay-analysis

Tools to fetch, organize, and analyze EU "Have Your Say" feedback and attachments.

## Features

- **Fetch feedback** from the EU Better Regulation API by `publicationId`
- **Download attachments** with retry logic and error tracking
- **Organize files** into folders by user type (NGO, TRADE_UNION, etc.)
- **Compare phases** across multiple feedback cycles using `feedback_id` as key
- **Export CSVs** with metadata for analysis

## Quick Start

### Installation

```bash
pip install git+https://github.com/spunfromsun/haveyoursay-analysis.git
```

Or for local development:

```bash
git clone https://github.com/spunfromsun/haveyoursay-analysis.git
cd haveyoursay-analysis
pip install -e .
```

### Basic Commands

```bash
# Fetch feedback for an initiative
haveyoursay-analysis fetch --publication-id 14488 --out data/14488

# Download attachments
haveyoursay-analysis download \
  --attachments-csv data/14488/attachments.csv \
  --out data/14488/files

# Organize by user type
haveyoursay-analysis organize \
  --attachments-dir data/14488/files \
  --attachments-csv data/14488/attachments.csv \
  --feedback-csv data/14488/feedback.csv \
  --out data/14488/organized \
  --only NGO --only TRADE_UNION

# Compare two phases
haveyoursay-analysis compare \
  --feedback-1 phase2/feedback.csv \
  --feedback-2 phase3/feedback.csv \
  --attachments-1 phase2/attachments.csv \
  --attachments-2 phase3/attachments.csv \
  --label-1 "Phase 2" \
  --label-2 "Phase 3"
```

## Docker Usage

```bash
# Build image
docker build -t haveyoursay-analysis .

# Fetch data
docker run --rm -v $(pwd)/data:/data haveyoursay-analysis \
  fetch --publication-id 14488 --out /data/14488

# Or use docker-compose
docker-compose run --rm haveyoursay \
  fetch --publication-id 14488 --out /data/14488
```

## Documentation

- [Getting Started](getting_started.md)
- [CLI Reference](cli_reference.md)
- [Examples](examples.md)
- [API Reference](api.md)

## Notes on the EU API

The EC "Better Regulation" API structure has evolved. This tool:
- Parses feedback using the `content` field when present
- Falls back to older `_embedded` structures if needed
- Handles pagination automatically

If the document download endpoint changes, adjust the URL template in `src/haveyoursay_analysis/files.py`.

## Acknowledgments

This project is inspired by [luiscape/haveyoursay](https://github.com/luiscape/haveyoursay), which provides comprehensive database-driven tools for EU Better Regulation data collection. This implementation takes a different architectural approach focused on lightweight, direct-to-CSV workflows.

## License

MIT

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
