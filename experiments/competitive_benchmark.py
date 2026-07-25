"""
CreditMind 竞品对比实验
=========================
在同一份 LendingClub 2018-2019 数据上对比三种方法论：

- 模型 A (Leaky Baseline): 仿 navyaneel/credit-risk-model
    · 17 特征，保留 grade/sub_grade（目标泄露）
    · 仅 LabelEncoding + 标准化
    · Logistic Regression
    · 无交叉验证、无 PSI 验证

- 模型 B (Feature-Heavy): 仿 shashi-hue/loan-default-risk-system
    · 数值 + 分类全量特征（约 80+）
    · LabelEncoding（无 IV/WoE）
    · XGBoost + 简单 GridSearch
    · 有 SHAP，无 PSI 时间稳定性验证

- 模型 C (CreditMind): IV/WoE + PSI + 贪心去共线性 + XGBoost
    · IV≥0.02 筛选 + PSI<0.25 + 贪心去共线性
    · 明确排除 grade/sub_grade（防泄露）
    · XGBoost + scale_pos_weight
    · SHAP + PSI 双解释

输出：
- results/summary.csv  对比表
- results/model_a_roc.png / model_b_roc.png / model_c_roc.png
- results/psi_report.csv  CreditMind 的 PSI 稳定性报告
- results/shap_top15.png  CreditMind 的 SHAP Top15 特征
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# ------------------------------------------------------------------
# 路径配置
# ------------------------------------------------------------------
DATA_CSV = Path(
    "/Users/yolanda/NanTe2025/金融AIagent暑假集训/模块四/lendingclub_default_prediction/lendingclub_2018_2019_sample.csv"
)
OUT_DIR = Path(__file__).resolve().parent / "results"
OUT_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------
# 数据加载与基础清洗
# ------------------------------------------------------------------
def load_raw() -> pd.DataFrame:
    df = pd.read_csv(DATA_CSV, low_memory=False)
    print(f"[load] raw shape: {df.shape}")
    print(f"[load] default rate: {df['default'].mean():.4f}")
    return df


def encode_basic(df: pd.DataFrame) -> pd.DataFrame:
    """基础编码：term、emp_length、分类列 LabelEncoding。保留所有列（含 grade/sub_grade）。"""
    df = df.copy()

    # term → 数字
    if "term" in df.columns:
        df["term_months"] = df["term"].astype(str).str.extract(r"(\d+)").astype(float)
        df.drop(columns=["term"], inplace=True)

    # emp_length → 有序数值
    emp_map = {
        "< 1 year": 0, "1 year": 1, "2 years": 2, "3 years": 3,
        "4 years": 4, "5 years": 5, "6 years": 6, "7 years": 7,
        "8 years": 8, "9 years": 9, "10+ years": 10,
    }
    if "emp_length" in df.columns:
        df["emp_length"] = df["emp_length"].map(emp_map).fillna(-1)

    # 日期列直接删除（无法直接编码）
    for c in ["issue_d", "earliest_cr_line", "last_credit_pull_d"]:
        if c in df.columns:
            df.drop(columns=[c], inplace=True)

    # 其余 object 列 → category codes
    for c in df.select_dtypes(include=["object"]).columns:
        df[c] = df[c].astype("category").cat.codes

    # 常数列删除
    for c in df.columns:
        if c != "default" and df[c].nunique() <= 1:
            df.drop(columns=[c], inplace=True)

    # 高缺失列删除（>80%）
    for c in list(df.columns):
        if c != "default" and df[c].isnull().mean() > 0.8:
            df.drop(columns=[c], inplace=True)

    # 数值列填缺失
    for c in df.select_dtypes(include=[np.number]).columns:
        if c != "default":
            df[c] = df[c].fillna(df[c].median())

    return df


# ------------------------------------------------------------------
# IV/WoE 与 PSI（CreditMind 方法论核心，迁移自 V2.md）
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
        tab = pd.crosstab(groups, t)
        tab = tab.replace(0, 0.5)  # 平滑
        woe = np.log(tab[1] / tab[0])
        iv = ((tab[1] / tab[1].sum()) - (tab[0] / tab[0].sum())) * woe
        return float(iv.sum())
    except Exception:
        return 0.0


def calculate_psi(baseline: pd.Series, comparison: pd.Series, n_bins: int = 10) -> float:
    b = baseline.dropna()
    c = comparison.dropna()
    if len(b) < 50 or len(c) < 50 or b.nunique() <= 1:
        return 0.0
    try:
        bins = pd.qcut(b, n_bins, retbins=True, duplicates="drop")[1]
        bins[0] = -np.inf
        bins[-1] = np.inf
        b_counts = pd.cut(b, bins=bins).value_counts(normalize=True).sort_index()
        c_counts = pd.cut(c, bins=bins).value_counts(normalize=True).sort_index()
        psi = ((b_counts - c_counts) * np.log((b_counts + 1e-6) / (c_counts + 1e-6))).sum()
        return float(psi)
    except Exception:
        return 0.0


def greedy_select(candidates, iv_series, corr, threshold=0.7):
    sorted_feats = sorted(candidates, key=lambda f: iv_series.get(f, 0), reverse=True)
    selected = []
    for f in sorted_feats:
        if f not in corr.columns:
            selected.append(f)
            continue
        conflict = any(abs(corr.loc[f, s]) >= threshold for s in selected if s in corr.columns)
        if not conflict:
            selected.append(f)
    return selected


# ------------------------------------------------------------------
# 模型 A：Leaky Baseline（仿 navyaneel）
# ------------------------------------------------------------------
def run_model_a(df_encoded: pd.DataFrame):
    print("\n" + "=" * 70)
    print("模型 A: Leaky Baseline (navyaneel 风格)")
    print("=" * 70)

    # 17 特征，包含 grade/sub_grade（目标泄露）
    feats_a = [
        "loan_amnt", "int_rate", "installment", "grade", "sub_grade",
        "term_months", "emp_length", "home_ownership", "annual_inc",
        "verification_status", "purpose", "dti", "delinq_2yrs",
        "inq_last_6mths", "open_acc", "pub_rec", "revol_util",
    ]
    feats_a = [c for c in feats_a if c in df_encoded.columns]
    print(f"[A] 使用特征数: {len(feats_a)}")
    print(f"[A] 是否包含 grade/sub_grade: {'grade' in feats_a or 'sub_grade' in feats_a}")

    X = df_encoded[feats_a]
    y = df_encoded["default"]

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    scaler = StandardScaler()
    X_tr_s = scaler.fit_transform(X_tr)
    X_te_s = scaler.transform(X_te)

    lr = LogisticRegression(
        penalty="l2", C=1.0, max_iter=1000, solver="lbfgs",
        class_weight="balanced", random_state=RANDOM_STATE,
    )
    lr.fit(X_tr_s, y_tr)
    prob = lr.predict_proba(X_te_s)[:, 1]
    pred = (prob >= 0.5).astype(int)

    auc = roc_auc_score(y_te, prob)
    fpr, tpr, _ = roc_curve(y_te, prob)
    ks = max(tpr - fpr)

    metrics = {
        "AUC-ROC": auc,
        "KS": ks,
        "Accuracy": accuracy_score(y_te, pred),
        "Precision": precision_score(y_te, pred, zero_division=0),
        "Recall": recall_score(y_te, pred),
        "F1": f1_score(y_te, pred),
        "特征数": len(feats_a),
        "数据泄露": "是 (grade/sub_grade)" if ("grade" in feats_a or "sub_grade" in feats_a) else "否",
        "PSI稳定性": "未验证",
        "可解释性": "系数",
    }
    print(f"[A] AUC={auc:.4f}, KS={ks:.4f}")
    _plot_roc(fpr, tpr, auc, "Model A (Leaky Baseline)", OUT_DIR / "model_a_roc.png")
    return metrics


# ------------------------------------------------------------------
# 模型 B：Feature-Heavy（仿 shashi-hue）
# ------------------------------------------------------------------
def run_model_b(df_encoded: pd.DataFrame):
    print("\n" + "=" * 70)
    print("模型 B: Feature-Heavy (shashi-hue 风格)")
    print("=" * 70)

    # 全量特征（排除 default），不排除 grade/sub_grade
    feats_b = [c for c in df_encoded.columns if c != "default"]
    print(f"[B] 使用特征数: {len(feats_b)}")
    print(f"[B] 是否包含 grade/sub_grade: {'grade' in feats_b or 'sub_grade' in feats_b}")

    X = df_encoded[feats_b]
    y = df_encoded["default"]

    X_tr, X_te, y_tr, y_te = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    scale_pos = (y_tr == 0).sum() / (y_tr == 1).sum()

    # 简单 GridSearch（控制范围以加快速度）
    param_grid = {
        "max_depth": [4, 6],
        "n_estimators": [100, 200],
        "learning_rate": [0.1],
    }
    xgb_base = xgb.XGBClassifier(
        subsample=0.8, colsample_bytree=0.8,
        scale_pos_weight=scale_pos,
        eval_metric="auc", random_state=RANDOM_STATE,
        n_jobs=-1, tree_method="hist",
    )
    gs = GridSearchCV(xgb_base, param_grid, scoring="roc_auc", cv=3, verbose=0)
    gs.fit(X_tr, y_tr)
    print(f"[B] best params: {gs.best_params_}")

    prob = gs.predict_proba(X_te)[:, 1]
    pred = (prob >= 0.5).astype(int)
    auc = roc_auc_score(y_te, prob)
    fpr, tpr, _ = roc_curve(y_te, prob)
    ks = max(tpr - fpr)

    metrics = {
        "AUC-ROC": auc,
        "KS": ks,
        "Accuracy": accuracy_score(y_te, pred),
        "Precision": precision_score(y_te, pred, zero_division=0),
        "Recall": recall_score(y_te, pred),
        "F1": f1_score(y_te, pred),
        "特征数": len(feats_b),
        "数据泄露": "未明确排除 (含 grade/sub_grade)",
        "PSI稳定性": "未验证",
        "可解释性": "SHAP",
    }
    print(f"[B] AUC={auc:.4f}, KS={ks:.4f}")
    _plot_roc(fpr, tpr, auc, "Model B (Feature-Heavy)", OUT_DIR / "model_b_roc.png")
    return metrics


# ------------------------------------------------------------------
# 模型 C：CreditMind（IV/WoE + PSI + 贪心去共线性 + XGBoost）
# ------------------------------------------------------------------
def run_model_c(df_raw: pd.DataFrame):
    print("\n" + "=" * 70)
    print("模型 C: CreditMind (IV/WoE + PSI + 贪心去共线性 + XGBoost)")
    print("=" * 70)

    df = encode_basic(df_raw.copy())
    target = df["default"]
    feats = [c for c in df.columns if c != "default"]

    # 明确排除 grade/sub_grade（防目标泄露）
    leak_cols = ["grade", "sub_grade"]
    feats_safe = [c for c in feats if c not in leak_cols]
    print(f"[C] 排除泄露列: {leak_cols}")
    print(f"[C] 候选特征数: {len(feats_safe)}")

    # Step 1: IV 计算
    iv_series = pd.Series({f: calculate_iv(df[f], target) for f in feats_safe})
    iv_series = iv_series.sort_values(ascending=False)
    qualified = iv_series[iv_series >= 0.02].index.tolist()
    print(f"[C] IV≥0.02 合格特征: {len(qualified)}")

    # Step 2: PSI（Train vs Test）
    X_tr_raw, X_te_raw, y_tr, y_te = train_test_split(
        df[feats_safe], target, test_size=0.2, random_state=RANDOM_STATE, stratify=target
    )
    psi_series = pd.Series({f: calculate_psi(X_tr_raw[f], X_te_raw[f]) for f in qualified})
    stable = psi_series[psi_series < 0.25].index.tolist()
    print(f"[C] PSI<0.25 稳定特征: {len(stable)}")

    # Step 3: 贪心去共线性
    corr = X_tr_raw[stable].corr()
    final_feats = greedy_select(stable, iv_series, corr, threshold=0.7)
    print(f"[C] 去共线性后最终特征: {len(final_feats)}")
    print(f"[C] 最终特征: {final_feats[:20]}")

    # Step 4: 训练 XGBoost
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
    pred = (prob >= 0.5).astype(int)
    auc = roc_auc_score(y_te, prob)
    fpr, tpr, _ = roc_curve(y_te, prob)
    ks = max(tpr - fpr)

    metrics = {
        "AUC-ROC": auc,
        "KS": ks,
        "Accuracy": accuracy_score(y_te, pred),
        "Precision": precision_score(y_te, pred, zero_division=0),
        "Recall": recall_score(y_te, pred),
        "F1": f1_score(y_te, pred),
        "特征数": len(final_feats),
        "数据泄露": "否 (明确排除 grade/sub_grade)",
        "PSI稳定性": "已验证 (PSI<0.25)",
        "可解释性": "SHAP + IV 双解释",
    }
    print(f"[C] AUC={auc:.4f}, KS={ks:.4f}")

    # SHAP Top15
    try:
        import shap
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_te)
        plt.figure(figsize=(10, 7))
        shap.summary_plot(shap_values, X_te, max_display=15, show=False, plot_type="bar")
        plt.title("CreditMind — SHAP Top15 Feature Importance")
        plt.tight_layout()
        plt.savefig(OUT_DIR / "shap_top15.png", dpi=120)
        plt.close()
        print(f"[C] SHAP plot saved")
    except Exception as e:
        print(f"[C] SHAP skipped: {e}")

    # PSI 报告
    psi_report = pd.DataFrame({
        "feature": psi_series.index,
        "psi": psi_series.values,
        "grade": ["稳定" if p < 0.1 else "轻微漂移" if p < 0.25 else "显著漂移⚠"
                  for p in psi_series.values],
    })
    psi_report.to_csv(OUT_DIR / "psi_report.csv", index=False)
    print(f"[C] PSI report saved")

    _plot_roc(fpr, tpr, auc, "Model C (CreditMind)", OUT_DIR / "model_c_roc.png")

    # 保存 CreditMind 的特征清单
    with open(OUT_DIR / "creditmind_features.json", "w") as f:
        json.dump({
            "final_features": final_feats,
            "iv_top15": iv_series.head(15).to_dict(),
            "psi_summary": {
                "stable": int((psi_series < 0.1).sum()),
                "mild_drift": int(((psi_series >= 0.1) & (psi_series < 0.25)).sum()),
                "significant_drift": int((psi_series >= 0.25).sum()),
            },
        }, f, indent=2, ensure_ascii=False)
    return metrics


# ------------------------------------------------------------------
# 可视化辅助
# ------------------------------------------------------------------
def _plot_roc(fpr, tpr, auc, title, path):
    plt.figure(figsize=(7, 6))
    plt.plot(fpr, tpr, lw=2, label=f"AUC = {auc:.4f}")
    plt.plot([0, 1], [0, 1], "--", color="gray", lw=1)
    plt.xlabel("False Positive Rate")
    plt.ylabel("True Positive Rate")
    plt.title(title)
    plt.legend(loc="lower right")
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close()


# ------------------------------------------------------------------
# 三模型对比图
# ------------------------------------------------------------------
def plot_comparison(summary: pd.DataFrame):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    models = summary["model"].tolist()
    aucs = summary["AUC-ROC"].tolist()
    kss = summary["KS"].tolist()
    nfeats = summary["特征数"].tolist()

    colors = ["#e74c3c", "#f39c12", "#27ae60"]

    axes[0].bar(models, aucs, color=colors, edgecolor="black")
    axes[0].set_title("AUC-ROC 对比")
    axes[0].set_ylim(0.5, max(aucs) * 1.05)
    for i, v in enumerate(aucs):
        axes[0].text(i, v + 0.005, f"{v:.4f}", ha="center", fontweight="bold")

    axes[1].bar(models, nfeats, color=colors, edgecolor="black")
    axes[1].set_title("特征数对比（少即是多）")
    for i, v in enumerate(nfeats):
        axes[1].text(i, v + 1, str(v), ha="center", fontweight="bold")

    plt.tight_layout()
    plt.savefig(OUT_DIR / "comparison_overview.png", dpi=120)
    plt.close()
    print(f"[对比图] saved → {OUT_DIR / 'comparison_overview.png'}")


# ------------------------------------------------------------------
# 主入口
# ------------------------------------------------------------------
def main():
    print("=" * 70)
    print("CreditMind 竞品对比实验")
    print("数据: LendingClub 2018-2019 sample")
    print("=" * 70)

    df_raw = load_raw()
    df_encoded = encode_basic(df_raw.copy())

    m_a = run_model_a(df_encoded)
    m_b = run_model_b(df_encoded)
    m_c = run_model_c(df_raw)

    summary = pd.DataFrame([
        {"model": "A: Leaky Baseline", **m_a},
        {"model": "B: Feature-Heavy", **m_b},
        {"model": "C: CreditMind", **m_c},
    ])
    summary.to_csv(OUT_DIR / "summary.csv", index=False)
    print("\n" + "=" * 70)
    print("对比汇总")
    print("=" * 70)
    print(summary.to_string(index=False))

    plot_comparison(summary)
    print(f"\n[done] 所有结果保存到: {OUT_DIR}")


if __name__ == "__main__":
    main()
