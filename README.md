# CreditMind · AI 信贷风控大脑

> 让消费贷尽调从 2 小时压缩到 15 分钟，且每个判断都有据可查。

模块四路演项目 · 尹红艳 · 2026-07-25

---

## 项目简介

CreditMind 是面向消费贷/P2P 场景的「智能访谈 + 违约预测 + 可解释报告」一体化 Agent。

**核心差异化**：
- IV/WoE + PSI + 贪心去共线性工程化特征筛选方法论
- 多轮对话驱动的贷前信息采集
- 明确排除 grade/sub_grade 目标泄露特征
- SHAP + IV 双解释

**竞品对比实验结果**（在同一份 LendingClub 15 万行数据上）：

| 模型 | 特征数 | AUC | 数据泄露 | PSI 稳定性 |
|---|---|---|---|---|
| A: Leaky Baseline | 17 | 0.6995 | ❌ 是 | 未验证 |
| B: Feature-Heavy | 81 | 0.7167 | ❌ 包含 | 未验证 |
| **C: CreditMind** | **19** | **0.7093** | **✅ 否** | **✅ 已验证** |

---

## 📚 文档导航

| 文档 | 内容 |
|---|---|
| `00-competitive-analysis.md` | 竞品分析 + 对比实验结果 |
| `01-project-positioning.md` | 项目定位句 + 电梯演讲 |
| `02-user-pain-points.md` | 用户痛点表 |
| `03-business-flow.md` | 业务流程图 |
| `04-ai-intervention-points.md` | AI 介入点说明 |
| `05-mvp-features.md` | MVP 功能清单 |
| `06-prd-v0.1.md` | PRD v0.1 |
| `07-pitch-deck-v0.1.md` | 路演 PPT 大纲 |
| **`08-business-plan.md`** | **商业计划书（BP）** |
| **`09-demo-video-script.md`** | **Demo 视频录制脚本** |
| `CreditMind-Pitch-Deck.pptx` | 13 页路演 PPT |

---

## 快速开始

### 1. 环境依赖

```bash
pip install xgboost shap scikit-learn pandas numpy streamlit
# 可选（LLM 访谈模式）：
pip install openai
```

### 2. 训练模型

```bash
cd 模块四/CreditMind
python model_server.py train
```

输出：`artifacts/creditmind_xgb.json` + `artifacts/feature_meta.json`

### 3. 启动 Web Demo

```bash
streamlit run app.py
```

浏览器打开 http://localhost:8501

### 4. 测试推理

```bash
python model_server.py test    # 测试虚拟 Case
python cases.py                # 验证 3 个预设 Case
```

---

## 项目结构

```
CreditMind/
├── model_server.py              # 模型服务层（训练+推理+SHAP）
├── interview_agent.py           # 智能访谈 Agent（多轮对话）
├── extractor.py                 # 特征抽取器（对话→JSON）
├── report_generator.py          # 尽调报告生成器（Markdown）
├── cases.py                     # 3 个虚拟借款人 Case
├── app.py                       # Streamlit Web Demo
├── artifacts/
│   ├── creditmind_xgb.json      # 训练好的 XGBoost 模型
│   └── feature_meta.json        # 特征元信息
├── experiments/
│   ├── competitive_benchmark.py # 竞品对比实验脚本
│   └── results/                 # 实验结果（图表+CSV）
├── 00-competitive-analysis.md   # 竞品分析文档
├── 01-project-positioning.md    # 项目定位句+电梯演讲
├── 02-user-pain-points.md       # 用户痛点表
├── 03-business-flow.md          # 业务流程图
├── 04-ai-intervention-points.md # AI 介入点说明
├── 05-mvp-features.md           # MVP 功能清单
├── 06-prd-v0.1.md               # PRD v0.1
├── 07-pitch-deck-v0.1.md        # 路演材料初稿
├── 08-business-plan.md          # 商业计划书（BP）
├── 09-demo-video-script.md      # Demo 视频录制脚本
├── CreditMind-Pitch-Deck.pptx   # 13 页路演 PPT
└── README.md                    # 本文件
```

---

## 使用方式

### 模式 1：预设 Case 演示（路演推荐）

3 个预设 Case：
- 🟢 **李明**（低风险）：35 岁互联网工程师，年薪 80 万，借 10 万装修
- 🟡 **张伟**（中风险）：35 岁电商老板，借 15 万经营周转
- 🔴 **王强**（高风险）：40 岁自由职业者，借 30 万债务重组

### 模式 2：手动输入特征

直接输入 19 项特征值，实时推理。

### 模式 3：Agent 访谈模拟

模拟 Agent 与借款人的多轮对话（需配置 LLM API Key，否则降级为表单模式）。

```bash
# 配置 LLM（可选）
export DEEPSEEK_API_KEY=sk-xxxx
export LLM_BASE_URL=https://api.deepseek.com/v1
export LLM_MODEL=deepseek-chat
```

---

## 核心特征清单（19 项）

| # | 特征 | IV | 业务含义 |
|---|---|---|---|
| 1 | int_rate | 0.398 | 贷款利率 |
| 2 | term_months | 0.160 | 贷款期限 |
| 3 | tot_hi_cred_lim | 0.057 | 总高信用额度 |
| 4 | loan_amnt | 0.056 | 申请借款金额 |
| 5 | open_rv_24m | 0.047 | 24个月内新开循环账户 |
| 6 | home_ownership | 0.039 | 房屋所有权 |
| 7 | mort_acc | 0.038 | 抵押账户数 |
| 8 | total_bc_limit | 0.033 | 信用卡总额度 |
| 9 | num_tl_op_past_12m | 0.030 | 12个月内新开账户 |
| 10 | mo_sin_rcnt_rev_tl_op | 0.028 | 最近开循环账户距今 |
| 11 | mo_sin_old_rev_tl_op | 0.026 | 最早开循环账户距今 |
| 12 | mths_since_recent_bc | 0.025 | 最近开信用卡距今 |
| 13 | verification_status | 0.024 | 收入验证状态 |
| 14 | inq_last_6mths | 0.022 | 6个月内查询次数 |
| 15 | emp_length | 0.020 | 工作年限 |
| 16 | mths_since_recent_inq | 0.020 | 最近查询距今 |
| 17 | inq_last_12m | 0.020 | 12个月内查询次数 |
| 18 | annual_inc | 0.020 | 年收入 |
| 19 | mo_sin_old_il_acct | 0.020 | 最早开分期账户距今 |

所有特征均经过 **IV≥0.02 + PSI<0.25 + 贪心去共线性（|r|≥0.7）** 三重验证。

---

## 路演演示流程

1. **开场**（30 秒）：自我介绍 + 一句话定位
2. **痛点**（1 分钟）：客户经理单笔尽调 1-2 小时
3. **解决方案**（1 分钟）：三层联动（访谈+推理+报告）
4. **竞品对比实验**（2 分钟）：少即是多的金句
5. **Demo 演示**（2 分钟）：选张伟 Case 现场演示
6. **护城河 + Roadmap + Ask**（1.5 分钟）

详见 `07-pitch-deck-v0.1.md`。

---

## 合规声明

- CreditMind **不直接放款**，只做建议+人审
- 模型已排除 `grade`/`sub_grade` 目标泄露特征
- 全程对话+评分+因子留痕，可供监管审计
- 本系统仅供路演演示，不构成实际放款决策

---

## License

MIT License · 尹红艳 · 2026
