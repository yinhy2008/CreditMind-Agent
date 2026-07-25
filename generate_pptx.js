/**
 * CreditMind 路演 PPT 生成脚本
 * 基于 07-pitch-deck-v0.1.md 的 13 页大纲
 * 配色：Ocean Gradient（深蓝 065A82 + 青色 1C7293 + 午夜蓝 21295C）
 */
const pptxgen = require("pptxgenjs");
const path = require("path");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3" × 7.5"
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
  slide.addText(`${pageNum} / 13`, {
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

// ========== Slide 6: 竞品对比实验 ⭐ ==========
let s6 = pres.addSlide();
s6.background = { color: C.offWhite };
addTitleBar(s6, "竞品对比实验 ⭐", 6);
s6.addText("在 LendingClub 15 万条数据上对比三种方法论", {
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
s6.addTable(tableData, {
  x: 0.6, y: 1.6, w: 12.1, h: 2.8,
  colW: [4.3, 1.7, 1.5, 2.0, 2.6],
  border: { pt: 1, color: C.light },
  rowH: [0.55, 0.75, 0.75, 0.75],
});

// 插入对比图
const imgPath = path.join(__dirname, "experiments", "results", "comparison_overview.png");
s6.addImage({ path: imgPath, x: 1.5, y: 4.6, w: 10.3, h: 2.2, sizing: { type: "contain", w: 10.3, h: 2.2 } });

// ========== Slide 7: 三大护城河 ==========
let s7 = pres.addSlide();
s7.background = { color: C.offWhite };
addTitleBar(s7, "三大护城河", 7);

const moats = [
  { num: "1", title: "方法论深度", desc: "唯一把「IV/WoE → PSI → 贪心去共线性 → 四套方案」完整工程化的项目", color: C.navy },
  { num: "2", title: "数据泄露防护", desc: "明确识别并排除 grade/sub_grade 目标泄露（navyaneel 直接用了泄露特征，AUC 虚高）", color: C.teal },
  { num: "3", title: "Agent 产品化层", desc: "把静态 Notebook 升级为「对话采集 → 模型推理 → 报告生成」Agent 闭环", color: C.midnight },
];
moats.forEach((m, i) => {
  const y = 1.5 + i * 1.6;
  s7.addShape(pres.shapes.RECTANGLE, {
    x: 1, y: y, w: 11.3, h: 1.35, fill: { color: C.white }, line: { color: C.light, width: 1 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
  });
  s7.addShape(pres.shapes.OVAL, {
    x: 1.3, y: y + 0.3, w: 0.75, h: 0.75, fill: { color: m.color }, line: { type: "none" },
  });
  s7.addText(m.num, { x: 1.3, y: y + 0.3, w: 0.75, h: 0.75, fontSize: 28, fontFace: F.header, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });
  s7.addText(m.title, { x: 2.3, y: y + 0.2, w: 9.5, h: 0.5, fontSize: 20, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
  s7.addText(m.desc, { x: 2.3, y: y + 0.7, w: 9.5, h: 0.55, fontSize: 14, fontFace: F.body, color: C.muted, margin: 0 });
});

// ========== Slide 8: SHAP 可解释性 ==========
let s8 = pres.addSlide();
s8.background = { color: C.offWhite };
addTitleBar(s8, "可解释性：SHAP Top3", 8);

const shapPath = path.join(__dirname, "experiments", "results", "shap_top15.png");
s8.addImage({ path: shapPath, x: 0.6, y: 1.3, w: 7.5, h: 5.2, sizing: { type: "contain", w: 7.5, h: 5.2 } });

s8.addShape(pres.shapes.RECTANGLE, {
  x: 8.5, y: 1.3, w: 4.2, h: 5.2, fill: { color: C.white }, line: { color: C.light, width: 1 },
  shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
});
s8.addText("示例解读", { x: 8.7, y: 1.5, w: 3.8, h: 0.4, fontSize: 16, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
s8.addText([
  { text: '"这位借款人违约概率 72%\n\n', options: { fontSize: 13, color: C.dark } },
  { text: "主要风险因子：\n", options: { fontSize: 13, color: C.dark, bold: true } },
  { text: "1. int_rate（利率）13.5%\n   — 高于平均，平台已识别较高风险\n\n", options: { fontSize: 12, color: C.muted } },
  { text: "2. dti（负债收入比）35%\n   — 偏高，偿债压力大\n\n", options: { fontSize: 12, color: C.muted } },
  { text: "3. inq_last_6mths 5 次\n   — 频繁申贷，资金紧张信号\n\n", options: { fontSize: 12, color: C.muted } },
  { text: '建议话术：\'根据您的信用状况，建议降低申请金额或提供担保\'"', options: { fontSize: 12, color: C.accent, italic: true } },
], { x: 8.7, y: 2.0, w: 3.8, h: 4.3, fontFace: F.body, valign: "top", margin: 0 });

// ========== Slide 9: Demo 演示 ==========
let s9 = pres.addSlide();
s9.background = { color: C.midnight };
s9.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 13.3, h: 0.15, fill: { color: C.accent }, line: { type: "none" } });
s9.addText("现场 Demo", { x: 0.6, y: 0.4, w: 12, h: 0.7, fontSize: 32, fontFace: F.header, color: C.white, bold: true, margin: 0 });
s9.addText("35 岁深圳电商老板借 20 万", { x: 0.6, y: 1.1, w: 12, h: 0.5, fontSize: 18, fontFace: F.body, color: C.accent, margin: 0 });

const demoSteps = [
  { step: "1", title: "启动 Agent", desc: "输入客户基本信息" },
  { step: "2", title: "多轮访谈", desc: "Agent 自动提问 19 项特征" },
  { step: "3", title: "模型推理", desc: "实时输出违约概率" },
  { step: "4", title: "报告生成", desc: "Markdown 尽调报告 + SHAP Top3" },
];
demoSteps.forEach((d, i) => {
  const y = 2.0 + i * 1.1;
  s9.addShape(pres.shapes.OVAL, { x: 1, y: y, w: 0.7, h: 0.7, fill: { color: C.accent }, line: { type: "none" } });
  s9.addText(d.step, { x: 1, y: y, w: 0.7, h: 0.7, fontSize: 24, fontFace: F.header, color: C.midnight, bold: true, align: "center", valign: "middle", margin: 0 });
  s9.addText(d.title, { x: 2, y: y, w: 4, h: 0.35, fontSize: 18, fontFace: F.body, color: C.white, bold: true, margin: 0 });
  s9.addText(d.desc, { x: 2, y: y + 0.35, w: 8, h: 0.35, fontSize: 14, fontFace: F.body, color: C.light, margin: 0 });
});
s9.addText("预期时长：5-10 分钟", { x: 0.6, y: 6.5, w: 12, h: 0.4, fontSize: 14, fontFace: F.body, color: C.accent, italic: true, margin: 0 });

// ========== Slide 10: 团队 ==========
let s10 = pres.addSlide();
s10.background = { color: C.offWhite };
addTitleBar(s10, "团队与学术背书", 10);

s10.addShape(pres.shapes.OVAL, { x: 1, y: 1.5, w: 2.2, h: 2.2, fill: { color: C.navy }, line: { type: "none" } });
s10.addText("尹\n红\n艳", { x: 1, y: 1.5, w: 2.2, h: 2.2, fontSize: 28, fontFace: F.header, color: C.white, bold: true, align: "center", valign: "middle", margin: 0 });

s10.addText("尹红艳（Yolanda）", { x: 3.5, y: 1.5, w: 8.5, h: 0.5, fontSize: 24, fontFace: F.header, color: C.midnight, bold: true, margin: 0 });
s10.addText("深圳大学南特金融科技学院 · 金融科技与风险控制硕士（2025.09 入学）", { x: 3.5, y: 2.0, w: 8.5, h: 0.4, fontSize: 14, fontFace: F.body, color: C.muted, margin: 0 });

const creds = [
  "🎓 深圳大学南特金融科技学院 · 金融科技与风险控制硕士",
  "📜 CFA 持证 · CQF 考生 · PMP 认证 · 腾讯云 AI 认证",
  "💼 5 年家族办公室渠道经理 + 5 年万科/招商地产 ERP 业务分析师",
  "🔬 硕士课题：信贷违约预测模型（本项目核心引擎）",
];
creds.forEach((c, i) => {
  s10.addText(c, { x: 3.5, y: 2.6 + i * 0.45, w: 8.5, h: 0.4, fontSize: 14, fontFace: F.body, color: C.dark, margin: 0 });
});

s10.addShape(pres.shapes.RECTANGLE, {
  x: 1, y: 5.0, w: 11.3, h: 1.5, fill: { color: C.white }, line: { color: C.light, width: 1 },
  shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
});
s10.addShape(pres.shapes.RECTANGLE, { x: 1, y: 5.0, w: 0.1, h: 1.5, fill: { color: C.accent }, line: { type: "none" } });
s10.addText("学术 IP", { x: 1.3, y: 5.1, w: 10.7, h: 0.4, fontSize: 16, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
s10.addText("硕士课题方向：信贷违约预测模型\n已完成：LendingClub 2018-2019 数据完整建模流程（V1.ipynb + V2.md）\n本次路演核心：把课题成果产品化为 CreditMind Agent", {
  x: 1.3, y: 5.5, w: 10.7, h: 1.2, fontSize: 13, fontFace: F.body, color: C.muted, margin: 0,
});

// ========== Slide 11: Roadmap ==========
let s11 = pres.addSlide();
s11.background = { color: C.offWhite };
addTitleBar(s11, "Roadmap", 11);

const phases = [
  { title: "Phase 1: MVP", time: "5 天（模块四+五）", items: ["单轮输入 + Agent 访谈", "模型推理 + 报告生成", "Streamlit Web Demo", "3 个预设 Case"], color: C.navy, status: "✅ 已完成" },
  { title: "Phase 2: 产品化", time: "1-2 个月", items: ["FastAPI + Docker", "OCR 多模态采集", "模型校准（Isotonic）", "Word/PDF 导出"], color: C.teal, status: "⏳ 计划中" },
  { title: "Phase 3: 企业级", time: "3-6 个月", items: ["多用户并发", "企业级 SaaS", "实时交易系统对接", "多产品线支持"], color: C.midnight, status: "📋 远期" },
];
phases.forEach((p, i) => {
  const x = 0.6 + i * 4.2;
  s11.addShape(pres.shapes.RECTANGLE, {
    x: x, y: 1.5, w: 3.9, h: 4.5, fill: { color: C.white }, line: { color: C.light, width: 1 },
    shadow: { type: "outer", blur: 6, offset: 2, angle: 135, color: "000000", opacity: 0.08 },
  });
  s11.addShape(pres.shapes.RECTANGLE, { x: x, y: 1.5, w: 3.9, h: 0.6, fill: { color: p.color }, line: { type: "none" } });
  s11.addText(p.title, { x: x + 0.2, y: 1.5, w: 3.5, h: 0.6, fontSize: 16, fontFace: F.body, color: C.white, bold: true, valign: "middle", margin: 0 });
  s11.addText(p.time, { x: x + 0.2, y: 2.2, w: 3.5, h: 0.35, fontSize: 12, fontFace: F.body, color: C.muted, margin: 0 });
  p.items.forEach((it, j) => {
    s11.addText("• " + it, { x: x + 0.2, y: 2.7 + j * 0.45, w: 3.5, h: 0.4, fontSize: 13, fontFace: F.body, color: C.dark, margin: 0 });
  });
  s11.addShape(pres.shapes.RECTANGLE, { x: x + 0.2, y: 5.4, w: 3.5, h: 0.4, fill: { color: C.offWhite }, line: { type: "none" } });
  s11.addText(p.status, { x: x + 0.2, y: 5.4, w: 3.5, h: 0.4, fontSize: 13, fontFace: F.body, color: p.color, bold: true, align: "center", valign: "middle", margin: 0 });
});

s11.addText("Phase 2 会进一步丰富信贷特征工程与多模态采集，覆盖更多消费贷细分场景。", {
  x: 0.6, y: 6.3, w: 12.1, h: 0.4, fontSize: 13, fontFace: F.body, color: C.muted, italic: true, align: "center", margin: 0,
});

// ========== Slide 12: 诚实短板与 Ask ==========
let s12 = pres.addSlide();
s12.background = { color: C.offWhite };
addTitleBar(s12, "诚实短板与 Ask", 12);

s12.addText("已知短板（主动说明）", { x: 0.6, y: 1.2, w: 6, h: 0.4, fontSize: 18, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
const shortcomings = [
  { issue: "数据规模 15 万行", plan: "接 2007-2019 全量" },
  { issue: "特征衍生深度不足", plan: "加衍生特征工程层" },
  { issue: "无模型校准", plan: "Isotonic / Platt" },
  { issue: "仅文本对话", plan: "加 OCR" },
];
shortcomings.forEach((s, i) => {
  const y = 1.7 + i * 0.7;
  s12.addShape(pres.shapes.RECTANGLE, { x: 0.6, y: y, w: 5.8, h: 0.6, fill: { color: C.white }, line: { color: C.light, width: 1 } });
  s12.addText(s.issue, { x: 0.8, y: y, w: 3, h: 0.6, fontSize: 13, fontFace: F.body, color: C.red, valign: "middle", margin: 0 });
  s12.addText("→ " + s.plan, { x: 3.8, y: y, w: 2.5, h: 0.6, fontSize: 13, fontFace: F.body, color: C.green, valign: "middle", margin: 0 });
});

s12.addText("Ask", { x: 7, y: 1.2, w: 5.5, h: 0.4, fontSize: 18, fontFace: F.body, color: C.midnight, bold: true, margin: 0 });
const asks = [
  "Agent × 风控 的产品化路径，特别是合规边界设计",
  "IV/WoE+PSI 方法论在生产环境的工程化最佳实践",
  "多模态采集（OCR/语音）的落地经验",
];
asks.forEach((a, i) => {
  const y = 1.7 + i * 1.0;
  s12.addShape(pres.shapes.RECTANGLE, { x: 7, y: y, w: 5.7, h: 0.85, fill: { color: C.midnight }, line: { type: "none" } });
  s12.addText(`${i + 1}. ${a}`, { x: 7.2, y: y, w: 5.3, h: 0.85, fontSize: 14, fontFace: F.body, color: C.white, valign: "middle", margin: 0 });
});

// ========== Slide 13: 致谢 ==========
let s13 = pres.addSlide();
s13.background = { color: C.midnight };
s13.addShape(pres.shapes.RECTANGLE, { x: 0, y: 0, w: 13.3, h: 0.15, fill: { color: C.accent }, line: { type: "none" } });
s13.addShape(pres.shapes.RECTANGLE, { x: 0, y: 7.35, w: 13.3, h: 0.15, fill: { color: C.accent }, line: { type: "none" } });
s13.addText("感谢各位导师点评！", { x: 1, y: 2.0, w: 11.3, h: 1.0, fontSize: 44, fontFace: F.header, color: C.white, bold: true, align: "center", margin: 0 });
s13.addShape(pres.shapes.LINE, { x: 5, y: 3.3, w: 3.3, h: 0, line: { color: C.accent, width: 2 } });
s13.addText("CreditMind · AI 信贷风控大脑", { x: 1, y: 3.6, w: 11.3, h: 0.5, fontSize: 22, fontFace: F.header, color: C.accent, align: "center", margin: 0 });
s13.addText("让消费贷尽调从 2 小时压缩到 15 分钟，且每个判断都有据可查。", {
  x: 1, y: 4.2, w: 11.3, h: 0.5, fontSize: 16, fontFace: F.body, color: C.light, italic: true, align: "center", margin: 0,
});
s13.addText("尹红艳 · 2026-07-25", { x: 1, y: 5.5, w: 11.3, h: 0.4, fontSize: 16, fontFace: F.body, color: C.white, align: "center", margin: 0 });

// ========== 生成文件 ==========
pres.writeFile({ fileName: "CreditMind-Pitch-Deck.pptx" }).then(() => {
  console.log("✅ CreditMind-Pitch-Deck.pptx 已生成");
});
