"use strict";

const translations = {
  "zh-CN": {
    brandSubtitle: "前沿选题雷达", navOpportunities: "研究机会", navTopics: "聚类证据",
    navPapers: "论文浏览", navUpdates: "论文增量", navLearning: "学习与复现", navData: "方法与数据", navAbout: "关于", localReadOnly: "本地研究工作台",
    dashboardEyebrow: "FRONTIER OPPORTUNITY RADAR", opportunitiesTitle: "哪些方向更适合写论文？",
    topicsTitle: "聚类证据", papersTitle: "论文证据", updatesTitle: "论文增量", learningTitle: "学习与复现", dataTitle: "方法与数据", aboutPageTitle: "关于平台",
    updatesEyebrow: "PAPER INGESTION", updatesHeading: "从公开网址拉取论文增量", updatesIntro: "输入论文集页面或 JSON 地址；系统解析、标准化并去重。拉取不会自动调用付费 AI。",
    newPaperSource: "新增论文来源", sourceUrl: "公开网址", sourceConference: "会议", sourceYear: "年份", sourceParser: "页面类型", parserAuto: "自动识别",
    downloadPdfs: "同时下载公开 PDF（较慢）", startPull: "开始拉取", pullSafety: "仅允许公网 HTTP/HTTPS 地址；本地和内网地址会被拒绝。", jobProgress: "任务进度", pullResult: "本次拉取结果", noPullYet: "尚未开始拉取。", savedSources: "已保存来源", localPapers: "本地论文", pullAgain: "再次拉取", noSavedSources: "还没有保存的来源。",
    directionUpdateHeading: "分析未归类论文与新方向候选", directionUpdateIntro: "这是独立的 AI 任务；只有点击后才运行。结果保存为草稿，不会自动修改正式 13 个方向。", analysisLimit: "本次最多分析", analyseNewPapers: "用 AI 分析新论文", noDirectionUpdate: "尚未运行方向更新。", mappedExisting: "映射到现有方向", candidatePapers: "候选论文", noPendingPapers: "没有等待分析的新论文", draftCandidate: "候选方向草稿",
    learningEyebrow: "LEARN → REPRODUCE → RESEARCH", learningHeading: "把前沿方向变成可执行的学习与复现路径", learningIntro: "先圈定必须掌握的知识、前置缺口和学习边界，再把知识地图投影成 7/30/90 天安排。",
    planSettings: "学习路线设置", chooseDirection: "前沿方向", duration: "时间投影", weeklyHours: "每周小时", experience: "当前基础", zeroFoundation: "零基础", beginner: "入门", intermediate: "中等", advanced: "进阶", computeProfile: "算力条件", cpuOnly: "纯 CPU", singleGpu: "单卡或 CPU", multiGpu: "多卡", cloudFlexible: "弹性云资源", generatePlan: "生成知识路线", mockHint: "学习周期只影响节奏，不改变必须掌握的知识边界。默认 mock 模式不产生费用。", noPlanYet: "选择一个方向后生成知识路线。",
    knowledgeCurriculum: "知识课程边界", startingPoint: "起点假设", targetCapability: "最终能力", estimatedHours: "研究就绪约需", minimumHours: "读懂论文约需", availableHours: "所选周期可用", requiredNodes: "必备知识节点", optionalNodes: "可选补充", minimumPath: "先达到：结构化读论文", minimumPathHint: "这不是研究就绪；它只让你有能力开始读锚点论文。", startNow: "现在只做第一关", startNowHint: "先不要展开完整知识图，也不要急着读前沿论文。学完指定小节，亲手完成过关证据。", startResources: "第一关资料", startEvidence: "离开资料前必须做到", deferTopics: "暂时不用学", exitCriteria: "学成标准", gapDiagnosis: "前置缺口诊断（需要时展开）", currentAssumption: "当前假设", targetLevel: "需要补到", diagnosticQuestions: "先自测", masteryMilestones: "按能力关卡推进", milestoneHint: "不要按天数硬赶。只有能独立通过验收，才进入下一关。", gateChecks: "过关证据", commonFailures: "常见假掌握", linkedKnowledge: "本关知识", starterResources: "从这些可靠资料开始", resourceHint: "只学指定章节，达到停止条件就离开资料，转入练习和论文。", recommendedSections: "只学这些章节", stopRule: "停止条件", knowledgeTree: "完整分层知识地图", whyRequired: "为什么必须学", learnThese: "具体学什么", skipForNow: "边界：暂时不用学", masteryChecks: "掌握检查", resourceSearch: "方向资料检索词", prerequisites: "前置节点", planStages: "按时间安排（次要）", calendarProjection: "把知识地图投影成阶段计划", calendarHint: "先确认知识范围；只有需要执行节奏时再展开。", anchorPapers: "锚点论文（第三关使用）", reproductionLadder: "复现阶梯", researchHypotheses: "最小研究假设", researchExit: "复现与研究出口", researchExitHint: "通过论文阅读关卡后再展开，避免现在分散注意力。", deliverable: "交付物", acceptance: "验收标准", markDone: "标记完成", completed: "已完成", required: "必须掌握", paperLiteracy: "论文可读路径", optional: "可选", cloudReady: "云端已配置", mockMode: "Mock 免费测试", cloudMissing: "云端缺少 API Key", jobFailed: "任务失败", jobRunning: "任务执行中", parsedPapers: "解析", newPapers: "新增", duplicatePapers: "重复", rejectedPapers: "拒绝",
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
    navPapers: "Papers", navUpdates: "Paper updates", navLearning: "Learn & reproduce", navData: "Method & data", navAbout: "About", localReadOnly: "Local research workbench",
    dashboardEyebrow: "FRONTIER OPPORTUNITY RADAR", opportunitiesTitle: "Which directions are more practical to publish in?",
    topicsTitle: "Cluster evidence", papersTitle: "Paper evidence", updatesTitle: "Paper updates", learningTitle: "Learn & reproduce", dataTitle: "Method & data", aboutPageTitle: "About",
    updatesEyebrow: "PAPER INGESTION", updatesHeading: "Pull paper updates from a public URL", updatesIntro: "Enter a proceedings page or JSON feed. The system parses, normalizes, and deduplicates without invoking paid AI.",
    newPaperSource: "Add paper source", sourceUrl: "Public URL", sourceConference: "Conference", sourceYear: "Year", sourceParser: "Page type", parserAuto: "Auto-detect",
    downloadPdfs: "Also download public PDFs (slower)", startPull: "Start pull", pullSafety: "Only public HTTP/HTTPS URLs are accepted; local and private-network targets are rejected.", jobProgress: "Job progress", pullResult: "Pull result", noPullYet: "No pull has started.", savedSources: "Saved sources", localPapers: "local papers", pullAgain: "Pull again", noSavedSources: "No saved sources yet.",
    directionUpdateHeading: "Analyse unclassified papers and new direction candidates", directionUpdateIntro: "This is a separate AI task and runs only when clicked. Results stay as drafts and never alter the 13 published directions automatically.", analysisLimit: "Maximum papers", analyseNewPapers: "Analyse new papers with AI", noDirectionUpdate: "No direction update has run.", mappedExisting: "Mapped to existing directions", candidatePapers: "Candidate papers", noPendingPapers: "No new papers are waiting for analysis", draftCandidate: "Direction candidate draft",
    learningEyebrow: "LEARN → REPRODUCE → RESEARCH", learningHeading: "Turn a frontier direction into a learning and reproduction path", learningIntro: "First bound required knowledge, prerequisite gaps, and what to defer; only then project the map onto 7/30/90 days.",
    planSettings: "Curriculum settings", chooseDirection: "Frontier direction", duration: "Time projection", weeklyHours: "Hours per week", experience: "Experience", zeroFoundation: "Zero foundation", beginner: "Beginner", intermediate: "Intermediate", advanced: "Advanced", computeProfile: "Compute profile", cpuOnly: "CPU only", singleGpu: "Single GPU or CPU", multiGpu: "Multiple GPUs", cloudFlexible: "Flexible cloud", generatePlan: "Generate knowledge path", mockHint: "Duration changes pacing, not the required knowledge boundary. Mock mode is free by default.", noPlanYet: "Choose a direction and generate a knowledge path.",
    knowledgeCurriculum: "Curriculum boundary", startingPoint: "Starting assumption", targetCapability: "Target capability", estimatedHours: "Research-ready effort", minimumHours: "Paper-literacy effort", availableHours: "Available in selected period", requiredNodes: "Required knowledge nodes", optionalNodes: "Optional additions", minimumPath: "First target: structured paper literacy", minimumPathHint: "This is not research-ready; it only makes you capable of starting the anchor papers.", startNow: "Do only Gate 1 now", startNowHint: "Do not expand the full map or rush into frontier papers yet. Use the prescribed sections, then produce the passing evidence yourself.", startResources: "Gate 1 resources", startEvidence: "Before leaving the resources, you must", deferTopics: "Defer for now", exitCriteria: "Exit criteria", gapDiagnosis: "Prerequisite gap diagnosis (expand if needed)", currentAssumption: "Current assumption", targetLevel: "Target level", diagnosticQuestions: "Self-check first", masteryMilestones: "Advance through capability gates", milestoneHint: "Do not race the calendar. Move on only after passing the checks independently.", gateChecks: "Passing evidence", commonFailures: "False-mastery traps", linkedKnowledge: "Knowledge in this gate", starterResources: "Start with these reviewed resources", resourceHint: "Use only the prescribed sections. Leave the resource as soon as the stop rule passes, then practise and read papers.", recommendedSections: "Use only these sections", stopRule: "Stop rule", knowledgeTree: "Complete layered knowledge map", whyRequired: "Why it is required", learnThese: "What to learn", skipForNow: "Boundary: defer for now", masteryChecks: "Mastery checks", resourceSearch: "Direction-resource search terms", prerequisites: "Prerequisite nodes", planStages: "Calendar projection (secondary)", calendarProjection: "Project the knowledge map onto stages", calendarHint: "Confirm the knowledge boundary first; expand this only when you need execution pacing.", anchorPapers: "Anchor papers (use at Gate 3)", reproductionLadder: "Reproduction ladder", researchHypotheses: "Minimum research hypotheses", researchExit: "Reproduction and research exit", researchExitHint: "Expand only after passing the paper-reading gate so it does not split your attention now.", deliverable: "Deliverable", acceptance: "Acceptance", markDone: "Mark done", completed: "Completed", required: "Required", paperLiteracy: "Paper-literacy path", optional: "Optional", cloudReady: "Cloud configured", mockMode: "Free mock test", cloudMissing: "Cloud API key missing", jobFailed: "Job failed", jobRunning: "Job running", parsedPapers: "Parsed", newPapers: "New", duplicatePapers: "Duplicates", rejectedPapers: "Rejected",
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
  activeLearningPlan: null,
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

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    ...options,
    headers: { Accept: "application/json", ...(options.body ? { "Content-Type": "application/json" } : {}), ...(options.headers || {}) },
  });
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
    updates: "updatesTitle", learning: "learningTitle", data: "dataTitle", about: "aboutPageTitle",
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
  populateLearningDirections();
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

function populateLearningDirections() {
  const select = $("#learning-direction");
  if (!select || !state.dashboard) return;
  const current = select.value;
  const directions = state.dashboard.opportunities?.directions || [];
  select.innerHTML = directions.map((direction) =>
    `<option value="${escapeHtml(direction.id)}">${escapeHtml(localize(direction.title))}</option>`
  ).join("");
  if ([...select.options].some((option) => option.value === current)) select.value = current;
}

async function pollJob(jobId, onUpdate) {
  for (let attempt = 0; attempt < 180; attempt += 1) {
    const job = await fetchJson(`/api/jobs/${encodeURIComponent(jobId)}`);
    onUpdate(job);
    if (["completed", "failed", "cancelled"].includes(job.status)) return job;
    await new Promise((resolve) => setTimeout(resolve, 800));
  }
  throw new Error("Job did not finish within the browser polling window.");
}

function renderPullJob(job) {
  const target = $("#paper-pull-status");
  if (job.status === "failed") {
    target.innerHTML = `<div class="job-error"><strong>${escapeHtml(t("jobFailed"))}</strong><p>${escapeHtml(job.error?.message || "Unknown error")}</p></div>`;
    return;
  }
  if (job.status !== "completed") {
    const percent = job.progress_total ? Math.round(job.progress_current / job.progress_total * 100) : 0;
    target.innerHTML = `<div class="job-status"><strong>${escapeHtml(t("jobRunning"))}: ${escapeHtml(job.stage)}</strong><div class="progress-track"><span style="width:${percent}%"></span></div><small>${job.progress_current}/${job.progress_total}</small></div>`;
    return;
  }
  const result = job.result;
  target.innerHTML = `<div class="result-metrics">
    <div><strong>${result.parsed}</strong><span>${escapeHtml(t("parsedPapers"))}</span></div>
    <div><strong>${result.new}</strong><span>${escapeHtml(t("newPapers"))}</span></div>
    <div><strong>${result.duplicate}</strong><span>${escapeHtml(t("duplicatePapers"))}</span></div>
    <div><strong>${result.rejected}</strong><span>${escapeHtml(t("rejectedPapers"))}</span></div>
  </div>`;
}

async function submitPaperPull(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const created = await fetchJson("/api/paper-pulls", {
      method: "POST",
      body: JSON.stringify({
        url: $("#source-url").value.trim(),
        conference: $("#source-conference").value.trim(),
        year: Number($("#source-year").value),
        parser: $("#source-parser").value,
        download_pdf: $("#source-download-pdf").checked,
        remember_source: true,
      }),
    });
    await pollJob(created.job_id, renderPullJob);
    await loadWorkbenchStatus();
  } catch (error) {
    renderPullJob({ status: "failed", error: { message: error.message } });
  } finally {
    button.disabled = false;
  }
}

async function pullSavedSource(sourceId, button) {
  button.disabled = true;
  try {
    const created = await fetchJson(`/api/paper-sources/${encodeURIComponent(sourceId)}/pull`, { method: "POST" });
    showSection("updates");
    await pollJob(created.job_id, renderPullJob);
    await loadWorkbenchStatus();
  } catch (error) {
    renderPullJob({ status: "failed", error: { message: error.message } });
  } finally {
    button.disabled = false;
  }
}

async function loadWorkbenchStatus() {
  const [sourcePayload, paperPayload, cloud, updates] = await Promise.all([
    fetchJson("/api/paper-sources"), fetchJson("/api/local/papers?limit=1"), fetchJson("/api/cloud/status"), fetchJson("/api/direction-updates?limit=1"),
  ]);
  $("#local-paper-count").textContent = `${paperPayload.count.toLocaleString()} ${t("localPapers")}`;
  $("#cloud-status").textContent = cloud.provider === "mock" ? t("mockMode") : (cloud.configured ? t("cloudReady") : t("cloudMissing"));
  $("#cloud-status").classList.toggle("warning-badge", !cloud.configured);
  const target = $("#saved-sources");
  target.innerHTML = sourcePayload.items.length ? sourcePayload.items.map((source) => `
    <div class="saved-source-row">
      <div><strong>${escapeHtml(source.conference)} ${source.year}</strong><a href="${escapeHtml(safeUrl(source.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(source.url)}</a><small>${escapeHtml(source.parser_type)} · ${escapeHtml(source.last_pulled_at || "—")}</small></div>
      <button class="secondary-button saved-source-pull" data-source-id="${escapeHtml(source.id)}">${escapeHtml(t("pullAgain"))}</button>
    </div>`).join("") : `<div class="empty-state">${escapeHtml(t("noSavedSources"))}</div>`;
  $$('.saved-source-pull').forEach((button) => button.addEventListener("click", () => pullSavedSource(button.dataset.sourceId, button)));
  if (updates.items.length) renderDirectionArtifact(updates.items[0].artifact);
}

function renderDirectionArtifact(artifact) {
  const mapped = artifact.assignments.filter((item) => item.direction_id).length;
  const candidates = artifact.candidates || [];
  $("#direction-update-status").innerHTML = `<p class="direction-synthesis">${escapeHtml(artifact.synthesis)}</p>
    <div class="result-metrics direction-result-metrics"><div><strong>${mapped}</strong><span>${escapeHtml(t("mappedExisting"))}</span></div><div><strong>${artifact.assignments.length - mapped}</strong><span>${escapeHtml(t("candidatePapers"))}</span></div></div>
    <div class="candidate-list">${candidates.map((candidate) => `<article><span class="panel-kicker">${escapeHtml(t("draftCandidate"))}</span><h4>${escapeHtml(candidate.title)}</h4><p>${escapeHtml(candidate.summary)}</p><strong>${escapeHtml(candidate.difference_from_existing)}</strong><small>${escapeHtml(candidate.recommended_action)}</small><div class="conference-chips">${candidate.evidence_paper_ids.map((id) => `<span class="chip">${escapeHtml(id)}</span>`).join("")}</div></article>`).join("")}</div>`;
}

function renderDirectionJob(job) {
  const target = $("#direction-update-status");
  if (job.status === "failed") {
    target.innerHTML = `<div class="job-error"><strong>${escapeHtml(t("jobFailed"))}</strong><p>${escapeHtml(job.error?.message || "Unknown error")}</p></div>`;
    return;
  }
  if (job.status !== "completed") {
    const percent = job.progress_total ? Math.round(job.progress_current / job.progress_total * 100) : 0;
    target.innerHTML = `<div class="job-status"><strong>${escapeHtml(t("jobRunning"))}: ${escapeHtml(job.stage)}</strong><div class="progress-track"><span style="width:${percent}%"></span></div><small>${job.progress_current}/${job.progress_total}</small></div>`;
    return;
  }
  if (!job.result.update_id) {
    target.innerHTML = `<div class="empty-state">${escapeHtml(t("noPendingPapers"))}</div>`;
    return;
  }
  renderDirectionArtifact({
    run_id: state.runId,
    assignments: job.result.assignments,
    candidates: job.result.candidates,
    synthesis: job.result.synthesis,
  });
}

async function submitDirectionUpdate(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const created = await fetchJson("/api/direction-updates", {
      method: "POST",
      body: JSON.stringify({
        run_id: state.runId,
        paper_limit: Number($("#direction-paper-limit").value),
        language: state.language,
      }),
    });
    await pollJob(created.job_id, renderDirectionJob);
  } catch (error) {
    renderDirectionJob({ status: "failed", error: { message: error.message } });
  } finally {
    button.disabled = false;
  }
}

function renderLearningJob(job) {
  const target = $("#learning-plan-output");
  if (job.status === "failed") {
    target.innerHTML = `<div class="job-error"><strong>${escapeHtml(t("jobFailed"))}</strong><p>${escapeHtml(job.error?.message || "Unknown error")}</p></div>`;
    return;
  }
  if (job.status !== "completed") {
    const percent = job.progress_total ? Math.round(job.progress_current / job.progress_total * 100) : 0;
    target.innerHTML = `<div class="job-status"><strong>${escapeHtml(t("jobRunning"))}: ${escapeHtml(job.stage)}</strong><div class="progress-track"><span style="width:${percent}%"></span></div><small>${job.progress_current}/${job.progress_total}</small></div>`;
  }
}

async function submitLearningPlan(event) {
  event.preventDefault();
  const button = event.currentTarget.querySelector('button[type="submit"]');
  button.disabled = true;
  try {
    const created = await fetchJson("/api/learning/plans", {
      method: "POST",
      body: JSON.stringify({
        run_id: state.runId,
        direction_id: $("#learning-direction").value,
        duration_days: Number($("#learning-duration").value),
        language: state.language,
        experience_level: $("#learning-experience").value,
        weekly_hours: Number($("#learning-hours").value),
        compute_profile: $("#learning-compute").value,
      }),
    });
    const job = await pollJob(created.job_id, renderLearningJob);
    if (job.status === "completed") {
      state.activeLearningPlan = await fetchJson(`/api/learning/plans/${encodeURIComponent(job.result.plan_id)}`);
      renderLearningPlan(state.activeLearningPlan);
    }
  } catch (error) {
    renderLearningJob({ status: "failed", error: { message: error.message } });
  } finally {
    button.disabled = false;
  }
}

function renderLearningPlan(plan) {
  const artifact = plan.artifact;
  const progress = Object.fromEntries((plan.progress || []).map((item) => [item.task_id, item]));
  const scope = artifact.knowledge_scope;
  const requiredIds = new Set(scope.must_learn_node_ids);
  const minimumPathIds = new Set(scope.minimum_viable_node_ids);
  const nodeTitles = Object.fromEntries(artifact.knowledge_tree.map((node) => [node.id, node.title]));
  let knowledgeIndex = 0;
  const knowledgeGroups = [...new Set(artifact.knowledge_tree.map((node) => node.category))].map((category) => {
    const categoryNodes = artifact.knowledge_tree.filter((node) => node.category === category);
    return `<section class="knowledge-category"><header><span>${escapeHtml(category)}</span><strong>${categoryNodes.length}</strong></header><div class="knowledge-node-list">${categoryNodes.map((node) => {
      const index = knowledgeIndex++;
      const isRequired = requiredIds.has(node.id);
      const isMinimumPath = minimumPathIds.has(node.id);
      const prerequisites = node.prerequisites.map((id) => `<span class="dependency-chip">${escapeHtml(nodeTitles[id] || id)}</span>`).join("");
      const resourceQueries = node.resource_queries.map((query) => `<span class="search-query">${escapeHtml(query)}</span>`).join("");
      return `<details class="knowledge-node ${isRequired ? "required-node" : "optional-node"} ${isMinimumPath ? "minimum-path-node" : ""}" ${index === 0 ? "open" : ""}>
        <summary><span class="knowledge-sequence">${String(index + 1).padStart(2, "0")}</span><div><strong>${escapeHtml(node.title)}</strong><small>${escapeHtml(node.depth)} · ${node.estimated_hours}h</small></div><span class="knowledge-status">${escapeHtml(t(isMinimumPath ? "paperLiteracy" : isRequired ? "required" : "optional"))}</span></summary>
        <div class="knowledge-node-body"><p class="knowledge-reason"><strong>${escapeHtml(t("whyRequired"))}</strong>${escapeHtml(node.why_required)}</p>
          <div class="knowledge-detail-grid">
            <section><h5>${escapeHtml(t("learnThese"))}</h5>${listMarkup(node.what_to_learn)}</section>
            <section><h5>${escapeHtml(t("masteryChecks"))}</h5>${listMarkup(node.mastery_checks)}</section>
            <section><h5>${escapeHtml(t("skipForNow"))}</h5>${listMarkup(node.not_required)}</section>
            <section><h5>${escapeHtml(t("resourceSearch"))}</h5><div class="search-query-list">${resourceQueries}</div></section>
          </div>
          ${prerequisites ? `<div class="knowledge-dependencies"><strong>${escapeHtml(t("prerequisites"))}</strong>${prerequisites}</div>` : ""}
        </div>
      </details>`;
    }).join("")}</div></section>`;
  }).join("");
  const gaps = artifact.gap_diagnosis.map((gap) => `<article class="gap-card"><h4>${escapeHtml(gap.area)}</h4><dl><div><dt>${escapeHtml(t("currentAssumption"))}</dt><dd>${escapeHtml(gap.current_assumption)}</dd></div><div><dt>${escapeHtml(t("targetLevel"))}</dt><dd>${escapeHtml(gap.target_level)}</dd></div></dl><strong>${escapeHtml(t("diagnosticQuestions"))}</strong>${listMarkup(gap.diagnostic_questions)}<div class="gap-bridges">${gap.bridge_node_ids.map((id) => `<span>${escapeHtml(nodeTitles[id] || id)}</span>`).join("")}</div></article>`).join("");
  const minimumPath = scope.minimum_viable_node_ids.map((id, index) => `<span><b>${index + 1}</b>${escapeHtml(nodeTitles[id] || id)}</span>`).join("");
  const milestones = artifact.mastery_milestones.map((milestone, index) => `<article class="mastery-milestone">
    <header><span>${String(index + 1).padStart(2, "0")}</span><div><h4>${escapeHtml(milestone.title)}</h4><p>${escapeHtml(milestone.capability)}</p></div><strong>${milestone.estimated_hours}h</strong></header>
    <div class="milestone-nodes"><b>${escapeHtml(t("linkedKnowledge"))}</b>${milestone.node_ids.map((id) => `<span>${escapeHtml(nodeTitles[id] || id)}</span>`).join("")}</div>
    <div class="milestone-evidence"><section><h5>${escapeHtml(t("gateChecks"))}</h5>${listMarkup(milestone.gate_checks)}</section><section><h5>${escapeHtml(t("commonFailures"))}</h5>${listMarkup(milestone.common_failures)}</section></div>
  </article>`).join("");
  const resources = artifact.starter_resources.map((resource, index) => `<article class="starter-resource">
    <header><span>${String(index + 1).padStart(2, "0")}</span><div><a href="${escapeHtml(safeUrl(resource.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(resource.title)}</a><small>${escapeHtml(resource.provider)} · ${escapeHtml(resource.resource_type)} · ${escapeHtml(resource.language)}</small></div></header>
    <p>${escapeHtml(resource.purpose)}</p>
    <section><h5>${escapeHtml(t("recommendedSections"))}</h5>${listMarkup(resource.recommended_sections)}</section>
    <div class="resource-stop"><strong>${escapeHtml(t("stopRule"))}</strong><span>${escapeHtml(resource.stop_rule)}</span></div>
  </article>`).join("");
  const firstMilestone = artifact.mastery_milestones[0];
  const firstMilestoneNodeIds = new Set(firstMilestone.node_ids);
  const firstResources = artifact.starter_resources
    .filter((resource) => resource.node_ids.some((id) => firstMilestoneNodeIds.has(id)))
    .slice(0, 3)
    .map((resource) => `<li><a href="${escapeHtml(safeUrl(resource.url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(resource.title)}</a><span>${escapeHtml(resource.recommended_sections.join(" · "))}</span></li>`)
    .join("");
  const stages = artifact.stages.map((stage) => `<article class="plan-stage"><header><span>DAY ${stage.day_start}—${stage.day_end}</span><h4>${escapeHtml(stage.title)}</h4></header>${stage.tasks.map((task) => {
    const done = progress[task.id]?.status === "done";
    return `<div class="plan-task ${done ? "task-done" : ""}"><h5>${escapeHtml(task.title)}</h5>${listMarkup(task.actions)}<p><strong>${escapeHtml(t("deliverable"))}:</strong> ${escapeHtml(task.deliverable)}</p><p><strong>${escapeHtml(t("acceptance"))}:</strong> ${escapeHtml(task.acceptance)}</p><button class="secondary-button plan-task-toggle" data-task-id="${escapeHtml(task.id)}" data-done="${done}">${escapeHtml(done ? t("completed") : t("markDone"))}</button></div>`;
  }).join("")}</article>`).join("");
  const anchors = artifact.anchor_papers.map((paper) => `<li><span class="chip">${escapeHtml(paper.reproduction_level)}</span><a href="${escapeHtml(safeUrl(paper.source_url))}" target="_blank" rel="noopener noreferrer">${escapeHtml(paper.title)}</a><p>${escapeHtml(paper.reason)}</p></li>`).join("");
  const ladder = artifact.reproduction_ladder.map((level) => `<div><strong>${escapeHtml(level.level)} · ${escapeHtml(level.title)}</strong><p>${escapeHtml(level.goal)}</p><small>${escapeHtml(level.acceptance)}</small></div>`).join("");
  const hypotheses = artifact.research_hypotheses.map((item) => `<article><h4>${escapeHtml(item.question)}</h4><p>${escapeHtml(item.novelty)}</p><strong>${escapeHtml(item.minimum_experiment)}</strong>${listMarkup(item.risks)}</article>`).join("");
  $("#learning-plan-output").innerHTML = `<div class="learning-plan-header"><span class="panel-kicker">${escapeHtml(t("knowledgeCurriculum"))}</span><h2>${escapeHtml(artifact.direction_title)}</h2><p>${escapeHtml(artifact.executive_summary)}</p></div>
    <section class="curriculum-scope">
      <div class="curriculum-goal"><span>${escapeHtml(t("startingPoint"))}</span><p>${escapeHtml(scope.starting_point)}</p><span>${escapeHtml(t("targetCapability"))}</span><strong>${escapeHtml(scope.target_capability)}</strong></div>
      <div class="curriculum-metrics"><div><strong>${scope.minimum_viable_hours}h</strong><span>${escapeHtml(t("minimumHours"))}</span></div><div><strong>${scope.estimated_total_hours}h</strong><span>${escapeHtml(t("estimatedHours"))}</span></div><div><strong>${scope.must_learn_node_ids.length}</strong><span>${escapeHtml(t("requiredNodes"))}</span></div><div class="feasibility-${escapeHtml(scope.feasibility)}"><strong>${scope.available_hours}h</strong><span>${escapeHtml(t("availableHours"))}</span></div></div>
      <p class="projection-note">${escapeHtml(scope.projection_note)}</p>
      <section class="minimum-path"><div><h4>${escapeHtml(t("minimumPath"))}</h4><p>${escapeHtml(t("minimumPathHint"))}</p></div><div class="minimum-path-flow">${minimumPath}</div></section>
      <div class="curriculum-boundaries"><section><h4>${escapeHtml(t("deferTopics"))}</h4>${listMarkup(scope.defer_topics)}</section><section><h4>${escapeHtml(t("exitCriteria"))}</h4>${listMarkup(scope.exit_criteria)}</section></div>
    </section>
    <section class="start-now"><header><span>${escapeHtml(t("startNow"))}</span><strong>${firstMilestone.estimated_hours}h</strong></header><h3>${escapeHtml(firstMilestone.title)}</h3><p>${escapeHtml(t("startNowHint"))}</p><div class="start-now-grid"><section><h4>${escapeHtml(t("startResources"))}</h4><ol>${firstResources}</ol></section><section><h4>${escapeHtml(t("startEvidence"))}</h4>${listMarkup(firstMilestone.gate_checks)}</section></div></section>
    <section class="learning-block"><div class="learning-block-heading"><h3>${escapeHtml(t("masteryMilestones"))}</h3><p>${escapeHtml(t("milestoneHint"))}</p></div><div class="mastery-roadmap">${milestones}</div></section>
    <section class="learning-block"><div class="learning-block-heading"><h3>${escapeHtml(t("starterResources"))}</h3><p>${escapeHtml(t("resourceHint"))}</p></div><div class="starter-resource-grid">${resources}</div></section>
    <section class="learning-block"><h3>${escapeHtml(t("anchorPapers"))}</h3><ol class="anchor-list">${anchors}</ol></section>
    <details class="calendar-projection"><summary><div><strong>${escapeHtml(t("researchExit"))}</strong><span>${escapeHtml(t("researchExitHint"))}</span></div><span>L0—L4</span></summary><div class="deferred-learning-content"><section class="learning-block"><h3>${escapeHtml(t("reproductionLadder"))}</h3><div class="reproduction-ladder">${ladder}</div></section><section class="learning-block"><h3>${escapeHtml(t("researchHypotheses"))}</h3><div class="hypothesis-list">${hypotheses}</div></section></div></details>
    <details class="calendar-projection"><summary><div><strong>${escapeHtml(t("gapDiagnosis"))}</strong><span>${escapeHtml(t("diagnosticQuestions"))}</span></div><span>${artifact.gap_diagnosis.length} GAPS</span></summary><div class="deferred-learning-content"><div class="gap-grid">${gaps}</div></div></details>
    <details class="calendar-projection knowledge-map-projection"><summary><div><strong>${escapeHtml(t("knowledgeTree"))}</strong><span>${escapeHtml(t("minimumPathHint"))}</span></div><span>${artifact.knowledge_tree.length} NODES</span></summary><div class="knowledge-tree">${knowledgeGroups}</div></details>
    <details class="calendar-projection"><summary><div><strong>${escapeHtml(t("calendarProjection"))}</strong><span>${escapeHtml(t("calendarHint"))}</span></div><span>${artifact.duration_days} DAYS</span></summary><div class="plan-stages">${stages}</div></details>`;
  $$('.plan-task-toggle').forEach((button) => button.addEventListener("click", () => toggleLearningTask(plan.id, button.dataset.taskId, button.dataset.done === "true")));
}

async function toggleLearningTask(planId, taskId, isDone) {
  try {
    state.activeLearningPlan = await fetchJson(`/api/learning/plans/${encodeURIComponent(planId)}/tasks/${encodeURIComponent(taskId)}`, {
      method: "PATCH", body: JSON.stringify({ status: isDone ? "todo" : "done", notes: "", actual_hours: null }),
    });
    renderLearningPlan(state.activeLearningPlan);
  } catch (error) {
    showError(error);
  }
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
  $("#paper-pull-form").addEventListener("submit", submitPaperPull);
  $("#direction-update-form").addEventListener("submit", submitDirectionUpdate);
  $("#learning-plan-form").addEventListener("submit", submitLearningPlan);
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
    await Promise.all([loadRuns(), loadWorkbenchStatus()]);
  } catch (error) {
    showError(error);
  }
});
