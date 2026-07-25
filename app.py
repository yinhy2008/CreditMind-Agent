"""
CreditMind · Streamlit Web Demo
================================
路演演示界面。

运行：streamlit run app.py

功能：
1. 选择预设 Case 或手动输入
2. 模拟 Agent 访谈（或直接用 Case 数据）
3. 模型推理 + SHAP 解释
4. 生成尽调报告
"""
from __future__ import annotations

import sys
from pathlib import Path

# 确保能 import 同目录模块
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from model_server import CreditMindModel, FEATURE_META
from cases import CASES, list_cases
from report_generator import generate_report
from extractor import validate_features


# ------------------------------------------------------------------
# 页面配置
# ------------------------------------------------------------------
st.set_page_config(
    page_title="CreditMind · AI 信贷风控大脑",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource
def get_model():
    return CreditMindModel.get()


# ------------------------------------------------------------------
# 公共辅助：分类特征中文映射 / 推理结果渲染 / 特征可读展示
# ------------------------------------------------------------------
CAT_CN = {
    "RENT": "租房", "MORTGAGE": "按揭购房", "OWN": "自有住房", "OTHER": "其他",
    "Verified": "已验证", "Source Verified": "第三方已验证", "Not Verified": "未验证",
}


def show_prediction(pred: dict):
    """渲染推理结果：风险指标 + SHAP Top3 + 自然语言解读（三模式共用）。"""
    prob_pct = pred["default_probability"] * 100
    risk_emoji = {"低风险": "🟢", "中风险": "🟡", "高风险": "🔴"}[pred["risk_level"]]
    c1, c2, c3 = st.columns(3)
    c1.metric("违约概率", f"{prob_pct:.1f}%")
    c2.metric("风险等级", f"{risk_emoji} {pred['risk_level']}")
    c3.metric("模型 AUC", f"{pred['auc']:.4f}")

    st.subheader("📈 关键风险因子（SHAP Top3）")
    shap_data = []
    for f in pred.get("shap_top", []):
        shap_data.append({
            "因子": f["description"],
            "当前值": f"{f['value']}{f['unit']}",
            "SHAP 贡献": f"{f['shap_value']:+.4f}",
            "方向": "🔴 推高风险" if f["direction"] == "推高" else "🟢 降低风险",
        })
    if shap_data:
        st.table(shap_data)
    st.info(pred.get("narration", ""))


def feature_display(fname: str, val):
    """把特征值转成可读中文展示，返回 (label, 显示文本)。"""
    meta = FEATURE_META.get(fname, {})
    label = meta.get("desc", fname)
    unit = meta.get("unit", "")
    if meta.get("type") == "cat":
        cats = meta.get("categories", [])
        if isinstance(val, int) and 0 <= val < len(cats):
            disp = CAT_CN.get(cats[val], cats[val])
        else:
            disp = str(val)
    elif isinstance(val, (int, float)):
        disp = f"{val:,.1f}{unit}"
    else:
        disp = str(val)
    return label, disp


# ------------------------------------------------------------------
# 侧边栏
# ------------------------------------------------------------------
st.sidebar.title("🧠 CreditMind")
st.sidebar.caption("AI 信贷风控大脑")
st.sidebar.divider()

mode = st.sidebar.radio("选择模式", ["📋 预设 Case 演示", "✏️ 手动输入特征", "💬 Agent 访谈模拟"])

st.sidebar.divider()
st.sidebar.markdown("### 模型信息")
model = get_model()
st.sidebar.markdown(f"- **AUC**: {model.auc:.4f}")
st.sidebar.markdown(f"- **特征数**: {len(model.features)}")
st.sidebar.markdown("- **方法论**: IV/WoE + PSI + 贪心去共线性")
st.sidebar.markdown("- **模型**: XGBoost + SHAP")

st.sidebar.divider()
st.sidebar.markdown("### 合规声明")
st.sidebar.warning("本系统仅供演示，不构成放款决策。最终决策需人工审核。")


# ------------------------------------------------------------------
# 主页面
# ------------------------------------------------------------------
st.title("🧠 CreditMind · AI 信贷风控大脑")
st.caption("让消费贷尽调从 2 小时压缩到 15 分钟，且每个判断都有据可查。")

# ------------------------------------------------------------------
# 模式 1：预设 Case 演示
# ------------------------------------------------------------------
if mode == "📋 预设 Case 演示":
    st.header("📋 预设 Case 演示")

    col1, col2, col3 = st.columns(3)
    case_list = list_cases()
    selected = None

    for i, (col, c) in enumerate(zip([col1, col2, col3], case_list)):
        with col:
            risk_emoji = {"低风险": "🟢", "中风险": "🟡", "高风险": "🔴"}[c["expected_risk"]]
            if st.button(f"{risk_emoji} {c['name']}\n{c['profile'][:20]}...", key=f"case_{c['id']}"):
                selected = c["id"]

    if selected:
        case = CASES[selected]
        # 切换 case 时清空上一次的推理 / 报告
        st.session_state.case_pred = None
        st.session_state.case_report = None
        st.divider()
        st.header(f"📄 Case: {case['name']}")

        # 客户信息
        st.subheader("👤 客户基本信息")
        ci = case["customer_info"]
        info_col1, info_col2, info_col3 = st.columns(3)
        info_col1.metric("客户姓名", ci["name"])
        info_col2.metric("申请金额", f"{ci['loan_amnt']:,} 元")
        info_col3.metric("申请用途", ci["purpose"])

        # 特征表（中文业务含义）
        st.subheader("📊 借款人特征（19 项）")
        feats = case["features"]
        feat_cols = st.columns(4)
        for i, (fname, val) in enumerate(feats.items()):
            label, disp = feature_display(fname, val)
            with feat_cols[i % 4]:
                st.metric(label, disp)

        # 第一步：推理
        if st.button("🔮 推理", type="primary"):
            with st.spinner("正在推理..."):
                pred = model.explain(feats)
            st.session_state.case_pred = pred
            st.rerun()

        pred = st.session_state.get("case_pred")
        if pred is not None:
            st.divider()
            st.subheader("🔮 模型推理")
            show_prediction(pred)

            # 第二步：生成尽调报告
            if st.button("📄 生成尽调报告", type="primary"):
                report = generate_report(
                    customer_info=ci,
                    features=feats,
                    prediction=pred,
                    dialogue_summary=f"客户 {case['name']}，{case['profile']}。",
                )
                st.session_state.case_report = report
                st.rerun()

            if st.session_state.get("case_report"):
                st.divider()
                st.subheader("📄 尽调报告")
                st.markdown(st.session_state.case_report)
                st.download_button("下载报告 (Markdown)", st.session_state.case_report,
                                   file_name=f"creditmind_report_{selected}.md")


# ------------------------------------------------------------------
# 模式 2：手动输入特征
# ------------------------------------------------------------------
elif mode == "✏️ 手动输入特征":
    st.header("✏️ 手动输入特征")
    st.caption("输入 19 项特征值，进行风险推理。")

    feats = {}
    col1, col2, col3 = st.columns(3)
    cols = [col1, col2, col3]
    for i, fname in enumerate(model.features):
        meta = FEATURE_META.get(fname, {})
        label = meta.get("desc", fname)        # 业务含义，而非后台字段名
        unit = meta.get("unit", "")
        with cols[i % 3]:
            if meta.get("type") == "cat":
                cats = meta.get("categories", [])
                cn_opts = [CAT_CN.get(c, c) for c in cats]
                sel = st.selectbox(label, options=cn_opts, key=f"input_{fname}_cat")
                feats[fname] = cats.index(cats[cn_opts.index(sel)])
            else:
                help_text = f"单位：{unit}" if unit else None
                val = st.number_input(
                    label, value=0.0, format="%.2f",
                    key=f"input_{fname}", help=help_text,
                )
                feats[fname] = val

    if st.button("🔮 推理", type="primary"):
        # 校验
        validation = validate_features(feats)
        if not validation["is_valid"]:
            st.warning("特征值异常：")
            for a in validation["anomalies"]:
                st.write(f"- {a['feature']} = {a['value']}（合理范围 {a['range']}）")

        with st.spinner("推理中..."):
            pred = model.explain(feats)

        # 保存推理结果到 session_state，供下方结果区与报告按钮使用
        st.session_state.manual_pred = pred
        st.session_state.manual_feats = dict(feats)
        st.session_state.manual_report = None
        st.rerun()

    # 推理结果展示（推理后持久可见）
    pred = st.session_state.get("manual_pred")
    if pred is not None:
        show_prediction(pred)

        # 生成尽调报告（与访谈模式一致）
        if st.button("📝 生成尽调报告", type="primary"):
            feats0 = st.session_state.manual_feats
            pred0 = st.session_state.manual_pred
            report = generate_report(
                customer_info={"name": "手动录入客户", "loan_amnt": feats0.get("loan_amnt", 0)},
                features=feats0,
                prediction=pred0,
                dialogue_summary="（手动录入特征值，无访谈对话）",
            )
            st.session_state.manual_report = report
            st.rerun()

        if st.session_state.get("manual_report"):
            st.markdown(st.session_state.manual_report)
            st.download_button(
                "⬇️ 下载报告",
                st.session_state.manual_report,
                file_name="creditmind_manual_report.md",
            )


# ------------------------------------------------------------------
# 模式 3：Agent 访谈模拟
# ------------------------------------------------------------------
elif mode == "💬 Agent 访谈模拟":
    st.header("💬 Agent 访谈模拟")
    st.caption("模拟 CreditMind Agent 与借款人的多轮对话访谈。")

    # 初始化 session state
    if "agent" not in st.session_state:
        from interview_agent import InterviewAgent
        st.session_state.agent = InterviewAgent()
        st.session_state.agent_started = False
        st.session_state.messages = []

    agent = st.session_state.agent

    # 启动按钮
    if not st.session_state.agent_started:
        cust_name = st.text_input("客户姓名", value="张三")
        loan_amnt = st.number_input("申请金额（元）", value=200000, step=10000)
        purpose = st.text_input("贷款用途", value="经营周转")

        if st.button("🚀 启动访谈", type="primary"):
            opening = agent.start({"loan_amnt": loan_amnt})
            st.session_state.messages.append({"role": "assistant", "content": opening})
            st.session_state.agent_started = True
            st.rerun()
    else:
        # 显示对话
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

        # 进度
        prog = agent.progress()
        st.sidebar.markdown(f"### 访谈进度\n{prog['collected']}/{prog['total']}")

        if prog["complete"]:
            st.success("✅ 访谈完成！")
            feats = agent.get_features()
            # 补全缺失字段
            for f in agent.features:
                if f not in feats or feats[f] is None:
                    feats[f] = 0.0

            # 第一步：推理
            if st.button("🔮 推理", type="primary"):
                with st.spinner("推理中..."):
                    pred = model.explain(feats)
                st.session_state.interview_pred = pred
                st.session_state.interview_feats = dict(feats)
                st.rerun()

            pred = st.session_state.get("interview_pred")
            if pred is not None:
                st.divider()
                st.subheader("🔮 模型推理")
                show_prediction(pred)

                # 第二步：生成尽调报告
                if st.button("📄 生成尽调报告", type="primary"):
                    feats0 = st.session_state.interview_feats
                    pred0 = st.session_state.interview_pred
                    report = generate_report(
                        customer_info={"name": "访谈客户", "loan_amnt": feats0.get("loan_amnt", 0)},
                        features=feats0,
                        prediction=pred0,
                        dialogue_summary="\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:10]]),
                    )
                    st.session_state.interview_report = report
                    st.rerun()

                if st.session_state.get("interview_report"):
                    st.divider()
                    st.subheader("📄 尽调报告")
                    st.markdown(st.session_state.interview_report)
                    st.download_button("下载报告", st.session_state.interview_report,
                                       file_name="creditmind_interview_report.md")
        else:
            # 用户输入
            user_input = st.chat_input("请回答问题...")
            if user_input:
                st.session_state.messages.append({"role": "user", "content": user_input})
                resp = agent.chat(user_input)
                st.session_state.messages.append({"role": "assistant", "content": resp})
                st.rerun()


# ------------------------------------------------------------------
# 页脚
# ------------------------------------------------------------------
st.divider()
st.caption("CreditMind · AI 信贷风控大脑 · 模块四路演 Demo · 2026-07-25")
