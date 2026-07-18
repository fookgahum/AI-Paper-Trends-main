<div align="right"><a href="README.md">English</a> | <strong>中文</strong></div>

# AI 论文趋势分析

AI Paper Trends 是一个本地运行的计算机会议论文研究工作台与可复现数据流水线。它可以获取公开论文、构建研究主题、总结前沿选题，并把选定方向转化为可执行的学习和复现计划。

## 当前功能

- 获取 OpenReview 公开的论文元数据；会议公开时还可读取决定和评分。
- 支持原有 BERTopic 后端，以及快速、可复现的 TF-IDF + KMeans 纯 CPU 后端。
- 在耗时建模阶段持续输出进度心跳，用于区分正常运行和卡住。
- 为 OpenReview 数据生成主题、评分、决定构成、CSV、HTML 和图片报告。
- 将 24 个底层聚类综合为 13 个可读的前沿研究方向，说明方向现状、现在为什么值得关注、可写的论文切入点和需要避开的同质化做法。
- 按个人/低资源、普通实验室、理论优势、资源型实验室四类条件给出“切入友好度”排序，并展示算力、数据、工程和理论门槛。
- 从方向结论下钻到代表论文和完整论文列表，按会议、方向、底层主题和发表类型筛选，并打开官方来源核查。
- 从 ICLR、ICML、ACL 官方来源重新生成仓库内的 2026 年数据。
- 从公开 JSON、HTML 或 ACL Anthology 地址增量拉取论文，统一字段、写入 SQLite 去重、保存来源快照，并可选下载公开 PDF；这一步不调用 AI。
- 拉取后可手动启动 AI 方向更新：把新论文映射到现有方向，或保存有论文证据的新方向候选草稿；正式 13 个方向不会被自动修改。
- 先为选定方向生成带前置诊断的知识边界：必备/可选知识、依赖顺序、明确暂缓内容、掌握检查、资料检索词、锚点论文和研究能力出口；7/30/90 天安排只是知识地图的次级时间投影。
- 默认使用确定性 mock 客户端免费跑通学习流程，也可以通过一个配置文件切换到 OpenAI 兼容的云端 API。

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

浏览器打开 `http://127.0.0.1:8000`。不需要安装 Docker。打开网站不会自动开始训练。已发布分析快照位于 `data/web/`；论文来源、任务、学习进度和计划保存在 Git 忽略的 `data/local/app.db`。

更新代码后必须在原终端按 `Ctrl+C` 停止旧服务，再重新执行启动命令；当前启动方式不会自动重载 Python 后端。新版页面会检测学习产物版本，发现旧服务时会直接提示重启。

## 论文增量

在网站的“论文增量”页输入公开论文集或 JSON 地址，即可执行拉取、解析、去重和可选 PDF 下载；整个过程与 AI 分离。也可以使用等价命令：

```powershell
python -m scripts.pull_papers "https://example.org/papers.json" --conference DEMO --year 2026 --parser json
```

第一版支持常见 JSON 列表（包括 OpenReview 风格的 `notes` 数据）、ACL Anthology 会议页面，以及论文卡片中包含摘要的常规 HTML。无法识别的页面会明确记录为失败任务，不会静默导入残缺数据。

新论文最初保持 `unanalysed` 状态，只有明确点击“用 AI 分析新论文”后才会产生方向映射或新方向候选。结果作为 SQLite 草稿持久化，因此 2026 新方向可以持续更新，同时正式网站快照仍然稳定、可复核。

## AI 学习计划与云端 API 位置

学习页面现在以知识为主。选择“零基础”后，会依次圈定编程与实验工程、数学统计、机器学习/Transformer、方向专属核心、论文证据阅读、基线复现和研究设计。路线区分“能结构化读论文”和“能独立复现并设计研究”两个终点，并用 5 个能力关卡控制推进；每关都给出过关证据和常见的假掌握。起步资料来自本地审核过的 URL 白名单，每份资料只指定必要章节和停止条件，避免把整门课或整本书当成前置任务。完整知识图、缺口诊断、研究出口和 7/30/90 天投影默认折叠，零基础学生首屏只看到第一关该做什么。

如果选择的周期明显不足，页面会同时显示论文可读路径、研究就绪路径和可用小时，不会为了凑 30 天删除必备知识或伪装成已经掌握。

默认的 [`settings/cloud_ai.yaml`](settings/cloud_ai.yaml) 使用 `provider: mock`，网站和测试都不会产生云端费用。真实云端请求只集中在 [`src/cloud_ai/client.py`](src/cloud_ai/client.py)。接入兼容 Chat Completions 的云服务时：

1. 将 `settings/cloud_ai.yaml` 的 `provider` 改成 `openai_compatible`，填写服务 `base_url` 和实际 `model`。
2. 只通过进程环境变量提供密钥：

```powershell
$env:CLOUD_AI_API_KEY = "你的密钥"
python -m uvicorn web.app:app --host 127.0.0.1 --port 8000
```

云端返回必须通过本地 Pydantic 合同：知识依赖无环、最短路径包含全部前置、能力关卡无重复且覆盖全部必修节点、论文 ID 来自当前证据、资料 URL 只能来自服务端白名单、计划日期连续、任务有可度量产物与验收标准、复现阶梯严格覆盖 L0–L4。格式错误会成为失败任务，不会保存成可用计划。

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

原始数据、本地 SQLite 状态、处理中间文件和模型产物由 Git 忽略；仓库只提交体积较小、供网站读取的已发布快照。

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
docs/                     架构与产品设计文档
scripts/                  2026 官方数据导入、建模与导出命令
settings/cloud_ai.yaml     不含密钥的云端提供方/模型配置
src/cloud_ai/              mock/真实 AI 边界、结构校验与学习服务
src/paper_sources/         网址解析、标准化、去重和 PDF 拉取
src/storage/               本地 SQLite 结构与应用查询
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
