# Getting Started

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

### Requirements

- Python 3.10 or later
- `pip` or `conda`

## First Run

### 1. Fetch Feedback

The first step is to fetch feedback data for a specific EU initiative using its `publicationId`.

Example: Initiative 14488 (AI Act consultation)

```bash
haveyoursay-analysis fetch \
  --publication-id 14488 \
  --out data/14488
```

This creates:
- `feedback.csv` - Feedback metadata (feedback_id, userType, country, author, etc.)
- `attachments.csv` - Attachment metadata (document_id, file_name, linked to feedback_id)
- `feedback_raw.json` - Raw API response (for auditing)

### 2. Download Attachments

Using the `attachments.csv` from step 1, download actual document files:

```bash
haveyoursay-analysis download \
  --attachments-csv data/14488/attachments.csv \
  --out data/14488/files
```

The output shows:
- Downloaded count
- Failed count (network errors, missing files)

### 3. Organize by User Type

Group files into folders for easier analysis:

```bash
haveyoursay-analysis organize \
  --attachments-dir data/14488/files \
  --attachments-csv data/14488/attachments.csv \
  --feedback-csv data/14488/feedback.csv \
  --out data/14488/organized \
  --only NGO --only TRADE_UNION
```

This copies (or moves with `--move`) files into:
```
data/14488/organized/
├── NGO/
│   ├── file1.pdf
│   ├── file2.docx
│   └── ...
└── TRADE_UNION/
    ├── file3.pdf
    └── ...
```

## Common Workflows

### Comparing Across Phases

If you have multiple feedback collections (e.g., Phase 2 and Phase 3):

```bash
haveyoursay-analysis compare \
  --feedback-1 phase2/feedback.csv \
  --feedback-2 phase3/feedback.csv \
  --attachments-1 phase2/attachments.csv \
  --attachments-2 phase3/attachments.csv \
  --label-1 "Phase 2" \
  --label-2 "Phase 3" \
  --report-out comparison.csv
```

This shows:
- New feedback entries in Phase 3
- Removed feedback (only in Phase 2)
- User type distribution changes
- Attachment count changes

### Filtering Downloads

Only download attachments from specific user types:

```bash
haveyoursay-analysis download \
  --attachments-csv data/14488/attachments.csv \
  --out data/14488/files \
  --only NGO --only ACADEMIC_RESEARCH_INSTITTUTION
```

### Using Docker

Build and run without installing locally:

```bash
docker build -t haveyoursay-analysis .
docker run --rm -v $(pwd)/data:/data haveyoursay-analysis \
  fetch --publication-id 14488 --out /data/14488
```

Or with `docker-compose`:

```bash
docker-compose run --rm haveyoursay \
  fetch --publication-id 14488 --out /data/14488
```

## File Structure

After a full run, your data directory looks like:

```
data/
└── 14488/
    ├── feedback.csv               # Metadata: feedback_id, userType, country, ...
    ├── attachments.csv            # Metadata: feedback_id, document_id, file_name, ...
    ├── feedback_raw.json          # Raw API response
    ├── files/                     # Downloaded files (all user types mixed)
    │   ├── document1.pdf
    │   ├── document2.docx
    │   └── ...
    └── organized/                 # Organized by user type
        ├── NGO/
        │   └── ...
        └── TRADE_UNION/
            └── ...
```

## Troubleshooting

### API timeouts or rate limits

The tool uses exponential backoff (up to 5 retries). If you hit rate limits, add delays between requests or split large fetches.

### Missing `document_id` in attachments.csv

Some feedback entries may not have attachments. The CSV will have empty `document_id` cells, and the download tool will skip them.

### Filenames with special characters

The tool preserves filenames from the API. Some may have unusual characters; check your file system limits.

## Next Steps

- Check out [CLI Reference](cli_reference.md) for all available options
- See [Examples](examples.md) for real-world use cases
- Read the [API Reference](api.md) to understand the data structures
