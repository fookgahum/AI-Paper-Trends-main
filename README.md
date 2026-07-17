<div align="right"><strong>English</strong> | <a href="README_cn.md">中文</a></div>

# AI Paper Trends

AI Paper Trends is a local research dashboard and reproducible analysis pipeline for public computer-science conference papers. It can fetch public OpenReview submissions, import selected official 2026 proceedings, build topic models, generate reports, and serve the exported results through a bilingual read-only website.

## Current capabilities

- Fetch public OpenReview paper metadata, decisions, and ratings when the venue exposes them.
- Build topics with the original BERTopic backend or the fast deterministic TF-IDF + KMeans CPU backend.
- Emit progress heartbeats around long-running model stages.
- Generate topic, rating, decision, CSV, HTML, and image reports for OpenReview runs.
- Synthesize 24 base clusters into 13 readable frontier directions with research summaries, timely open questions, practical paper entry points, and commoditization warnings.
- Rank entry friendliness for individual, standard-lab, theory-strong, and resource-rich profiles while exposing compute, data, engineering, and theory barriers.
- Drill from each recommendation into representative and supporting papers, filter by venue/direction/base topic/type, and verify against official source links.
- Rebuild the included 2026 dataset from official ICLR, ICML, and ACL sources.

## Included 2026 web dataset

The tracked web snapshot contains 600 papers: a fixed random sample of 200 accepted or published papers from each official ICLR 2026, ICML 2026, and ACL 2026 source (seed `2026`). As of 2026-07-17, the official NeurIPS 2026 submission page exposes no papers, so ACL is used as the third real CCF-A venue.

The website's entry-friendliness score combines resource fit, cross-venue breadth, evaluation-oriented entry signals, evidence volume, and competition headroom. It is a topic-selection heuristic, not an acceptance probability. The snapshot contains one year of accepted/published work and cannot reveal submission volume, rejected-work distributions, or multi-year momentum.

## Start the website

Install Python 3.10 or newer and the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Start the local server:

```powershell
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000`. Docker is not required. Opening the website never starts model training; it only reads the committed files in `data/web/`.

## Rebuild the 2026 dataset

The full workflow downloads official public metadata, samples 200 papers per venue, builds 24 deterministic base topics on CPU, synthesizes 13 frontier directions with evidence metrics, and exports the web snapshot:

```powershell
python -u -m scripts.build_2026_dashboard
```

Reuse the downloaded sample or both the sample and trained topic output:

```powershell
python -u -m scripts.build_2026_dashboard --skip-fetch
python -u -m scripts.build_2026_dashboard --skip-fetch --skip-model
```

Raw data, processed CSV files, and model artifacts remain Git-ignored. Only the compact read-only web export is committed.

## Run an OpenReview analysis

```powershell
python main.py --config configs/iclr_2025_full_analysis.yaml
```

Add `--force-rerun` to ignore cached raw/topic files. If anonymous OpenReview access is challenged, provide `OPENREVIEW_USERNAME` and `OPENREVIEW_PASSWORD` through process environment variables; never commit credentials.

Key topic-model options are:

```yaml
topic_modeling:
  enabled: true
  backend: bertopic          # or tfidf_kmeans
  min_topic_size: 30         # BERTopic backend
  topic_count: 24            # TF-IDF + KMeans backend
  random_seed: 2026
  embedding_batch_size: 32
  cpu_threads: 0             # 0 = all logical CPUs
  heartbeat_seconds: 15
```

## Project structure

```text
configs/                  Analysis and web-dataset configurations
data/web/                 Committed read-only dashboard snapshots
docs/images/              Example analysis output
scripts/                  Official 2026 import/build/export commands
src/get_papers.py         OpenReview ingestion
src/run_topic_modeling.py BERTopic and lightweight CPU topic backends
src/analyze.py            Statistical reports and static charts
tests/                    Unit and HTTP integration tests
web/                      FastAPI API, templates, CSS, JavaScript, ECharts
main.py                   OpenReview pipeline entry point
```

## Verify

```powershell
python -m unittest discover -s tests -v
python -m compileall -q main.py src scripts web tests
node --check web/static/js/app.js
```

## License

Released under the [MIT License](LICENSE). Apache ECharts is included under the Apache License 2.0; see `web/static/vendor/NOTICE.txt`.
