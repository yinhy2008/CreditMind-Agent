"""
CreditMind · 模型服务层
=======================
复用 V1.ipynb 的 preprocess + V2.md 的 IV/WoE+PSI+贪心去共线性方法论，
训练 XGBoost 模型并提供推理 API（含 SHAP Top3 解释）。

核心能力：
- train()              : 训练模型并保存到 artifacts/
- predict(features)    : 输入 19 特征 JSON，输出违约概率 + 风险等级
- explain(features)    : 输出 SHAP Top3 因子 + 自然语言解读
- get_feature_template(): 返回 19 特征的提问模板（供 Agent 使用）

依赖：xgboost, shap, scikit-learn, pandas, numpy
"""
from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

# SHAP 可选（MVP 允许降级）
try:
    import shap
    SHAP_OK = True
except ImportError:
    SHAP_OK = False

# ------------------------------------------------------------------
# 路径配置
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ARTIFACTS_DIR = BASE_DIR / "artifacts"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

DATA_CSV = BASE_DIR.parent / "lendingclub_default_prediction" / "lendingclub_2018_2019_sample.csv"
MODEL_PATH = ARTIFACTS_DIR / "creditmind_xgb.json"
SCALER_PATH = ARTIFACTS_DIR / "feature_meta.json"

RANDOM_STATE = 42

# ------------------------------------------------------------------
# CreditMind 最终 19 特征（来自竞品对比实验 creditmind_features.json）
# 顺序固定，与训练时保持一致
# ------------------------------------------------------------------
FINAL_FEATURES = [
    "int_rate", "term_months", "tot_hi_cred_lim", "loan_amnt",
    "open_rv_24m", "home_ownership", "mort_acc", "total_bc_limit",
    "num_tl_op_past_12m", "mo_sin_rcnt_rev_tl_op", "mo_sin_old_rev_tl_op",
    "mths_since_recent_bc", "verification_status", "inq_last_6mths",
    "emp_length", "mths_since_recent_inq", "inq_last_12m",
    "annual_inc", "mo_sin_old_il_acct",
]

# 特征元信息：类型、业务含义、单位、提问模板
FEATURE_META = {
    "int_rate": {"type": "float", "unit": "%", "desc": "贷款利率", "question": "您申请的贷款年利率是多少？（如 12.5%）"},
    "loan_amnt": {"type": "float", "unit": "元", "desc": "申请借款金额", "question": "您本次申请借款多少金额？"},
    "term_months": {"type": "float", "unit": "月", "desc": "贷款期限", "question": "您申请的贷款期限是 36 个月还是 60 个月？"},
    "tot_hi_cred_lim": {"type": "float", "unit": "元", "desc": "总高信用额度", "question": "您所有信用卡和循环账户的总额度大约是多少？"},
    "funded_amnt": {"type": "float", "unit": "元", "desc": "放款金额", "question": "您本次申请借款多少金额？"},
    "open_rv_24m": {"type": "int", "unit": "个", "desc": "24个月内新开循环账户数", "question": "过去 24 个月您新开了几个信用卡或循环账户？"},
    "home_ownership": {"type": "cat", "categories": ["RENT", "MORTGAGE", "OWN", "OTHER"], "desc": "房屋所有权", "question": "您目前的住房是租房、按揭、自有还是其他？"},
    "mort_acc": {"type": "int", "unit": "个", "desc": "抵押账户数", "question": "您名下有几个房贷抵押账户？"},
    "total_bc_limit": {"type": "float", "unit": "元", "desc": "信用卡总额度", "question": "您所有信用卡的额度加起来大约多少？"},
    "num_tl_op_past_12m": {"type": "int", "unit": "个", "desc": "12个月内新开账户数", "question": "过去 12 个月您新开了几个信用账户？"},
    "mo_sin_rcnt_rev_tl_op": {"type": "float", "unit": "月", "desc": "最近开循环账户距今年月", "question": "您最近一次开信用卡是几个月前？"},
    "mo_sin_old_rev_tl_op": {"type": "float", "unit": "月", "desc": "最早开循环账户距今年月", "question": "您最早开的一张信用卡是几个月前？"},
    "mths_since_recent_bc": {"type": "float", "unit": "月", "desc": "最近开信用卡距今月数", "question": "您最近一次开信用卡距今几个月？"},
    "verification_status": {"type": "cat", "categories": ["Verified", "Source Verified", "Not Verified"], "yes_value": "Source Verified", "no_value": "Not Verified", "desc": "收入验证状态", "question": "您的收入是否经过平台或第三方验证？"},
    "inq_last_6mths": {"type": "int", "unit": "次", "desc": "6个月内查询次数", "question": "过去 6 个月您的征信被查询过几次？"},
    "emp_length": {"type": "float", "unit": "年", "desc": "工作年限", "question": "您在当前雇主工作多少年了？（<1 年填 0）"},
    "mths_since_recent_inq": {"type": "float", "unit": "月", "desc": "最近查询距今月数", "question": "您最近一次被查询征信是几个月前？"},
    "inq_last_12m": {"type": "int", "unit": "次", "desc": "12个月内查询次数", "question": "过去 12 个月您的征信被查询过几次？"},
    "annual_inc": {"type": "float", "unit": "元", "desc": "年收入", "question": "您的家庭年税前收入大约是多少？"},
    "mo_sin_old_il_acct": {"type": "float", "unit": "月", "desc": "最早开分期账户距今月数", "question": "您最早开的一个分期贷款账户是几个月前？"},
}


# ------------------------------------------------------------------
# 数据预处理（复用 V1.ipynb 的 preprocess 逻辑，简化版）
# ------------------------------------------------------------------
def load_and_preprocess(csv_path: Path = DATA_CSV) -> pd.DataFrame:
    """加载 LendingClub 数据并做基础编码，返回可用于 IV/PSI 计算的 DataFrame。"""
    df = pd.read_csv(csv_path, low_memory=False)
    df = df.copy()

    # term → term_months
    if "term" in df.columns:
        df["term_months"] = df["term"].astype(str).str.extract(r"(\d+)").astype(float)
        df.drop(columns=["term"], inplace=True)

    # emp_length → 数值
    emp_map = {
        "< 1 year": 0, "1 year": 1, "2 years": 2, "3 years": 3,
        "4 years": 4, "5 years": 5, "6 years": 6, "7 years": 7,
        "8 years": 8, "9 years": 9, "10+ years": 10,
    }
    if "emp_length" in df.columns:
        df["emp_length"] = df["emp_length"].map(emp_map).fillna(-1)

    # 日期列删除
    for c in ["issue_d", "earliest_cr_line", "last_credit_pull_d"]:
        if c in df.columns:
            df.drop(columns=[c], inplace=True)

    # 分类列 → category codes
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype("category").cat.codes

    # 常数列删除
    for c in list(df.columns):
        if c != "default" and df[c].nunique() <= 1:
            df.drop(columns=[c], inplace=True)

    # 高缺失列删除
    for c in list(df.columns):
        if c != "default" and df[c].isnull().mean() > 0.8:
            df.drop(columns=[c], inplace=True)

    # 数值列填缺失（用中位数）
    for c in df.select_dtypes(include=[np.number]).columns:
        if c != "default":
            df[c] = df[c].fillna(df[c].median())

    return df


# ------------------------------------------------------------------
# IV / PSI（复用 competitive_benchmark.py 的实现）
# ------------------------------------------------------------------
def calculate_iv(series: pd.Series, target: pd.Series, n_bins: int = 10) -> float:
    s = series.dropna()
    t = target.loc[s.index]
    if s.nunique() <= 1 or len(s) < 50:
        return 0.0
    try:
        if s.dtype.kind in "ifb" and s.nunique() > n_bins:
            bins = pd.qcut(s, n_bins, retbins=True, duplicates="drop")[1]
            bins[0] = -np.inf
            bins[-1] = np.inf
            groups = pd.cut(s, bins=bins, include_lowest=True)
        else:
            groups = s
        tab = pd.crosstab(groups, t).replace(0, 0.5)
        woe = np.log(tab[1] / tab[0])
        iv = ((tab[1] / tab[1].sum()) - (tab[0] / tab[0].sum())) * woe
        return float(iv.sum())
    except Exception:
        return 0.0


def calculate_psi(baseline: pd.Series, comparison: pd.Series, n_bins: int = 10) -> float:
    b, c = baseline.dropna(), comparison.dropna()
    if len(b) < 50 or len(c) < 50 or b.nunique() <= 1:
        return 0.0
    try:
        bins = pd.qcut(b, n_bins, retbins=True, duplicates="drop")[1]
        bins[0], bins[-1] = -np.inf, np.inf
        b_counts = pd.cut(b, bins=bins).value_counts(normalize=True).sort_index()
        c_counts = pd.cut(c, bins=bins).value_counts(normalize=True).sort_index()
        return float(((b_counts - c_counts) * np.log((b_counts + 1e-6) / (c_counts + 1e-6))).sum())
    except Exception:
        return 0.0


def greedy_select(candidates, iv_series, corr, threshold=0.7):
    sorted_feats = sorted(candidates, key=lambda f: iv_series.get(f, 0), reverse=True)
    selected = []
    for f in sorted_feats:
        if f not in corr.columns:
            selected.append(f)
            continue
        if not any(abs(corr.loc[f, s]) >= threshold for s in selected if s in corr.columns):
            selected.append(f)
    return selected


# ------------------------------------------------------------------
# 训练流程
# ------------------------------------------------------------------
def train():
    """完整训练流程：加载 → IV/PSI 筛选 → 贪心去共线性 → XGBoost 训练 → 保存。"""
    print("=" * 60)
    print("CreditMind 模型训练")
    print("=" * 60)

    df = load_and_preprocess()
    print(f"[load] shape: {df.shape}, default rate: {df['default'].mean():.4f}")

    target = df["default"]
    feats = [c for c in df.columns if c != "default"]

    # 排除目标泄露列
    leak_cols = ["grade", "sub_grade"]
    feats_safe = [c for c in feats if c not in leak_cols]
    print(f"[train] 排除泄露列: {leak_cols}, 候选特征: {len(feats_safe)}")

    # IV 计算
    iv_series = pd.Series({f: calculate_iv(df[f], target) for f in feats_safe})
    qualified = iv_series[iv_series >= 0.02].index.tolist()
    print(f"[train] IV≥0.02 合格特征: {len(qualified)}")

    # 划分
    X_tr_raw, X_te_raw, y_tr, y_te = train_test_split(
        df[feats_safe], target, test_size=0.2, random_state=RANDOM_STATE, stratify=target
    )

    # PSI
    psi_series = pd.Series({f: calculate_psi(X_tr_raw[f], X_te_raw[f]) for f in qualified})
    stable = psi_series[psi_series < 0.25].index.tolist()
    print(f"[train] PSI<0.25 稳定特征: {len(stable)}")

    # 贪心去共线性
    corr = X_tr_raw[stable].corr()
    final_feats = greedy_select(stable, iv_series, corr, threshold=0.7)
    print(f"[train] 最终特征: {len(final_feats)}")
    print(f"[train] 特征清单: {final_feats}")

    # 训练 XGBoost
    X_tr = X_tr_raw[final_feats]
    X_te = X_te_raw[final_feats]
    scale_pos = (y_tr == 0).sum() / (y_tr == 1).sum()

    model = xgb.XGBClassifier(
        n_estimators=200, max_depth=6, learning_rate=0.1,
        subsample=0.8, colsample_bytree=0.8,
        scale_pos_weight=scale_pos,
        eval_metric="auc", random_state=RANDOM_STATE,
        n_jobs=-1, tree_method="hist",
    )
    model.fit(X_tr, y_tr, eval_set=[(X_te, y_te)], verbose=False)

    prob = model.predict_proba(X_te)[:, 1]
    auc = roc_auc_score(y_te, prob)
    print(f"[train] AUC on test: {auc:.4f}")

    # 保存模型
    model.save_model(str(MODEL_PATH))
    print(f"[train] model saved → {MODEL_PATH}")

    # 保存特征元信息
    meta = {
        "final_features": final_feats,
        "iv_top15": iv_series.head(15).to_dict(),
        "auc": auc,
        "psi_summary": {
            "stable": int((psi_series < 0.1).sum()),
            "mild_drift": int(((psi_series >= 0.1) & (psi_series < 0.25)).sum()),
            "significant_drift": int((psi_series >= 0.25).sum()),
        },
    }
    with open(SCALER_PATH, "w") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"[train] meta saved → {SCALER_PATH}")

    return model, final_feats, auc


# ------------------------------------------------------------------
# 推理服务
# ------------------------------------------------------------------
class CreditMindModel:
    """CreditMind 模型推理服务（单例）。"""

    _instance = None

    def __init__(self):
        self.model = xgb.XGBClassifier()
        self.model.load_model(str(MODEL_PATH))
        with open(SCALER_PATH) as f:
            meta = json.load(f)
        self.features = meta["final_features"]
        self.auc = meta["auc"]
        self._explainer = None

    @classmethod
    def get(cls) -> "CreditMindModel":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _get_explainer(self):
        if self._explainer is None and SHAP_OK:
            self._explainer = shap.TreeExplainer(self.model)
        return self._explainer

    def predict(self, features: dict[str, Any]) -> dict:
        """输入 19 特征 JSON，输出违约概率 + 风险等级。"""
        # 构造单行 DataFrame，按训练特征顺序
        row = {}
        for f in self.features:
            v = features.get(f, 0)
            # 分类列已经在 preprocess 阶段编码为数值，这里直接用
            row[f] = float(v) if v not in (None, "") else 0.0

        X = pd.DataFrame([row], columns=self.features)
        prob = float(self.model.predict_proba(X)[0, 1])

        # 风险等级
        if prob < 0.30:
            risk_level = "低风险"
        elif prob < 0.60:
            risk_level = "中风险"
        else:
            risk_level = "高风险"

        return {
            "default_probability": round(prob, 4),
            "risk_level": risk_level,
            "auc": self.auc,
        }

    def explain(self, features: dict[str, Any], top_k: int = 3) -> dict:
        """输出 SHAP Top-K 因子 + 自然语言解读。"""
        result = self.predict(features)
        prob = result["default_probability"]

        explainer = self._get_explainer()
        if explainer is None:
            return {**result, "shap_top": [], "note": "SHAP 不可用"}

        row = {}
        for f in self.features:
            v = features.get(f, 0)
            row[f] = float(v) if v not in (None, "") else 0.0
        X = pd.DataFrame([row], columns=self.features)

        sv = explainer.shap_values(X)[0]
        # 取绝对值 Top-K
        idx_sorted = np.argsort(-np.abs(sv))[:top_k]
        top_factors = []
        for i in idx_sorted:
            fname = self.features[i]
            shap_val = float(sv[i])
            feat_val = row[fname]
            meta = FEATURE_META.get(fname, {})
            direction = "推高" if shap_val > 0 else "降低"
            top_factors.append({
                "feature": fname,
                "description": meta.get("desc", fname),
                "value": feat_val,
                "unit": meta.get("unit", ""),
                "shap_value": round(shap_val, 4),
                "direction": direction,
            })

        # 自然语言解读
        factor_text = "、".join([f"{f['description']}({f['value']}{f['unit']})" for f in top_factors])
        narration = (
            f"该借款人违约概率为 {prob*100:.1f}%，{result['risk_level']}。"
            f"主要风险驱动因子（SHAP Top{top_k}）：{factor_text}。"
        )

        return {**result, "shap_top": top_factors, "narration": narration}

    def get_feature_template(self) -> list[dict]:
        """返回 19 特征的提问模板（供 Agent 使用）。"""
        template = []
        for f in self.features:
            meta = FEATURE_META.get(f, {})
            template.append({
                "feature": f,
                "type": meta.get("type", "float"),
                "desc": meta.get("desc", f),
                "unit": meta.get("unit", ""),
                "question": meta.get("question", f"请输入 {f}："),
                "categories": meta.get("categories"),
                "yes_value": meta.get("yes_value"),
                "no_value": meta.get("no_value"),
            })
        return template


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "train":
        train()
    elif len(sys.argv) > 1 and sys.argv[1] == "test":
        # 用一个虚拟 Case 测试推理
        if not MODEL_PATH.exists():
            print("模型未训练，先运行: python model_server.py train")
            sys.exit(1)
        m = CreditMindModel.get()
        # 虚拟 Case：35 岁深圳电商老板借 20 万
        case = {
            "int_rate": 13.5, "term_months": 36, "tot_hi_cred_lim": 80000,
            "loan_amnt": 200000, "open_rv_24m": 3, "home_ownership": 1,  # MORTGAGE
            "mort_acc": 1, "total_bc_limit": 50000, "num_tl_op_past_12m": 2,
            "mo_sin_rcnt_rev_tl_op": 6, "mo_sin_old_rev_tl_op": 120,
            "mths_since_recent_bc": 6, "verification_status": 1,  # Source Verified
            "inq_last_6mths": 3, "emp_length": 5, "mths_since_recent_inq": 2,
            "inq_last_12m": 5, "annual_inc": 300000, "mo_sin_old_il_acct": 60,
        }
        result = m.explain(case)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("用法: python model_server.py [train|test]")
