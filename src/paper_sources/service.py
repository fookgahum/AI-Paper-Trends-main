"""Fetch, normalize, deduplicate, and persist papers from a public URL."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import re
import socket
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

from src.storage import LocalDatabase


@dataclass(frozen=True)
class FetchedDocument:
    """A downloaded source document, separated from HTTP for deterministic tests."""

    url: str
    content: bytes
    content_type: str


FetchFunction = Callable[[str], FetchedDocument]


class PaperPullError(RuntimeError):
    """Raised when a paper source cannot be safely fetched or parsed."""


class PaperPullService:
    """Run observable paper-ingestion jobs against configured URLs."""

    def __init__(
        self,
        database: LocalDatabase,
        artifact_root: Path,
        fetch: Optional[FetchFunction] = None,
    ) -> None:
        self.database = database
        self.artifact_root = artifact_root
        self._fetch = fetch or fetch_public_document

    def create_job(self, payload: Dict[str, Any]) -> Dict[str, str]:
        """Persist a reusable source and queue its first pull job."""
        source_id = self.database.create_source(payload)
        job_id = self.database.create_job(
            "paper_pull", {"source_id": source_id, **payload}
        )
        return {"source_id": source_id, "job_id": job_id}

    def create_job_for_source(self, source_id: str) -> str:
        source = self.database.get_source(source_id)
        return self.database.create_job(
            "paper_pull", {"source_id": source_id, "url": source["url"]}
        )

    def run_job(self, job_id: str, source_id: str) -> None:
        """Execute a pull job and leave its complete state in SQLite."""
        try:
            source = self.database.get_source(source_id)
            self.database.update_job(
                job_id, status="running", stage="fetching", progress_total=5
            )
            document = self._fetch(source["url"])
            self._save_source_snapshot(job_id, document)
            self.database.update_job(
                job_id, stage="parsing", progress_current=1, progress_total=5
            )
            raw_papers = parse_document(document, source["parser_type"])
            self.database.update_job(
                job_id, stage="normalizing", progress_current=2, progress_total=5
            )
            normalized, rejected = normalize_papers(raw_papers, source)
            self.database.update_job(
                job_id, stage="deduplicating", progress_current=3, progress_total=5
            )
            counts = self.database.upsert_papers(normalized, source_id)
            pdf_counts = {"downloaded": 0, "failed": 0}
            if source["download_pdf"]:
                self.database.update_job(
                    job_id, stage="downloading_pdfs", progress_current=4
                )
                pdf_counts = self._download_pdfs(normalized, job_id)
            self.database.mark_source_pulled(source_id)
            result = {
                "source_id": source_id,
                "parsed": len(raw_papers),
                "accepted": len(normalized),
                "rejected": rejected,
                **counts,
                "pdfs": pdf_counts,
            }
            self.database.update_job(
                job_id,
                status="completed",
                stage="completed",
                progress_current=5,
                progress_total=5,
                result=result,
            )
        except Exception as error:
            self.database.update_job(
                job_id,
                status="failed",
                stage="failed",
                error={"type": type(error).__name__, "message": str(error)},
            )

    def _save_source_snapshot(self, job_id: str, document: FetchedDocument) -> None:
        suffix = ".json" if "json" in document.content_type else ".html"
        directory = self.artifact_root / "source_snapshots"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"{job_id}{suffix}").write_bytes(document.content)

    def _download_pdfs(
        self, papers: Iterable[Dict[str, Any]], job_id: str
    ) -> Dict[str, int]:
        counts = {"downloaded": 0, "failed": 0}
        directory = self.artifact_root / "papers"
        directory.mkdir(parents=True, exist_ok=True)
        rows = [paper for paper in papers if paper.get("pdf_url")]
        for index, paper in enumerate(rows, 1):
            self.database.update_job(
                job_id,
                stage=f"downloading_pdfs:{index}/{len(rows)}",
                progress_current=4,
                progress_total=5,
            )
            pdf_url = paper.get("pdf_url")
            try:
                document = self._fetch(pdf_url)
                if "pdf" not in document.content_type.lower() and not document.content.startswith(
                    b"%PDF"
                ):
                    raise PaperPullError(f"Not a PDF response: {pdf_url}")
                (directory / f"{paper['id']}.pdf").write_bytes(document.content)
                counts["downloaded"] += 1
            except Exception:
                counts["failed"] += 1
        return counts

def validate_public_url(url: str) -> None:
    """Reject local-network targets to keep the user-entered fetch endpoint safe."""
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise PaperPullError("Paper source must be an HTTP or HTTPS URL")
    if parsed.username or parsed.password:
        raise PaperPullError("Credentials are not allowed in paper-source URLs")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(parsed.hostname, None)}
    except socket.gaierror as error:
        raise PaperPullError(f"Cannot resolve paper-source host: {parsed.hostname}") from error
    for address in addresses:
        ip = ipaddress.ip_address(address)
        if not ip.is_global:
            raise PaperPullError("Paper sources must resolve to a public internet address")


def fetch_public_document(url: str) -> FetchedDocument:
    """Fetch one bounded public document after rejecting private-network targets."""
    validate_public_url(url)
    with httpx.Client(
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
        headers={"User-Agent": "AI-Paper-Trends/2.0 (+local research tool)"},
    ) as client:
        response = client.get(url)
        response.raise_for_status()
        validate_public_url(str(response.url))
        if len(response.content) > 50 * 1024 * 1024:
            raise PaperPullError("Source response exceeds the 50 MB safety limit")
        return FetchedDocument(
            url=str(response.url),
            content=response.content,
            content_type=response.headers.get(
                "content-type", "application/octet-stream"
            ),
        )


def parse_document(document: FetchedDocument, parser_type: str = "auto") -> List[Dict[str, Any]]:
    """Parse common JSON feeds or proceedings-style HTML pages."""
    parser = parser_type.lower().strip()
    if parser == "auto":
        parser = "json" if "json" in document.content_type.lower() else "html"
    if parser == "json":
        return _parse_json(document)
    if parser in {"html", "acl"}:
        return _parse_html(document, acl_only=parser == "acl")
    raise PaperPullError(f"Unsupported parser type: {parser_type}")


def normalize_papers(
    papers: Iterable[Dict[str, Any]], source: Dict[str, Any]
) -> tuple[List[Dict[str, Any]], int]:
    """Map parser output to the application's stable paper schema."""
    normalized: List[Dict[str, Any]] = []
    rejected = 0
    seen: set[str] = set()
    for row in papers:
        title = _clean_text(row.get("title"))
        abstract = _clean_text(row.get("abstract"))
        if not title or not abstract:
            rejected += 1
            continue
        official_id = _clean_text(row.get("official_id"))
        digest_input = official_id or f"{source['conference']}|{source['year']}|{title.casefold()}"
        paper_id = "paper_" + hashlib.sha256(digest_input.encode("utf-8")).hexdigest()[:24]
        raw_source_url = str(row.get("source_url") or "").strip()
        source_url = (
            urljoin(source["url"], raw_source_url)
            if raw_source_url
            else f"{source['url']}#paper-{paper_id.removeprefix('paper_')}"
        )
        if paper_id in seen:
            rejected += 1
            continue
        seen.add(paper_id)
        normalized.append(
            {
                "id": paper_id,
                "official_id": official_id or None,
                "conference": source["conference"],
                "year": int(source["year"]),
                "title": title,
                "abstract": abstract,
                "authors": _string_list(row.get("authors")),
                "keywords": _string_list(row.get("keywords")),
                "decision": _clean_text(row.get("decision")) or "Published",
                "source_url": source_url,
                "pdf_url": urljoin(source_url, str(row["pdf_url"])) if row.get("pdf_url") else None,
                "code_urls": _string_list(row.get("code_urls")),
            }
        )
    return normalized, rejected


def _parse_json(document: FetchedDocument) -> List[Dict[str, Any]]:
    try:
        payload = json.loads(document.content.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise PaperPullError("Source is not valid UTF-8 JSON") from error
    rows: Any = payload
    if isinstance(payload, dict):
        for key in ("papers", "results", "items", "submissions", "notes", "data"):
            if isinstance(payload.get(key), list):
                rows = payload[key]
                break
    if not isinstance(rows, list):
        raise PaperPullError("JSON source must contain a paper list")
    return [_json_paper(row, document.url) for row in rows if isinstance(row, dict)]


def _json_paper(row: Dict[str, Any], base_url: str) -> Dict[str, Any]:
    content = row.get("content") if isinstance(row.get("content"), dict) else {}

    def first(*names: str, default: Any = None) -> Any:
        for name in names:
            for owner in (row, content):
                value = owner.get(name)
                if isinstance(value, dict) and "value" in value:
                    value = value["value"]
                if value not in (None, "", []):
                    return value
        return default

    official_id = first("id", "paper_id", "forum", "doi")
    source_url = first("source_url", "url", "paper_url")
    if not source_url and official_id and "openreview.net" in (urlparse(base_url).hostname or ""):
        source_url = f"https://openreview.net/forum?id={official_id}"
    return {
        "official_id": official_id,
        "title": first("title", "name"),
        "abstract": first("abstract", "summary", "description"),
        "authors": first("authors", "author", default=[]),
        "keywords": first("keywords", "topics", default=[]),
        "decision": first("decision", "status", default="Published"),
        "source_url": urljoin(base_url, str(source_url or official_id or "")),
        "pdf_url": first("pdf_url", "pdf", "pdfUrl"),
        "code_urls": first("code_urls", "code", "repository", default=[]),
    }


def _parse_html(document: FetchedDocument, acl_only: bool = False) -> List[Dict[str, Any]]:
    soup = BeautifulSoup(document.content, "html.parser")
    papers: List[Dict[str, Any]] = []
    hostname = urlparse(document.url).hostname or ""
    if acl_only or "aclanthology.org" in hostname.lower():
        papers = _parse_acl_page(soup, document.url)
        if papers:
            return papers

    containers = soup.select(
        "article, .paper, .paper-card, .paper-item, li.paper, li.publication"
    )
    for container in containers:
        title_node = container.select_one("h1, h2, h3, .title, .paper-title")
        link = (title_node.select_one("a") if title_node else None) or container.select_one("a[href]")
        abstract_node = container.select_one(".abstract, .summary, [data-abstract]")
        authors_node = container.select_one(".authors, .author-list, [data-authors]")
        pdf_link = container.select_one("a[href$='.pdf'], a.pdf")
        if not title_node or not abstract_node:
            continue
        papers.append(
            {
                "title": title_node.get_text(" ", strip=True),
                "abstract": abstract_node.get_text(" ", strip=True),
                "authors": _split_people(authors_node.get_text(" ", strip=True)) if authors_node else [],
                "source_url": urljoin(document.url, link.get("href", "")) if link else document.url,
                "pdf_url": urljoin(document.url, pdf_link.get("href", "")) if pdf_link else None,
            }
        )
    if papers:
        return papers

    # Useful fallback for simple exported HTML: metadata lives directly on links.
    for link in soup.select("a[data-title][data-abstract]"):
        papers.append(
            {
                "title": link.get("data-title"),
                "abstract": link.get("data-abstract"),
                "authors": _split_people(link.get("data-authors", "")),
                "source_url": urljoin(document.url, link.get("href", "")),
                "pdf_url": urljoin(document.url, link.get("data-pdf", "")) if link.get("data-pdf") else None,
            }
        )
    return papers


def _parse_acl_page(soup: BeautifulSoup, base_url: str) -> List[Dict[str, Any]]:
    papers: List[Dict[str, Any]] = []
    abstracts: Dict[str, str] = {}
    for node in soup.select('[id^="abstract-"]'):
        number = str(node.get("id", "")).rsplit("--", 1)[-1]
        body = node.select_one(".card-body") or node
        text = body.get_text(" ", strip=True)
        if number and text:
            abstracts[number] = text
    pattern = re.compile(r"/\d{4}\.[^/]+\.\d+/$")
    seen: set[str] = set()
    for link in soup.find_all("a", href=pattern):
        official_id = link.get("href", "").strip("/")
        number = official_id.rsplit(".", 1)[-1]
        if official_id in seen or number == "0":
            continue
        container = link.find_parent("div", class_="d-sm-flex") or link.find_parent(
            ["p", "div", "li", "article"]
        )
        if container is None:
            continue
        abstract_node = container.select_one(".abstract")
        abstract = (
            abstract_node.get_text(" ", strip=True)
            if abstract_node
            else abstracts.get(number) or link.get("data-abstract")
        )
        if not abstract:
            continue
        paper_url = urljoin(base_url, link.get("href", ""))
        author_links = container.select('a[href^="/people/"]')
        authors_node = container.select_one(".lead, .authors")
        authors = [item.get_text(" ", strip=True) for item in author_links]
        if not authors and authors_node:
            authors = _split_people(authors_node.get_text(" ", strip=True))
        seen.add(official_id)
        papers.append(
            {
                "official_id": official_id,
                "title": link.get_text(" ", strip=True),
                "abstract": abstract,
                "authors": authors,
                "source_url": paper_url,
                "pdf_url": paper_url.rstrip("/") + ".pdf",
            }
        )
    return papers


def _clean_text(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).split())


def _string_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, str):
        if value.startswith("http"):
            return [value.strip()]
        return [part.strip() for part in re.split(r"[,;]", value) if part.strip()]
    if isinstance(value, dict):
        value = [value]
    result: List[str] = []
    for item in value:
        if isinstance(item, dict):
            item = item.get("name") or item.get("url") or item.get("value")
        text = _clean_text(item)
        if text:
            result.append(text)
    return result


def _split_people(value: str) -> List[str]:
    cleaned = re.sub(r"\s+(?:and|&|、)\s+", ",", value, flags=re.IGNORECASE)
    return [item.strip() for item in re.split(r"[,;]", cleaned) if item.strip()]
