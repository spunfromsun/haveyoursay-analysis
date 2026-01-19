from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Optional

import backoff
import requests
from tqdm import tqdm

# Default document download endpoint. Adjust if the EC API changes.
BASE_URL = "https://ec.europa.eu/info/law/better-regulation"
DOCUMENT_URL_TEMPLATE = f"{BASE_URL}/api/document/{{document_id}}"


@backoff.on_exception(backoff.expo, (requests.RequestException,), max_tries=5)
def _download(url: str, timeout: int = 60) -> bytes:
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return r.content


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def build_document_url(document_id: str | int, language: str = "EN") -> str:
    return f"{DOCUMENT_URL_TEMPLATE.format(document_id=document_id)}?language={language}"


def download_attachments_from_csv(
    attachments_csv: Path,
    out_dir: Path,
    language: str = "EN",
    only_user_types: Optional[Iterable[str]] = None,
    skip_existing: bool = True,
) -> tuple[int, int]:
    """
    Read `attachments.csv` with columns: feedback_id, document_id, file_name, userType
    and download files into `out_dir`.

    Returns (downloaded_count, failed_count).
    """
    import pandas as pd

    ensure_dir(out_dir)

    df = pd.read_csv(attachments_csv)
    if only_user_types:
        df = df[df["userType"].isin(list(only_user_types))]

    downloaded = 0
    failed = 0
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Downloading attachments"):
        doc_id = row.get("document_id")
        fname = row.get("file_name") or f"{doc_id}"
        if not doc_id:
            failed += 1
            continue

        # derive output path
        out_path = out_dir / str(fname)
        if skip_existing and out_path.exists():
            continue

        url = build_document_url(doc_id, language=language)
        try:
            content = _download(url)
            with open(out_path, "wb") as f:
                f.write(content)
            downloaded += 1
        except Exception:
            failed += 1

    return downloaded, failed


def organize_by_user_type(
    attachments_dir: Path,
    feedback_csv: Path,
    out_dir: Path,
    only_user_types: Optional[Iterable[str]] = None,
    move: bool = False,
) -> int:
    """
    Organize files into subfolders by `userType` using `feedback.csv` mapping.
    If `move` is False, files are copied; otherwise moved.

    Returns number of files organized.
    """
    import shutil
    import pandas as pd

    ensure_dir(out_dir)

    fb = pd.read_csv(feedback_csv)
    fb = fb[["feedback_id", "userType"]].dropna()
    mapping = dict(zip(fb["feedback_id"].astype(str), fb["userType"].astype(str)))

    count = 0
    for p in attachments_dir.iterdir():
        if not p.is_file():
            continue
        # Heuristic: assume filename prefix is feedback_id, else skip
        fid = p.stem.split("_")[0]
        user_type = mapping.get(fid)
        if not user_type:
            continue
        if only_user_types and user_type not in set(only_user_types):
            continue

        target_dir = out_dir / user_type
        ensure_dir(target_dir)
        target = target_dir / p.name
        if move:
            shutil.move(str(p), str(target))
        else:
            shutil.copy2(str(p), str(target))
        count += 1

    return count
