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
    attachments_csv: Path,
    feedback_csv: Path,
    out_dir: Path,
    only_user_types: Optional[Iterable[str]] = None,
    move: bool = False,
) -> int:
    """
    Organize files into subfolders by `userType` using mappings from
    `attachments.csv` (file_name -> feedback_id) and `feedback.csv` (feedback_id -> userType).

    If `move` is False, files are copied; otherwise moved.

    Returns number of files organized.
    """
    import shutil
    import pandas as pd

    ensure_dir(out_dir)

    fb = pd.read_csv(feedback_csv)
    fb = fb[["feedback_id", "userType"]].dropna()
    fid_to_user = dict(zip(fb["feedback_id"].astype(str), fb["userType"].astype(str)))

    at = pd.read_csv(attachments_csv)
    at = at[["file_name", "feedback_id"]].dropna()
    fname_to_fid = dict(zip(at["file_name"].astype(str), at["feedback_id"].astype(str)))

    count = 0
    only_set = set(only_user_types) if only_user_types else None

    for p in attachments_dir.iterdir():
        if not p.is_file():
            continue
        fname = p.name
        fid = fname_to_fid.get(fname)
        if not fid:
            continue
        user_type = fid_to_user.get(fid)
        if not user_type:
            continue
        if only_set and user_type not in only_set:
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
