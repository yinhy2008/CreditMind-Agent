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

from model_server import CreditMindModel
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
        st.divider()
        st.header(f"📄 Case: {case['name']}")

        # 客户信息
        st.subheader("👤 客户基本信息")
        ci = case["customer_info"]
        info_col1, info_col2, info_col3 = st.columns(3)
        info_col1.metric("客户姓名", ci["name"])
        info_col2.metric("申请金额", f"{ci['loan_amnt']:,} 元")
        info_col3.metric("申请用途", ci["purpose"])

        # 特征表
        st.subheader("📊 借款人特征（19 项）")
        feats = case["features"]
        feat_cols = st.columns(4)
        for i, (fname, val) in enumerate(feats.items()):
            with feat_cols[i % 4]:
                st.metric(fname, f"{val:,.1f}")

        # 推理
        st.divider()
        st.subheader("🔮 模型推理")
        with st.spinner("正在推理..."):
            pred = model.explain(feats)

        # 结果展示
        res_col1, res_col2, res_col3 = st.columns(3)
        prob_pct = pred["default_probability"] * 100
        risk_emoji = {"低风险": "🟢", "中风险": "🟡", "高风险": "🔴"}[pred["risk_level"]]

        res_col1.metric("违约概率", f"{prob_pct:.1f}%")
        res_col2.metric("风险等级", f"{risk_emoji} {pred['risk_level']}")
        res_col3.metric("模型 AUC", f"{pred['auc']:.4f}")

        # SHAP Top3
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

        # 自然语言解读
        st.info(pred.get("narration", ""))

        # 报告
        st.divider()
        st.subheader("📄 尽调报告")
        report = generate_report(
            customer_info=ci,
            features=feats,
            prediction=pred,
            dialogue_summary=f"客户 {case['name']}，{case['profile']}。",
        )
        st.markdown(report)
        st.download_button("下载报告 (Markdown)", report, file_name=f"creditmind_report_{selected}.md")


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
        with cols[i % 3]:
            val = st.number_input(f"{fname}", value=0.0, format="%.2f", key=f"input_{fname}")
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

        prob_pct = pred["default_probability"] * 100
        risk_emoji = {"低风险": "🟢", "中风险": "🟡", "高风险": "🔴"}[pred["risk_level"]]

        c1, c2, c3 = st.columns(3)
        c1.metric("违约概率", f"{prob_pct:.1f}%")
        c2.metric("风险等级", f"{risk_emoji} {pred['risk_level']}")
        c3.metric("模型 AUC", f"{pred['auc']:.4f}")

        st.info(pred.get("narration", ""))

        shap_data = []
        for f in pred.get("shap_top", []):
            shap_data.append({
                "因子": f["description"],
                "当前值": f"{f['value']}{f['unit']}",
                "SHAP": f"{f['shap_value']:+.4f}",
                "方向": "🔴" if f["direction"] == "推高" else "🟢",
            })
        if shap_data:
            st.table(shap_data)


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
            if st.button("🔮 生成尽调报告", type="primary"):
                feats = agent.get_features()
                # 补全缺失字段
                for f in agent.features:
                    if f not in feats or feats[f] is None:
                        feats[f] = 0.0

                pred = model.explain(feats)
                report = generate_report(
                    customer_info={"name": "访谈客户", "loan_amnt": feats.get("loan_amnt", 0)},
                    features=feats,
                    prediction=pred,
                    dialogue_summary="\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[:10]]),
                )
                st.markdown(report)
                st.download_button("下载报告", report, file_name="creditmind_interview_report.md")
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
