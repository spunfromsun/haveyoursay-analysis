from __future__ import annotations

from pathlib import Path
from typing import Optional, List

import typer
from tqdm import tqdm

from .api import fetch_feedback, extract_feedback_and_attachments
from .files import download_attachments_from_csv, organize_by_user_type
from .compare import compare_phases, compare_attachments, generate_report

app = typer.Typer(help="Tools for EU 'Have Your Say' feedback & attachments")


@app.command()
def fetch(
    publication_id: int = typer.Option(..., help="EC publicationId, e.g., 14488"),
    out: Path = typer.Option(Path("data"), help="Output folder for JSON and CSVs"),
    page_size: int = typer.Option(100, help="API page size"),
    language: str = typer.Option("EN", help="Language parameter for API"),
):
    """Fetch feedback JSON and export normalized CSVs."""
    out.mkdir(parents=True, exist_ok=True)

    typer.echo(f"Fetching feedback for publicationId={publication_id}")
    rows = fetch_feedback(publication_id, page_size=page_size, language=language)
    typer.echo(f"Fetched {len(rows)} feedback items")

    # Save raw JSON for audit
    raw_path = out / "feedback_raw.json"
    import json

    with open(raw_path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    # Normalize and save CSVs
    data = extract_feedback_and_attachments(rows)
    import pandas as pd

    fb_df = pd.DataFrame(data["feedback"]).drop_duplicates()
    at_df = pd.DataFrame(data["attachments"]).drop_duplicates()

    fb_df.to_csv(out / "feedback.csv", index=False)
    at_df.to_csv(out / "attachments.csv", index=False)

    typer.echo(f"Wrote: {out / 'feedback.csv'} and {out / 'attachments.csv'}")


@app.command()
def download(
    attachments_csv: Path = typer.Option(..., help="Path to attachments.csv"),
    out: Path = typer.Option(..., help="Output directory for files"),
    language: str = typer.Option("EN", help="Language for document endpoint"),
    only: Optional[List[str]] = typer.Option(None, help="Filter by userType, e.g., NGO TRADE_UNION"),
    skip_existing: bool = typer.Option(True, help="Skip files that already exist"),
):
    """Download attachments from attachments.csv using EC document endpoint."""
    downloaded, failed = download_attachments_from_csv(
        attachments_csv=attachments_csv,
        out_dir=out,
        language=language,
        only_user_types=only,
        skip_existing=skip_existing,
    )
    typer.echo(f"Downloaded: {downloaded}, Failed: {failed}")


@app.command()
def organize(
    attachments_dir: Path = typer.Option(..., help="Directory with downloaded attachments"),
    attachments_csv: Path = typer.Option(..., help="Path to attachments.csv"),
    feedback_csv: Path = typer.Option(..., help="Path to feedback.csv"),
    out: Path = typer.Option(..., help="Output base directory for userType folders"),
    only: Optional[List[str]] = typer.Option(None, help="Filter by userType; repeat flag for multiple values, e.g., --only NGO --only TRADE_UNION"),
    move: bool = typer.Option(False, help="Move files instead of copy"),
):
    """Organize downloaded attachments into subfolders by userType using attachments.csv and feedback.csv."""
    n = organize_by_user_type(
        attachments_dir=attachments_dir,
        attachments_csv=attachments_csv,
        feedback_csv=feedback_csv,
        out_dir=out,
        only_user_types=only,
        move=move,
    )
    typer.echo(f"Organized {n} files into {out}")


@app.command()
def compare(
    feedback_1: Path = typer.Option(..., help="Path to first feedback.csv (e.g., Phase 2)"),
    feedback_2: Path = typer.Option(..., help="Path to second feedback.csv (e.g., Phase 3)"),
    attachments_1: Path = typer.Option(..., help="Path to first attachments.csv"),
    attachments_2: Path = typer.Option(..., help="Path to second attachments.csv"),
    label_1: str = typer.Option("Phase 1", help="Label for first dataset"),
    label_2: str = typer.Option("Phase 2", help="Label for second dataset"),
    report_out: Optional[Path] = typer.Option(None, help="Output file for detailed comparison CSV"),
):
    """Compare two phases by feedback_id; show differences in entries and attachments."""
    f_comp = compare_phases(feedback_1, feedback_2, label_1=label_1, label_2=label_2)
    a_comp = compare_attachments(attachments_1, attachments_2, label_1=label_1, label_2=label_2)

    report = generate_report(f_comp, a_comp, output_csv=report_out)
    typer.echo(report)


if __name__ == "__main__":
    app()
