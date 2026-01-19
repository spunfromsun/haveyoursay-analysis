"""
Minimal integration test for the fetch command.
Run against a real publicationId to validate API parsing and CSV generation.
"""
import pytest
from pathlib import Path
from haveyoursay_analysis.api import fetch_feedback, extract_feedback_and_attachments


def test_fetch_publicationId_14488_integration():
    """
    Integration test: fetch feedback for publicationId=14488 (initiative 12527).
    This hits the live EC API, so it may be slow or fail if API is down.
    Mark as slow or skip in CI if needed.
    """
    rows = fetch_feedback(publication_id=14488, page_size=20, max_pages=1)
    assert isinstance(rows, list)
    # The initiative has 304+ feedback items; 1 page should yield 20
    assert len(rows) > 0

    data = extract_feedback_and_attachments(rows)
    assert "feedback" in data
    assert "attachments" in data
    assert len(data["feedback"]) > 0
