# Examples

## Example 1: Full Workflow for AI Act Consultation (Initiative 14488)

Initiative 14488 is the EU AI Act consultation. We'll fetch, organize, and analyze feedback.

### Step 1: Fetch Feedback

```bash
haveyoursay-analysis fetch \
  --publication-id 14488 \
  --out data/ai_act
```

**Output:**
- `data/ai_act/feedback.csv` - 304 feedback entries
- `data/ai_act/attachments.csv` - 260 attachments
- `data/ai_act/feedback_raw.json` - Raw API data

### Step 2: Download Attachments

```bash
haveyoursay-analysis download \
  --attachments-csv data/ai_act/attachments.csv \
  --out data/ai_act/files
```

**Output:**
```
Downloaded: 257, Failed: 0
```

### Step 3: Organize by Organization Type

Filter to NGO and trade union feedback only:

```bash
haveyoursay-analysis organize \
  --attachments-dir data/ai_act/files \
  --attachments-csv data/ai_act/attachments.csv \
  --feedback-csv data/ai_act/feedback.csv \
  --out data/ai_act/ngo_and_unions \
  --only NGO --only TRADE_UNION
```

**Output:**
```
Organized 58 files into data/ai_act/ngo_and_unions
```

### Step 4: Analyze in Python

Use the CSVs for analysis:

```python
import pandas as pd

feedback = pd.read_csv("data/ai_act/feedback.csv")
attachments = pd.read_csv("data/ai_act/attachments.csv")

# Count feedback by user type
print(feedback['userType'].value_counts())

# Find feedback with the most attachments
feedback_attachment_counts = attachments.groupby('feedback_id').size()
top_contributors = feedback_attachment_counts.nlargest(10)
print(top_contributors)
```

---

## Example 2: Comparing Two Collection Phases

You have Phase 2 (initial collection) and Phase 3 (updated/reopened collection) for the same initiative.

### Setup

Assuming you have:
- `phase2/feedback.csv` and `phase2/attachments.csv`
- `phase3/feedback.csv` and `phase3/attachments.csv`

### Run Comparison

```bash
haveyoursay-analysis compare \
  --feedback-1 phase2/feedback.csv \
  --feedback-2 phase3/feedback.csv \
  --attachments-1 phase2/attachments.csv \
  --attachments-2 phase3/attachments.csv \
  --label-1 "Initial Collection (Phase 2)" \
  --label-2 "Updated Collection (Phase 3)" \
  --report-out phase_comparison_report.csv
```

**Output:**
```
================================================================================
COMPARISON REPORT: Initial Collection (Phase 2) vs Updated Collection (Phase 3)
================================================================================

FEEDBACK SUMMARY
--------------------------------------------------------------------------------
Initial Collection (Phase 2): 304 entries
Updated Collection (Phase 3): 133 entries
Common feedback_ids: 0
Only in Initial Collection (Phase 2): 304
Only in Updated Collection (Phase 3): 133

USER TYPE DISTRIBUTION
--------------------------------------------------------------------------------
Initial Collection (Phase 2):
  NGO: 55
  COMPANY: 87
  BUSINESS_ASSOCIATION: 75
  ...
Updated Collection (Phase 3):
  NGO: 15
  COMPANY: 25
  BUSINESS_ASSOCIATION: 50
  ...

ATTACHMENT SUMMARY
================================================================================
```

**Interpretation:**
- The two phases have different participant sets (no feedback_id overlap)
- Phase 2 had significantly more feedback (304 vs 133)
- User type participation shifted between phases
- Each phase had one attachment per feedback entry

### Follow-up Analysis

```python
import pandas as pd

# Load the comparison report
comparison = pd.read_csv("phase_comparison_report.csv")

# Find only-in-phase-2 feedback
phase2_only = comparison[comparison['status'] == 'Only in Initial Collection (Phase 2)']
print(f"{len(phase2_only)} feedback entries unique to Phase 2")

# Analyze user type shifts
phase2_feedback = pd.read_csv("phase2/feedback.csv")
phase3_feedback = pd.read_csv("phase3/feedback.csv")

print("\nNGO participation:")
print(f"  Phase 2: {(phase2_feedback['userType'] == 'NGO').sum()}")
print(f"  Phase 3: {(phase3_feedback['userType'] == 'NGO').sum()}")
```

---

## Example 3: Targeted Analysis - NGOs Only

Focus analysis on NGO feedback and attachments.

### Download & Organize (NGO-only)

```bash
# Step 1: Fetch all feedback
haveyoursay-analysis fetch --publication-id 14488 --out data/ai_act

# Step 2: Download all attachments
haveyoursay-analysis download \
  --attachments-csv data/ai_act/attachments.csv \
  --out data/ai_act/files

# Step 3: Extract NGO feedback and files
haveyoursay-analysis organize \
  --attachments-dir data/ai_act/files \
  --attachments-csv data/ai_act/attachments.csv \
  --feedback-csv data/ai_act/feedback.csv \
  --out data/ai_act/ngo_only \
  --only NGO
```

### Analyze NGO Participation

```python
import pandas as pd

feedback = pd.read_csv("data/ai_act/feedback.csv")
attachments = pd.read_csv("data/ai_act/attachments.csv")

# Filter to NGO entries
ngo_feedback = feedback[feedback['userType'] == 'NGO']
ngo_attachments = attachments[attachments['feedback_id'].isin(ngo_feedback['feedback_id'])]

print(f"NGOs: {len(ngo_feedback)} organizations")
print(f"Total NGO attachments: {len(ngo_attachments)}")
print(f"Average attachments per NGO: {len(ngo_attachments) / len(ngo_feedback):.1f}")

# Geographic distribution (if country data is available)
print("\nNGO submissions by country:")
print(ngo_feedback['country'].value_counts().head(10))
```

---

## Example 4: Docker-based Workflow

Use Docker to ensure reproducibility across different machines.

### Build and Run

```bash
# Build the image
docker build -t haveyoursay-analysis .

# Fetch feedback
docker run --rm -v $(pwd)/data:/data haveyoursay-analysis \
  fetch --publication-id 14488 --out /data/ai_act

# Download attachments
docker run --rm -v $(pwd)/data:/data haveyoursay-analysis \
  download \
  --attachments-csv /data/ai_act/attachments.csv \
  --out /data/ai_act/files

# Organize
docker run --rm -v $(pwd)/data:/data haveyoursay-analysis \
  organize \
  --attachments-dir /data/ai_act/files \
  --attachments-csv /data/ai_act/attachments.csv \
  --feedback-csv /data/ai_act/feedback.csv \
  --out /data/ai_act/organized \
  --only NGO --only TRADE_UNION
```

### Using docker-compose

```bash
# Fetch
docker-compose run --rm haveyoursay \
  fetch --publication-id 14488 --out /data/ai_act

# Download
docker-compose run --rm haveyoursay \
  download \
  --attachments-csv /data/ai_act/attachments.csv \
  --out /data/ai_act/files

# Organize
docker-compose run --rm haveyoursay \
  organize \
  --attachments-dir /data/ai_act/files \
  --attachments-csv /data/ai_act/attachments.csv \
  --feedback-csv /data/ai_act/feedback.csv \
  --out /data/ai_act/organized \
  --only NGO --only TRADE_UNION
```

All data is persisted to `./data/` on your host machine.

---

## Example 5: Large-Scale Comparison (Multiple Initiatives)

Compare feedback across multiple initiatives.

### Script

```bash
#!/bin/bash

# Define initiatives
declare -A initiatives=(
    [14488]="AI Act"
    [14489]="Digital Services"
)

# Fetch all
for id in "${!initiatives[@]}"; do
    echo "Fetching ${initiatives[$id]} (ID: $id)..."
    haveyoursay-analysis fetch --publication-id "$id" --out "data/initiative_$id"
done

# Compare AI Act phases
haveyoursay-analysis compare \
  --feedback-1 "data/initiative_14488/feedback.csv" \
  --feedback-2 "data/initiative_14489/feedback.csv" \
  --attachments-1 "data/initiative_14488/attachments.csv" \
  --attachments-2 "data/initiative_14489/attachments.csv" \
  --label-1 "AI Act" \
  --label-2 "Digital Services" \
  --report-out "cross_initiative_comparison.csv"
```

---

## Tips & Tricks

### Resuming Interrupted Downloads

The `download` command respects existing files (with `--skip-existing`). Resume safely:

```bash
# Interrupted earlier; resume by running the same command again
haveyoursay-analysis download \
  --attachments-csv data/ai_act/attachments.csv \
  --out data/ai_act/files
```

### Analyzing Specific User Types

```bash
# Only download for companies
haveyoursay-analysis download \
  --attachments-csv data/ai_act/attachments.csv \
  --out data/ai_act/company_files \
  --only COMPANY

# Or organize first, then analyze subfolders
haveyoursay-analysis organize \
  --attachments-dir data/ai_act/files \
  --attachments-csv data/ai_act/attachments.csv \
  --feedback-csv data/ai_act/feedback.csv \
  --out data/ai_act/by_type \
  --only COMPANY --only NGO --only TRADE_UNION
```

### Automating Exports for Excel

```python
import pandas as pd

feedback = pd.read_csv("data/ai_act/feedback.csv")
attachments = pd.read_csv("data/ai_act/attachments.csv")

# Combine for Excel
merged = attachments.merge(feedback, on='feedback_id', how='left')
merged.to_excel("ai_act_analysis.xlsx", index=False)
```
