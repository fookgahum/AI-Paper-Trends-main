"use strict";

const translations = {
  "zh-CN": {
    brandSubtitle: "论文趋势分析", navOverview: "总览", navTopics: "主题分析",
    navPapers: "论文浏览", navData: "数据记录", navAbout: "关于",
    localReadOnly: "本地只读模式", dashboardEyebrow: "PUBLIC RESEARCH INTELLIGENCE",
    overviewTitle: "会议研究全景", topicsTitle: "主题分析", papersTitle: "论文浏览",
    dataTitle: "数据记录", aboutPageTitle: "关于平台", dataset: "数据集", conference: "会议",
    allConferences: "全部会议", loading: "正在读取分析结果…", scopeTitle: "数据范围说明",
    scopeNote: "当前为已录用/已发表论文固定随机样本，不代表全部投稿或真实录用率。",
    officialSources: "官方公开来源", paperCount: "论文样本", paperCountHelp: "当前筛选范围",
    conferenceCount: "会议数量", conferenceCountHelp: "CCF-A 会议", topicCount: "研究主题",
    topicCountHelp: "含全部模型分组", ratedCount: "公开评分覆盖", ratedCountHelp: "当前来源未公布评分时为 0",
    ranking: "RANKING", topTopicsTitle: "热门研究主题", topTopicsSubtitle: "按当前筛选范围内的论文数量排序",
    coverage: "COVERAGE", conferenceMixTitle: "会议样本构成", conferenceMixSubtitle: "各会议在当前样本中的论文数量",
    outcome: "OUTCOME", decisionTitle: "公开发表类型", decisionSubtitle: "来源网站提供的录用或发表类别",
    topicExplorerEyebrow: "TOPIC EXPLORER", topicExplorerTitle: "主题对比与下钻",
    topicExplorerSubtitle: "比较主题规模，并进入论文列表查看构成。", rank: "排名", topic: "主题",
    conferenceDistribution: "会议分布", actions: "操作", viewPapers: "查看论文",
    paperExplorerEyebrow: "PAPER EXPLORER", paperExplorerTitle: "搜索和筛选论文",
    paperExplorerSubtitle: "在标题、作者、关键词和摘要中搜索。", search: "搜索",
    searchPlaceholder: "搜索标题、作者、关键词或摘要", allTopics: "全部主题", decision: "类型",
    allDecisions: "全部类型", sort: "排序", sortTitle: "按标题", sortConference: "按会议",
    sortTopic: "按主题", sortRating: "按评分", applyFilters: "应用筛选", previous: "上一页", next: "下一页",
    pageStatus: "第 {page} / {pages} 页", paperResults: "{count} 篇论文", details: "查看详情",
    provenanceEyebrow: "DATA PROVENANCE", provenanceTitle: "数据来源和生成记录",
    provenanceSubtitle: "每项结果均保留会议、样本和公开来源信息。", source: "来源", scope: "范围",
    generatedAt: "生成时间", sampleSeed: "随机种子", sampleSize: "每会议样本", topicModel: "主题模型",
    aboutTitle: "关于这个网站", aboutBody: "本网站用于浏览公开会议论文样本、主题聚类结果和来源元数据。它是只读展示层，打开网页不会启动模型训练。",
    readOnly: "只读", readOnlyDetail: "不会修改分析数据", offlineCharts: "本地图表",
    offlineChartsDetail: "图表资源随项目提供", bilingual: "双语", bilingualDetail: "中文和英文界面",
    authors: "作者", abstract: "摘要", keywords: "关键词", publicationType: "发表类型",
    originalSource: "打开官方来源", noAbstract: "暂无摘要", noKeywords: "未提供关键词",
    noResults: "没有符合当前条件的论文。", loadFailed: "无法加载网站数据：", unknown: "未知",
    acceptedSample: "已录用/已发表论文样本", fixedRandomSample: "固定随机抽样", year: "年份"
  },
  "en-US": {
    brandSubtitle: "Research trend analysis", navOverview: "Overview", navTopics: "Topics",
    navPapers: "Papers", navData: "Data records", navAbout: "About",
    localReadOnly: "Local read-only mode", dashboardEyebrow: "PUBLIC RESEARCH INTELLIGENCE",
    overviewTitle: "Conference research landscape", topicsTitle: "Topic analysis", papersTitle: "Paper explorer",
    dataTitle: "Data records", aboutPageTitle: "About", dataset: "Dataset", conference: "Conference",
    allConferences: "All conferences", loading: "Loading analysis results…", scopeTitle: "Dataset scope",
    scopeNote: "This is a fixed random sample of accepted or published papers, not all submissions or a true acceptance-rate sample.",
    officialSources: "Official public sources", paperCount: "Paper sample", paperCountHelp: "Current filter scope",
    conferenceCount: "Conferences", conferenceCountHelp: "CCF-A venues", topicCount: "Research topics",
    topicCountHelp: "All model groups included", ratedCount: "Public rating coverage", ratedCountHelp: "Zero when sources do not publish ratings",
    ranking: "RANKING", topTopicsTitle: "Leading research topics", topTopicsSubtitle: "Ranked by paper count in the current filter scope",
    coverage: "COVERAGE", conferenceMixTitle: "Conference sample mix", conferenceMixSubtitle: "Paper count contributed by each conference",
    outcome: "OUTCOME", decisionTitle: "Published presentation types", decisionSubtitle: "Acceptance or publication category supplied by the source",
    topicExplorerEyebrow: "TOPIC EXPLORER", topicExplorerTitle: "Compare and drill into topics",
    topicExplorerSubtitle: "Compare topic volume and open the underlying paper list.", rank: "Rank", topic: "Topic",
    conferenceDistribution: "Conference mix", actions: "Actions", viewPapers: "View papers",
    paperExplorerEyebrow: "PAPER EXPLORER", paperExplorerTitle: "Search and filter papers",
    paperExplorerSubtitle: "Search titles, authors, keywords, and abstracts.", search: "Search",
    searchPlaceholder: "Search title, author, keyword, or abstract", allTopics: "All topics", decision: "Type",
    allDecisions: "All types", sort: "Sort", sortTitle: "By title", sortConference: "By conference",
    sortTopic: "By topic", sortRating: "By rating", applyFilters: "Apply filters", previous: "Previous", next: "Next",
    pageStatus: "Page {page} of {pages}", paperResults: "{count} papers", details: "View details",
    provenanceEyebrow: "DATA PROVENANCE", provenanceTitle: "Sources and generation record",
    provenanceSubtitle: "Every result retains conference, sample, and public source metadata.", source: "Source", scope: "Scope",
    generatedAt: "Generated at", sampleSeed: "Random seed", sampleSize: "Sample per venue", topicModel: "Topic model",
    aboutTitle: "About this website", aboutBody: "This site explores public conference-paper samples, topic-model results, and source metadata. It is a read-only presentation layer and never starts model training when opened.",
    readOnly: "Read-only", readOnlyDetail: "Does not modify analysis data", offlineCharts: "Local charts",
    offlineChartsDetail: "Chart assets ship with the project", bilingual: "Bilingual", bilingualDetail: "Chinese and English interface",
    authors: "Authors", abstract: "Abstract", keywords: "Keywords", publicationType: "Publication type",
    originalSource: "Open official source", noAbstract: "No abstract available", noKeywords: "No keywords supplied",
    noResults: "No papers match the current filters.", loadFailed: "Unable to load dashboard data: ", unknown: "Unknown",
    acceptedSample: "Accepted/published paper sample", fixedRandomSample: "Fixed random sample", year: "Year"
  }
};

const state = {
  language: localStorage.getItem("ai-paper-language") || "zh-CN",
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
  const activeSection = $('.nav-item.active')?.dataset.section || "overview";
  updatePageTitle(activeSection);
}

function updatePageTitle(section) {
  const key = {
    overview: "overviewTitle",
    topics: "topicsTitle",
    papers: "papersTitle",
    data: "dataTitle",
    about: "aboutPageTitle",
  }[section];
  $("#page-title").textContent = t(key);
}

function showSection(section) {
  $$('.nav-item').forEach((button) => button.classList.toggle("active", button.dataset.section === section));
  $$('.page-section').forEach((element) => element.classList.toggle("active", element.id === section));
  updatePageTitle(section);
  $('.sidebar').classList.remove("open");
  window.scrollTo({ top: 0, behavior: "smooth" });
  Object.values(state.charts).forEach((chart) => chart.resize());
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
    renderDashboard();
    state.page = 1;
    await loadPapers();
    setLoading(false);
  } catch (error) {
    showError(error);
  }
}

function populateConferenceSelect() {
  const select = $("#conference-select");
  const options = [`<option value="">${escapeHtml(t("allConferences"))}</option>`];
  state.dashboard.filters.conferences.forEach((conference) => {
    options.push(`<option value="${escapeHtml(conference)}">${escapeHtml(conference)}</option>`);
  });
  select.innerHTML = options.join("");
  select.value = state.conference;
}

function renderDashboard() {
  const { overview, topics, conference_counts: conferences, decision_counts: decisions, manifest } = state.dashboard;
  $("#metric-papers").textContent = overview.paper_count.toLocaleString();
  $("#metric-conferences").textContent = overview.conference_count.toLocaleString();
  $("#metric-topics").textContent = overview.topic_count.toLocaleString();
  $("#metric-rated").textContent = overview.rated_paper_count.toLocaleString();
  $("#scope-note").textContent = manifest.scope_note?.[state.language] || t("scopeNote");
  renderCharts(topics, conferences, decisions);
  renderTopicsTable(topics);
  populatePaperFilters();
  renderProvenance(manifest);
}

function chartTextStyle() {
  return { fontFamily: 'Inter, "Noto Sans SC", "Microsoft YaHei", sans-serif', color: "#687583" };
}

function prepareChart(id) {
  if (!state.charts[id]) state.charts[id] = echarts.init(document.getElementById(id));
  return state.charts[id];
}

function renderCharts(topics, conferences, decisions) {
  const topicRows = topics.slice(0, 12).reverse();
  prepareChart("topics-chart").setOption({
    animationDuration: 450,
    textStyle: chartTextStyle(),
    grid: { left: 26, right: 36, top: 18, bottom: 18, containLabel: true },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    xAxis: { type: "value", min: 0, splitLine: { lineStyle: { color: "#edf1f4" } } },
    yAxis: { type: "category", data: topicRows.map((row) => row.topic_name), axisLabel: { width: 280, overflow: "truncate" }, axisTick: { show: false } },
    series: [{ type: "bar", data: topicRows.map((row) => row.paper_count), barWidth: 18, itemStyle: { color: "#3b79a8", borderRadius: [0, 5, 5, 0] }, label: { show: true, position: "right", color: "#17212b" } }],
  });

  prepareChart("conference-chart").setOption({
    animationDuration: 450,
    textStyle: chartTextStyle(),
    grid: { left: 20, right: 18, top: 20, bottom: 34, containLabel: true },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    xAxis: { type: "category", data: conferences.map((row) => row.conference), axisTick: { show: false } },
    yAxis: { type: "value", min: 0, splitLine: { lineStyle: { color: "#edf1f4" } } },
    series: [{ type: "bar", data: conferences.map((row) => row.paper_count), barMaxWidth: 46, itemStyle: { color: "#c6943e", borderRadius: [5, 5, 0, 0] }, label: { show: true, position: "top", color: "#17212b" } }],
  });

  const decisionRows = decisions.slice(0, 8).reverse();
  prepareChart("decision-chart").setOption({
    animationDuration: 450,
    textStyle: chartTextStyle(),
    grid: { left: 18, right: 28, top: 20, bottom: 24, containLabel: true },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
    xAxis: { type: "value", min: 0, splitLine: { lineStyle: { color: "#edf1f4" } } },
    yAxis: { type: "category", data: decisionRows.map((row) => row.decision), axisLabel: { width: 150, overflow: "truncate" }, axisTick: { show: false } },
    series: [{ type: "bar", data: decisionRows.map((row) => row.paper_count), barWidth: 16, itemStyle: { color: "#6d7c4c", borderRadius: [0, 5, 5, 0] }, label: { show: true, position: "right", color: "#17212b" } }],
  });
}

function renderTopicsTable(topics) {
  $("#topics-table-body").innerHTML = topics.map((row, index) => {
    const distribution = Object.entries(row.conferences)
      .sort((a, b) => b[1] - a[1])
      .map(([name, count]) => `<span class="chip">${escapeHtml(name)} ${count}</span>`)
      .join("");
    return `<tr>
      <td>${index + 1}</td>
      <td><strong>${escapeHtml(row.topic_name)}</strong></td>
      <td class="topic-count">${row.paper_count.toLocaleString()}</td>
      <td><div class="conference-chips">${distribution}</div></td>
      <td><button class="link-button topic-paper-link" data-topic="${escapeHtml(row.topic_name)}">${escapeHtml(t("viewPapers"))}</button></td>
    </tr>`;
  }).join("");
  $$('.topic-paper-link').forEach((button) => button.addEventListener("click", () => {
    $("#topic-filter").value = button.dataset.topic;
    state.page = 1;
    showSection("papers");
    loadPapers();
  }));
}

function populatePaperFilters() {
  const topicSelect = $("#topic-filter");
  const currentTopic = topicSelect.value;
  topicSelect.innerHTML = `<option value="">${escapeHtml(t("allTopics"))}</option>` +
    state.dashboard.filters.topics.map((topic) => `<option value="${escapeHtml(topic)}">${escapeHtml(topic)}</option>`).join("");
  if ([...topicSelect.options].some((option) => option.value === currentTopic)) topicSelect.value = currentTopic;

  const decisionSelect = $("#decision-filter");
  const currentDecision = decisionSelect.value;
  decisionSelect.innerHTML = `<option value="">${escapeHtml(t("allDecisions"))}</option>` +
    state.dashboard.filters.decisions.map((decision) => `<option value="${escapeHtml(decision)}">${escapeHtml(decision)}</option>`).join("");
  if ([...decisionSelect.options].some((option) => option.value === currentDecision)) decisionSelect.value = currentDecision;
}

async function loadPapers() {
  if (!state.runId) return;
  const params = new URLSearchParams({ page: state.page, page_size: state.pageSize, sort: $("#paper-sort").value });
  if (state.conference) params.set("conference", state.conference);
  if ($("#topic-filter").value) params.set("topic", $("#topic-filter").value);
  if ($("#decision-filter").value) params.set("decision", $("#decision-filter").value);
  if ($("#paper-search").value.trim()) params.set("q", $("#paper-search").value.trim());
  try {
    const payload = await fetchJson(`/api/runs/${encodeURIComponent(state.runId)}/papers?${params}`);
    renderPapers(payload);
  } catch (error) {
    showError(error);
  }
}

function renderPapers(payload) {
  $("#paper-total").textContent = t("paperResults", { count: payload.total.toLocaleString() });
  $("#paper-list").innerHTML = payload.items.length ? payload.items.map((paper) => `
    <article class="paper-card">
      <div class="paper-meta">
        <span class="chip">${escapeHtml(paper.conference)} ${escapeHtml(paper.year)}</span>
        <span class="chip">${escapeHtml(paper.topic_name)}</span>
        <span class="chip">${escapeHtml(paper.decision)}</span>
      </div>
      <h3>${escapeHtml(paper.title)}</h3>
      <p>${escapeHtml((paper.abstract || t("noAbstract")).slice(0, 280))}${paper.abstract?.length > 280 ? "…" : ""}</p>
      <div class="paper-card-footer">
        <span class="authors">${escapeHtml((paper.authors || []).join(", "))}</span>
        <button class="link-button paper-detail-button" data-paper-id="${escapeHtml(paper.id)}">${escapeHtml(t("details"))}</button>
      </div>
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
      <div class="paper-meta">
        <span class="chip">${escapeHtml(paper.conference)} ${escapeHtml(paper.year)}</span>
        <span class="chip">${escapeHtml(paper.topic_name)}</span>
        <span class="chip">${escapeHtml(paper.decision)}</span>
      </div>
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

function renderProvenance(manifest) {
  $("#run-details").innerHTML = [
    [t("generatedAt"), new Date(manifest.generated_at).toLocaleString(state.language)],
    [t("sampleSeed"), manifest.sample_seed ?? t("unknown")],
    [t("sampleSize"), manifest.sample_size_per_conference ?? t("unknown")],
    [t("topicModel"), manifest.topic_model ?? t("unknown")],
  ].map(([label, value]) => `<div class="provenance-card"><span>${escapeHtml(label)}</span><strong>${escapeHtml(value)}</strong><small>${escapeHtml(manifest.title)}</small></div>`).join("");
  $("#sources-table-body").innerHTML = manifest.sources.map((source) => `<tr>
    <td><strong>${escapeHtml(source.conference)}</strong></td>
    <td><a href="${escapeHtml(safeUrl(source.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.label)}</a></td>
    <td>${Number(source.paper_count).toLocaleString()}</td>
    <td>${escapeHtml(source.scope || t("acceptedSample"))}</td>
  </tr>`).join("");
}

function rerenderLanguageDependentContent() {
  applyTranslations();
  if (state.dashboard) {
    populateConferenceSelect();
    renderDashboard();
    loadPapers();
  }
}

function bindEvents() {
  $$('.nav-item').forEach((button) => button.addEventListener("click", () => showSection(button.dataset.section)));
  $$('.language-switch button').forEach((button) => button.addEventListener("click", () => {
    state.language = button.dataset.lang;
    localStorage.setItem("ai-paper-language", state.language);
    rerenderLanguageDependentContent();
  }));
  $("#run-select").addEventListener("change", (event) => {
    state.runId = event.target.value;
    state.conference = "";
    loadDashboard();
  });
  $("#conference-select").addEventListener("change", (event) => {
    state.conference = event.target.value;
    loadDashboard();
  });
  $("#paper-filters").addEventListener("submit", (event) => {
    event.preventDefault();
    state.page = 1;
    loadPapers();
  });
  $("#previous-page").addEventListener("click", () => { state.page -= 1; loadPapers(); });
  $("#next-page").addEventListener("click", () => { state.page += 1; loadPapers(); });
  $("#dialog-close").addEventListener("click", () => $("#paper-dialog").close());
  $("#paper-dialog").addEventListener("click", (event) => {
    if (event.target === $("#paper-dialog")) $("#paper-dialog").close();
  });
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
