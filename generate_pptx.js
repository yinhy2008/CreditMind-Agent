/**
 * CreditMind 路演 PPT 生成脚本
 * 基于 07-pitch-deck-v0.1.md 的 13 页大纲
 * 配色：Ocean Gradient（深蓝 065A82 + 青色 1C7293 + 午夜蓝 21295C）
 */
const pptxgen = require("pptxgenjs");
const path = require("path");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 14.3" × 7.5"
pres.author = "尹红艳";
pres.title = "CreditMind · AI 信贷风控大脑";

// 配色
const C = {
  navy: "065A82",      // 主色 深蓝
  teal: "1C7293",      // 次色 青色
  midnight: "21295C",  // 深夜蓝（标题/结尾）
  white: "FFFFFF",
  offWhite: "F8FAFC",
  light: "E2E8F0",
  muted: "64748B",
  dark: "1E293B",
  accent: "14B8A6",    // 薄荷绿强调
  red: "EF4444",       // 高风险
  yellow: "F59E0B",    // 中风险
  green: "10B981",     // 低风险
  gray: "94A3B8",
};

// 字体
const F = { header: "Georgia", body: "Calibri" };

// 辅助：添加页脚
function addFooter(slide, pageNum) {
  slide.addText("CreditMind · AI 信贷风控大脑", {
    x: 0.5, y: 7.0, w: 6, h: 0.3, fontSize: 9, color: C.muted, fontFace: F.body, margin: 0,
  });
  slide.addText(`${pageNum} / 15`, {
    x: 12.3, y: 7.0, w: 0.5, h: 0.3, fontSize: 9, color: C.muted, align: "right", margin: 0,
  });
}

// 辅助：标题栏
function addTitleBar(slide, title, pageNum) {
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0, y: 0, w: 13.3, h: 0.08, fill: { color: C.accent }, line: { type: "none" },
  });
  slide.addText(title, {
    x: 0.6, y: 0.3, w: 12, h: 0.6, fontSize: 28, fontFace: F.header, color: C.midnight, bold: true, margin: 0,
  });
  addFooter(slide, pageNum);
}

// ========== Slide 1: 封面 ==========
let s1 = pres.addSlide();
s1.background = { color: C.midnight };
s1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 0, w: 13.3, h: 0.15, fill: { color: C.accent }, line: { type: "none" },
});
s1.addShape(pres.shapes.RECTANGLE, {
  x: 0, y: 7.35, w: 13.3, h: 0.15, fill: { color: C.accent }, line: { type: "none" },
});
s1.addText("CreditMind", {
  x: 1, y: 1.8, w: 11.3, h: 1.2, fontSize: 60, fontFace: F.header, color: C.white, bold: true, margin: 0,
});
s1.addText("AI 信贷风控大脑", {
  x: 1, y: 3.0, w: 11.3, h: 0.7, fontSize: 32, fontFace: F.header, color: C.accent, margin: 0,
});
s1.addText("让消费贷尽调从 2 小时压缩到 15 分钟，且每个判断都有据可查。", {
  x: 1, y: 4.0, w: 11.3, h: 0.6, fontSize: 18, fontFace: F.body, color: C.light, italic: true, margin: 0,
});
s1.addShape(pres.shapes.LINE, {
  x: 1, y: 5.0, w: 3, h: 0, line: { color: C.accent, width: 2 },
});
s1.addText("尹红艳", {
  x: 1, y: 5.2, w: 6, h: 0.4, fontSize: 18, fontFace: F.body, color: C.white, bold: true, margin: 0,
});
s1.addText("深圳大学南特金融科技学院 · 金融科技与风险控制硕士", {
  x: 1, y: 5.6, w: 8, h: 0.35, fontSize: 13, fontFace: F.body, color: C.light, margin: 0,
});
s1.addText("2026-07-25 · 模块四路演", {
  x: 1, y: 5.95, w: 8, h: 0.35, fontSize: 13, fontFace: F.body, color: C.light, margin: 0,
});

// ========== Slide 2: 一句话定位 ==========
let s2 = pres.addSlide();
s2.background = { color: C.offWhite };
addTitleBar(s2, "一句话定位", 2);
s2.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1.4, w: 11.3, h: 1.6, fill: { color: C.white }, line: { color: C.light, width: 1 },
  shadow: { type: "outer", blur: 8, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
});
s2.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 1.4, w: 0.1, h: 1.6, fill: { color: C.accent }, line: { type: "none" },
});
s2.addText([
  { text: "CreditMind 是面向消费贷/P2P 场景的", options: { fontSize: 18, color: C.dark } },
  { text: "「智能访谈 + 违约预测 + 可解释报告」", options: { fontSize: 18, color: C.navy, bold: true } },
  { text: "一体化 Agent。", options: { fontSize: 18, color: C.dark } },
], { x: 1.3, y: 1.6, w: 10.7, h: 1.2, fontFace: F.body, valign: "middle", margin: 0 });

const items2 = [
  { emoji: "🎯", title: "目标客户", desc: "消费贷/P2P 平台的客户经理与风控初审员" },
  { emoji: "💡", title: "核心价值", desc: "单笔尽调 1-2h → 15min" },
  { emoji: "🔒", title: "合规边界", desc: "不直接放款，只做建议+人审" },
];
items2.forEach((it, i) => {
  const y = 3.4 + i * 1.1;
  s2.addShape(pres.shapes.OVAL, {
    x: 1.2, y: y, w: 0.7, h: 0.7, fill: { color: C.navy }, line: { type: "none" },
  });
  s2.addText(it.emoji, { x: 1.2, y: y, w: 0.7, h: 0.7, fontSize: 24, align: "center", valign: "middle", margin: 0 });
  s2.addText(it.title, { x: 2.1, y: y, w: 3, h: 0.35, fontSize: 16, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
  s2.addText(it.desc, { x: 2.1, y: y + 0.35, w: 9, h: 0.35, fontSize: 14, fontFace: F.body, color: C.muted, margin: 0 });
});

// ========== Slide 3: 痛点 ==========
let s3 = pres.addSlide();
s3.background = { color: C.offWhite };
addTitleBar(s3, "痛点：客户经理的一天", 3);
s3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.3, w: 12.1, h: 1.4, fill: { color: C.white }, line: { color: C.light, width: 1 },
  shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.06 },
});
s3.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.3, w: 0.1, h: 1.4, fill: { color: C.red }, line: { type: "none" },
});
s3.addText('"每天打 20 多个访谈电话，每个 1-2 小时，光访谈就吃掉半天。真正的风控分析没时间做，只能凭经验草草判断。"', {
  x: 0.9, y: 1.4, w: 11.6, h: 1.2, fontSize: 16, fontFace: F.body, color: C.dark, italic: true, valign: "middle", margin: 0,
});

const pains = [
  { title: "单笔访谈 1-2 小时", freq: "每日 20+ 次", level: 5, color: C.red },
  { title: "模型黑盒，拒贷解释不清", freq: "每周 3-5 次", level: 5, color: C.red },
  { title: "新人/老人标准不一致", freq: "持续", level: 4, color: C.yellow },
  { title: "模型跨时间漂移", freq: "季度", level: 4, color: C.yellow },
  { title: "AI 决策合规边界不清", freq: "年度", level: 5, color: C.red },
];
pains.forEach((p, i) => {
  const y = 3.1 + i * 0.72;
  s3.addShape(pres.shapes.RECTANGLE, {
    x: 0.6, y: y, w: 12.1, h: 0.6, fill: { color: i % 2 === 0 ? C.white : C.light }, line: { type: "none" },
  });
  s3.addText(p.title, { x: 0.8, y: y, w: 5, h: 0.6, fontSize: 14, fontFace: F.body, color: C.dark, valign: "middle", margin: 0 });
  s3.addText(p.freq, { x: 6, y: y, w: 3, h: 0.6, fontSize: 13, fontFace: F.body, color: C.muted, valign: "middle", margin: 0 });
  const stars = "★".repeat(p.level) + "☆".repeat(5 - p.level);
  s3.addText(stars, { x: 9.5, y: y, w: 3, h: 0.6, fontSize: 14, color: p.color, valign: "middle", margin: 0 });
});

// ========== Slide 4: 解决方案 ==========
let s4 = pres.addSlide();
s4.background = { color: C.offWhite };
addTitleBar(s4, "解决方案：三层联动", 4);

const layers = [
  { num: "1", title: "Agent 多轮访谈", desc: "自动收集 19 项核心特征", time: "5-10 min", color: C.navy },
  { num: "2", title: "违约预测模型", desc: "IV/WoE+PSI+XGBoost", time: "秒级", color: C.teal },
  { num: "3", title: "尽调报告生成", desc: "Markdown + SHAP Top3", time: "3 min", color: C.midnight },
];
layers.forEach((l, i) => {
  const y = 1.5 + i * 1.5;
  s4.addShape(pres.shapes.RECTANGLE, {
    x: 1.5, y: y, w: 10.3, h: 1.25, fill: { color: C.white }, line: { color: C.light, width: 1 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
  });
  s4.addShape(pres.shapes.RECTANGLE, {
    x: 1.5, y: y, w: 1.0, h: 1.25, fill: { color: l.color }, line: { type: "none" },
  });
  s4.addText(l.num, { x: 1.5, y: y, w: 1.0, h: 1.25, fontSize: 36, fontFace: F.header, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
  s4.addText(l.title, { x: 2.7, y: y + 0.15, w: 6, h: 0.5, fontSize: 20, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
  s4.addText(l.desc, { x: 2.7, y: y + 0.65, w: 6, h: 0.4, fontSize: 14, fontFace: F.body, color: C.muted, margin: 0 });
  s4.addShape(pres.shapes.RECTANGLE, {
    x: 9.5, y: y + 0.3, w: 2.0, h: 0.6, fill: { color: C.offWhite }, line: { type: "none" },
  });
  s4.addText(l.time, { x: 9.5, y: y + 0.3, w: 2.0, h: 0.6, fontSize: 16, fontFace: F.body, color: C.accent, bold: true, align: "center", valign: "middle", margin: 0 });
});

s4.addText("人审仍是必要的 — Agent 只做信息采集和初稿，客户经理做最终复核。", {
  x: 1.5, y: 6.2, w: 10.3, h: 0.5, fontSize: 14, fontFace: F.body, color: C.muted, italic: true, align: "center", margin: 0,
});

// ========== Slide 5: AI 介入点 ==========
let s5 = pres.addSlide();
s5.background = { color: C.offWhite };
addTitleBar(s5, "5 个 AI 介入点", 5);

const points = [
  { num: "1", title: "多轮访谈", ai: "LLM 对话", replace: "客户经理 1-2h 访谈", color: C.navy },
  { num: "2", title: "特征抽取", ai: "NER + function calling", replace: "手工整理 Excel", color: C.teal },
  { num: "3", title: "违约预测", ai: "XGBoost", replace: "经验判断", color: C.midnight },
  { num: "4", title: "SHAP 解释", ai: "TreeExplainer", replace: "数据科学家临时解释", color: C.navy },
  { num: "5", title: "报告生成", ai: "LLM 模板填充", replace: "30min 手写报告", color: C.teal },
];
points.forEach((p, i) => {
  const col = i % 3;
  const row = Math.floor(i / 3);
  const x = 0.6 + col * 4.2;
  const y = 1.5 + row * 2.3;
  s5.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 3.9, h: 2.0, fill: { color: C.white }, line: { color: C.light, width: 1 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
  });
  s5.addShape(pres.shapes.OVAL, {
    x: x + 0.2, y: y + 0.2, w: 0.7, h: 0.7, fill: { color: p.color }, line: { type: "none" },
  });
  s5.addText(p.num, { x: x + 0.2, y: y + 0.2, w: 0.7, h: 0.7, fontSize: 24, fontFace: F.header, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
  s5.addText(p.title, { x: x + 1.0, y: y + 0.25, w: 2.7, h: 0.4, fontSize: 17, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
  s5.addText("AI: " + p.ai, { x: x + 1.0, y: y + 0.7, w: 2.7, h: 0.35, fontSize: 12, fontFace: F.body, color: C.accent, margin: 0 });
  s5.addText("替代: " + p.replace, { x: x + 0.2, y: y + 1.2, w: 3.5, h: 0.6, fontSize: 12, fontFace: F.body, color: C.muted, margin: 0 });
});

s5.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 6.2, w: 12.1, h: 0.55, fill: { color: C.midnight }, line: { type: "none" },
});
s5.addText("🔒 合规红线：AI 不直接放款，不使用 grade/sub_grade 泄露特征", {
  x: 0.6, y: 6.2, w: 12.1, h: 0.55, fontSize: 14, fontFace: F.body, color: C.white, bold: true, align: "center", valign: "middle", margin: 0,
});

// ========== Slide 6: 四类竞品全景 ==========
let s6 = pres.addSlide();
s6.background = { color: C.offWhite };
addTitleBar(s6, "四类竞品全景", 6);
s6.addText("调研前先看四类竞品，确保 CreditMind 的差异化定位站得住脚", {
  x: 0.6, y: 1.0, w: 12, h: 0.4, fontSize: 14, fontFace: F.body, color: C.muted, margin: 0,
});

const cats = [
  { tag: "A", title: "大厂对公尽调 Agent", sub: "看「天花板」", rep: "TRAE / 中电金信 / 云从 / 腾讯云", cap: "面向对公贷，多模态采集(OCR/语音)，依赖大厂基础设施", color: C.navy },
  { tag: "B", title: "海外 AI 信贷风控 Agent", sub: "看产品形态", rep: "Underwrite.ai / Zentis / LendingIQ / digiqt", cap: "承保/尽调/违约预测分层；已有分级决策概念", color: C.teal },
  { tag: "C", title: "开源 LendingClub 违约预测", sub: "看模型层竞品", rep: "navyaneel / shashi-hue", cap: "方法论差异：IV/WoE、PSI、数据泄露防护", color: C.midnight },
  { tag: "D", title: "智能信贷报告 SaaS", sub: "看商业模式", rep: "金锋报 FinDoc / 达观 Agent", cap: "报告自动生成，开箱即用网页版，对公客户经理", color: C.accent },
];
cats.forEach((c, i) => {
  const col = i % 2;
  const row = Math.floor(i / 2);
  const x = 0.6 + col * 6.3;
  const y = 1.6 + row * 2.6;
  s6.addShape(pres.shapes.RECTANGLE, {
    x: x, y: y, w: 6.0, h: 2.4, fill: { color: C.white }, line: { color: C.light, width: 1 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
  });
  s6.addShape(pres.shapes.RECTANGLE, { x: x, y: y, w: 0.12, h: 2.4, fill: { color: c.color }, line: { type: "none" } });
  s6.addShape(pres.shapes.OVAL, { x: x + 0.3, y: y + 0.3, w: 0.7, h: 0.7, fill: { color: c.color }, line: { type: "none" } });
  s6.addText(c.tag, { x: x + 0.3, y: y + 0.3, w: 0.7, h: 0.7, fontSize: 24, fontFace: F.header, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
  s6.addText(c.title, { x: x + 1.2, y: y + 0.32, w: 4.6, h: 0.5, fontSize: 17, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
  s6.addText(c.sub, { x: x + 1.2, y: y + 0.82, w: 4.6, h: 0.3, fontSize: 11, fontFace: F.body, color: C.accent, bold: true, margin: 0 });
  s6.addText("代表：" + c.rep, { x: x + 0.3, y: y + 1.25, w: 5.5, h: 0.4, fontSize: 11, fontFace: F.body, color: C.dark, margin: 0 });
  s6.addText(c.cap, { x: x + 0.3, y: y + 1.65, w: 5.5, h: 0.6, fontSize: 11, fontFace: F.body, color: C.muted, margin: 0 });
});

// ========== Slide 7: 竞品对比实验 ⭐ ==========
let s7 = pres.addSlide();
s7.background = { color: C.offWhite };
addTitleBar(s7, "竞品对比实验 ⭐", 7);
s7.addText("在 LendingClub 15 万条数据上对比三种方法论 · A/B/C AUC、特征数、泄露风险、PSI 稳定性", {
  x: 0.6, y: 1.0, w: 12, h: 0.4, fontSize: 14, fontFace: F.body, color: C.muted, margin: 0,
});

// 对比表
const tableData = [
  [
    { text: "模型", options: { fill: { color: C.midnight }, color: C.white, bold: true, fontSize: 14, align: "center", valign: "middle" } },
    { text: "AUC", options: { fill: { color: C.midnight }, color: C.white, bold: true, fontSize: 14, align: "center", valign: "middle" } },
    { text: "特征数", options: { fill: { color: C.midnight }, color: C.white, bold: true, fontSize: 14, align: "center", valign: "middle" } },
    { text: "数据泄露", options: { fill: { color: C.midnight }, color: C.white, bold: true, fontSize: 14, align: "center", valign: "middle" } },
    { text: "PSI 稳定性", options: { fill: { color: C.midnight }, color: C.white, bold: true, fontSize: 14, align: "center", valign: "middle" } },
  ],
  [
    { text: "A: Leaky Baseline\n(navyaneel/credit-risk-model)", options: { fontSize: 11, align: "left", valign: "middle" } },
    { text: "0.6995", options: { fontSize: 13, align: "center", valign: "middle" } },
    { text: "17", options: { fontSize: 13, align: "center", valign: "middle" } },
    { text: "❌ 是", options: { fontSize: 13, color: C.red, align: "center", valign: "middle", bold: true } },
    { text: "未验证", options: { fontSize: 13, color: C.muted, align: "center", valign: "middle" } },
  ],
  [
    { text: "B: Feature-Heavy\n(shashi-hue/loan-default-risk-system)", options: { fontSize: 11, align: "left", valign: "middle" } },
    { text: "0.7167", options: { fontSize: 13, align: "center", valign: "middle" } },
    { text: "81", options: { fontSize: 13, align: "center", valign: "middle" } },
    { text: "❌ 包含", options: { fontSize: 13, color: C.red, align: "center", valign: "middle", bold: true } },
    { text: "未验证", options: { fontSize: 13, color: C.muted, align: "center", valign: "middle" } },
  ],
  [
    { text: "C: CreditMind\n(本项目)", options: { fontSize: 12, align: "left", valign: "middle", bold: true, color: C.navy, fill: { color: "DBEAFE" } } },
    { text: "0.7093", options: { fontSize: 14, align: "center", valign: "middle", bold: true, color: C.navy, fill: { color: "DBEAFE" } } },
    { text: "19", options: { fontSize: 14, align: "center", valign: "middle", bold: true, color: C.navy, fill: { color: "DBEAFE" } } },
    { text: "✅ 否", options: { fontSize: 14, color: C.green, align: "center", valign: "middle", bold: true, fill: { color: "DBEAFE" } } },
    { text: "✅ 已验证", options: { fontSize: 14, color: C.green, align: "center", valign: "middle", bold: true, fill: { color: "DBEAFE" } } },
  ],
];
s7.addTable(tableData, {
  x: 0.6, y: 1.6, w: 12.1, h: 2.8,
  colW: [4.3, 1.7, 1.5, 2.0, 2.6],
  border: { pt: 1, color: C.light },
  rowH: [0.55, 0.75, 0.75, 0.75],
});

// 插入对比图
const imgPath = path.join(__dirname, "experiments", "results", "comparison_overview.png");
s7.addImage({ path: imgPath, x: 1.5, y: 4.7, w: 10.3, h: 2.2, sizing: { type: "contain", w: 10.3, h: 2.2 } });

// ========== Slide 8: 三大护城河 ==========
let s8 = pres.addSlide();
s8.background = { color: C.offWhite };
addTitleBar(s8, "三大护城河", 8);

const moats = [
  { num: "1", title: "方法论深度", desc: "唯一把「IV/WoE → PSI → 贪心去共线性 → 四套方案」完整工程化的项目", color: C.navy },
  { num: "2", title: "数据泄露防护", desc: "明确识别并排除 grade/sub_grade 目标泄露（navyaneel 直接用了泄露特征，AUC 虚高）", color: C.teal },
  { num: "3", title: "Agent 产品化层", desc: "把静态 Notebook 升级为「对话采集 → 模型推理 → 报告生成」Agent 闭环", color: C.midnight },
];
moats.forEach((m, i) => {
  const y = 1.5 + i * 1.6;
  s8.addShape(pres.shapes.RECTANGLE, {
    x: 1, y: y, w: 11.3, h: 1.35, fill: { color: C.white }, line: { color: C.light, width: 1 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
  });
  s8.addShape(pres.shapes.OVAL, {
    x: 1.3, y: y + 0.3, w: 0.75, h: 0.75, fill: { color: m.color }, line: { type: "none" },
  });
  s8.addText(m.num, { x: 1.3, y: y + 0.3, w: 0.75, h: 0.75, fontSize: 28, fontFace: F.header, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
  s8.addText(m.title, { x: 2.3, y: y + 0.2, w: 9.5, h: 0.5, fontSize: 20, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
  s8.addText(m.desc, { x: 2.3, y: y + 0.7, w: 9.5, h: 0.55, fontSize: 14, fontFace: F.body, color: C.muted, margin: 0 });
});

// ========== Slide 9: 违约预测模型深度 ==========
let s9 = pres.addSlide();
s9.background = { color: C.offWhite };
addTitleBar(s9, "违约预测模型深度", 9);

// 左半：方法论 + 模型架构
s9.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 1.2, w: 6.2, h: 4.5, fill: { color: C.white }, line: { color: C.light, width: 1 },
  shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
});
s9.addShape(pres.shapes.RECTANGLE, { x: 0.5, y: 1.2, w: 0.1, h: 4.5, fill: { color: C.accent }, line: { type: "none" } });
s9.addText("方法论", { x: 0.75, y: 1.35, w: 5.9, h: 0.4, fontSize: 18, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });

const methods = [
  { tag: "①", title: "IV 信息价值筛选", desc: "IV≥0.02，剔除预测力弱或无业务意义特征" },
  { tag: "②", title: "WoE 证据权重分箱", desc: "连续/类别变量转单调可分箱，提升稳定性" },
  { tag: "③", title: "PSI 群体稳定性", desc: "PSI<0.25，本项目 28 个 IV 合格特征全部通过" },
  { tag: "④", title: "贪心去共线性", desc: "|r|≥0.7 时只保留一个，最终精选 19 特征" },
  { tag: "⑤", title: "数据泄露防护", desc: "明确排除 grade / sub_grade 等放款后字段" },
];
methods.forEach((m, i) => {
  const y = 1.85 + i * 0.78;
  s9.addText(m.tag, { x: 0.8, y: y, w: 0.5, h: 0.6, fontSize: 22, fontFace: F.header, color: C.accent, bold: true, margin: 0 });
  s9.addText(m.title, { x: 1.4, y: y, w: 5.2, h: 0.3, fontSize: 14, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
  s9.addText(m.desc, { x: 1.4, y: y + 0.3, w: 5.2, h: 0.45, fontSize: 11, fontFace: F.body, color: C.muted, margin: 0 });
});

// 左下：相对 V1/V2 的改进（迁移 DianJin 数据处理 skill）
s9.addShape(pres.shapes.RECTANGLE, {
  x: 0.5, y: 5.85, w: 6.2, h: 0.95, fill: { color: "F0F9FF" }, line: { color: C.accent, width: 1 },
});
s9.addText("相对原模型的改进（迁移 DianJin skill）", { x: 0.65, y: 5.9, w: 6.0, h: 0.25, fontSize: 11, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
s9.addText([
  { text: "V1.ipynb ", options: { fontSize: 9, color: C.muted } },
  { text: "相关性排序 → 贪心去共线\n", options: { fontSize: 9, color: C.dark } },
  { text: "V2.md     ", options: { fontSize: 9, color: C.muted } },
  { text: "IV/WoE+PSI+四套方案+SafetyGate\n", options: { fontSize: 9, color: C.dark } },
  { text: "CreditMind", options: { fontSize: 9, color: C.accent, bold: true } },
  { text: " 工程化精选 19 特征 + Agent 推理 + SHAP 双解释 + 泄露排除", options: { fontSize: 9, color: C.dark } },
], { x: 0.65, y: 6.15, w: 6.0, h: 0.6, fontFace: F.body, valign: "top", margin: 0 });

// 右半上：模型架构
s9.addShape(pres.shapes.RECTANGLE, {
  x: 7.0, y: 1.2, w: 5.8, h: 2.5, fill: { color: C.white }, line: { color: C.light, width: 1 },
  shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
});
s9.addShape(pres.shapes.RECTANGLE, { x: 7.0, y: 1.2, w: 0.1, h: 2.5, fill: { color: C.navy }, line: { type: "none" } });
s9.addText("模型架构", { x: 7.25, y: 1.35, w: 5.5, h: 0.4, fontSize: 18, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
s9.addText([
  { text: "算法    ", options: { fontSize: 12, color: C.muted } },
  { text: "XGBoost 梯度提升树\n", options: { fontSize: 13, color: C.dark, bold: true } },
  { text: "特征数  ", options: { fontSize: 12, color: C.muted } },
  { text: "19（IV≥0.02 + PSI<0.25）\n", options: { fontSize: 13, color: C.dark, bold: true } },
  { text: "训练集  ", options: { fontSize: 12, color: C.muted } },
  { text: "120,000 行（80%）/ 测试 30,000 行（20%）\n", options: { fontSize: 13, color: C.dark, bold: true } },
  { text: "违约率  ", options: { fontSize: 12, color: C.muted } },
  { text: "14.81%（接近真实市场分布）\n", options: { fontSize: 13, color: C.dark, bold: true } },
  { text: "AUC     ", options: { fontSize: 12, color: C.muted } },
  { text: "0.7093（与 81 特征 baseline 相当）\n", options: { fontSize: 13, color: C.accent, bold: true } },
  { text: "可解释  ", options: { fontSize: 12, color: C.muted } },
  { text: "SHAP 全局 + 局部双解释", options: { fontSize: 13, color: C.dark, bold: true } },
], { x: 7.25, y: 1.8, w: 5.5, h: 1.85, fontFace: F.body, valign: "top", margin: 0 });

// 右半下：Top6 特征 IV 榜
s9.addShape(pres.shapes.RECTANGLE, {
  x: 7.0, y: 3.95, w: 5.8, h: 2.85, fill: { color: C.white }, line: { color: C.light, width: 1 },
  shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
});
s9.addShape(pres.shapes.RECTANGLE, { x: 7.0, y: 3.95, w: 0.1, h: 2.85, fill: { color: C.teal }, line: { type: "none" } });
s9.addText("Top 6 特征 IV 榜", { x: 7.25, y: 4.05, w: 5.5, h: 0.4, fontSize: 18, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });

const topFeats = [
  ["int_rate", "0.398", "贷款利率"],
  ["term_months", "0.160", "贷款期限"],
  ["tot_hi_cred_lim", "0.057", "总高信用额度"],
  ["loan_amnt", "0.056", "申请金额"],
  ["open_rv_24m", "0.047", "24月内新开循环账户"],
  ["home_ownership", "0.039", "房屋所有权"],
];
topFeats.forEach((f, i) => {
  const y = 4.55 + i * 0.36;
  s9.addText(`${i + 1}. ${f[0]}`, { x: 7.25, y: y, w: 2.4, h: 0.32, fontSize: 12, fontFace: F.body, color: C.dark, bold: true, margin: 0 });
  s9.addText(`IV=${f[1]}`, { x: 9.65, y: y, w: 1.2, h: 0.32, fontSize: 12, fontFace: F.body, color: C.accent, bold: true, margin: 0 });
  s9.addText(f[2], { x: 10.85, y: y, w: 1.85, h: 0.32, fontSize: 11, fontFace: F.body, color: C.muted, margin: 0 });
});

// ========== Slide 10: SHAP 可解释性 ==========
let s10 = pres.addSlide();
s10.background = { color: C.offWhite };
addTitleBar(s10, "可解释性：SHAP Top3", 10);

const shapPath = path.join(__dirname, "experiments", "results", "shap_top15.png");
s10.addImage({ path: shapPath, x: 0.6, y: 1.3, w: 7.5, h: 5.2, sizing: { type: "contain", w: 7.5, h: 5.2 } });

s10.addShape(pres.shapes.RECTANGLE, {
  x: 8.5, y: 1.3, w: 4.2, h: 5.2, fill: { color: C.white }, line: { color: C.light, width: 1 },
  shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
});
s10.addText("示例解读", { x: 8.7, y: 1.5, w: 3.8, h: 0.4, fontSize: 16, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
s10.addText([
  { text: '"这位借款人违约概率 72%\n\n', options: { fontSize: 13, color: C.dark } },
  { text: "主要风险因子：\n", options: { fontSize: 13, color: C.dark, bold: true } },
  { text: "1. int_rate（利率）13.5%\n   — 高于平均，平台已识别较高风险\n\n", options: { fontSize: 12, color: C.muted } },
  { text: "2. dti（负债收入比）35%\n   — 偏高，偿债压力大\n\n", options: { fontSize: 12, color: C.muted } },
  { text: "3. inq_last_6mths 5 次\n   — 频繁申贷，资金紧张信号\n\n", options: { fontSize: 12, color: C.muted } },
  { text: '建议话术：\'根据您的信用状况，建议降低申请金额或提供担保\'"', options: { fontSize: 12, color: C.accent, italic: true } },
], { x: 8.7, y: 2.0, w: 3.8, h: 4.3, fontFace: F.body, valign: "top", margin: 0 });

// ========== Slide 11: Demo 演示 ==========
let s11 = pres.addSlide();
s11.background = { color: C.midnight };
s11.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 13.3, h: 0.15, fill: { color: C.accent }, line: { type: "none" } });
s11.addText("现场 Demo", { x: 0.6, y: 0.4, w: 12, h: 0.7, fontSize: 32, fontFace: F.header, color: C.white, bold: true, margin: 0 });
s11.addText("35 岁深圳电商老板借 20 万", { x: 0.6, y: 1.1, w: 12, h: 0.5, fontSize: 18, fontFace: F.body, color: C.accent, margin: 0 });

const demoSteps = [
  { step: "1", title: "启动 Agent", desc: "输入客户基本信息" },
  { step: "2", title: "多轮访谈", desc: "Agent 自动提问 19 项特征" },
  { step: "3", title: "模型推理", desc: "实时输出违约概率" },
  { step: "4", title: "报告生成", desc: "Markdown 尽调报告 + SHAP Top3" },
];
demoSteps.forEach((d, i) => {
  const y = 2.0 + i * 1.1;
  s11.addShape(pres.shapes.OVAL, { x: 1, y: y, w: 0.7, h: 0.7, fill: { color: C.accent }, line: { type: "none" } });
  s11.addText(d.step, { x: 1, y: y, w: 0.7, h: 0.7, fontSize: 24, fontFace: F.header, color: C.midnight, bold: true, align: "center", valign: "middle", margin: 0 });
  s11.addText(d.title, { x: 2, y: y, w: 4, h: 0.35, fontSize: 18, fontFace: F.body, color: C.white, bold: true, margin: 0 });
  s11.addText(d.desc, { x: 2, y: y + 0.35, w: 8, h: 0.35, fontSize: 14, fontFace: F.body, color: C.light, margin: 0 });
});
s11.addText("Demo 视频：2 分钟（35 岁深圳电商老板借 20 万 · 4 步完整流程）", { x: 0.6, y: 6.5, w: 12, h: 0.4, fontSize: 14, fontFace: F.body, color: C.accent, italic: true, margin: 0 });

// ========== Slide 12: 项目价值证明 ==========
let s12 = pres.addSlide();
s12.background = { color: C.offWhite };
addTitleBar(s12, "项目价值证明", 12);
s12.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 1.0, w: 12.1, h: 0.7, fill: { color: C.midnight }, line: { type: "none" },
});
s12.addText([
  { text: "差异化定位为什么站得住脚？ ", options: { fontSize: 15, color: C.white, bold: true } },
  { text: "方法论证据 × 工程化证据 × 商业化证据 三重闭环", options: { fontSize: 15, color: C.accent } },
], { x: 0.8, y: 1.0, w: 11.7, h: 0.7, fontFace: F.body, valign: "middle", margin: 0 });

const proofs = [
  {
    tag: "①", title: "方法论证据", sub: "量化对比实验（15 万行 LendingClub）",
    color: C.navy,
    items: [
      "AUC 0.7093 · 与 81 特征 baseline 相当",
      "19 特征 = A(17) 少 1 个，B(81) 减 76.5%",
      "IV/WoE + PSI 双验证，28 特征全部 PSI<0.25",
      "明确排除 grade/sub_grade 数据泄露",
      "结论：少即是多，方法论决定一切",
    ],
  },
  {
    tag: "②", title: "工程化证据", sub: "对标 4 类竞品 + 可复现 Demo",
    color: C.teal,
    items: [
      "A 大厂对公：多模态采集但闭源",
      "B 海外 Agent：已有分级决策概念",
      "C 开源项目：navyaneel/shashi-hue 直接对标",
      "D 报告 SaaS：商业模式可借鉴",
      "CreditMind：唯一 Agent 闭环 + IV/PSI 工程",
    ],
  },
  {
    tag: "③", title: "商业化证据", sub: "用户价值 + 投资人逻辑",
    color: C.midnight,
    items: [
      "单笔尽调 2h → 15min（效率提升 8x）",
      "每个判断都有据可查（SHAP + IV）",
      "合规边界：AI 不放款，只做建议+人审",
      "目标客户：消费贷/P2P 客户经理",
      "Phase 2：FastAPI+Docker 企业级部署",
    ],
  },
];
proofs.forEach((p, i) => {
  const x = 0.6 + i * 4.2;
  s12.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.9, w: 3.9, h: 4.0, fill: { color: C.white }, line: { color: C.light, width: 1 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
  });
  s12.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.9, w: 3.9, h: 0.7, fill: { color: p.color }, line: { type: "none" } });
  s12.addText(p.tag + " " + p.title, { x: x + 0.2, y: 1.9, w: 3.5, h: 0.7, fontSize: 16, fontFace: F.body, color: C.white, bold: true, valign: "middle", margin: 0 });
  s12.addText(p.sub, { x: x + 0.2, y: 2.7, w: 3.5, h: 0.4, fontSize: 11, fontFace: F.body, color: C.muted, italic: true, margin: 0 });
  p.items.forEach((it, j) => {
    s12.addText("• " + it, { x: x + 0.2, y: 3.2 + j * 0.5, w: 3.5, h: 0.45, fontSize: 12, fontFace: F.body, color: C.dark, margin: 0 });
  });
});

s12.addShape(pres.shapes.RECTANGLE, {
  x: 0.6, y: 6.1, w: 12.1, h: 0.75, fill: { color: "F0F9FF" }, line: { color: C.accent, width: 1 },
});
s12.addText([
  { text: "对投资人：", options: { fontSize: 13, color: C.midnight, bold: true } },
  { text: "方法论 + 量化对比 + 工程闭环 → 可复制、可扩展的 AI 风控基础设施    ", options: { fontSize: 13, color: C.dark } },
  { text: "对用户：", options: { fontSize: 13, color: C.midnight, bold: true } },
  { text: "2h→15min + 每个判断有据可查 + 合规人审兜底", options: { fontSize: 13, color: C.dark } },
], { x: 0.8, y: 6.1, w: 11.7, h: 0.75, fontFace: F.body, valign: "middle", margin: 0 });

// ========== Slide 13: Roadmap ==========
let s13 = pres.addSlide();
s13.background = { color: C.offWhite };
addTitleBar(s13, "Roadmap", 13);

const phases = [
  { title: "Phase 1: MVP", time: "5 天（模块四+五）", items: ["单轮输入 + Agent 访谈", "模型推理 + 报告生成", "Streamlit Web Demo", "3 个预设 Case"], color: C.navy, status: "✅ 已完成" },
  { title: "Phase 2: 产品化", time: "1-2 个月", items: ["FastAPI + Docker", "OCR 多模态采集", "模型校准（Isotonic）", "Word/PDF 导出"], color: C.teal, status: "⏳ 计划中" },
  { title: "Phase 3: 企业级", time: "3-6 个月", items: ["多用户并发", "企业级 SaaS", "实时交易系统对接", "多产品线支持"], color: C.midnight, status: "📋 远期" },
];
phases.forEach((p, i) => {
  const x = 0.6 + i * 4.2;
  s13.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.5, w: 3.9, h: 4.5, fill: { color: C.white }, line: { color: C.light, width: 1 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
  });
  s13.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.5, w: 3.9, h: 0.6, fill: { color: p.color }, line: { type: "none" } });
  s13.addText(p.title, { x: x + 0.2, y: 1.5, w: 3.5, h: 0.6, fontSize: 16, fontFace: F.body, color: C.white, bold: true, valign: "middle", margin: 0 });
  s13.addText(p.time, { x: x + 0.2, y: 2.2, w: 3.5, h: 0.35, fontSize: 12, fontFace: F.body, color: C.muted, margin: 0 });
  p.items.forEach((it, j) => {
    s13.addText("• " + it, { x: x + 0.2, y: 2.7 + j * 0.45, w: 3.5, h: 0.4, fontSize: 13, fontFace: F.body, color: C.dark, margin: 0 });
  });
  s13.addShape(pres.shapes.RECTANGLE, { x: x + 0.2, y: 5.4, w: 3.5, h: 0.4, fill: { color: C.offWhite }, line: { type: "none" } });
  s13.addText(p.status, { x: x + 0.2, y: 5.4, w: 3.5, h: 0.4, fontSize: 13, fontFace: F.body, color: p.color, bold: true, align: "center", valign: "middle", margin: 0 });
});

s13.addText("Phase 2 会进一步丰富信贷特征工程与多模态采集，覆盖更多消费贷细分场景。", {
  x: 0.6, y: 6.3, w: 12.1, h: 0.4, fontSize: 13, fontFace: F.body, color: C.muted, italic: true, align: "center", margin: 0,
});

// ========== Slide 14: 诚实短板与 Ask ==========
let s14 = pres.addSlide();
s14.background = { color: C.offWhite };
addTitleBar(s14, "诚实短板与 Ask", 14);

s14.addText("已知短板（主动说明）", { x: 0.6, y: 1.2, w: 6, h: 0.4, fontSize: 18, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
const shortcomings = [
  { issue: "数据规模 15 万行", plan: "接 2007-2019 全量" },
  { issue: "特征衍生深度不足", plan: "加衍生特征工程层" },
  { issue: "无模型校准", plan: "Isotonic / Platt" },
  { issue: "仅文本对话", plan: "加 OCR" },
];
shortcomings.forEach((s, i) => {
  const y = 1.7 + i * 0.7;
  s14.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: y, w: 5.8, h: 0.6, fill: { color: C.white }, line: { color: C.light, width: 1 } });
  s14.addText(s.issue, { x: 0.8, y: y, w: 3, h: 0.6, fontSize: 13, fontFace: F.body, color: C.red, valign: "middle", margin: 0 });
  s14.addText("→ " + s.plan, { x: 3.8, y: y, w: 2.5, h: 0.6, fontSize: 13, fontFace: F.body, color: C.green, valign: "middle", margin: 0 });
});

s14.addText("Ask", { x: 7, y: 1.2, w: 5.5, h: 0.4, fontSize: 18, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
const asks = [
  "Agent × 风控 的产品化路径，特别是合规边界设计",
  "IV/WoE+PSI 方法论在生产环境的工程化最佳实践",
  "多模态采集（OCR/语音）的落地经验",
];
asks.forEach((a, i) => {
  const y = 1.7 + i * 1.0;
  s14.addShape(pres.shapes.RECTANGLE, { x: 7, y: y, w: 5.7, h: 0.85, fill: { color: C.midnight }, line: { type: "none" } });
  s14.addText(`${i + 1}. ${a}`, { x: 7.2, y: y, w: 5.3, h: 0.85, fontSize: 14, fontFace: F.body, color: C.white, valign: "middle", margin: 0 });
});

// ========== Slide 15: 致谢 ==========
let s15 = pres.addSlide();
s15.background = { color: C.midnight };
s15.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 13.3, h: 0.15, fill: { color: C.accent }, line: { type: "none" } });
s15.addShape(pres.shapes.RECTANGLE, { x: 0, y: 7.35, w: 13.3, h: 0.15, fill: { color: C.accent }, line: { type: "none" } });
s15.addText("感谢各位导师点评！", { x: 1, y: 2.0, w: 11.3, h: 1.0, fontSize: 44, fontFace: F.header, color: C.white, bold: true, align: "center", margin: 0 });
s15.addShape(pres.shapes.LINE, { x: 5, y: 3.3, w: 3.3, h: 0, line: { color: C.accent, width: 2 } });
s15.addText("CreditMind · AI 信贷风控大脑", { x: 1, y: 3.6, w: 11.3, h: 0.5, fontSize: 22, fontFace: F.header, color: C.accent, align: "center", margin: 0 });
s15.addText("让消费贷尽调从 2 小时压缩到 15 分钟，且每个判断都有据可查。", {
  x: 1, y: 4.2, w: 11.3, h: 0.5, fontSize: 16, fontFace: F.body, color: C.light, italic: true, align: "center", margin: 0,
});
s15.addText("尹红艳 · 2026-07-25", { x: 1, y: 5.5, w: 11.3, h: 0.4, fontSize: 16, fontFace: F.body, color: C.white, align: "center", margin: 0 });

// ========== 生成文件 ==========
pres.writeFile({ fileName: "CreditMind-Pitch-Deck.pptx" }).then(() => {
  console.log("✅ CreditMind-Pitch-Deck.pptx 已生成");
});
