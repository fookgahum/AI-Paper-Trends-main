"""Build BERTopic topics from cached OpenReview paper metadata."""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from pathlib import Path
from time import perf_counter
from typing import Any, Dict, Iterator, List, Tuple


def _log(message: str) -> None:
    """Print a stage marker immediately, including when stdout is redirected."""
    print(message, flush=True)


@contextmanager
def _tracked_stage(name: str, heartbeat_seconds: int) -> Iterator[None]:
    """Log elapsed time while a long-running stage is still active."""
    started = perf_counter()
    stopped = threading.Event()

    def report_progress() -> None:
        while not stopped.wait(heartbeat_seconds):
            elapsed = perf_counter() - started
            _log(f"[topic-model] HEARTBEAT: {name} is running ({elapsed:.0f}s).")

    _log(f"[topic-model] START: {name}.")
    reporter = threading.Thread(
        target=report_progress,
        name="topic-model-heartbeat",
        daemon=True,
    )
    reporter.start()
    succeeded = False
    try:
        yield
        succeeded = True
    finally:
        stopped.set()
        reporter.join(timeout=1)
        status = "DONE" if succeeded else "FAILED"
        _log(
            f"[topic-model] {status}: {name} in "
            f"{perf_counter() - started:.1f}s."
        )


def _resolve_cpu_threads(configured_threads: int) -> int:
    """Resolve zero to all logical CPUs and preserve explicit positive values."""
    return configured_threads or max(1, os.cpu_count() or 1)


def _configure_torch_threads(cpu_threads: int) -> None:
    """Configure PyTorch's CPU worker pools without failing on repeat runs."""
    import torch

    torch.set_num_threads(cpu_threads)
    interop_threads = min(cpu_threads, 4)
    try:
        torch.set_num_interop_threads(interop_threads)
    except RuntimeError:
        # PyTorch only allows changing this pool before parallel work starts.
        interop_threads = torch.get_num_interop_threads()
    _log(
        f"[topic-model] CPU parallelism: {torch.get_num_threads()} compute "
        f"threads, {interop_threads} inter-op threads."
    )


def load_and_preprocess_data(file_path: Path) -> Tuple[Any, List[str]]:
    """Load JSONL papers and combine title, keywords, and abstract for modeling."""
    import pandas as pd

    if not file_path.exists():
        raise FileNotFoundError(f"Input data not found: {file_path}")

    _log(f"[topic-model] Loading paper data: {file_path}")
    dataframe = pd.read_json(file_path, lines=True)
    required_columns = {"title", "abstract"}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Input data is missing columns: {sorted(missing_columns)}")

    dataframe = dataframe.dropna(subset=["title", "abstract"]).reset_index(drop=True)
    if dataframe.empty:
        raise ValueError("No papers with both a title and abstract are available.")

    if "keywords" not in dataframe.columns:
        dataframe["keywords"] = [[] for _ in range(len(dataframe))]
    dataframe["keywords_str"] = dataframe["keywords"].apply(
        lambda keywords: " ".join(map(str, keywords))
        if isinstance(keywords, list)
        else ""
    )
    dataframe["text_for_analysis"] = (
        dataframe["title"].astype(str)
        + ". "
        + dataframe["keywords_str"]
        + ". "
        + dataframe["abstract"].astype(str)
    )
    documents = dataframe["text_for_analysis"].tolist()
    if len(documents) < 2:
        raise ValueError("Topic modeling requires at least two valid papers.")

    _log(f"[topic-model] Loaded {len(dataframe)} valid papers.")
    return dataframe, documents


def download_embedding_model(model_id: str, cache_dir: Path) -> Path:
    """Download a ModelScope snapshot when it is not already cached."""
    expected_path = cache_dir / model_id
    if expected_path.exists():
        _log(f"[topic-model] Using cached embedding model: {expected_path}")
        return expected_path

    from modelscope.hub.snapshot_download import snapshot_download

    cache_dir.mkdir(parents=True, exist_ok=True)
    _log(f"[topic-model] Downloading embedding model: {model_id}")
    downloaded_path = snapshot_download(model_id, cache_dir=str(cache_dir))
    return Path(downloaded_path)


def _save_topic_labels(topic_model: Any, output_path: Path) -> None:
    """Persist concise keyword labels for the analysis and charts."""
    import yaml

    topic_labels: Dict[int, str] = {}
    for topic_id in topic_model.get_topics():
        if topic_id == -1:
            continue
        words = topic_model.get_topic(topic_id) or []
        label = " / ".join(word for word, _ in words[:4])
        topic_labels[int(topic_id)] = label or f"Topic {topic_id}"

    with output_path.open("w", encoding="utf-8") as file:
        yaml.safe_dump(topic_labels, file, allow_unicode=True, sort_keys=True)
    _log(f"[topic-model] Saved topic labels to: {output_path}")


def _run_tfidf_kmeans(
    dataframe: Any,
    documents: List[str],
    topic_config: Dict[str, Any],
    processed_data_dir: Path,
    output_dir: Path,
    input_path: Path,
    cpu_threads: int,
    heartbeat_seconds: int,
) -> Path:
    """Fit a lightweight, deterministic CPU topic model for dashboard builds."""
    os.environ["LOKY_MAX_CPU_COUNT"] = str(cpu_threads)
    with _tracked_stage("importing lightweight topic dependencies", heartbeat_seconds):
        import joblib
        import yaml
        from sklearn.cluster import KMeans
        from sklearn.feature_extraction.text import TfidfVectorizer
        from threadpoolctl import threadpool_limits

    topic_count = min(
        int(topic_config.get("topic_count", 24)), max(2, len(documents) // 2)
    )
    random_seed = int(topic_config.get("random_seed", 2026))
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.9,
        max_features=12000,
        sublinear_tf=True,
    )
    with _tracked_stage(
        f"vectorizing {len(documents)} papers with TF-IDF", heartbeat_seconds
    ):
        matrix = vectorizer.fit_transform(documents)
    _log(
        f"[topic-model] TF-IDF matrix: {matrix.shape[0]} papers x "
        f"{matrix.shape[1]} terms."
    )

    cluster_model = KMeans(
        n_clusters=topic_count,
        random_state=random_seed,
        n_init=20,
        max_iter=500,
    )
    with _tracked_stage(
        f"clustering papers into {topic_count} topics on {cpu_threads} CPU threads",
        heartbeat_seconds,
    ):
        with threadpool_limits(limits=cpu_threads):
            topics = cluster_model.fit_predict(matrix)

    feature_names = vectorizer.get_feature_names_out()
    labels: Dict[int, str] = {}
    for topic_id, center in enumerate(cluster_model.cluster_centers_):
        top_indices = center.argsort()[-4:][::-1]
        keywords = [feature_names[index] for index in top_indices if center[index] > 0]
        label = " / ".join(keywords) or f"Topic {topic_id}"
        labels[topic_id] = f"{label} · T{topic_id}"

    output_dir.mkdir(parents=True, exist_ok=True)
    processed_data_dir.mkdir(parents=True, exist_ok=True)
    output_path = processed_data_dir / f"{input_path.stem}_with_topics.csv"
    artifact_path = output_dir / f"tfidf_kmeans_{input_path.stem}.joblib"
    with _tracked_stage("saving lightweight topic-model artifacts", heartbeat_seconds):
        joblib.dump(
            {"vectorizer": vectorizer, "cluster_model": cluster_model},
            artifact_path,
        )
        with (output_dir / "topic_labels.yaml").open("w", encoding="utf-8") as file:
            yaml.safe_dump(labels, file, allow_unicode=True, sort_keys=True)
        dataframe["Topic"] = topics
        dataframe.to_csv(output_path, index=False, encoding="utf-8-sig")
    _log(f"[topic-model] Saved lightweight model to: {artifact_path}")
    _log(f"[topic-model] Saved topic assignments to: {output_path}")
    return output_path


def main(
    config: Dict[str, Any],
    input_path: Path,
    processed_data_dir: Path,
    output_dir: Path,
    models_cache_dir: Path,
) -> Path:
    """Fit the configured topic backend and save per-paper topic assignments."""
    topic_config = config.get("topic_modeling", {})
    backend = topic_config.get("backend", "bertopic")
    model_id = topic_config.get(
        "model_id", "sentence-transformers/all-mpnet-base-v2"
    )
    min_topic_size = topic_config.get("min_topic_size", 30)
    embedding_batch_size = topic_config.get("embedding_batch_size", 32)
    heartbeat_seconds = topic_config.get("heartbeat_seconds", 15)
    cpu_threads = _resolve_cpu_threads(topic_config.get("cpu_threads", 0))

    dataframe, documents = load_and_preprocess_data(input_path)
    if backend == "tfidf_kmeans":
        _log(f"[topic-model] Backend: TF-IDF + KMeans ({cpu_threads} CPUs).")
        return _run_tfidf_kmeans(
            dataframe,
            documents,
            topic_config,
            processed_data_dir,
            output_dir,
            input_path,
            cpu_threads,
            heartbeat_seconds,
        )

    with _tracked_stage("importing ML dependencies", heartbeat_seconds):
        from bertopic import BERTopic
        from hdbscan import HDBSCAN
        from sentence_transformers import SentenceTransformer
        from umap import UMAP

    _configure_torch_threads(cpu_threads)

    effective_min_topic_size = min(min_topic_size, max(2, len(documents) // 2))
    if effective_min_topic_size != min_topic_size:
        _log(
            f"Adjusted min_topic_size from {min_topic_size} to "
            f"{effective_min_topic_size} for {len(documents)} papers."
        )

    with _tracked_stage("preparing the embedding model", heartbeat_seconds):
        local_model_path = download_embedding_model(model_id, models_cache_dir)
        embedding_model = SentenceTransformer(str(local_model_path))

    with _tracked_stage(
        f"encoding {len(documents)} papers (batch size {embedding_batch_size})",
        heartbeat_seconds,
    ):
        embeddings = embedding_model.encode(
            documents,
            batch_size=embedding_batch_size,
            show_progress_bar=True,
            convert_to_numpy=True,
        )

    umap_model = UMAP(
        n_neighbors=15,
        n_components=5,
        min_dist=0.0,
        metric="cosine",
        n_jobs=cpu_threads,
    )
    hdbscan_model = HDBSCAN(
        min_cluster_size=effective_min_topic_size,
        metric="euclidean",
        cluster_selection_method="eom",
        prediction_data=True,
        core_dist_n_jobs=cpu_threads,
    )

    topic_model = BERTopic(
        embedding_model=embedding_model,
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        min_topic_size=effective_min_topic_size,
        verbose=True,
        language="english",
    )

    with _tracked_stage(
        "BERTopic dimensionality reduction and clustering", heartbeat_seconds
    ):
        topics, _ = topic_model.fit_transform(documents, embeddings)

    output_dir.mkdir(parents=True, exist_ok=True)
    processed_data_dir.mkdir(parents=True, exist_ok=True)
    model_path = output_dir / f"bertopic_model_{input_path.stem}"
    output_path = processed_data_dir / f"{input_path.stem}_with_topics.csv"
    with _tracked_stage("saving topic-model artifacts", heartbeat_seconds):
        topic_model.save(str(model_path), serialization="safetensors")
        _log(f"[topic-model] Saved BERTopic model to: {model_path}")
        _save_topic_labels(topic_model, output_dir / "topic_labels.yaml")
        dataframe["Topic"] = topics
        dataframe.to_csv(output_path, index=False, encoding="utf-8-sig")
        _log(f"[topic-model] Saved topic assignments to: {output_path}")
    return output_path
