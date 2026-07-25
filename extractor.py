"""
CreditMind · 特征抽取器
========================
从对话历史中抽取结构化特征 JSON。

兜底策略：
1. 优先用 interview_agent 已采集的特征（最准）
2. LLM function calling 补充缺失字段
3. 正则/关键词兜底
4. 仍缺失的字段标记为 0（模型按缺失值处理）
"""
from __future__ import annotations

import re
from typing import Any

from model_server import CreditMindModel, FEATURE_META


def extract_from_dialogue(dialogue: list[dict], collected: dict = None) -> dict:
    """从对话历史 + 已采集字段中抽取完整特征 JSON。

    Args:
        dialogue: [{role, content}] 对话历史
        collected: interview_agent 已采集的字段（优先级最高）

    Returns:
        19 项特征的 dict
    """
    model = CreditMindModel.get()
    features = {f: 0.0 for f in model.features}

    # 1. 优先用已采集的字段
    if collected:
        for k, v in collected.items():
            if k in features and v not in (None, ""):
                features[k] = float(v)

    # 2. 从对话历史中补充缺失字段
    full_text = " ".join([d["content"] for d in dialogue])
    for fname in model.features:
        if features[fname] != 0.0:
            continue  # 已有值
        meta = FEATURE_META.get(fname, {})
        val = _extract_from_text(full_text, fname, meta)
        if val is not None:
            features[fname] = float(val)

    return features


def _extract_from_text(text: str, fname: str, meta: dict) -> Any:
    """从文本中抽取单个特征值。"""
    ftype = meta.get("type", "float")

    if ftype == "cat":
        cats = meta.get("categories", [])
        text_lower = text.lower()
        for c in cats:
            if c.lower() in text_lower:
                return cats.index(c)
        return None

    # 数值型
    numbers = re.findall(r"[\d,]+\.?\d*", text.replace(" ", ""))
    if not numbers:
        return None
    raw = numbers[-1].replace(",", "")
    try:
        val = float(raw)
    except ValueError:
        return None

    unit = meta.get("unit", "")
    if unit == "元" and ("万" in text or "w" in text.lower()):
        val *= 10000

    return val


def validate_features(features: dict) -> dict:
    """校验特征值是否在合理范围内，标记异常。"""
    anomalies = []
    ranges = {
        "int_rate": (0, 36),
        "term_months": (12, 60),
        "loan_amnt": (500, 1000000),
        "annual_inc": (0, 10000000),
        "dti": (0, 100),
        "inq_last_6mths": (0, 50),
        "inq_last_12m": (0, 100),
        "emp_length": (0, 50),
        "mort_acc": (0, 20),
    }
    for f, (lo, hi) in ranges.items():
        if f in features:
            v = features[f]
            if v < lo or v > hi:
                anomalies.append({"feature": f, "value": v, "range": [lo, hi]})

    return {
        "anomalies": anomalies,
        "is_valid": len(anomalies) == 0,
    }


if __name__ == "__main__":
    # 测试
    dialogue = [
        {"role": "user", "content": "我借 20 万，利率 13.5%，期限 36 个月"},
        {"role": "user", "content": "年收入 30 万，工作 5 年了"},
        {"role": "user", "content": "按揭房，信用卡额度 5 万"},
    ]
    features = extract_from_dialogue(dialogue)
    print("抽取结果:")
    for k, v in features.items():
        print(f"  {k}: {v}")

    print("\n校验:")
    print(validate_features(features))
