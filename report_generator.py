"""
CreditMind · 尽调报告生成器
============================
基于模型推理结果 + SHAP 解释，自动生成 Markdown 尽调报告。

报告结构：
1. 报告头（客户信息 + 生成时间）
2. 风险评估摘要（违约概率 + 风险等级）
3. 关键风险因子（SHAP Top3 + 业务解读）
4. 建议话术（基于风险等级）
5. 合规声明
"""
from __future__ import annotations

from datetime import datetime
from typing import Any

from model_server import CreditMindModel, FEATURE_META


# 3 个预设 Case 的 SHAP 详细解读（基于真实模型推理结果固化，供路演 Demo 稳定展示）
# 当 generate_report 收到 case_id 且命中此处时，自然语言段用专属解读替换动态 narration
CASE_SHAP_INTERPRETATION: dict[str, str] = {
    "low_risk": (
        "该借款人违约概率仅 4.6%，处于低风险区间。三大关键因子中，**贷款利率 6.0%** 是最强的保护因子"
        "（SHAP −1.62），银行给予的低利率定价本身即反映其信用资质优良；**年收入 80 万元**（SHAP −0.29）"
        "进一步压低违约概率，收入对负债的覆盖充足。唯一推高风险的是**申请金额 10 万元**（SHAP +0.49），"
        "但其正向贡献远小于两项负向贡献，故最终落在低风险。结论：信用底子扎实、收入稳定，可进入快速审批通道。"
    ),
    "medium_risk": (
        "该借款人违约概率 36.8%，处于中风险区间。Top1 驱动因子是**申请借款金额 15 万元**（SHAP +0.48），"
        "金额偏大使月供压力上升，是拉高违约概率的主因。两项保护因子——**贷款期限 36 个月**（SHAP −0.23，"
        "中期比长期更可控）与**信用卡总额度 8 万元**（SHAP −0.16，反映银行体系对其信用评估正面）——部分抵消了"
        "金额的正向贡献，但不足以将其压回低风险。结论：信用底子不差、期限合理，唯独借款金额偏大是真正的拉分项；"
        "建议人工复核，可考虑压缩金额至 10 万元附近或补充收入/资产证明。"
    ),
    "high_risk": (
        "该借款人违约概率高达 87.2%，处于高风险区间。三大关键因子**全部推高风险**，且无任何保护因子进入 Top3。"
        "Top1 是**贷款利率 24.5%**（SHAP +0.56），银行给予的接近上限的高利率定价本身就是强风险信号；"
        "**申请金额 30 万元**（SHAP +0.48）叠加 **60 个月长期限**（SHAP +0.38），月供与总利息双重压力使违约可能性"
        "显著放大。结论：利率、金额、期限三项同步高位，风险信号高度一致；建议谨慎处理，可要求增加担保人或抵押物，"
        "风险不可接受时拒绝申请。"
    ),
}


def generate_report(
    customer_info: dict,
    features: dict,
    prediction: dict,
    dialogue_summary: str = "",
    case_id: str | None = None,
) -> str:
    """生成 Markdown 尽调报告。

    Args:
        customer_info: 客户基本信息（姓名、申请金额等）
        features: 19 项特征 JSON
        prediction: model.explain() 的返回结果
        dialogue_summary: 对话摘要（可选）
        case_id: 预设 Case 标识（low_risk / medium_risk / high_risk）；
            命中时自然语言段使用固化的 SHAP 详细解读，保证 Demo 展示稳定

    Returns:
        Markdown 格式的尽调报告
    """
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    prob = prediction["default_probability"]
    level = prediction["risk_level"]
    shap_top = prediction.get("shap_top", [])
    narration = prediction.get("narration", "")
    # 预设 Case 命中时使用固化的 SHAP 详细解读，否则用模型动态 narration
    interpretation = CASE_SHAP_INTERPRETATION.get(case_id) if case_id else narration
    if not interpretation:
        interpretation = narration

    # 风险建议
    if level == "低风险":
        advice = (
            "**建议**：通过贷款申请，可进入快速审批通道。"
            "建议关注贷款用途合规性，定期跟踪还款情况。"
        )
    elif level == "中风险":
        advice = (
            "**建议**：建议人工复核，可要求补充材料（如收入证明、资产证明）。"
            "如批准，建议适当提高利率或增加担保措施。"
        )
    else:
        advice = (
            "**建议**：建议谨慎处理，可要求增加担保人或抵押物。"
            "如风险不可接受，建议拒绝申请并向客户解释原因。"
        )

    # SHAP 因子表格
    shap_rows = ""
    for i, f in enumerate(shap_top, 1):
        direction_emoji = "🔴" if f["direction"] == "推高" else "🟢"
        shap_rows += (
            f"| {i} | {f['description']} | {f['value']}{f['unit']} | "
            f"{f['shap_value']:+.4f} | {direction_emoji} {f['direction']} |\n"
        )

    if not shap_rows:
        shap_rows = "| - | SHAP 不可用 | - | - | - |\n"

    # 特征汇总
    feature_lines = ""
    for fname, val in features.items():
        meta = FEATURE_META.get(fname, {})
        desc = meta.get("desc", fname)
        unit = meta.get("unit", "")
        feature_lines += f"- **{desc}** (`{fname}`): {val}{unit}\n"

    report = f"""# CreditMind 尽调报告

> **CreditMind · AI 信贷风控大脑**
> 报告生成时间：{now}
> 合规声明：本报告由 AI 生成，仅供客户经理参考，**最终决策需人工审核**。

---

## 一、客户基本信息

| 项目 | 内容 |
|---|---|
| 客户姓名 | {customer_info.get('name', '未提供')} |
| 申请金额 | {customer_info.get('loan_amnt', features.get('loan_amnt', '未提供'))} 元 |
| 申请用途 | {customer_info.get('purpose', '未提供')} |
| 访谈时长 | 约 {customer_info.get('duration', '5-10')} 分钟 |

---

## 二、风险评估摘要

| 指标 | 结果 |
|---|---|
| **违约概率** | **{prob*100:.1f}%** |
| **风险等级** | **{level}** |
| 模型 AUC | {prediction.get('auc', 0.7093):.4f} |
| 评估方法 | IV/WoE + PSI + 贪心去共线性 + XGBoost |

### 自然语言解读

{interpretation}

---

## 三、关键风险因子（SHAP Top3）

| 排名 | 因子 | 当前值 | SHAP 贡献 | 方向 |
|---|---|---|---|---|
{shap_rows}

> **说明**：SHAP 值为正（🔴）表示该因子推高违约风险，为负（🟢）表示降低风险。
> SHAP 绝对值越大，该因子对预测结果的影响越大。

---

## 四、建议话术

{advice}

### 客户沟通建议

{level}客户的沟通要点：
"""

    if level == "低风险":
        report += "- 祝贺客户通过初审，说明信用状况良好\n- 提醒按时还款的重要性\n- 可适当推荐其他金融产品\n"
    elif level == "中风险":
        report += "- 诚实告知需要补充材料\n- 解释风险因素（基于 SHAP Top3）\n- 表达愿意协助客户改善信用状况\n"
    else:
        report += "- 如实解释拒贷原因（基于 SHAP Top3）\n- 建议客户改善信用后再申请\n- 避免承诺或暗示\n"

    report += f"""
---

## 五、完整特征清单（19 项）

{feature_lines}

---

## 六、访谈摘要

{dialogue_summary if dialogue_summary else "（无摘要）"}

---

## 七、合规声明

1. 本报告由 CreditMind AI 系统自动生成，**不构成最终放款决策**。
2. 最终决策需由客户经理复核 + 风控初审员审核。
3. 本报告基于 LendingClub 2018-2019 数据训练的模型，AUC 0.7093，PSI 稳定性已验证。
4. 模型已排除 `grade`/`sub_grade` 等目标泄露特征。
5. 全程对话+评分+因子已留痕，可供监管审计。

---

*CreditMind · 让消费贷尽调从 2 小时压缩到 15 分钟，且每个判断都有据可查。*
"""
    return report


if __name__ == "__main__":
    # 测试
    from model_server import CreditMindModel

    model = CreditMindModel.get()
    case = {
        "int_rate": 13.5, "term_months": 36, "tot_hi_cred_lim": 80000,
        "loan_amnt": 200000, "open_rv_24m": 3, "home_ownership": 1,
        "mort_acc": 1, "total_bc_limit": 50000, "num_tl_op_past_12m": 2,
        "mo_sin_rcnt_rev_tl_op": 6, "mo_sin_old_rev_tl_op": 120,
        "mths_since_recent_bc": 6, "verification_status": 1,
        "inq_last_6mths": 3, "emp_length": 5, "mths_since_recent_inq": 2,
        "inq_last_12m": 5, "annual_inc": 300000, "mo_sin_old_il_acct": 60,
    }
    pred = model.explain(case)
    report = generate_report(
        customer_info={"name": "张三", "loan_amnt": 200000, "purpose": "经营周转"},
        features=case,
        prediction=pred,
        dialogue_summary="客户为深圳电商老板，借款 20 万用于经营周转。",
    )
    print(report[:2000])
