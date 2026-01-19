# haveyoursay-analysis

Standalone toolkit to fetch EU "Have Your Say" feedback for a given `publicationId`, extract attachment metadata, download attachments, and organize files for analysis.

## Quick Start

- Install in your virtual environment:
  - `pip install -e .` from this folder, or
  - `pipx install haveyoursay-analysis` (after publishing).

- Commands:
  - `haveyoursay-analysis fetch --publication-id 14488 --out data/14488`
    - Saves raw JSON, `feedback.csv`, and `attachments.csv`.
  - `haveyoursay-analysis download --attachments-csv data/14488/attachments.csv --out data/14488/attachments`
    - Downloads attachment files. Uses the EU API document endpoint by default.
  - `haveyoursay-analysis organize --attachments-dir data/14488/attachments --feedback-csv data/14488/feedback.csv --out data/14488/attachments_by_type --only NGO TRADE_UNION`
    - Moves/copies files into subfolders by `userType`.

## Notes on the EU API

The EC "Better Regulation" API structure has evolved. This tool parses feedback using the `content` field when present, falling back to older `_embedded` structures if needed. If the document download endpoint changes, adjust the URL template in [src/haveyoursay_analysis/files.py](src/haveyoursay_analysis/files.py).

## License

MIT
