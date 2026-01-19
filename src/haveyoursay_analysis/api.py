from __future__ import annotations

import backoff
import json
from typing import Any, Dict, List, Optional

import requests

BASE_URL = "https://ec.europa.eu/info/law/better-regulation"
FEEDBACK_ENDPOINT = f"{BASE_URL}/api/allFeedback"


class ApiError(Exception):
    pass


@backoff.on_exception(backoff.expo, (requests.RequestException,), max_tries=5)
def _get(url: str, params: Optional[Dict[str, Any]] = None, timeout: int = 30) -> requests.Response:
    resp = requests.get(url, params=params, timeout=timeout)
    resp.raise_for_status()
    return resp


def fetch_feedback(
    publication_id: int,
    page_size: int = 100,
    language: str = "EN",
    max_pages: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch feedback items for a given publicationId.
    Handles current API (`content`) and legacy (`_embedded.feedback`) structures.
    """
    feedback: List[Dict[str, Any]] = []
    page = 0

    while True:
        params = {
            "publicationId": publication_id,
            "size": page_size,
            "page": page,
            "language": language,
        }
        r = _get(FEEDBACK_ENDPOINT, params=params)
        data = r.json()

        items: List[Dict[str, Any]] = []
        if isinstance(data, dict):
            if "content" in data and isinstance(data["content"], list):
                items = data["content"]
            elif "_embedded" in data and isinstance(data["_embedded"], dict):
                embedded = data["_embedded"]
                if "feedback" in embedded and isinstance(embedded["feedback"], list):
                    items = embedded["feedback"]

        if not items:
            break

        feedback.extend(items)

        # pagination control
        total_pages: Optional[int] = None
        if "totalPages" in data:
            # some APIs return `totalPages`
            try:
                total_pages = int(data["totalPages"])  # type: ignore
            except Exception:
                total_pages = None
        elif "pageable" in data and isinstance(data["pageable"], dict):
            # current API often returns `pageable` and `totalElements`
            # we continue until `items` is empty
            total_pages = None

        page += 1
        if max_pages is not None and page >= max_pages:
            break
        if total_pages is not None and page >= total_pages:
            break

    return feedback


def extract_feedback_and_attachments(rows: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """
    Normalize feedback and attachment metadata from raw items.
    Returns dict with keys: `feedback`, `attachments`.
    """
    feedback_norm: List[Dict[str, Any]] = []
    attachments_norm: List[Dict[str, Any]] = []

    for row in rows:
        # feedback-level fields
        fid = row.get("id") or row.get("feedbackId")
        user_type = row.get("userType")
        author = row.get("author")
        country = row.get("country")
        created = row.get("createdDate") or row.get("created")

        feedback_norm.append({
            "feedback_id": fid,
            "userType": user_type,
            "author": author,
            "country": country,
            "created": created,
        })

        # attachments (varied structures: `attachments`, `documents`)
        docs = []
        if isinstance(row.get("attachments"), list):
            docs = row["attachments"]
        elif isinstance(row.get("documents"), list):
            docs = row["documents"]

        for d in docs:
            document_id = d.get("documentId") or d.get("id")
            file_name = d.get("fileName") or d.get("name")
            attachments_norm.append({
                "feedback_id": fid,
                "document_id": document_id,
                "file_name": file_name,
                "userType": user_type,
            })

    return {"feedback": feedback_norm, "attachments": attachments_norm}
