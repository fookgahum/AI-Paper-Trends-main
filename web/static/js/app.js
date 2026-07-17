"use strict";

const translations = {
  "zh-CN": {
    brandSubtitle: "前沿选题雷达", navOpportunities: "研究机会", navTopics: "聚类证据",
    navPapers: "论文浏览", navData: "方法与数据", navAbout: "关于", localReadOnly: "本地只读分析",
    dashboardEyebrow: "FRONTIER OPPORTUNITY RADAR", opportunitiesTitle: "哪些方向更适合写论文？",
    topicsTitle: "聚类证据", papersTitle: "论文证据", dataTitle: "方法与数据", aboutPageTitle: "关于平台",
    dataset: "数据集", conference: "会议", allConferences: "全部会议", loading: "正在生成方向建议…",
    decisionCaveatTitle: "先说明“容易写”的含义", decisionCaveat: "切入友好度衡量资源匹配、可做题型和证据广度，不是录用率，也不保证论文发表。",
    heuristicBadge: "决策辅助 · 非录用预测", heroEyebrow: "ANSWER FIRST", heroTitle: "不要再看关键词串，直接看哪里值得切入",
    heroBody: "每个方向都给出前沿在做什么、为什么现在值得关注、适合什么论文形态、资源门槛、风险和代表论文。",
    researchProfile: "你的研究条件", bestDirection: "当前最友好方向", bestDirectionHelp: "随研究条件重新排序",
    entryScore: "切入友好度", entryScoreHelp: "0–100 启发式分数", directionCount: "前沿方向",
    directionCountHelp: "覆盖全部底层主题", evidencePapers: "证据论文", evidencePapersHelp: "当前会议筛选范围",
    priorityRanking: "PRIORITY RANKING", opportunityRankingTitle: "研究方向切入友好度",
    opportunityRankingSubtitle: "按当前研究条件排序；横轴从 0 开始。", filteredScoreNote: "分数仍基于完整 600 篇样本，论文数显示当前会议筛选。",
    howToRead: "HOW TO READ", readingTitle: "推荐先看这三件事", readFit: "资源是否匹配",
    readFitDetail: "单项短板会显著降低分数。", readShape: "能写什么论文", readShapeDetail: "优先选择评测、分析、轻量方法或攻防研究。",
    readRisk: "哪里容易同质化", readRiskDetail: "论文多不等于更容易，拥挤方向需要更清楚的差异。", viewMethodology: "查看评分方法",
    topChoicesEyebrow: "SHORTLIST", topChoicesTitle: "优先考虑的三个方向", topChoicesSubtitle: "这是基于当前研究条件的建议，而不是简单按论文数量排序。",
    directionBriefsEyebrow: "DIRECTION BRIEFS", directionBriefsTitle: "前沿方向逐项总结", directionBriefsSubtitle: "结论后面保留样本量、会议分布和代表论文，方便核查。",
    recommendationFilter: "显示", allDirections: "全部方向", recommendedOnly: "优先切入", cautionOnly: "谨慎/高门槛",
    scorePriority: "优先切入", scoreViable: "可以考虑", scoreCaution: "资源敏感", samplePapers: "样本论文", competition: "样本拥挤度",
    competitionHigh: "高", competitionMediumHigh: "中高", competitionMedium: "中", competitionLower: "较低",
    evidenceHigh: "证据较强", evidenceMedium: "证据中等", whyNow: "为什么现在值得看", entryPoints: "可写的切入点",
    paperShapes: "适合的论文形态", bestFor: "更适合", avoidTitle: "不要这样做", resourceBarrier: "资源门槛",
    compute: "算力", data: "数据", engineering: "工程", theory: "理论",
    representativePapers: "代表论文", viewDirectionPapers: "查看相关论文", fullSample: "完整样本", currentFilter: "当前筛选",
    topicEvidenceEyebrow: "EVIDENCE LAYER", topicEvidenceTitle: "底层聚类只用于提供证据", topicEvidenceSubtitle: "关键词主题不再充当结论；它们用于追踪方向由哪些论文分组构成。",
    clusterVolume: "CLUSTER VOLUME", clusterSizeTitle: "底层主题样本量", clusterSizeSubtitle: "24 个聚类，共 600 篇论文；条形图从 0 开始。",
    rank: "排名", frontierDirection: "归属前沿方向", rawCluster: "底层关键词聚类", paperCount: "论文数",
    conferenceDistribution: "会议分布", actions: "操作", viewPapers: "查看论文", topic: "底层主题",
    paperExplorerEyebrow: "PAPER EVIDENCE", paperExplorerTitle: "查看支撑结论的论文", paperExplorerSubtitle: "按前沿方向下钻，也可搜索标题、作者、关键词和摘要。",
    search: "搜索", searchPlaceholder: "搜索标题、作者、关键词或摘要", allTopics: "全部底层主题", decision: "类型", allDecisions: "全部类型",
    sort: "排序", sortTitle: "按标题", sortConference: "按会议", sortTopic: "按底层主题", applyFilters: "应用筛选",
    previous: "上一页", next: "下一页", pageStatus: "第 {page} / {pages} 页", paperResults: "{count} 篇论文", details: "查看详情",
    methodologyEyebrow: "METHOD & PROVENANCE", methodologyTitle: "评分方法与数据边界", methodologySubtitle: "让建议可解释、可复核，也明确它不能回答什么。",
    scoreMethodTitle: "切入友好度如何计算", formulaResource: "资源匹配", formulaBreadth: "跨会议覆盖", formulaEvaluation: "评测型切入信号",
    formulaEvidence: "样本证据量", formulaCompetition: "样本拥挤余量", limitationsTitle: "这份建议不能证明什么", generatedAt: "生成时间", sampleSeed: "随机种子", sampleSize: "每会议样本",
    topicModel: "底层主题模型", source: "官方来源", scope: "范围", aboutTitle: "这个网站现在回答什么",
    aboutBody: "它把公开前沿论文转成可行动的选题判断：方向现状、论文形态、进入门槛、同质化风险和可核查证据。聚类只是底层工具，不再是最终答案。",
    answerFirst: "结论优先", answerFirstDetail: "先给方向建议，再展开证据。", transparent: "方法透明", transparentDetail: "分数构成、样本和局限都可见。",
    bilingual: "中英双语", bilingualDetail: "总结、方法和界面均可切换。", authors: "作者", abstract: "摘要", keywords: "关键词",
    originalSource: "打开官方来源", noAbstract: "暂无摘要", noKeywords: "未提供关键词", noResults: "没有符合当前条件的论文。",
    loadFailed: "无法加载网站数据：", unknown: "未知", noDirections: "当前筛选下没有方向。"
  },
  "en-US": {
    brandSubtitle: "Frontier opportunity radar", navOpportunities: "Research opportunities", navTopics: "Cluster evidence",
    navPapers: "Papers", navData: "Method & data", navAbout: "About", localReadOnly: "Local read-only analysis",
    dashboardEyebrow: "FRONTIER OPPORTUNITY RADAR", opportunitiesTitle: "Which directions are more practical to publish in?",
    topicsTitle: "Cluster evidence", papersTitle: "Paper evidence", dataTitle: "Method & data", aboutPageTitle: "About",
    dataset: "Dataset", conference: "Conference", allConferences: "All conferences", loading: "Building direction recommendations…",
    decisionCaveatTitle: "What “easier to enter” means", decisionCaveat: "Entry friendliness measures resource fit, viable paper shapes, and evidence breadth. It is not an acceptance rate or publication guarantee.",
    heuristicBadge: "Decision aid · not acceptance prediction", heroEyebrow: "ANSWER FIRST", heroTitle: "Move beyond keyword strings and see where to enter",
    heroBody: "Each direction explains the frontier, why it matters now, viable paper shapes, resource barriers, risks, and representative evidence.",
    researchProfile: "Your research profile", bestDirection: "Most accessible now", bestDirectionHelp: "Re-ranked for your profile",
    entryScore: "Entry friendliness", entryScoreHelp: "0–100 heuristic", directionCount: "Frontier directions",
    directionCountHelp: "Covers every base cluster", evidencePapers: "Evidence papers", evidencePapersHelp: "Current conference filter",
    priorityRanking: "PRIORITY RANKING", opportunityRankingTitle: "Research-direction entry friendliness",
    opportunityRankingSubtitle: "Ranked for the selected profile; the axis begins at zero.", filteredScoreNote: "Scores use the full 600-paper sample; paper counts reflect the conference filter.",
    howToRead: "HOW TO READ", readingTitle: "Read these three things first", readFit: "Resource fit",
    readFitDetail: "One major bottleneck materially lowers the score.", readShape: "Viable paper shapes", readShapeDetail: "Prefer evaluation, analysis, lightweight methods, or attack/defense work.",
    readRisk: "Commoditization risk", readRiskDetail: "More papers do not mean easier entry; crowded areas need sharper differentiation.", viewMethodology: "View scoring method",
    topChoicesEyebrow: "SHORTLIST", topChoicesTitle: "Three directions to consider first", topChoicesSubtitle: "Recommendations reflect your research profile, not paper volume alone.",
    directionBriefsEyebrow: "DIRECTION BRIEFS", directionBriefsTitle: "Frontier direction briefs", directionBriefsSubtitle: "Every conclusion retains sample size, venue mix, and representative papers for verification.",
    recommendationFilter: "Show", allDirections: "All directions", recommendedOnly: "Priority entries", cautionOnly: "Caution / high barrier",
    scorePriority: "Priority entry", scoreViable: "Worth considering", scoreCaution: "Resource-sensitive", samplePapers: "Sample papers", competition: "Sample density",
    competitionHigh: "High", competitionMediumHigh: "Medium-high", competitionMedium: "Medium", competitionLower: "Lower",
    evidenceHigh: "Stronger evidence", evidenceMedium: "Moderate evidence", whyNow: "Why it matters now", entryPoints: "Practical entry points",
    paperShapes: "Viable paper shapes", bestFor: "Best fit", avoidTitle: "Avoid this", resourceBarrier: "Resource barriers",
    compute: "Compute", data: "Data", engineering: "Engineering", theory: "Theory",
    representativePapers: "Representative papers", viewDirectionPapers: "View related papers", fullSample: "Full sample", currentFilter: "Current filter",
    topicEvidenceEyebrow: "EVIDENCE LAYER", topicEvidenceTitle: "Clusters are evidence, not the answer", topicEvidenceSubtitle: "Keyword clusters trace which paper groups support each readable frontier direction.",
    clusterVolume: "CLUSTER VOLUME", clusterSizeTitle: "Base-cluster sample volume", clusterSizeSubtitle: "24 clusters across 600 papers; bars begin at zero.",
    rank: "Rank", frontierDirection: "Frontier direction", rawCluster: "Raw keyword cluster", paperCount: "Papers",
    conferenceDistribution: "Conference mix", actions: "Actions", viewPapers: "View papers", topic: "Base topic",
    paperExplorerEyebrow: "PAPER EVIDENCE", paperExplorerTitle: "Inspect the papers behind each conclusion", paperExplorerSubtitle: "Drill down by frontier direction or search titles, authors, keywords, and abstracts.",
    search: "Search", searchPlaceholder: "Search title, author, keyword, or abstract", allTopics: "All base topics", decision: "Type", allDecisions: "All types",
    sort: "Sort", sortTitle: "By title", sortConference: "By conference", sortTopic: "By base topic", applyFilters: "Apply filters",
    previous: "Previous", next: "Next", pageStatus: "Page {page} of {pages}", paperResults: "{count} papers", details: "View details",
    methodologyEyebrow: "METHOD & PROVENANCE", methodologyTitle: "Scoring method and data boundaries", methodologySubtitle: "Make recommendations explainable and explicit about what they cannot establish.",
    scoreMethodTitle: "How entry friendliness is calculated", formulaResource: "Resource fit", formulaBreadth: "Cross-venue breadth", formulaEvaluation: "Evaluation-entry signal",
    formulaEvidence: "Evidence volume", formulaCompetition: "Sample-density headroom", limitationsTitle: "What these recommendations cannot establish", generatedAt: "Generated at", sampleSeed: "Random seed", sampleSize: "Sample per venue",
    topicModel: "Base topic model", source: "Official source", scope: "Scope", aboutTitle: "What this website now answers",
    aboutBody: "It turns public frontier papers into actionable topic choices: direction status, viable paper shapes, entry barriers, commoditization risks, and inspectable evidence. Clustering remains a tool, not the final answer.",
    answerFirst: "Answer first", answerFirstDetail: "Recommendation before evidence drill-down.", transparent: "Transparent method", transparentDetail: "Scores, samples, and caveats stay visible.",
    bilingual: "Bilingual", bilingualDetail: "Summaries, methods, and interface in Chinese or English.", authors: "Authors", abstract: "Abstract", keywords: "Keywords",
    originalSource: "Open official source", noAbstract: "No abstract available", noKeywords: "No keywords supplied", noResults: "No papers match the current filters.",
    loadFailed: "Unable to load dashboard data: ", unknown: "Unknown", noDirections: "No directions match this filter."
  }
};

const state = {
  language: localStorage.getItem("ai-paper-language") || "zh-CN",
  profile: localStorage.getItem("ai-paper-profile") || "individual",
  runId: null,
  conference: "",
  dashboard: null,
  page: 1,
  pageSize: 20,
  charts: {},
};

const $ = (selector) => document.querySelector(selector);
const $$ = (selector) => [...document.querySelectorAll(selector)];
const t = (key, replacements = {}) => {
  let value = translations[state.language][key] || translations["en-US"][key] || key;
  Object.entries(replacements).forEach(([name, replacement]) => {
    value = value.replace(`{${name}}`, String(replacement));
  });
  return value;
};
const localize = (value) => {
  if (value && typeof value === "object" && !Array.isArray(value)) {
    return value[state.language] || value["en-US"] || Object.values(value)[0] || "";
  }
  return String(value ?? "");
};
const escapeHtml = (value) => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&#039;");
const safeUrl = (value) => {
  try {
    const url = new URL(value);
    return url.protocol === "https:" ? url.href : "#";
  } catch (_) {
    return "#";
  }
};

async function fetchJson(url) {
  const response = await fetch(url, { headers: { Accept: "application/json" } });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail || `${response.status} ${response.statusText}`);
  }
  return response.json();
}

function applyTranslations() {
  document.documentElement.lang = state.language;
  $$('[data-i18n]').forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  $$('[data-i18n-placeholder]').forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  $$('.language-switch button').forEach((button) => {
    button.classList.toggle("active", button.dataset.lang === state.language);
  });
  const section = $('.nav-item.active')?.dataset.section || "opportunities";
  updatePageTitle(section);
}

function updatePageTitle(section) {
  const key = {
    opportunities: "opportunitiesTitle", topics: "topicsTitle", papers: "papersTitle",
    data: "dataTitle", about: "aboutPageTitle",
  }[section];
  $("#page-title").textContent = t(key);
}

function showSection(section) {
  $$('.nav-item').forEach((button) => button.classList.toggle("active", button.dataset.section === section));
  $$('.page-section').forEach((element) => element.classList.toggle("active", element.id === section));
  updatePageTitle(section);
  $('.sidebar').classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
  setTimeout(() => Object.values(state.charts).forEach((chart) => chart.resize()), 0);
}

function setLoading(isLoading) {
  $("#loading").classList.toggle("hidden", !isLoading);
  if (isLoading) $("#error-panel").classList.add("hidden");
}

function showError(error) {
  setLoading(false);
  const panel = $("#error-panel");
  panel.textContent = `${t("loadFailed")}${error.message || error}`;
  panel.classList.remove("hidden");
}

async function loadRuns() {
  const payload = await fetchJson("/api/runs");
  const select = $("#run-select");
  select.innerHTML = payload.items.map((run) =>
    `<option value="${escapeHtml(run.run_id)}">${escapeHtml(run.title)}</option>`
  ).join("");
  if (!payload.items.length) throw new Error("No exported result snapshots were found.");
  state.runId = payload.items[0].run_id;
  await loadDashboard();
}

async function loadDashboard() {
  setLoading(true);
  const params = new URLSearchParams();
  if (state.conference) params.set("conference", state.conference);
  try {
    state.dashboard = await fetchJson(`/api/runs/${encodeURIComponent(state.runId)}/dashboard?${params}`);
    populateConferenceSelect();
    populateProfileSelect();
    renderAll();
    state.page = 1;
    await loadPapers();
    setLoading(false);
  } catch (error) {
    showError(error);
  }
}

function populateConferenceSelect() {
  const select = $("#conference-select");
  select.innerHTML = `<option value="">${escapeHtml(t("allConferences"))}</option>` +
    state.dashboard.filters.conferences.map((conference) =>
      `<option value="${escapeHtml(conference)}">${escapeHtml(conference)}</option>`
    ).join("");
  select.value = state.conference;
}

function populateProfileSelect() {
  const profiles = state.dashboard.opportunities?.profiles || [];
  if (!profiles.some((profile) => profile.id === state.profile)) {
    state.profile = profiles[0]?.id || "individual";
  }
  const select = $("#profile-select");
  select.innerHTML = profiles.map((profile) =>
    `<option value="${escapeHtml(profile.id)}">${escapeHtml(localize(profile.title))}</option>`
  ).join("");
  select.value = state.profile;
  const profile = profiles.find((item) => item.id === state.profile);
  $("#profile-description").textContent = profile ? localize(profile.description) : "";
}

function scoreBand(score) {
  if (score >= 80) return "priority";
  if (score >= 65) return "viable";
  return "caution";
}

function scoreBandLabel(score) {
  return t({ priority: "scorePriority", viable: "scoreViable", caution: "scoreCaution" }[scoreBand(score)]);
}

function competitionLabel(value) {
  return t({ high: "competitionHigh", medium_high: "competitionMediumHigh", medium: "competitionMedium", lower: "competitionLower" }[value] || "unknown");
}

function sortedDirections() {
  const directions = state.dashboard.opportunities?.directions || [];
  return [...directions].sort((a, b) => {
    const scoreDiff = (b.scores?.[state.profile]?.score || 0) - (a.scores?.[state.profile]?.score || 0);
    return scoreDiff || b.paper_count - a.paper_count;
  });
}

function renderAll() {
  renderOpportunities();
  renderTopics();
  populatePaperFilters();
  renderMethodology();
  renderProvenance(state.dashboard.manifest);
}

function renderOpportunities() {
  const directions = sortedDirections();
  const best = directions[0];
  $("#metric-best-direction").textContent = best ? localize(best.title) : "—";
  $("#metric-best-score").textContent = best ? best.scores[state.profile].score : "—";
  $("#metric-directions").textContent = directions.length.toLocaleString();
  $("#metric-papers").textContent = state.dashboard.overview.paper_count.toLocaleString();
  $("#opportunity-chart-subtitle").textContent = state.conference ? t("filteredScoreNote") : t("opportunityRankingSubtitle");
  renderOpportunityChart(directions);
  renderTopOpportunities(directions.slice(0, 3));
  renderOpportunityCards(directions);
}

function chartTextStyle() {
  return { fontFamily: 'Inter, "Noto Sans SC", "Microsoft YaHei", sans-serif', color: "#687583" };
}

function prepareChart(id) {
  if (!state.charts[id]) state.charts[id] = echarts.init(document.getElementById(id));
  return state.charts[id];
}

function renderOpportunityChart(directions) {
  const rows = [...directions].reverse();
  const chart = prepareChart("opportunity-chart");
  chart.setOption({
    animationDuration: 450,
    textStyle: chartTextStyle(),
    grid: { left: 22, right: 42, top: 16, bottom: 22, containLabel: true },
    tooltip: {
      trigger: "item",
      formatter: (params) => {
        const row = params.data.meta;
        return `<strong>${escapeHtml(localize(row.title))}</strong><br>${escapeHtml(t("entryScore"))}: ${row.scores[state.profile].score}/100<br>${escapeHtml(t("samplePapers"))}: ${row.paper_count}<br>${escapeHtml(t("competition"))}: ${escapeHtml(competitionLabel(row.competition_pressure))}`;
      },
    },
    xAxis: { type: "value", min: 0, max: 100, splitLine: { lineStyle: { color: "#edf1f4" } } },
    yAxis: {
      type: "category",
      data: rows.map((row) => localize(row.title)),
      axisLabel: { width: 210, overflow: "truncate" }, axisTick: { show: false },
    },
    series: [{
      type: "bar", barWidth: 18,
      data: rows.map((row) => ({
        value: row.scores[state.profile].score, directionId: row.id, meta: row,
        itemStyle: { color: "#3b79a8", borderRadius: [0, 5, 5, 0] },
      })),
      label: { show: true, position: "right", color: "#17212b", formatter: "{c}" },
    }],
  }, true);
  chart.off("click");
  chart.on("click", (params) => {
    const card = document.getElementById(`direction-${params.data.directionId}`);
    card?.scrollIntoView({ behavior: "smooth", block: "start" });
  });
}

function renderTopOpportunities(directions) {
  $("#top-opportunities").innerHTML = directions.map((direction, index) => {
    const score = direction.scores[state.profile].score;
    return `<article class="shortlist-card rank-${index + 1}">
      <div class="shortlist-rank">0${index + 1}</div>
      <div class="score-pill band-${scoreBand(score)}"><strong>${score}</strong><span>${escapeHtml(scoreBandLabel(score))}</span></div>
      <h3>${escapeHtml(localize(direction.title))}</h3>
      <p>${escapeHtml(localize(direction.summary))}</p>
      <div class="shortlist-meta">
        <span>${direction.paper_count} ${escapeHtml(t("samplePapers"))}</span>
        <span>${escapeHtml(t("competition"))}: ${escapeHtml(competitionLabel(direction.competition_pressure))}</span>
      </div>
      <button class="link-button jump-direction" data-direction-id="${escapeHtml(direction.id)}">${escapeHtml(t("whyNow"))} →</button>
    </article>`;
  }).join("");
  $$('.jump-direction').forEach((button) => button.addEventListener("click", () => {
    document.getElementById(`direction-${button.dataset.directionId}`)?.scrollIntoView({ behavior: "smooth", block: "start" });
  }));
}

function barrierMarkup(barriers) {
  return ["compute", "data", "engineering", "theory"].map((name) => {
    const level = Number(barriers[name]);
    const segments = Array.from({ length: 5 }, (_, index) => `<span class="${index < level ? "active" : ""}"></span>`).join("");
    return `<div class="barrier-row"><span>${escapeHtml(t(name))}</span><div class="barrier-scale" aria-label="${escapeHtml(t(name))}: ${level}/5">${segments}</div><strong>${level}/5</strong></div>`;
  }).join("");
}

function listMarkup(items) {
  return `<ul>${(items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}</ul>`;
}

function renderOpportunityCards(directions) {
  const filter = $("#recommendation-filter").value;
  const visible = directions.filter((direction) => {
    const band = scoreBand(direction.scores[state.profile].score);
    if (filter === "recommended") return band === "priority";
    if (filter === "caution") return band === "caution";
    return true;
  });
  $("#opportunity-grid").innerHTML = visible.length ? visible.map((direction, index) => {
    const score = direction.scores[state.profile].score;
    const currentCount = direction.filtered_paper_count;
    const conferenceChips = Object.entries(
      direction.filtered_conference_counts || direction.conference_counts
    )
      .map(([name, count]) => `<span class="chip">${escapeHtml(name)} ${count}</span>`).join("");
    const shapes = localize(direction.paper_shapes) || [];
    const entries = localize(direction.entry_points) || [];
    const representatives = direction.representative_papers.map((paper) =>
      `<li><a href="${escapeHtml(safeUrl(paper.source_url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(paper.title)}</a><span>${escapeHtml(paper.conference)}</span></li>`
    ).join("");
    return `<article class="direction-card" id="direction-${escapeHtml(direction.id)}">
      <header class="direction-card-header">
        <div>
          <span class="direction-index">${String(index + 1).padStart(2, "0")}</span>
          <h3>${escapeHtml(localize(direction.title))}</h3>
          <div class="direction-tags">
            <span class="status-tag band-${scoreBand(score)}">${escapeHtml(scoreBandLabel(score))}</span>
            <span class="status-tag neutral">${escapeHtml(direction.evidence_confidence === "high" ? t("evidenceHigh") : t("evidenceMedium"))}</span>
          </div>
        </div>
        <div class="direction-score"><strong>${score}</strong><span>/ 100</span><small>${escapeHtml(t("entryScore"))}</small></div>
      </header>
      <p class="direction-summary">${escapeHtml(localize(direction.summary))}</p>
      <div class="direction-evidence-strip">
        <div><strong>${direction.paper_count}</strong><span>${escapeHtml(t("fullSample"))}</span></div>
        <div><strong>${currentCount}</strong><span>${escapeHtml(t("currentFilter"))}</span></div>
        <div><strong>${direction.breadth_score}</strong><span>${escapeHtml(t("formulaBreadth"))}</span></div>
        <div><strong>${escapeHtml(competitionLabel(direction.competition_pressure))}</strong><span>${escapeHtml(t("competition"))}</span></div>
      </div>
      <div class="direction-columns">
        <section><h4>${escapeHtml(t("whyNow"))}</h4><p>${escapeHtml(localize(direction.why_now))}</p></section>
        <section><h4>${escapeHtml(t("entryPoints"))}</h4>${listMarkup(entries)}</section>
      </div>
      <div class="paper-shapes"><strong>${escapeHtml(t("paperShapes"))}</strong>${shapes.map((shape) => `<span class="chip accent-chip">${escapeHtml(shape)}</span>`).join("")}</div>
      <div class="direction-columns lower-columns">
        <section><h4>${escapeHtml(t("resourceBarrier"))}</h4>${barrierMarkup(direction.barriers)}</section>
        <section class="fit-risk"><div><h4>${escapeHtml(t("bestFor"))}</h4><p>${escapeHtml(localize(direction.best_for))}</p></div><div class="avoid-box"><h4>${escapeHtml(t("avoidTitle"))}</h4><p>${escapeHtml(localize(direction.avoid))}</p></div></section>
      </div>
      <div class="conference-chips">${conferenceChips}</div>
      <details class="representative-details">
        <summary>${escapeHtml(t("representativePapers"))}</summary>
        <ol>${representatives}</ol>
      </details>
      <button class="primary-button view-direction-papers" data-direction-id="${escapeHtml(direction.id)}">${escapeHtml(t("viewDirectionPapers"))}</button>
    </article>`;
  }).join("") : `<div class="loading-panel">${escapeHtml(t("noDirections"))}</div>`;
  $$('.view-direction-papers').forEach((button) => button.addEventListener("click", () => {
    $("#direction-filter").value = button.dataset.directionId;
    $("#topic-filter").value = "";
    state.page = 1;
    showSection("papers");
    loadPapers();
  }));
}

function renderTopics() {
  const topics = state.dashboard.topics;
  const rows = [...topics].reverse();
  prepareChart("topics-chart").setOption({
    animationDuration: 450,
    textStyle: chartTextStyle(),
    grid: { left: 22, right: 42, top: 18, bottom: 18, containLabel: true },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    xAxis: { type: "value", min: 0, splitLine: { lineStyle: { color: "#edf1f4" } } },
    yAxis: { type: "category", data: rows.map((row) => row.topic_name), axisLabel: { width: 230, overflow: "truncate" }, axisTick: { show: false } },
    series: [{ type: "bar", data: rows.map((row) => row.paper_count), barWidth: 14, itemStyle: { color: "#6d7c4c", borderRadius: [0, 4, 4, 0] }, label: { show: true, position: "right", color: "#17212b" } }],
  }, true);
  $("#topics-table-body").innerHTML = topics.map((row, index) => {
    const distribution = Object.entries(row.conferences).sort((a, b) => b[1] - a[1])
      .map(([name, count]) => `<span class="chip">${escapeHtml(name)} ${count}</span>`).join("");
    return `<tr><td>${index + 1}</td><td><strong>${escapeHtml(localize(row.direction_title))}</strong></td><td>${escapeHtml(row.topic_name)}</td><td class="topic-count">${row.paper_count}</td><td><div class="conference-chips">${distribution}</div></td><td><button class="link-button topic-paper-link" data-topic="${escapeHtml(row.topic_name)}">${escapeHtml(t("viewPapers"))}</button></td></tr>`;
  }).join("");
  $$('.topic-paper-link').forEach((button) => button.addEventListener("click", () => {
    $("#topic-filter").value = button.dataset.topic;
    $("#direction-filter").value = "";
    state.page = 1;
    showSection("papers");
    loadPapers();
  }));
}

function populatePaperFilters() {
  const filters = state.dashboard.filters;
  const directionSelect = $("#direction-filter");
  const currentDirection = directionSelect.value;
  directionSelect.innerHTML = `<option value="">${escapeHtml(t("allDirections"))}</option>` +
    filters.directions.map((direction) => `<option value="${escapeHtml(direction.id)}">${escapeHtml(localize(direction.title))}</option>`).join("");
  if ([...directionSelect.options].some((option) => option.value === currentDirection)) directionSelect.value = currentDirection;

  const topicSelect = $("#topic-filter");
  const currentTopic = topicSelect.value;
  topicSelect.innerHTML = `<option value="">${escapeHtml(t("allTopics"))}</option>` +
    filters.topics.map((topic) => `<option value="${escapeHtml(topic)}">${escapeHtml(topic)}</option>`).join("");
  if ([...topicSelect.options].some((option) => option.value === currentTopic)) topicSelect.value = currentTopic;

  const decisionSelect = $("#decision-filter");
  const currentDecision = decisionSelect.value;
  decisionSelect.innerHTML = `<option value="">${escapeHtml(t("allDecisions"))}</option>` +
    filters.decisions.map((decision) => `<option value="${escapeHtml(decision)}">${escapeHtml(decision)}</option>`).join("");
  if ([...decisionSelect.options].some((option) => option.value === currentDecision)) decisionSelect.value = currentDecision;
}

async function loadPapers() {
  if (!state.runId) return;
  const params = new URLSearchParams({ page: state.page, page_size: state.pageSize, sort: $("#paper-sort").value });
  if (state.conference) params.set("conference", state.conference);
  if ($("#direction-filter").value) params.set("direction", $("#direction-filter").value);
  if ($("#topic-filter").value) params.set("topic", $("#topic-filter").value);
  if ($("#decision-filter").value) params.set("decision", $("#decision-filter").value);
  if ($("#paper-search").value.trim()) params.set("q", $("#paper-search").value.trim());
  try {
    renderPapers(await fetchJson(`/api/runs/${encodeURIComponent(state.runId)}/papers?${params}`));
  } catch (error) {
    showError(error);
  }
}

function renderPapers(payload) {
  $("#paper-total").textContent = t("paperResults", { count: payload.total.toLocaleString() });
  $("#paper-list").innerHTML = payload.items.length ? payload.items.map((paper) => `
    <article class="paper-card">
      <div class="paper-meta"><span class="chip">${escapeHtml(paper.conference)} ${escapeHtml(paper.year)}</span><span class="chip accent-chip">${escapeHtml(localize(paper.direction_title))}</span><span class="chip">${escapeHtml(paper.decision)}</span></div>
      <h3>${escapeHtml(paper.title)}</h3>
      <p>${escapeHtml((paper.abstract || t("noAbstract")).slice(0, 280))}${paper.abstract?.length > 280 ? "…" : ""}</p>
      <div class="paper-card-footer"><span class="authors">${escapeHtml((paper.authors || []).join(", "))}</span><button class="link-button paper-detail-button" data-paper-id="${escapeHtml(paper.id)}">${escapeHtml(t("details"))}</button></div>
    </article>`).join("") : `<div class="loading-panel">${escapeHtml(t("noResults"))}</div>`;
  $("#page-status").textContent = t("pageStatus", { page: payload.page, pages: payload.pages || 1 });
  $("#previous-page").disabled = payload.page <= 1;
  $("#next-page").disabled = payload.page >= payload.pages;
  $$('.paper-detail-button').forEach((button) => button.addEventListener("click", () => openPaper(button.dataset.paperId)));
}

async function openPaper(paperId) {
  try {
    const paper = await fetchJson(`/api/runs/${encodeURIComponent(state.runId)}/papers/${encodeURIComponent(paperId)}`);
    const keywords = paper.keywords?.length ? paper.keywords.join(", ") : t("noKeywords");
    $("#paper-dialog-content").innerHTML = `
      <div class="paper-meta"><span class="chip">${escapeHtml(paper.conference)} ${escapeHtml(paper.year)}</span><span class="chip accent-chip">${escapeHtml(localize(paper.direction_title))}</span><span class="chip">${escapeHtml(paper.decision)}</span></div>
      <h2>${escapeHtml(paper.title)}</h2>
      <div class="detail-section"><h3>${escapeHtml(t("authors"))}</h3><p>${escapeHtml(paper.authors.join(", "))}</p></div>
      <div class="detail-section"><h3>${escapeHtml(t("abstract"))}</h3><p>${escapeHtml(paper.abstract || t("noAbstract"))}</p></div>
      <div class="detail-section"><h3>${escapeHtml(t("keywords"))}</h3><p>${escapeHtml(keywords)}</p></div>
      <div class="detail-section"><a class="primary-button" href="${escapeHtml(safeUrl(paper.source_url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(t("originalSource"))}</a></div>`;
    $("#paper-dialog").showModal();
  } catch (error) {
    showError(error);
  }
}

function renderMethodology() {
  const analysis = state.dashboard.opportunities;
  $("#methodology-note").textContent = localize(analysis.methodology);
  const formula = analysis.score_formula || {};
  const rows = [
    ["formulaResource", formula.resource_fit], ["formulaBreadth", formula.cross_venue_breadth],
    ["formulaEvaluation", formula.evaluation_signal], ["formulaEvidence", formula.evidence_strength],
    ["formulaCompetition", formula.competition_headroom],
  ];
  $("#score-formula-grid").innerHTML = rows.map(([label, weight]) =>
    `<div><strong>${Math.round(Number(weight) * 100)}%</strong><span>${escapeHtml(t(label))}</span></div>`
  ).join("");
  $("#analysis-limitations").innerHTML = (localize(analysis.limitations) || [])
    .map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function renderProvenance(manifest) {
  $("#run-details").innerHTML = [
    [t("generatedAt"), new Date(manifest.generated_at).toLocaleString(state.language)],
    [t("sampleSeed"), manifest.sample_seed ?? t("unknown")],
    [t("sampleSize"), manifest.sample_size_per_conference ?? t("unknown")],
    [t("topicModel"), manifest.topic_model ?? t("unknown")],
  ].map(([label, value]) => `<div class="provenance-card"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong><small>${escapeHtml(manifest.title)}</small></div>`).join("");
  $("#sources-table-body").innerHTML = manifest.sources.map((source) => `<tr><td><strong>${escapeHtml(source.conference)}</strong></td><td><a href="${escapeHtml(safeUrl(source.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.label)}</a></td><td>${Number(source.paper_count).toLocaleString()}</td><td>${escapeHtml(source.scope || "")}</td></tr>`).join("");
}

function rerenderLanguageDependentContent() {
  applyTranslations();
  if (state.dashboard) {
    populateConferenceSelect();
    populateProfileSelect();
    renderAll();
    loadPapers();
  }
}

function bindEvents() {
  $('.brand').addEventListener("click", (event) => {
    event.preventDefault();
    showSection("opportunities");
  });
  $$('.nav-item').forEach((button) => button.addEventListener("click", () => showSection(button.dataset.section)));
  $$('.language-switch button').forEach((button) => button.addEventListener("click", () => {
    state.language = button.dataset.lang;
    localStorage.setItem("ai-paper-language", state.language);
    rerenderLanguageDependentContent();
  }));
  $("#run-select").addEventListener("change", (event) => {
    state.runId = event.target.value; state.conference = ""; loadDashboard();
  });
  $("#conference-select").addEventListener("change", (event) => {
    state.conference = event.target.value; loadDashboard();
  });
  $("#profile-select").addEventListener("change", (event) => {
    state.profile = event.target.value;
    localStorage.setItem("ai-paper-profile", state.profile);
    populateProfileSelect(); renderOpportunities();
  });
  $("#recommendation-filter").addEventListener("change", () => renderOpportunityCards(sortedDirections()));
  $("#methodology-link").addEventListener("click", () => showSection("data"));
  $("#paper-filters").addEventListener("submit", (event) => { event.preventDefault(); state.page = 1; loadPapers(); });
  $("#direction-filter").addEventListener("change", () => { if ($("#direction-filter").value) $("#topic-filter").value = ""; });
  $("#topic-filter").addEventListener("change", () => { if ($("#topic-filter").value) $("#direction-filter").value = ""; });
  $("#previous-page").addEventListener("click", () => { state.page -= 1; loadPapers(); });
  $("#next-page").addEventListener("click", () => { state.page += 1; loadPapers(); });
  $("#dialog-close").addEventListener("click", () => $("#paper-dialog").close());
  $("#paper-dialog").addEventListener("click", (event) => { if (event.target === $("#paper-dialog")) $("#paper-dialog").close(); });
  $("#mobile-menu").addEventListener("click", () => $('.sidebar').classList.toggle("open"));
  window.addEventListener("resize", () => Object.values(state.charts).forEach((chart) => chart.resize()));
}

document.addEventListener("DOMContentLoaded", async () => {
  bindEvents();
  applyTranslations();
  try {
    await loadRuns();
  } catch (error) {
    showError(error);
  }
});
