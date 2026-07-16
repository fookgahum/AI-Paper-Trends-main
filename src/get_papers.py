"""Retrieve public conference submissions and reviews from OpenReview API v2."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from statistics import fmean
from typing import Any, Dict, List, Optional

import openreview.api
from tqdm import tqdm


def _content_value(content: Mapping[str, Any], key: str, default: Any = None) -> Any:
    """Read either an API v2 ``{"value": ...}`` field or a plain value."""
    value = content.get(key, default)
    if isinstance(value, Mapping) and "value" in value:
        return value["value"]
    return value


def _reply_value(reply: Any, key: str, default: Any = None) -> Any:
    content = (
        reply.get("content", {})
        if isinstance(reply, Mapping)
        else getattr(reply, "content", {})
    )
    if not isinstance(content, Mapping):
        return default
    return _content_value(content, key, default)


def _reply_invitations(reply: Any) -> List[str]:
    invitations = (
        reply.get("invitations", [])
        if isinstance(reply, Mapping)
        else getattr(reply, "invitations", [])
    )
    return invitations or []


def _parse_numeric_rating(value: Any) -> Optional[float]:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        match = re.search(r"-?\d+(?:\.\d+)?", value)
        if match:
            return float(match.group(0))
    return None


def _extract_review_details(note: Any) -> Dict[str, Any]:
    """Extract the public decision and review scores embedded in note replies."""
    details = getattr(note, "details", {}) or {}
    replies = details.get("replies", []) if isinstance(details, Mapping) else []
    ratings: List[float] = []
    decision = "N/A"

    for reply in replies:
        invitations = _reply_invitations(reply)

        if any(invitation.endswith("/Decision") for invitation in invitations):
            decision_value = _reply_value(
                reply, "decision", _reply_value(reply, "recommendation", "N/A")
            )
            decision = str(decision_value or "N/A")

        if any(
            invitation.endswith("/Official_Review")
            or invitation.endswith("/Review")
            for invitation in invitations
        ):
            for field in ("rating", "recommendation", "overall_rating", "overall_assessment"):
                rating = _parse_numeric_rating(_reply_value(reply, field))
                if rating is not None:
                    ratings.append(rating)
                    break

    return {
        "decision": decision,
        "review_ratings": ratings,
        "avg_rating": round(fmean(ratings), 2) if ratings else None,
    }


def _extract_paper(note: Any, fetch_reviews: bool) -> Dict[str, Any]:
    content = note.content
    paper = {
        "id": note.id,
        "title": _content_value(content, "title", "N/A"),
        "abstract": _content_value(content, "abstract", "N/A"),
        "keywords": _content_value(content, "keywords", []) or [],
        "authors": _content_value(content, "authors", []) or [],
    }
    if fetch_reviews:
        paper.update(_extract_review_details(note))
    return paper


def _submission_invitation(client: openreview.api.OpenReviewClient, conference_id: str) -> str:
    """Resolve the venue's submission invitation, with common-name fallbacks."""
    try:
        venue_group = client.get_group(conference_id)
        submission_name = _content_value(venue_group.content, "submission_name")
        if submission_name:
            return f"{conference_id}/-/{submission_name}"
    except Exception as error:
        print(f"Could not read venue metadata; trying standard invitations: {error}")

    return f"{conference_id}/-/Submission"


def get_all_papers(
    client: openreview.api.OpenReviewClient,
    conference_id: str,
    fetch_reviews: bool = False,
    limit: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Fetch submissions, optionally embedding all public replies in the same request."""
    primary_invitation = _submission_invitation(client, conference_id)
    candidates = list(
        dict.fromkeys(
            [
                primary_invitation,
                f"{conference_id}/-/Submission",
                f"{conference_id}/-/Blind_Submission",
            ]
        )
    )
    details = "replies" if fetch_reviews else None
    errors: List[str] = []

    for invitation in candidates:
        print(f"Trying submission invitation: {invitation}")
        try:
            if limit is not None and limit <= 1000:
                notes: Iterable[Any] = client.get_notes(
                    invitation=invitation, limit=limit, details=details
                )
            else:
                notes = client.get_all_notes(invitation=invitation, details=details)
            notes = list(notes)
            if limit is not None:
                notes = notes[:limit]
            if notes:
                return [
                    _extract_paper(note, fetch_reviews)
                    for note in tqdm(notes, desc="Processing OpenReview submissions")
                ]
        except Exception as error:
            errors.append(f"{invitation}: {error}")

    message = "\n".join(errors) if errors else "No submissions were returned."
    raise RuntimeError(
        f"Unable to retrieve submissions for '{conference_id}'. Tried:\n{message}"
    )


def build_output_path(config: Dict[str, Any], raw_data_dir: Path) -> Path:
    """Return the deterministic JSONL cache path for a configuration."""
    conference_id = config["conference_id"]
    safe_name = conference_id.replace("/", "_").replace(".", "")
    suffix = "_reviews" if config.get("fetch_reviews", False) else ""
    limit = config.get("limit")
    limit_suffix = f"_limit{limit}" if limit is not None else ""
    return raw_data_dir / f"{safe_name}_papers{suffix}{limit_suffix}.jsonl"


def main(config: Dict[str, Any], raw_data_dir: Path) -> Path:
    """Fetch paper data and persist it as newline-delimited JSON."""
    username = os.getenv("OPENREVIEW_USERNAME")
    password = os.getenv("OPENREVIEW_PASSWORD")
    if bool(username) != bool(password):
        raise ValueError(
            "Set both OPENREVIEW_USERNAME and OPENREVIEW_PASSWORD, or neither."
        )
    client_options = {"baseurl": "https://api2.openreview.net"}
    if username and password:
        client_options.update({"username": username, "password": password})
    client = openreview.api.OpenReviewClient(**client_options)
    papers = get_all_papers(
        client=client,
        conference_id=config["conference_id"],
        fetch_reviews=config.get("fetch_reviews", False),
        limit=config.get("limit"),
    )

    output_path = build_output_path(config, raw_data_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as file:
        for paper in papers:
            file.write(json.dumps(paper, ensure_ascii=False) + "\n")

    print(f"Saved {len(papers)} papers to: {output_path}")
    return output_path
