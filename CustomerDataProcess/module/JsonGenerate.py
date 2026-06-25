import json
import numpy as np
import pandas as pd
from DataProcessing import preprocess_data


def safe_float(x, ndigits=2):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return round(float(x), ndigits)


def safe_int(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return int(x)


def safe_str(x):
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return None
    return str(x)

def get_customer_history_data(panel: pd.DataFrame, customer_id: str) -> list:
    """
    Build full customer transaction history from panel
    """

    customer_panel = (
        panel[panel["customer_id"] == customer_id]
        .sort_values("year_month")
    )

    history = []

    for _, row in customer_panel.iterrows():
        year_month = row["year_month"].strftime("%Y-%m")

        if row["num_orders"] == 0:
            history.append({
                "year_month": year_month,
                "status": "NOT_ACTIVE"
            })
        else:
            history.append({
                "year_month": year_month,
                "status": "ACTIVE",
                "total_sales": safe_float(row["total_sales"]),
                "num_orders": safe_int(row["num_orders"]),
                "avg_order_value": safe_float(row["avg_order_value"]),
                "deal_mix": {
                    "large": safe_int(row["num_large_deals"]),
                    "medium": safe_int(row["num_medium_deals"]),
                    "small": safe_int(row["num_small_deals"])
                },
                "ship_rate": safe_float(row["ship_rate"]),
                "cancel_rate": safe_float(row["cancel_rate"]),
                "trend_label": safe_str(row["trend_label"]),
                "trust_level": safe_str(row["trust_level"])
            })

    return history

def get_customer_context(panel: pd.DataFrame, customer_id: str) -> dict:
    latest_row = (
        panel[panel["customer_id"] == customer_id]
        .sort_values("year_month")
        .iloc[-1]
    )

    return {
        "customer_id": safe_str(latest_row["customer_id"]),
        "segment": "B2B",
        "data_sufficient": bool(latest_row["data_sufficient_flag"]),
        "active_months": safe_int(latest_row["active_months_count"])
    }

def build_customer_context_and_history(
    panel: pd.DataFrame,
    customer_id: str
) -> dict:
    return {
        "customer_context": get_customer_context(panel, customer_id),
        "history": get_customer_history_data(panel, customer_id)
    }



def panel_row_to_json(row) -> dict:
    """
    Convert one panel row (pd.Series) into Customer Intelligence JSON
    """

    snapshot = {
        "customer_context": {
            "customer_id": safe_str(row["customer_id"]),
            "segment": "B2B",
            "data_sufficient": bool(row["data_sufficient_flag"]),
            "active_months": safe_int(row["active_months_count"])
        },
        "behavior_summary": {
            "current_month": {
                "total_sales": safe_float(row["total_sales"]),
                "num_orders": safe_int(row["num_orders"]),
                "avg_order_value": safe_float(row["avg_order_value"]),
                "deal_mix": {
                    "large": safe_int(row["num_large_deals"]),
                    "medium": safe_int(row["num_medium_deals"]),
                    "small": safe_int(row["num_small_deals"])
                }
            },
            "engagement": {
                "active_ratio_3m": safe_float(row["active_ratio_3m"]),
                "orders_3m_avg": safe_float(row["orders_3m_avg"])
            }
        },

        "trust_profile": {
            "trust_score": safe_float(row["trust_score"]),
            "trust_level": safe_str(row["trust_level"]),
            "drivers": {
                "outcome": {
                    "level": safe_str(row["outcome_level"]),
                    "score": safe_float(row["outcome_score"])
                },
                "consistency": {
                    "level": safe_str(row["consistency_level"]),
                    "score": safe_float(row["consistency_score"])
                },
                "engagement": {
                    "level": safe_str(row["engagement_level"]),
                    "score": safe_float(row["engagement_score"])
                }
            },
            "weakest_driver": safe_str(row["weakest_driver"]),
            "explanation": safe_str(row["trust_explanation"])
        },

        "trend_profile": {
            "sales_trend": safe_str(row["sales_trend"]),
            "momentum_score": safe_float(row["momentum_score"]),
            "sales_growth_3m": safe_float(row["sales_3m_growth"])
        },

        "risk_flags": _build_risk_flags(row),

        "recommendation": {
            "action_type": _map_action_type(row),
            "priority": _map_priority(row),
            "strategy": safe_str(row["trust_action_hint"]),
            "do": _map_do_actions(row),
            "dont": _map_dont_actions(row)
        },

        "talking_points": _build_talking_points(row)
    }

    return snapshot

def _build_risk_flags(row):
    flags = []

    if not bool(row["data_sufficient_flag"]):
        flags.append({
            "type": "LOW_HISTORY",
            "description": "Khách hàng mới, chưa đủ lịch sử giao dịch."
        })

    if pd.notna(row["cancel_rate_3m"]) and row["cancel_rate_3m"] > 0.3:
        flags.append({
            "type": "HIGH_CANCELLATION",
            "description": "Tỷ lệ huỷ đơn gần đây ở mức cao."
        })

    if row["sales_trend"] == "DOWN":
        flags.append({
            "type": "DECLINING_TREND",
            "description": "Doanh thu có dấu hiệu giảm."
        })

    return flags

def _map_action_type(row):
    if row["trust_level"] == "HIGH" and row["sales_trend"] == "UP":
        return "PUSH_UPSELL"
    if row["trust_level"] in ["LOW", "MEDIUM"]:
        return "NURTURE"
    return "MAINTAIN"


def _map_priority(row):
    if row["sales_trend"] == "UP":
        return "HIGH"
    if row["sales_trend"] == "DOWN":
        return "LOW"
    return "MEDIUM"

def _map_do_actions(row):
    actions = []

    if row["trust_level"] == "HIGH":
        actions.append("Đề xuất gói phù hợp với lịch sử mua")
    else:
        actions.append("Giữ liên hệ định kỳ")

    if row["sales_trend"] == "UP":
        actions.append("Chủ động đề xuất giá trị gia tăng")

    return actions


def _map_dont_actions(row):
    actions = []

    if row["trust_level"] != "HIGH":
        actions.append("Không ép deal lớn")

    if row["sales_trend"] == "DOWN":
        actions.append("Tránh tăng giá đột ngột")

    return actions

def _build_talking_points(row):
    points = []

    if row["data_sufficient_flag"] == 0:
        points.append("Khách hàng đang ở giai đoạn đầu, cần xây dựng quan hệ.")

    if row["sales_trend"] == "UP":
        points.append("Khách hàng đang có xu hướng mua tăng.")

    if row["consistency_level"] == "WEAK":
        points.append("Cần theo dõi thêm để đánh giá độ ổn định hành vi mua.")

    return points


if __name__ == "__main__":
    panel = preprocess_data()
    sample_row = panel.iloc[0]
    customer_json = panel_row_to_json(sample_row)

    print(json.dumps(customer_json, ensure_ascii=False, indent=2))
