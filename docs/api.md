# API Reference

## Modules Overview

- **api.py**: Core API client for fetching EU feedback
- **files.py**: Download and file organization utilities
- **compare.py**: Phase comparison and analysis
- **cli.py**: Command-line interface (Typer)

---

## api.py

### `fetch_feedback(publication_id, page_size=100, language="EN", max_pages=None)`

Fetch feedback items for a given publication from the EC API.

**Parameters:**

- `publication_id` (int): EU Better Regulation publicationId
- `page_size` (int, default=100): Items per page
- `language` (str, default="EN"): Language code
- `max_pages` (int, optional): Limit pages fetched (for testing)

**Returns:**

- `List[Dict[str, Any]]`: Raw feedback items from API

**Raises:**

- `ApiError`: If the request fails after retries

**Example:**

```python
from haveyoursay_analysis.api import fetch_feedback

feedback = fetch_feedback(publication_id=14488, page_size=100)
print(f"Fetched {len(feedback)} feedback items")
```

### `extract_feedback_and_attachments(rows)`

Normalize raw API feedback into structured feedback and attachment records.

**Parameters:**

- `rows` (List[Dict[str, Any]]): Raw feedback rows from API

**Returns:**

- `Dict[str, List[Dict]]`: Keys "feedback" and "attachments", each a list of dicts

**Example:**

```python
from haveyoursay_analysis.api import fetch_feedback, extract_feedback_and_attachments

rows = fetch_feedback(publication_id=14488)
data = extract_feedback_and_attachments(rows)

feedback_records = data['feedback']  # List of normalized feedback
attachment_records = data['attachments']  # List of attachment metadata
```

---

## files.py

### `download_attachments_from_csv(attachments_csv, out_dir, language="EN", only_user_types=None, skip_existing=True)`

Download document files using attachment metadata from a CSV.

**Parameters:**

- `attachments_csv` (Path): CSV with columns: feedback_id, document_id, file_name, userType
- `out_dir` (Path): Output directory
- `language` (str, default="EN"): Language for document endpoint
- `only_user_types` (Iterable[str], optional): Filter by userType (e.g., ["NGO", "TRADE_UNION"])
- `skip_existing` (bool, default=True): Skip already-downloaded files

**Returns:**

- `Tuple[int, int]`: (downloaded_count, failed_count)

**Example:**

```python
from pathlib import Path
from haveyoursay_analysis.files import download_attachments_from_csv

downloaded, failed = download_attachments_from_csv(
    attachments_csv=Path("data/attachments.csv"),
    out_dir=Path("data/files"),
    only_user_types=["NGO", "TRADE_UNION"],
)
print(f"Downloaded: {downloaded}, Failed: {failed}")
```

### `organize_by_user_type(attachments_dir, attachments_csv, feedback_csv, out_dir, only_user_types=None, move=False)`

Organize downloaded files into folders by userType.

**Parameters:**

- `attachments_dir` (Path): Directory with downloaded files
- `attachments_csv` (Path): Attachments metadata (provides file_name → feedback_id mapping)
- `feedback_csv` (Path): Feedback metadata (provides feedback_id → userType mapping)
- `out_dir` (Path): Output base directory (will create subdirs per userType)
- `only_user_types` (Iterable[str], optional): Filter to specific userTypes
- `move` (bool, default=False): Move files (True) or copy (False)

**Returns:**

- `int`: Number of files organized

**Example:**

```python
from pathlib import Path
from haveyoursay_analysis.files import organize_by_user_type

count = organize_by_user_type(
    attachments_dir=Path("data/files"),
    attachments_csv=Path("data/attachments.csv"),
    feedback_csv=Path("data/feedback.csv"),
    out_dir=Path("data/organized"),
    only_user_types=["NGO", "TRADE_UNION"],
    move=False,
)
print(f"Organized {count} files")
```

---

## compare.py

### `compare_phases(feedback_csv_1, feedback_csv_2, label_1="Phase 1", label_2="Phase 2")`

Compare two feedback datasets by feedback_id.

**Parameters:**

- `feedback_csv_1` (Path): First feedback CSV
- `feedback_csv_2` (Path): Second feedback CSV
- `label_1` (str): Label for first dataset
- `label_2` (str): Label for second dataset

**Returns:**

- `Dict[str, Any]`: Comparison result with keys:
  - `total_1`, `total_2`: Total feedback count in each phase
  - `only_in_1`, `only_in_2`: Feedback unique to each phase (ids, count, data)
  - `common`: Common feedback_ids
  - `user_types_1`, `user_types_2`: User type distributions

**Example:**

```python
from pathlib import Path
from haveyoursay_analysis.compare import compare_phases

result = compare_phases(
    Path("phase2/feedback.csv"),
    Path("phase3/feedback.csv"),
    label_1="Phase 2",
    label_2="Phase 3",
)

print(f"Phase 2: {result['total_1']} entries")
print(f"Phase 3: {result['total_2']} entries")
print(f"Common: {result['common']['count']}")
```

### `compare_attachments(attachments_csv_1, attachments_csv_2, label_1="Phase 1", label_2="Phase 2")`

Compare two attachment datasets by feedback_id.

**Parameters:**

- `attachments_csv_1` (Path): First attachments CSV
- `attachments_csv_2` (Path): Second attachments CSV
- `label_1` (str): Label for first dataset
- `label_2` (str): Label for second dataset

**Returns:**

- `Dict[str, Any]`: Comparison result with keys:
  - `total_attachments_1`, `total_attachments_2`: Total attachments in each phase
  - `only_in_1`, `only_in_2`: Feedback with attachments unique to each phase
  - `attachment_changes`: Details of changed attachment counts

**Example:**

```python
from haveyoursay_analysis.compare import compare_attachments

result = compare_attachments(
    Path("phase2/attachments.csv"),
    Path("phase3/attachments.csv"),
    label_1="Phase 2",
    label_2="Phase 3",
)

print(f"Phase 2 attachments: {result['total_attachments_1']}")
print(f"Phase 3 attachments: {result['total_attachments_2']}")
```

### `generate_report(feedback_comparison, attachments_comparison, output_csv=None)`

Generate a human-readable comparison report.

**Parameters:**

- `feedback_comparison` (Dict): Result from `compare_phases()`
- `attachments_comparison` (Dict): Result from `compare_attachments()`
- `output_csv` (Path, optional): CSV file to save detailed comparison

**Returns:**

- `str`: Formatted report text

**Example:**

```python
from haveyoursay_analysis.compare import compare_phases, compare_attachments, generate_report

f_result = compare_phases(Path("phase2/feedback.csv"), Path("phase3/feedback.csv"))
a_result = compare_attachments(Path("phase2/attachments.csv"), Path("phase3/attachments.csv"))

report = generate_report(f_result, a_result, output_csv=Path("report.csv"))
print(report)
```

---

## Data Structures

### feedback.csv Columns

- `feedback_id`: Unique identifier for the feedback entry
- `userType`: Category of submitter (NGO, COMPANY, TRADE_UNION, etc.)
- `author`: Name or organization of author (may be empty)
- `country`: Country code (ISO 3166-1 alpha-3)
- `created`: Submission timestamp

### attachments.csv Columns

- `feedback_id`: Links to feedback entry
- `document_id`: EC document identifier
- `file_name`: Original filename
- `userType`: Copied from feedback for convenience

### Comparison Report Keys

**Feedback Comparison:**

- `label_1`, `label_2`: Phase labels
- `total_1`, `total_2`: Total entries
- `only_in_1`, `only_in_2`: Unique entries (count, ids, data dataframe)
- `common`: Shared entries
- `user_types_1`, `user_types_2`: User type value_counts dicts

**Attachment Comparison:**

- `label_1`, `label_2`: Phase labels
- `total_attachments_1`, `total_attachments_2`: Total attachment records
- `feedback_with_attachments_1`, `feedback_with_attachments_2`: Feedback entries with attachments
- `only_in_1`, `only_in_2`: Unique feedback (count, ids, attachment_count)
- `attachment_changes`: Dict of feedback_id → {before, after} for changed counts

---

## Error Handling

All modules use standard Python exceptions:

- `ValueError`: Invalid input (missing columns, bad paths)
- `FileNotFoundError`: CSV file not found
- `requests.RequestException`: Network/API errors (retried with backoff)

For API errors, the tool logs details and continues with partial results.

---

## Dependencies

Core dependencies (all included in `pyproject.toml`):

- `requests`: HTTP client with backoff retry
- `pandas`: Data manipulation and CSV I/O
- `typer`: CLI framework
- `tqdm`: Progress bars
- `backoff`: Retry logic

Optional for development:

- `pytest`: Testing
- `mypy`: Type checking
- `ruff`: Linting

---

## Examples

See [examples.md](examples.md) for real-world workflows combining these functions.
