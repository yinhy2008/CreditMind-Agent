"""
CreditMind · 虚拟借款人演示 Case
=================================
3 个预设 Case，覆盖低/中/高风险三档，供路演 Demo 使用。

数据来源：基于 LendingClub 2018-2019 真实数据分布设计的虚拟人物。
"""

CASES = {
    "low_risk": {
        "name": "李明",
        "profile": "35 岁，深圳某互联网公司高级工程师，年薪 80 万",
        "customer_info": {
            "name": "李明",
            "loan_amnt": 100000,
            "purpose": "家庭装修",
            "duration": "5-10",
        },
        "features": {
            "int_rate": 6.0, "term_months": 36, "tot_hi_cred_lim": 300000,
            "loan_amnt": 100000, "open_rv_24m": 0, "home_ownership": 1,
            "mort_acc": 2, "total_bc_limit": 200000, "num_tl_op_past_12m": 0,
            "mo_sin_rcnt_rev_tl_op": 36, "mo_sin_old_rev_tl_op": 240,
            "mths_since_recent_bc": 36, "verification_status": 1,
            "inq_last_6mths": 0, "emp_length": 10, "mths_since_recent_inq": 36,
            "inq_last_12m": 0, "annual_inc": 800000, "mo_sin_old_il_acct": 180,
        },
        "expected_risk": "低风险",
        "expected_prob_range": (0.02, 0.25),
    },
    "medium_risk": {
        "name": "张伟",
        "profile": "35 岁，深圳电商老板，借款 20 万用于经营周转",
        "customer_info": {
            "name": "张伟",
            "loan_amnt": 200000,
            "purpose": "经营周转",
            "duration": "5-10",
        },
        "features": {
            "int_rate": 11.0, "term_months": 36, "tot_hi_cred_lim": 120000,
            "loan_amnt": 150000, "open_rv_24m": 2, "home_ownership": 1,
            "mort_acc": 1, "total_bc_limit": 80000, "num_tl_op_past_12m": 1,
            "mo_sin_rcnt_rev_tl_op": 12, "mo_sin_old_rev_tl_op": 150,
            "mths_since_recent_bc": 12, "verification_status": 1,
            "inq_last_6mths": 1, "emp_length": 6, "mths_since_recent_inq": 8,
            "inq_last_12m": 2, "annual_inc": 400000, "mo_sin_old_il_acct": 90,
        },
        "expected_risk": "中风险",
        "expected_prob_range": (0.15, 0.50),
    },
    "high_risk": {
        "name": "王强",
        "profile": "40 岁，自由职业者，借款 30 万，信用历史较短",
        "customer_info": {
            "name": "王强",
            "loan_amnt": 300000,
            "purpose": "债务重组",
            "duration": "5-10",
        },
        "features": {
            "int_rate": 24.5, "term_months": 60, "tot_hi_cred_lim": 30000,
            "loan_amnt": 300000, "open_rv_24m": 6, "home_ownership": 0,
            "mort_acc": 0, "total_bc_limit": 20000, "num_tl_op_past_12m": 5,
            "mo_sin_rcnt_rev_tl_op": 2, "mo_sin_old_rev_tl_op": 36,
            "mths_since_recent_bc": 2, "verification_status": 2,
            "inq_last_6mths": 8, "emp_length": 1, "mths_since_recent_inq": 1,
            "inq_last_12m": 12, "annual_inc": 120000, "mo_sin_old_il_acct": 24,
        },
        "expected_risk": "高风险",
        "expected_prob_range": (0.50, 0.95),
    },
}


def get_case(case_id: str) -> dict:
    """获取预设 Case。"""
    return CASES[case_id]


def list_cases() -> list[dict]:
    """列出所有 Case。"""
    return [
        {"id": k, "name": v["name"], "profile": v["profile"], "expected_risk": v["expected_risk"]}
        for k, v in CASES.items()
    ]


if __name__ == "__main__":
    from model_server import CreditMindModel

    model = CreditMindModel.get()
    for cid, case in CASES.items():
        pred = model.explain(case["features"])
        in_range = case["expected_prob_range"][0] <= pred["default_probability"] <= case["expected_prob_range"][1]
        print(f"[{cid}] {case['name']}: P={pred['default_probability']:.4f}, "
              f"等级={pred['risk_level']}, 预期={case['expected_risk']}, "
              f"在预期区间={in_range}")
