<div align="right"><strong>English</strong> | <a href="README_cn.md">中文</a></div>

# AI Paper Trends

AI Paper Trends is a local research dashboard and reproducible analysis pipeline for public computer-science conference papers. It can fetch public papers, build topic models, summarize frontier opportunities, and turn a selected direction into an executable learning and reproduction plan.

## Current capabilities

- Fetch public OpenReview paper metadata, decisions, and ratings when the venue exposes them.
- Build topics with the original BERTopic backend or the fast deterministic TF-IDF + KMeans CPU backend.
- Emit progress heartbeats around long-running model stages.
- Generate topic, rating, decision, CSV, HTML, and image reports for OpenReview runs.
- Synthesize 24 base clusters into 13 readable frontier directions with research summaries, timely open questions, practical paper entry points, and commoditization warnings.
- Rank entry friendliness for individual, standard-lab, theory-strong, and resource-rich profiles while exposing compute, data, engineering, and theory barriers.
- Drill from each recommendation into representative and supporting papers, filter by venue/direction/base topic/type, and verify against official source links.
- Rebuild the included 2026 dataset from official ICLR, ICML, and ACL sources.
- Pull incremental papers from a public JSON/HTML/ACL Anthology URL, normalize fields, deduplicate in SQLite, save source snapshots, and optionally download public PDFs without invoking AI.
- Manually run an AI direction-update job after pulling: map new papers to an existing direction or save an evidence-grounded new-direction candidate as a draft, without changing the 13 published directions.
- Generate a prerequisite-aware curriculum boundary first: starting gaps, required and optional knowledge, dependency order, explicit deferrals, mastery checks, resource-search terms, grounded anchor papers, and research exit criteria. The 7/30/90-day plan is a secondary projection of that map.
- Close-read one selected paper with a three-minute brief, page-grounded logic and method breakdown, experimental-evidence audit, paper-specific prerequisite boundary, L0-L3 reproduction route, active-recall assessment, and cautious research extensions. Public ACL/OpenReview PDFs are parsed when available; failures downgrade visibly to abstract-only analysis.
- Run the complete learning workflow for free with the deterministic mock client, or switch one configuration file to an OpenAI-compatible cloud API.

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

Open `http://127.0.0.1:8000`. Docker is not required. Opening the website never starts model training. Published analysis snapshots stay in `data/web/`; local paper sources, jobs, learning progress, and generated plans stay in the Git-ignored `data/local/app.db`.

After updating the code, press `Ctrl+C` in the original terminal and run the start command again; this launch mode does not reload the Python backend automatically. The current frontend checks the learning-artifact contract and gives a restart message when it detects an outdated server.

## Paper updates

Use the **Paper updates** page to enter a public proceedings or JSON URL. Pulling, parsing, deduplication, and optional PDF download are independent of AI. The same workflow is available from PowerShell:

```powershell
python -m scripts.pull_papers "https://example.org/papers.json" --conference DEMO --year 2026 --parser json
```

The first implementation supports common JSON feeds (including OpenReview-style `notes` payloads), ACL Anthology event pages, and proceedings-style HTML whose paper cards contain abstracts. Unsupported page layouts fail visibly and retain a job error instead of silently importing incomplete records.

New papers remain `unanalysed` until you explicitly click **Analyse new papers with AI**. The resulting mappings and new-direction candidates are durable drafts in SQLite. This makes the “new 2026 direction” path updateable while keeping the published snapshot stable and reviewable.

## Single-paper AI close reading

Open **Papers**, inspect one paper, and choose **AI close-read this paper**. The system derives the official public PDF URL for ACL Anthology and OpenReview papers, stores the PDF only under Git-ignored `data/local/artifacts/`, extracts page-preserving chunks, and validates every generated evidence id, page, section, and excerpt against that local document. If a PDF is unavailable or has no extractable text, the artifact is explicitly restricted to title and abstract and cannot claim supported experiments.

The result is progressive rather than one long summary: a three-minute brief, recommended reading order, problem-to-conclusion logic chain, input/process/output method modules, experimental cautions, a bounded knowledge map, an L0-L3 minimum reproduction route, active-recall answers with feedback, and research extensions that state novelty risk and a minimum experiment. Repeated analyses and mastery progress are stored in `data/local/app.db`; cached PDFs can be reopened at their cited page.

## AI learning plans and the cloud API boundary

The learning page is knowledge-first. Selecting **Zero foundation** produces a layered route through programming/experiment engineering, mathematics and statistics, ML/Transformer foundations, direction-specific core concepts, paper evidence reading, baseline reproduction, and research design. It separates a shortest “structured paper literacy” path from the full “independent reproduction and research design” path, with five capability gates, passing evidence, and false-mastery traps. Starter materials come from a reviewed URL allowlist and prescribe only selected sections plus a stop rule. The full map, gap diagnosis, research exit, and calendar are folded away so a novice first sees only what Gate 1 requires.

If the selected duration is too short, the site reports the available hours against both capability thresholds instead of deleting required knowledge or pretending mastery.

The default [`settings/cloud_ai.yaml`](settings/cloud_ai.yaml) uses `provider: mock`, so the website and tests make no paid request. The only real cloud request implementation is [`src/cloud_ai/client.py`](src/cloud_ai/client.py). To use an OpenAI-compatible Chat Completions service:

1. Change `provider` to `openai_compatible`, set the service `base_url`, and set the actual `model` in `settings/cloud_ai.yaml`.
2. Set the API key only in the process environment:

```powershell
$env:CLOUD_AI_API_KEY = "your-key"
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

The returned JSON must pass the local Pydantic contract: a valid dependency DAG, a prerequisite-closed minimum path, non-overlapping mastery gates covering every required node, grounded paper IDs, starter URLs drawn only from the server allowlist, contiguous plan stages, measurable deliverables, and an ordered L0-L4 reproduction ladder. A malformed cloud response is recorded as a failed job and is not published as a plan.

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

Raw data, local SQLite state, processed CSV files, and model artifacts remain Git-ignored. Only the compact published web export is committed.

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
docs/                     Architecture and product design notes
scripts/                  Official builds and the URL paper-pull CLI
settings/cloud_ai.yaml     Cloud provider/model settings without secrets
src/cloud_ai/              Validated mock/real AI boundary and learning service
src/paper_analysis/        Public-PDF parsing, grounded close reading, and mastery checks
src/paper_sources/         URL parsing, normalization, deduplication, and PDF pull
src/storage/               Local SQLite schema and application queries
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
