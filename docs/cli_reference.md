# CLI Reference

## Overview

All commands follow the pattern:

```bash
haveyoursay-analysis COMMAND [OPTIONS]
```

Use `--help` for detailed options on any command.

## Commands

### fetch

Fetch feedback from the EU Better Regulation API.

```bash
haveyoursay-analysis fetch [OPTIONS]
```

**Options:**

- `--publication-id INTEGER` (required): EC publicationId (e.g., 14488 for AI Act)
- `--out PATH`: Output folder for JSON and CSVs (default: `data`)
- `--page-size INTEGER`: API page size (default: 100)
- `--language TEXT`: Language parameter for API (default: EN)

**Output Files:**

- `feedback.csv`: Normalized feedback metadata
- `attachments.csv`: Attachment metadata with feedback_id links
- `feedback_raw.json`: Raw API response (for auditing)

**Example:**

```bash
haveyoursay-analysis fetch --publication-id 14488 --out data/initiative_14488
```

---

### download

Download attachment files using attachment metadata.

```bash
haveyoursay-analysis download [OPTIONS]
```

**Options:**

- `--attachments-csv PATH` (required): Path to attachments.csv
- `--out PATH` (required): Output directory for files
- `--language TEXT`: Language for document endpoint (default: EN)
- `--only TEXT`: Filter by userType; repeat to specify multiple (e.g., `--only NGO --only TRADE_UNION`)
- `--skip-existing BOOL`: Skip files that already exist (default: True)

**Output:**

- Downloaded file count and failure count
- Files saved to `--out` directory

**Example:**

```bash
haveyoursay-analysis download \
  --attachments-csv data/initiative_14488/attachments.csv \
  --out data/initiative_14488/files \
  --only NGO --only TRADE_UNION
```

---

### organize

Organize downloaded files into folders by user type.

```bash
haveyoursay-analysis organize [OPTIONS]
```

**Options:**

- `--attachments-dir PATH` (required): Directory with downloaded files
- `--attachments-csv PATH` (required): Path to attachments.csv
- `--feedback-csv PATH` (required): Path to feedback.csv
- `--out PATH` (required): Output base directory for userType folders
- `--only TEXT`: Filter by userType; repeat for multiple values
- `--move BOOL`: Move files instead of copy (default: False)

**Output:**


> **Customization Note (Project-Specific):** The default `--only` examples (NGO, TRADE_UNION) reflect the original AI initiative analysis. For other projects, change the `--only` values and, if needed, adjust `organize_by_user_type` in `files.py` to reflect your stakeholder categories (e.g., companies, academia, public authority, country-specific filters).

**Example:**

```bash
haveyoursay-analysis organize \
  --attachments-dir data/initiative_14488/files \
  --attachments-csv data/initiative_14488/attachments.csv \
  --feedback-csv data/initiative_14488/feedback.csv \
  --out data/initiative_14488/organized \
  --only NGO --only TRADE_UNION
```

---

### compare

Compare two phases/cycles by feedback_id.

```bash
haveyoursay-analysis compare [OPTIONS]
```

**Options:**

- `--feedback-1 PATH` (required): Path to first feedback.csv (e.g., Phase 2)
- `--feedback-2 PATH` (required): Path to second feedback.csv (e.g., Phase 3)
- `--attachments-1 PATH` (required): Path to first attachments.csv
- `--attachments-2 PATH` (required): Path to second attachments.csv
- `--label-1 TEXT`: Label for first dataset (default: Phase 1)
- `--label-2 TEXT`: Label for second dataset (default: Phase 2)
- `--report-out PATH`: Output file for detailed comparison CSV (optional)

**Output:**

- Human-readable comparison report (to stdout)
- Optional CSV with detailed differences

**Comparison includes:**

- Total feedback count in each phase
- Common feedback_ids
- New and removed feedback
- User type distribution
- Attachment count changes

**Example:**

```bash
haveyoursay-analysis compare \
  --feedback-1 phase2/feedback.csv \
  --feedback-2 phase3/feedback.csv \
  --attachments-1 phase2/attachments.csv \
  --attachments-2 phase3/attachments.csv \
  --label-1 "Phase 2" \
  --label-2 "Phase 3" \
  --report-out comparison_report.csv
```

---

## Global Options

All commands support:

- `--help`: Show detailed help
- `--install-completion`: Install shell completion
- `--show-completion`: Show completion script

## Exit Codes

- `0`: Success
- `1`: Error (invalid input, missing file, API error, etc.)

---

## Common Patterns

### Full workflow in one session

```bash
# 1. Fetch
haveyoursay-analysis fetch --publication-id 14488 --out data/14488

# 2. Download (all files)
haveyoursay-analysis download \
  --attachments-csv data/14488/attachments.csv \
  --out data/14488/files

# 3. Organize (filter to NGO and TRADE_UNION)
haveyoursay-analysis organize \
  --attachments-dir data/14488/files \
  --attachments-csv data/14488/attachments.csv \
  --feedback-csv data/14488/feedback.csv \
  --out data/14488/organized \
  --only NGO --only TRADE_UNION

# 4. Compare phases
haveyoursay-analysis compare \
  --feedback-1 data/14488_v1/feedback.csv \
  --feedback-2 data/14488_v2/feedback.csv \
  --attachments-1 data/14488_v1/attachments.csv \
  --attachments-2 data/14488_v2/attachments.csv \
  --label-1 "Initial Collection" \
  --label-2 "Updated Collection" \
  --report-out diff_report.csv
```
