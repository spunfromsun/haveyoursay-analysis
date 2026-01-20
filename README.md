# haveyoursay-analysis

Standalone toolkit to fetch European Union (EU) "Have Your Say" feedback for a given `publicationId`, extract attachment metadata, download attachments, and organize files for analysis.

> **Note:** This project is inspired by and complements the [haveyoursay](https://github.com/ghxm/haveyoursay) tool. While the original project provides comprehensive database-driven collection and text extraction, this tool focuses on lightweight, direct API access with modern Python packaging for quick feedback and attachment downloads.

## Installation

### From GitHub (recommended for users)

```bash
pip install git+https://github.com/spunfromsun/haveyoursay-analysis.git
```

### Local Development

```bash
git clone https://github.com/spunfromsun/haveyoursay-analysis.git
cd haveyoursay-analysis
pip install -e ".[dev]"
```

### With Docker

```bash
docker build -t haveyoursay-analysis .
```

## Quick Start

### Fetch feedback for an initiative

```bash
haveyoursay-analysis fetch --publication-id 14488 --out data/14488
```

Outputs: `feedback.csv`, `attachments.csv`, `feedback_raw.json`

### Download attachments

```bash
haveyoursay-analysis download \
  --attachments-csv data/14488/attachments.csv \
  --out data/14488/files
```

### Organize by user type

```bash
haveyoursay-analysis organize \
  --attachments-dir data/14488/files \
  --attachments-csv data/14488/attachments.csv \
  --feedback-csv data/14488/feedback.csv \
  --out data/14488/organized \
  --only NGO --only TRADE_UNION
```

### Compare two phases

```bash
haveyoursay-analysis compare \
  --feedback-1 phase2/feedback.csv \
  --feedback-2 phase3/feedback.csv \
  --attachments-1 phase2/attachments.csv \
  --attachments-2 phase3/attachments.csv \
  --label-1 "Phase 2" \
  --label-2 "Phase 3"
```

## Ready to Use For

✅ **Any EU "Have Your Say" initiative** – by `publicationId`  
✅ **Cross-phase analysis** – compare feedback across multiple collection cycles  
✅ **Stakeholder filtering** – organize by user type (NGO, company, trade union, etc.)  
✅ **Bulk downloads** – fetch all attachments with retry logic and error tracking  
✅ **Metadata extraction** – structured CSV exports for analysis in pandas, Excel, or R  
✅ **Reproducible research** – containerized with Docker for consistent environments  

## Docker Usage

> **Note on Customization**: The stakeholder filtering by user type (NGO, TRADE_UNION) was designed for the original AI initiative analysis. If you adapt this tool for your own projects, customize the `organize` command filters and analysis logic for your stakeholder categories or analysis needs.
```bash
docker run --rm -v $(pwd)/data:/data haveyoursay-analysis \
  fetch --publication-id 14488 --out /data/14488

docker-compose run --rm haveyoursay \
  fetch --publication-id 14488 --out /data/14488
```

## Documentation

- [Getting Started](docs/getting_started.md) – Step-by-step tutorial
- [CLI Reference](docs/cli_reference.md) – All commands and options
- [Examples](docs/examples.md) – Real-world workflows
- [API Reference](docs/api.md) – Python API for programmatic use

## Notes on the EU API

The EC "Better Regulation" API structure has evolved. This tool parses feedback using the `content` field when present, falling back to older `_embedded` structures if needed. If the document download endpoint changes, adjust the URL template in [src/haveyoursay_analysis/files.py](src/haveyoursay_analysis/files.py).

## Acknowledgments

This project was inspired by [ghxm/haveyoursay](https://github.com/ghxm/haveyoursay), which provides comprehensive database-driven tools for EU Better Regulation data collection. This implementation takes a different architectural approach focused on lightweight, direct-to-CSV workflows.

## License

MIT
