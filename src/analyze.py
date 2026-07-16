"""Aggregate topic statistics and generate configured visualizations."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import seaborn as sns
import yaml


DECISION_TYPES = ["Oral", "Spotlight", "Poster", "Reject", "N/A"]


def normalize_decision(value: Any) -> str:
    """Map venue-specific decision text to the categories used by the reports."""
    decision = str(value).lower()
    if "oral" in decision:
        return "Oral"
    if "spotlight" in decision:
        return "Spotlight"
    if "reject" in decision:
        return "Reject"
    if "poster" in decision or "accept" in decision:
        return "Poster"
    return "N/A"


def create_analysis_dataframe(
    dataframe: pd.DataFrame, topic_labels: Dict[int, str]
) -> pd.DataFrame:
    """Calculate per-topic volume, ratings, decisions, and known acceptance rate."""
    required_columns = {"id", "Topic"}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f"Processed data is missing columns: {sorted(missing_columns)}")

    data = dataframe[dataframe["Topic"] != -1].copy()
    print(f"Removed {len(dataframe) - len(data)} BERTopic outliers.")
    if data.empty:
        return pd.DataFrame()

    if "decision" not in data.columns:
        data["decision"] = "N/A"
    if "avg_rating" not in data.columns:
        data["avg_rating"] = pd.NA
    data["avg_rating"] = pd.to_numeric(data["avg_rating"], errors="coerce")
    data["clean_decision"] = data["decision"].apply(normalize_decision)

    topic_stats = (
        data.groupby("Topic")
        .agg(paper_count=("id", "size"), avg_rating=("avg_rating", "mean"))
        .reset_index()
    )
    decision_counts = (
        data.groupby(["Topic", "clean_decision"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    analysis = topic_stats.merge(decision_counts, on="Topic", how="left")

    for decision_type in DECISION_TYPES:
        if decision_type not in analysis.columns:
            analysis[decision_type] = 0
        analysis[decision_type] = analysis[decision_type].fillna(0).astype(int)

    accepted = analysis["Oral"] + analysis["Spotlight"] + analysis["Poster"]
    known_decisions = accepted + analysis["Reject"]
    analysis["acceptance_rate"] = accepted.div(known_decisions.where(known_decisions > 0))

    analysis["Topic_Name"] = analysis["Topic"].map(topic_labels)
    fallback_names = analysis["Topic"].apply(lambda topic: f"Topic {topic}")
    analysis["Topic_Name"] = analysis["Topic_Name"].fillna(fallback_names)

    columns = [
        "Topic",
        "Topic_Name",
        "paper_count",
        "avg_rating",
        "acceptance_rate",
        *DECISION_TYPES,
    ]
    return analysis[columns].sort_values("paper_count", ascending=False).reset_index(drop=True)


def plot_topic_ranking(
    dataframe: pd.DataFrame,
    metric: str,
    conference: str,
    output_path: Path,
    top_n: int,
) -> Optional[Path]:
    """Create a horizontal ranking chart for paper count or reviewer score."""
    plot_data = dataframe.dropna(subset=[metric]).nlargest(top_n, metric)
    if plot_data.empty:
        print(f"Skipping {metric} chart because no values are available.")
        return None

    figure_height = max(8.0, len(plot_data) * 0.4 + 3.0)
    figure, axis = plt.subplots(figsize=(14, figure_height))
    palette = "viridis" if metric == "paper_count" else "plasma"
    sns.barplot(
        data=plot_data,
        x=metric,
        y="Topic_Name",
        hue="Topic_Name",
        palette=palette,
        legend=False,
        orient="h",
        ax=axis,
    )
    metric_title = metric.replace("_", " ").title()
    axis.set_title(f"Top {len(plot_data)} Topics by {metric_title} at {conference}")
    axis.set_xlabel(metric_title)
    axis.set_ylabel("Topic")
    axis.tick_params(axis="y", labelsize=10 if len(plot_data) > 30 else 12)
    figure.tight_layout()
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)
    print(f"Saved chart to: {output_path}")
    return output_path


def plot_decision_breakdown(
    dataframe: pd.DataFrame,
    conference: str,
    output_path: Path,
    top_n: int,
) -> Path:
    """Create a normalized decision composition chart for the most accepted topics."""
    plot_frame = dataframe.sort_values(
        ["acceptance_rate", "paper_count"], ascending=[False, False], na_position="last"
    ).head(top_n)
    decision_data = plot_frame.set_index("Topic_Name")[DECISION_TYPES]
    normalized = decision_data.div(decision_data.sum(axis=1).replace(0, pd.NA), axis=0).fillna(0)

    figure_height = max(10.0, len(normalized) * 0.5 + 4.0)
    figure, axis = plt.subplots(figsize=(18, figure_height))
    normalized.plot(kind="barh", stacked=True, colormap="viridis", width=0.8, ax=axis)

    paper_counts = plot_frame.set_index("Topic_Name")["paper_count"]
    for index, topic_name in enumerate(normalized.index):
        axis.text(1.01, index, f"n={paper_counts[topic_name]}", va="center", fontsize=10)

    axis.set_title(f"Top {len(plot_frame)} Topics: Decision Breakdown at {conference}", pad=40)
    axis.set_xlabel("Proportion of papers")
    axis.set_ylabel("Topic")
    axis.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    axis.set_xlim(0, 1)
    axis.invert_yaxis()
    axis.legend(
        title="Decision Type",
        loc="upper center",
        bbox_to_anchor=(0.5, 1.08),
        ncol=5,
        frameon=False,
    )
    figure.tight_layout(rect=[0, 0, 0.92, 1])
    figure.savefig(output_path, bbox_inches="tight")
    plt.close(figure)
    print(f"Saved chart to: {output_path}")
    return output_path


def save_summary_table(dataframe: pd.DataFrame, output_path: Path, top_n: int) -> List[Path]:
    """Save the topic summary in portable CSV and human-readable HTML formats."""
    display_columns = [
        "Topic_Name",
        "paper_count",
        "avg_rating",
        "acceptance_rate",
        *DECISION_TYPES,
    ]
    table = dataframe[display_columns].sort_values(
        ["acceptance_rate", "paper_count"], ascending=[False, False], na_position="last"
    ).head(top_n)

    csv_path = output_path.with_suffix(".csv")
    table.to_csv(csv_path, index=False, encoding="utf-8-sig")

    styler = table.style.format(
        {
            "avg_rating": "{:.2f}",
            "acceptance_rate": "{:.2%}",
            "paper_count": "{:.0f}",
            **{decision_type: "{:.0f}" for decision_type in DECISION_TYPES},
        },
        na_rep="N/A",
    ).bar(subset=["paper_count"], color="#5fba7d", align="left")
    if table["avg_rating"].notna().any():
        styler = styler.bar(
            subset=["avg_rating"],
            color="#d65f5f",
            align="left",
            vmin=table["avg_rating"].min(),
        )
    styler = styler.set_caption(
        f"Top {len(table)} Topics (sorted by known acceptance rate)"
    )

    html_path = output_path.with_suffix(".html")
    html_path.write_text(styler.to_html(), encoding="utf-8")
    print(f"Saved summary tables to: {csv_path} and {html_path}")
    return [csv_path, html_path]


def _load_topic_labels(labels_path: Path) -> Dict[int, str]:
    if not labels_path.exists():
        print("Topic labels not found; numeric fallback labels will be used.")
        return {}
    with labels_path.open("r", encoding="utf-8") as file:
        raw_labels = yaml.safe_load(file) or {}
    if not isinstance(raw_labels, dict):
        raise ValueError(f"Topic labels must be a mapping: {labels_path}")
    return {int(topic): str(label) for topic, label in raw_labels.items()}


def main(config: Dict[str, Any], input_path: Path, output_dir: Path) -> List[Path]:
    """Run configured analysis tasks and return all generated artifact paths."""
    if not input_path.exists():
        raise FileNotFoundError(f"Processed data not found: {input_path}")

    sns.set_theme(style="whitegrid", context="talk")
    dataframe = pd.read_csv(input_path)
    topic_labels = _load_topic_labels(output_dir / "topic_labels.yaml")
    analysis = create_analysis_dataframe(dataframe, topic_labels)
    if analysis.empty:
        raise ValueError("No non-outlier papers are available for analysis.")

    analysis_config = config.get("analysis", {})
    tasks = analysis_config.get("tasks", [])
    top_n = analysis_config.get("top_n", 65)
    conference = config.get("conference_id", "conference").split("/")[0]
    generated: List[Path] = []

    if "plot_paper_count" in tasks:
        path = plot_topic_ranking(
            analysis,
            "paper_count",
            conference,
            output_dir / "top_topics_by_count.png",
            top_n,
        )
        if path:
            generated.append(path)
    if "plot_avg_rating" in tasks:
        path = plot_topic_ranking(
            analysis,
            "avg_rating",
            conference,
            output_dir / "top_topics_by_rating.png",
            top_n,
        )
        if path:
            generated.append(path)
    if "plot_decision_breakdown" in tasks:
        generated.append(
            plot_decision_breakdown(
                analysis, conference, output_dir / "decision_breakdown.png", top_n
            )
        )
    if "generate_summary_table" in tasks:
        generated.extend(save_summary_table(analysis, output_dir / "summary_table", top_n))
    return generated
