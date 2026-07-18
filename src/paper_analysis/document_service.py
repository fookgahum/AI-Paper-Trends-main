"""Acquire public paper PDFs and turn them into page-grounded text chunks."""

from __future__ import annotations

import hashlib
import re
from io import BytesIO
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

from src.paper_sources import FetchedDocument, fetch_public_document
from src.storage import LocalDatabase


DocumentFetch = Callable[[str], FetchedDocument]


class PaperDocumentService:
    """Own public-PDF acquisition, extraction, fallback, and local artifacts."""

    def __init__(
        self,
        database: LocalDatabase,
        artifact_root: Path,
        fetch: Optional[DocumentFetch] = None,
    ) -> None:
        self.database = database
        self.artifact_root = artifact_root
        self._fetch = fetch or fetch_public_document

    def prepare(
        self,
        run_id: str,
        paper: Dict[str, Any],
        *,
        prefer_full_text: bool = True,
        force_refresh: bool = False,
    ) -> Dict[str, Any]:
        cached = self.database.get_latest_paper_document(run_id, paper["id"])
        if cached and not force_refresh:
            if cached["status"] == "full_text" or not prefer_full_text:
                return cached

        pdf_url = resolve_pdf_url(paper) if prefer_full_text else None
        error: Optional[Dict[str, str]] = None
        pdf_content: Optional[bytes] = None
        pages: List[str] = []
        if pdf_url:
            try:
                fetched = self._fetch(pdf_url)
                if "pdf" not in fetched.content_type.lower() and not fetched.content.startswith(
                    b"%PDF"
                ):
                    raise ValueError("The public URL did not return a PDF")
                pdf_content = fetched.content
                pages = extract_pdf_pages(pdf_content)
                if not any(page.strip() for page in pages):
                    raise ValueError("The PDF contains no extractable text")
            except Exception as exc:
                error = {"type": type(exc).__name__, "message": str(exc)}

        status = "full_text" if pages else "abstract_only"
        if status == "full_text":
            chunks = chunk_pages(pages)
            content_hash = hashlib.sha256(pdf_content or b"").hexdigest()
        else:
            abstract = clean_text(paper.get("abstract")) or "No abstract available."
            chunks = [
                {
                    "id": "abstract-1",
                    "page": 0,
                    "section": "Abstract",
                    "text": abstract,
                }
            ]
            content_hash = hashlib.sha256(abstract.encode("utf-8")).hexdigest()

        document_id = "document_" + hashlib.sha256(
            f"{run_id}|{paper['id']}|{content_hash}".encode("utf-8")
        ).hexdigest()[:20]
        local_pdf_path: Optional[str] = None
        if pdf_content:
            directory = self.artifact_root / "paper_documents"
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / f"{document_id}.pdf"
            path.write_bytes(pdf_content)
            local_pdf_path = str(path)
        payload = {
            "id": document_id,
            "run_id": run_id,
            "paper_id": paper["id"],
            "source_url": paper["source_url"],
            "pdf_url": pdf_url,
            "local_pdf_path": local_pdf_path,
            "status": status,
            "content_hash": content_hash,
            "page_count": len(pages),
            "chunks": chunks,
            "error": error,
        }
        self.database.save_paper_document(payload)
        return self.database.get_paper_document(document_id)

    def pdf_path(self, document_id: str) -> Path:
        document = self.database.get_paper_document(document_id)
        value = document.get("local_pdf_path")
        if not value:
            raise FileNotFoundError("This analysis has no locally cached PDF")
        path = Path(value).resolve()
        root = (self.artifact_root / "paper_documents").resolve()
        if path.parent != root or not path.is_file():
            raise FileNotFoundError("The cached PDF is missing")
        return path


def resolve_pdf_url(paper: Dict[str, Any]) -> Optional[str]:
    explicit = str(paper.get("pdf_url") or "").strip()
    if explicit.startswith("https://"):
        return explicit
    source = str(paper.get("source_url") or "").strip()
    parsed = urlparse(source)
    host = (parsed.hostname or "").lower()
    if source.lower().endswith(".pdf"):
        return source
    if host == "aclanthology.org":
        return source.rstrip("/") + ".pdf"
    if host.endswith("openreview.net"):
        paper_id = parse_qs(parsed.query).get("id", [""])[0]
        if paper_id:
            return f"https://openreview.net/pdf?id={paper_id}"
    return None


def extract_pdf_pages(content: bytes) -> List[str]:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError(
            "PDF extraction requires pypdf; install the project requirements first"
        ) from exc
    reader = PdfReader(BytesIO(content))
    if len(reader.pages) > 160:
        raise ValueError("PDF exceeds the 160-page analysis limit")
    return [clean_page_text(page.extract_text() or "") for page in reader.pages]


def chunk_pages(pages: List[str], target_chars: int = 1800) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []
    current_section = "Paper body"
    for page_number, page in enumerate(pages, 1):
        segments: List[tuple[str, str]] = []
        for line in page.splitlines():
            if looks_like_heading(line):
                current_section = line[:120]
                continue
            segments.extend(
                (current_section, part.strip())
                for part in re.split(r"(?<=[.!?])\s+", line)
                if part.strip()
            )
        buffer: List[str] = []
        size = 0
        page_chunk = 1
        buffer_section = current_section
        for section, paragraph in segments:
            if buffer and (
                section != buffer_section or size + len(paragraph) > target_chars
            ):
                chunks.append(
                    {
                        "id": f"p{page_number}-c{page_chunk}",
                        "page": page_number,
                        "section": buffer_section,
                        "text": " ".join(buffer),
                    }
                )
                page_chunk += 1
                buffer = []
                size = 0
            if not buffer:
                buffer_section = section
            buffer.append(paragraph)
            size += len(paragraph) + 1
        if buffer:
            chunks.append(
                {
                    "id": f"p{page_number}-c{page_chunk}",
                    "page": page_number,
                    "section": buffer_section,
                    "text": " ".join(buffer),
                }
            )
    return chunks or [
        {
            "id": "body-1",
            "page": 1,
            "section": "Paper body",
            "text": "No text extracted.",
        }
    ]


def looks_like_heading(value: str) -> bool:
    words = value.split()
    if not 1 <= len(words) <= 12 or len(value) > 120:
        return False
    return bool(re.match(r"^(?:\d+(?:\.\d+)*\s+)?[A-Z][^.!?]*$", value))


def clean_text(value: Any) -> str:
    text = str(value or "").replace("\x00", " ")
    return re.sub(r"\s+", " ", text).strip()


def clean_page_text(value: Any) -> str:
    lines = [clean_text(line) for line in str(value or "").splitlines()]
    return "\n".join(line for line in lines if line)
