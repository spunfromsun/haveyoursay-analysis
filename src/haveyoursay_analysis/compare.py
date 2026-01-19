from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

import pandas as pd


def load_feedback_csv(csv_path: Path) -> pd.DataFrame:
    """Load a feedback CSV with feedback_id as index."""
    df = pd.read_csv(csv_path)
    if "feedback_id" not in df.columns:
        raise ValueError(f"CSV {csv_path} missing 'feedback_id' column")
    df["feedback_id"] = df["feedback_id"].astype(str)
    return df.set_index("feedback_id")


def compare_phases(
    feedback_csv_1: Path,
    feedback_csv_2: Path,
    label_1: str = "Phase 1",
    label_2: str = "Phase 2",
) -> Dict[str, Any]:
    """
    Compare two feedback datasets by feedback_id.
    Returns summary of: new, removed, common, and changed entries.
    """
    df1 = load_feedback_csv(feedback_csv_1)
    df2 = load_feedback_csv(feedback_csv_2)

    ids_1 = set(df1.index)
    ids_2 = set(df2.index)

    only_in_1 = ids_1 - ids_2
    only_in_2 = ids_2 - ids_1
    common = ids_1 & ids_2

    result = {
        "label_1": label_1,
        "label_2": label_2,
        "total_1": len(df1),
        "total_2": len(df2),
        "only_in_1": {
            "count": len(only_in_1),
            "ids": sorted(list(only_in_1)),
            "data": df1.loc[list(only_in_1)] if only_in_1 else pd.DataFrame(),
        },
        "only_in_2": {
            "count": len(only_in_2),
            "ids": sorted(list(only_in_2)),
            "data": df2.loc[list(only_in_2)] if only_in_2 else pd.DataFrame(),
        },
        "common": {
            "count": len(common),
        },
    }

    # Analyze user type distribution
    result["user_types_1"] = df1["userType"].value_counts().to_dict() if "userType" in df1.columns else {}
    result["user_types_2"] = df2["userType"].value_counts().to_dict() if "userType" in df2.columns else {}

    return result


def compare_attachments(
    attachments_csv_1: Path,
    attachments_csv_2: Path,
    label_1: str = "Phase 1",
    label_2: str = "Phase 2",
) -> Dict[str, Any]:
    """
    Compare two attachment datasets by feedback_id.
    Returns summary of attachment counts per feedback.
    """
    df1 = pd.read_csv(attachments_csv_1)
    df2 = pd.read_csv(attachments_csv_2)

    if "feedback_id" not in df1.columns or "feedback_id" not in df2.columns:
        raise ValueError("CSVs missing 'feedback_id' column")

    df1["feedback_id"] = df1["feedback_id"].astype(str)
    df2["feedback_id"] = df2["feedback_id"].astype(str)

    # Count attachments per feedback
    counts_1 = df1.groupby("feedback_id").size()
    counts_2 = df2.groupby("feedback_id").size()

    ids_1 = set(counts_1.index)
    ids_2 = set(counts_2.index)

    only_in_1 = ids_1 - ids_2
    only_in_2 = ids_2 - ids_1
    common = ids_1 & ids_2

    # Analyze changes in common feedback
    changes = {}
    for fid in common:
        c1, c2 = counts_1[fid], counts_2[fid]
        if c1 != c2:
            changes[fid] = {"before": c1, "after": c2}

    result = {
        "label_1": label_1,
        "label_2": label_2,
        "total_attachments_1": len(df1),
        "total_attachments_2": len(df2),
        "feedback_with_attachments_1": len(counts_1),
        "feedback_with_attachments_2": len(counts_2),
        "only_in_1": {
            "count": len(only_in_1),
            "ids": sorted(list(only_in_1)),
            "attachment_count": sum(counts_1[fid] for fid in only_in_1),
        },
        "only_in_2": {
            "count": len(only_in_2),
            "ids": sorted(list(only_in_2)),
            "attachment_count": sum(counts_2[fid] for fid in only_in_2),
        },
        "attachment_changes": {
            "count": len(changes),
            "details": changes,
        },
    }

    return result


def generate_report(
    feedback_comparison: Dict[str, Any],
    attachments_comparison: Dict[str, Any],
    output_csv: Path | None = None,
) -> str:
    """
    Generate a human-readable comparison report.
    Optionally save details to CSV.
    """
    lines = []
    f_comp = feedback_comparison
    a_comp = attachments_comparison

    lines.append("=" * 80)
    lines.append(f"COMPARISON REPORT: {f_comp['label_1']} vs {f_comp['label_2']}")
    lines.append("=" * 80)
    lines.append("")

    # Feedback summary
    lines.append("FEEDBACK SUMMARY")
    lines.append("-" * 80)
    lines.append(f"{f_comp['label_1']}: {f_comp['total_1']} entries")
    lines.append(f"{f_comp['label_2']}: {f_comp['total_2']} entries")
    lines.append(f"Common feedback_ids: {f_comp['common']['count']}")
    lines.append(f"Only in {f_comp['label_1']}: {f_comp['only_in_1']['count']}")
    lines.append(f"Only in {f_comp['label_2']}: {f_comp['only_in_2']['count']}")
    lines.append("")

    # User type breakdown
    if f_comp["user_types_1"] or f_comp["user_types_2"]:
        lines.append("USER TYPE DISTRIBUTION")
        lines.append("-" * 80)
        lines.append(f"{f_comp['label_1']}:")
        for utype, count in sorted(f_comp["user_types_1"].items()):
            lines.append(f"  {utype}: {count}")
        lines.append(f"{f_comp['label_2']}:")
        for utype, count in sorted(f_comp["user_types_2"].items()):
            lines.append(f"  {utype}: {count}")
        lines.append("")

    # Attachments summary
    lines.append("ATTACHMENT SUMMARY")
    lines.append("-" * 80)
    lines.append(f"{a_comp['label_1']}: {a_comp['total_attachments_1']} total, {a_comp['feedback_with_attachments_1']} feedback")
    lines.append(f"{a_comp['label_2']}: {a_comp['total_attachments_2']} total, {a_comp['feedback_with_attachments_2']} feedback")
    lines.append("")

    lines.append("ATTACHMENT CHANGES")
    lines.append("-" * 80)
    lines.append(f"Feedback only in {a_comp['label_1']}: {a_comp['only_in_1']['count']} ({a_comp['only_in_1']['attachment_count']} attachments)")
    lines.append(f"Feedback only in {a_comp['label_2']}: {a_comp['only_in_2']['count']} ({a_comp['only_in_2']['attachment_count']} attachments)")
    lines.append(f"Attachment count changes: {a_comp['attachment_changes']['count']} feedback")
    lines.append("")

    if a_comp["attachment_changes"]["details"]:
        lines.append("CHANGED FEEDBACK (attachment count):")
        for fid, change in sorted(a_comp["attachment_changes"]["details"].items())[:20]:
            lines.append(f"  {fid}: {change['before']} → {change['after']}")
        if len(a_comp["attachment_changes"]["details"]) > 20:
            lines.append(f"  ... and {len(a_comp['attachment_changes']['details']) - 20} more")
    lines.append("")

    if output_csv:
        # Save detailed comparison
        details_list = []
        for fid in f_comp["only_in_1"]["ids"][:50]:
            details_list.append({
                "feedback_id": fid,
                "status": f"Only in {f_comp['label_1']}",
                "phase_1_present": True,
                "phase_2_present": False,
            })
        for fid in f_comp["only_in_2"]["ids"][:50]:
            details_list.append({
                "feedback_id": fid,
                "status": f"Only in {f_comp['label_2']}",
                "phase_1_present": False,
                "phase_2_present": True,
            })

        if details_list:
            details_df = pd.DataFrame(details_list)
            details_df.to_csv(output_csv, index=False)
            lines.append(f"Detailed comparison saved to: {output_csv}")

    lines.append("=" * 80)
    return "\n".join(lines)
