"""
CreditMind · 智能访谈 Agent
============================
基于 LLM 的多轮对话，自动采集 19 项核心特征。

设计要点：
- 不依赖 OpenClaw（避免路演时网关/依赖问题），直接用 OpenAI 兼容 API
- 支持 DeepSeek / OpenAI / 任意 OpenAI 兼容端点
- 提问模板来自 model_server.FEATURE_META
- 兜底：LLM 抽取失败时，用正则/关键词匹配
- 离线模式：无 API Key 时降级为"逐项表单提问"模式

依赖：openai（可选，无则降级）
"""
from __future__ import annotations

import json
import os
import re
from typing import Any, Optional

from model_server import CreditMindModel, FEATURE_META


# ------------------------------------------------------------------
# LLM 客户端（OpenAI 兼容）
# ------------------------------------------------------------------
class LLMClient:
    """轻量 LLM 客户端，支持 DeepSeek/OpenAI。"""

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("LLM_BASE_URL", "https://api.deepseek.com/v1")
        self.model = os.getenv("LLM_MODEL", "deepseek-chat")
        self._client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
            except ImportError:
                print("[LLM] openai 包未安装，降级为表单模式")

    @property
    def available(self) -> bool:
        return self._client is not None

    def chat(self, messages: list[dict], temperature: float = 0.3) -> str:
        if not self.available:
            return ""
        try:
            resp = self._client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=800,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM] 调用失败: {e}")
            return ""


# ------------------------------------------------------------------
# 访谈 Agent
# ------------------------------------------------------------------
class InterviewAgent:
    """CreditMind 智能访谈 Agent。"""

    def __init__(self):
        self.model = CreditMindModel.get()
        self.template = self.model.get_feature_template()
        self.llm = LLMClient()
        self.collected: dict[str, Any] = {}
        self.dialogue: list[dict] = []  # [{role, content}]
        self.current_idx = 0

    def reset(self):
        self.collected = {}
        self.dialogue = []
        self.current_idx = 0

    @property
    def features(self) -> list:
        """访谈模板中的全部特征名（顺序与模型一致）。"""
        return [t["feature"] for t in self.template]

    def start(self, customer_info: dict) -> str:
        """启动访谈，返回开场白。"""
        self.reset()
        # 记录客户基本信息
        for k, v in customer_info.items():
            if k in [t["feature"] for t in self.template]:
                self.collected[k] = v

        opening = (
            f"您好！我是 CreditMind 智能访谈助手。"
            f"接下来我会问您 {len(self.template)} 个问题，大约需要 5-10 分钟。"
            f"请您如实回答，我们会严格保护您的个人信息。"
            f"\n\n让我们开始吧。"
        )
        self.dialogue.append({"role": "assistant", "content": opening})

        # 第一个问题
        first_q = self._next_question()
        return f"{opening}\n\n{first_q}"

    def _next_question(self) -> str:
        """返回下一个未采集特征的问题。"""
        while self.current_idx < len(self.template):
            t = self.template[self.current_idx]
            if t["feature"] in self.collected and self.collected[t["feature"]] not in (None, ""):
                self.current_idx += 1
                continue
            return f"【问题 {self.current_idx + 1}/{len(self.template)}】{t['question']}"
        return "访谈已完成，正在生成尽调报告..."

    def chat(self, user_input: str) -> str:
        """用户回答后，Agent 处理并返回下一轮。"""
        self.dialogue.append({"role": "user", "content": user_input})

        if self.current_idx >= len(self.template):
            response = "访谈已完成，正在生成尽调报告..."
            self.dialogue.append({"role": "assistant", "content": response})
            return response

        t = self.template[self.current_idx]
        value = self._extract_value(user_input, t)

        if value is not None:
            # 抽取成功 → 记录并推进
            self.collected[t["feature"]] = value
            self.current_idx += 1
            collected_count = len([v for v in self.collected.values() if v not in (None, "")])
            label = self._value_label(t, value)
            if self.llm.available and self.current_idx < len(self.template):
                response = self._llm_respond(user_input, recorded=f"{t['desc']} = {label}")
            elif self.current_idx >= len(self.template):
                response = f"✅ 已记录：{t['desc']} = {label}。\n\n访谈已完成，正在生成尽调报告..."
            else:
                next_q = self._next_question()
                response = (
                    f"✅ 已记录：{t['desc']} = {label}"
                    f"（已采集 {collected_count}/{len(self.template)} 项）。\n\n{next_q}"
                )
        else:
            # 抽取失败 → 不推进，提示重答
            hint = self._extract_hint(t)
            response = f"⚠️ 未能识别您的回答。{hint}\n\n{self._next_question()}"

        self.dialogue.append({"role": "assistant", "content": response})
        return response

    def _value_label(self, t: dict, value: Any) -> str:
        """把内部存储值转为可读标签（推荐回答展示用）。"""
        if t.get("type") == "cat":
            cats = t.get("categories") or []
            if isinstance(value, int) and 0 <= value < len(cats):
                return cats[value]
            return str(value)
        unit = t.get("unit", "")
        return f"{value}{unit}" if unit else str(value)

    def _extract_hint(self, t: dict) -> str:
        """抽取失败时的重答提示。"""
        if t.get("yes_value") and t.get("no_value"):
            return f"请回答「是」（{t['yes_value']}）或「否」（{t['no_value']}）。"
        cats = t.get("categories") or []
        if cats:
            return f"可选值：{' / '.join(cats)}"
        return "请用数字回答。"

    def _llm_respond(self, user_input: str, recorded: str = "") -> str:
        """用 LLM 生成自然回应，并体现已记录的字段与取值。"""
        t = self.template[self.current_idx] if self.current_idx < len(self.template) else None
        next_q = t["question"] if t else "访谈已完成"

        system = (
            "你是 CreditMind 智能访谈助手，正在对一位借款人做贷前访谈。"
            "你的任务：1) 简短确认客户刚才的回答（提及已记录的字段与取值）；"
            "2) 问下一个问题。"
            "要求：每次回复不超过 80 字，语气专业友好，不要重复客户的原话。"
        )
        user_msg = (
            f"客户刚才回答：{user_input}\n"
            f"已记录的字段与取值：{recorded}\n"
            f"下一个要问的问题是：{next_q}\n"
            f"请生成回复。"
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_msg},
        ]
        resp = self.llm.chat(messages)
        if not resp:
            collected = len([v for v in self.collected.values() if v not in (None, "")])
            resp = f"✅ 已记录：{recorded}（已采集 {collected}/{len(self.template)} 项）。\n\n{next_q}"
        return resp

    def _extract_value(self, text: str, template: dict) -> Any:
        """从用户回答中抽取特征值。"""
        ftype = template["type"]
        fname = template["feature"]

        if ftype == "cat":
            # 分类列：匹配 categories
            cats = template.get("categories", [])
            for c in cats:
                if c.lower() in text.lower():
                    # 返回 category code（与 preprocess 一致）
                    return cats.index(c)
            # 是否类问题：yes/no 关键词映射到 yes_value/no_value
            yv, nv = template.get("yes_value"), template.get("no_value")
            if yv is not None and nv is not None and cats:
                tl = text.lower()
                yes_kw = ["是", "yes", "y", "对", "有", "经过", "已验证", "验证过", "已经过", "确认", "confirmed", "verified", "通过"]
                no_kw = ["否", "no", "n", "没", "未", "不", "not", "无"]
                if any(k in tl for k in yes_kw):
                    return cats.index(yv) if yv in cats else (cats.index(nv) if nv in cats else None)
                if any(k in tl for k in no_kw):
                    return cats.index(nv) if nv in cats else (cats.index(yv) if yv in cats else None)
            # 宽松匹配（住房所有权等）
            text_lower = text.lower()
            if "rent" in text_lower or "租房" in text_lower:
                return 0
            if "mortgage" in text_lower or "按揭" in text_lower or "房贷" in text_lower:
                return 1
            if "own" in text_lower or "自有" in text_lower:
                return 2
            return None

        # 数值型：提取数字
        numbers = re.findall(r"[\d,]+\.?\d*", text.replace(" ", ""))
        if not numbers:
            return None
        # 取最后一个数字（通常是答案）
        raw = numbers[-1].replace(",", "")
        try:
            val = float(raw)
        except ValueError:
            return None

        # 单位换算：年收入"万" → 元
        unit = template.get("unit", "")
        if unit == "元" and ("万" in text or "w" in text.lower()):
            val *= 10000
        # 利率已为百分比
        if unit == "%":
            val = val  # 保持原值

        return val

    def is_complete(self) -> bool:
        return self.current_idx >= len(self.template)

    def progress(self) -> dict:
        collected = len([v for v in self.collected.values() if v not in (None, "")])
        return {
            "collected": collected,
            "total": len(self.template),
            "complete": self.is_complete(),
            "features": dict(self.collected),
        }

    def get_features(self) -> dict:
        """返回已采集的特征（供模型推理）。"""
        return dict(self.collected)


# ------------------------------------------------------------------
# CLI 测试
# ------------------------------------------------------------------
if __name__ == "__main__":
    agent = InterviewAgent()
    print("=== CreditMind 智能访谈 Agent 测试 ===")
    print(f"LLM 可用: {agent.llm.available}")
    print(f"特征数: {len(agent.template)}")
    print()

    # 模拟访谈
    opening = agent.start({"loan_amnt": 200000})
    print(f"Agent: {opening}\n")

    # 模拟回答
    answers = [
        "13.5%", "36 个月", "8 万", "3 个", "按揭",
        "1 个", "5 万", "2 个", "6 个月前", "10 年前",
        "6 个月前", "经过验证", "3 次", "5 年", "2 个月前",
        "5 次", "30 万", "5 年前", "Source Verified",
    ]

    for ans in answers:
        print(f"用户: {ans}")
        resp = agent.chat(ans)
        print(f"Agent: {resp}\n")
        if agent.is_complete():
            break

    print("\n=== 采集结果 ===")
    print(json.dumps(agent.progress(), indent=2, ensure_ascii=False))
