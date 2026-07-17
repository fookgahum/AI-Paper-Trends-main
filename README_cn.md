<div align="right"><a href="README.md">English</a> | <strong>中文</strong></div>

# AI 论文趋势分析

AI Paper Trends 是一个本地运行的计算机会议论文分析网站与可复现数据流水线。它可以获取 OpenReview 公开论文、导入指定会议的官方论文集、构建研究主题、生成统计报告，并通过中英双语只读网站展示结果。

## 当前功能

- 获取 OpenReview 公开的论文元数据；会议公开时还可读取决定和评分。
- 支持原有 BERTopic 后端，以及快速、可复现的 TF-IDF + KMeans 纯 CPU 后端。
- 在耗时建模阶段持续输出进度心跳，用于区分正常运行和卡住。
- 为 OpenReview 数据生成主题、评分、决定构成、CSV、HTML 和图片报告。
- 将 24 个底层聚类综合为 13 个可读的前沿研究方向，说明方向现状、现在为什么值得关注、可写的论文切入点和需要避开的同质化做法。
- 按个人/低资源、普通实验室、理论优势、资源型实验室四类条件给出“切入友好度”排序，并展示算力、数据、工程和理论门槛。
- 从方向结论下钻到代表论文和完整论文列表，按会议、方向、底层主题和发表类型筛选，并打开官方来源核查。
- 从 ICLR、ICML、ACL 官方来源重新生成仓库内的 2026 年数据。

## 仓库内的 2026 网站数据

网站快照共 600 篇：ICLR 2026、ICML 2026、ACL 2026 各从官方公开的已录用或已发表论文中，以固定随机种子 `2026` 抽样 200 篇。截至 2026-07-17，NeurIPS 2026 官方投稿页没有可公开论文，因此第三个真实的 CCF-A 会议采用 ACL 2026。

网站的“切入友好度”综合资源匹配、跨会议覆盖、评测型切入信号、样本证据量和竞争余量。它是帮助选题的启发式指标，不是录用概率。数据只覆盖一年中的已录用/已发表样本，不能反映投稿总量、拒稿分布或跨年增长趋势。

## 启动网站

推荐使用 Python 3.10 或更高版本：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

启动本地服务：

```powershell
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

浏览器打开 `http://127.0.0.1:8000`。不需要安装 Docker。打开网站只会读取 `data/web/` 中已提交的结果，不会自动开始训练。

## 重新生成 2026 数据

完整命令会下载官方公开元数据、每个会议抽样 200 篇、在 CPU 上生成 24 个固定主题，再构建 13 个前沿方向及其证据指标并导出网站数据：

```powershell
python -u -m scripts.build_2026_dashboard
```

复用已下载样本，或同时复用已生成的主题结果：

```powershell
python -u -m scripts.build_2026_dashboard --skip-fetch
python -u -m scripts.build_2026_dashboard --skip-fetch --skip-model
```

原始数据、处理中间文件和模型产物由 Git 忽略；仓库只提交体积较小、供网站读取的最终快照。

## 运行 OpenReview 分析

```powershell
python main.py --config configs/iclr_2025_full_analysis.yaml
```

添加 `--force-rerun` 可以忽略缓存。如果 OpenReview 限制匿名访问，可以通过进程环境变量提供 `OPENREVIEW_USERNAME` 与 `OPENREVIEW_PASSWORD`，不要把账号密码提交到 Git。

主题建模的主要配置如下：

```yaml
topic_modeling:
  enabled: true
  backend: bertopic          # 或 tfidf_kmeans
  min_topic_size: 30         # BERTopic 后端使用
  topic_count: 24            # TF-IDF + KMeans 后端使用
  random_seed: 2026
  embedding_batch_size: 32
  cpu_threads: 0             # 0 表示使用全部逻辑核心
  heartbeat_seconds: 15
```

## 项目结构

```text
configs/                  分析与网站数据配置
data/web/                 提交到 Git 的只读网站快照
docs/images/              静态分析示例图
scripts/                  2026 官方数据导入、建模与导出命令
src/get_papers.py         OpenReview 数据获取
src/run_topic_modeling.py BERTopic 与轻量 CPU 主题后端
src/analyze.py            统计报告与静态图表
tests/                    单元测试和 HTTP 集成测试
web/                      FastAPI、模板、样式、脚本和 ECharts
main.py                   OpenReview 流水线入口
```

## 验证

```powershell
python -m unittest discover -s tests -v
python -m compileall -q main.py src scripts web tests
node --check web/static/js/app.js
```

## 许可证

项目使用 [MIT License](LICENSE)。内置 Apache ECharts 使用 Apache License 2.0，详见 `web/static/vendor/NOTICE.txt`。
