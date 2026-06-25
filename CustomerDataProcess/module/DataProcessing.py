import os
import numpy as np
import pandas as pd



data_path = r"T:\SaleAssistant\CustomerDataProcess.\data"
raw_data_file = os.path.join(data_path, "sales_data_sample.csv")

def normalize_status(x):
    if x == "SHIPPED":
        return "SHIPPED"
    elif x in ["CANCELLED", "CANCELED"]:
        return "CANCELLED"
    else:
        return "OTHER"
        
def label_trend(row):
    if row["sales_3m_growth"] > 0.15 and row["num_orders"] >= row["orders_3m_avg"]:
        return "Growing"
    elif row["sales_3m_growth"] < -0.15:
        return "Declining"
    else:
        return "Stable"
    
def score_bucket(x):
    if x >= 0.75:
        return "STRONG"
    elif x >= 0.5:
        return "OK"
    else:
        return "WEAK"
    
def trust_action_hint(row):
    if row["weakest_driver"] == "OUTCOME_RELIABILITY":
        return "Nên yêu cầu xác nhận đơn sớm, hạn chế ưu đãi sâu hoặc điều khoản thanh toán linh hoạt."

    if row["weakest_driver"] == "BEHAVIORAL_CONSISTENCY":
        return "Nên theo dõi thêm 1–2 chu kỳ mua để xác nhận xu hướng trước khi báo giá ưu đãi."

    if row["weakest_driver"] == "ENGAGEMENT_STABILITY":
        return "Nên chủ động follow-up và tạo tương tác đều đặn để kích hoạt lại nhu cầu."

    return "Có thể áp dụng chiến lược chốt đơn tiêu chuẩn."
    
def trust_explanation(row):
    explanations = []

    if row["data_sufficient_flag"] == 0:
        explanations.append(
            "Khách hàng còn mới, dữ liệu lịch sử chưa đủ dài để đánh giá độ tin cậy chính xác."
        )

    if row["outcome_level"] == "WEAK":
        explanations.append(
            "Tỷ lệ giao dịch thành công thấp hoặc có nhiều đơn bị hủy trong thời gian gần đây."
        )

    if row["consistency_level"] == "WEAK":
        explanations.append(
            "Hành vi mua sắm không ổn định, doanh thu dao động mạnh theo tháng."
        )

    if row["engagement_level"] == "WEAK":
        explanations.append(
            "Khách hàng không duy trì tương tác đều đặn trong các tháng gần đây."
        )

    if not explanations:
        explanations.append(
            "Hành vi giao dịch ổn định và đáng tin cậy trong thời gian gần đây."
        )

    return " ".join(explanations)

def recommend_action(row):
    # print(row)
    trust = row["trust_level"]
    trend = row["sales_trend"]

    if pd.isna(trust) or pd.isna(trend):
        return "INSUFFICIENT_DATA"

    if trust == "HIGH" and trend == "UP":
        return {
            "strategy": "PUSH_UPSELL",
            "discount_range": "0–5%",
            "priority": "HIGH"
        }

    if trust == "HIGH" and trend == "FLAT":
        return {
            "strategy": "MAINTAIN",
            "discount_range": "5–8%",
            "priority": "MEDIUM"
        }

    if trust == "HIGH" and trend == "DOWN":
        return {
            "strategy": "RETAIN",
            "discount_range": "8–12%",
            "priority": "HIGH"
        }

    if trust == "MEDIUM" and trend == "UP":
        return {
            "strategy": "SELECTIVE_PUSH",
            "discount_range": "5–8%",
            "priority": "MEDIUM"
        }

    if trust == "MEDIUM" and trend == "FLAT":
        return {
            "strategy": "OBSERVE",
            "discount_range": "3–5%",
            "priority": "LOW"
        }

    if trust == "MEDIUM" and trend == "DOWN":
        return {
            "strategy": "CAUTIOUS_RETAIN",
            "discount_range": "5–10%",
            "priority": "MEDIUM"
        }

    if trust == "LOW" and trend == "UP":
        return {
            "strategy": "TEST_ONLY",
            "discount_range": "0–3%",
            "priority": "LOW"
        }

    if trust == "LOW" and trend == "FLAT":
        return {
            "strategy": "LIMIT_EXPOSURE",
            "discount_range": "0–3%",
            "priority": "LOW"
        }

    return {
        "strategy": "RISK_CONTROL",
        "discount_range": "0%",
        "priority": "LOW"
    }

def preprocess_data():
    # Load raw data
    df_raw = pd.read_csv(raw_data_file, encoding="latin1")
    df = df_raw.copy()

    # Chuẩn hóa cột & kiểu dữ liệu
    df["ORDERDATE"] = pd.to_datetime(df["ORDERDATE"], errors="coerce")
    df["customer_id"] = df["CUSTOMERNAME"].str.strip()
    df["year_month"] = df["ORDERDATE"].dt.to_period("M").dt.to_timestamp()

    # Chuẩn hóa STATUS
    df["STATUS"] = df["STATUS"].str.upper().str.strip()
    def normalize_status(x):
        if x == "SHIPPED":
            return "SHIPPED"
        elif x in ["CANCELLED", "CANCELED"]:
            return "CANCELLED"
        else:
            return "OTHER"
    df["status_std"] = df["STATUS"].apply(normalize_status)

    # Chuẩn hóa DEALSIZE
    df["DEALSIZE"] = df["DEALSIZE"].str.capitalize()
    deal_map = {"Small": 1, "Medium": 2, "Large": 3}
    df["deal_size_num"] = df["DEALSIZE"].map(deal_map)

    # Tạo flags phục vụ aggregation
    df["is_shipped"] = (df["status_std"] == "SHIPPED").astype(int)
    df["is_cancelled"] = (df["status_std"] == "CANCELLED").astype(int)
    df["valid_order"] = (df["status_std"] != "CANCELLED").astype(int)

    # clean df
    clean_orders_df = df

    # Tạo bảng base aggregation
    panel = (
        clean_orders_df
        .groupby(["customer_id", "year_month"])
        .agg(
            total_sales=("SALES", lambda x: x[clean_orders_df.loc[x.index, "status_std"] == "SHIPPED"].sum()),
            num_orders=("ORDERNUMBER", lambda x: x[clean_orders_df.loc[x.index, "valid_order"] == 1].nunique()),
            total_orders=("ORDERNUMBER", "nunique"),
            shipped_orders=("is_shipped", "sum"),
            cancelled_orders=("is_cancelled", "sum"),
            num_order_lines=("ORDERLINENUMBER", "count"),
            avg_unit_price=("PRICEEACH", "mean"),
            num_product_lines=("PRODUCTLINE", "nunique"),
            avg_deal_size=("deal_size_num", "mean")
        )
        .reset_index()
    )

    # Derived Features – Behavior & Trust
    panel["avg_order_value"] = panel["total_sales"] / panel["num_orders"].replace(0, np.nan)
    panel["ship_rate"] = panel["shipped_orders"] / (
        panel["shipped_orders"] + panel["cancelled_orders"]
    )
    panel["ship_rate"] = panel["ship_rate"].clip(0, 1)
    panel["cancel_rate"] = panel["cancelled_orders"] / panel["total_orders"].replace(0, np.nan)
    panel["active_flag"] = (panel["num_orders"] > 0).astype(int)

    # Deal pattern features
    deal_counts = (
        clean_orders_df
        .groupby(["customer_id", "year_month", "DEALSIZE"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )
    panel = panel.merge(deal_counts, on=["customer_id", "year_month"], how="left")
    panel.rename(
        columns={
            "Small": "num_small_deals",
            "Medium": "num_medium_deals",
            "Large": "num_large_deals"
        },
        inplace=True
    )

    # panel raw
    customer_month_panel_raw = panel
    customer_month_panel_raw = customer_month_panel_raw.sort_values(
        ["customer_id", "year_month"]
    )
    panel = customer_month_panel_raw.copy()

    panel = panel.sort_values(
        ["customer_id", "year_month"]
    ).reset_index(drop=True)

    lag_features = [
        "total_sales",
        "num_orders",
        "avg_order_value"
    ]

    for col in lag_features:
        panel[f"{col}_lag1"] = (
            panel
            .groupby("customer_id")[col]
            .shift(1)
        )

        panel[f"{col}_lag3"] = (
            panel
            .groupby("customer_id")[col]
            .shift(3)
        )

    panel["sales_3m_avg"] = (
        panel
        .groupby("customer_id")["total_sales"]
        .rolling(window=3, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    panel["orders_3m_avg"] = (
        panel
        .groupby("customer_id")["num_orders"]
        .rolling(window=3, min_periods=1)
        .mean()
        .reset_index(level=0, drop=True)
    )

    panel["sales_3m_growth"] = (
        panel["total_sales"] / panel["sales_3m_avg"]
    ) - 1

    panel["trend_label"] = panel.apply(label_trend, axis=1)
    panel["momentum_score"] = (
        0.6 * panel["sales_3m_growth"].fillna(0) +
        0.4 * (panel["num_orders"] / panel["orders_3m_avg"].replace(0, np.nan)).fillna(0)
    )

    full_idx = (
        panel
        .groupby("customer_id")["year_month"]
        .apply(lambda x: pd.date_range(x.min(), x.max(), freq="MS"))
    )

    full_idx = full_idx.explode().reset_index()
    full_idx.columns = ["customer_id", "year_month"]

    panel = full_idx.merge(
        panel,
        on=["customer_id", "year_month"],
        how="left"
    )

    panel["total_sales_log"] = np.log1p(panel["total_sales"])
    panel["avg_order_value_log"] = np.log1p(panel["avg_order_value"])

    panel["active_month_flag"] = (panel["num_orders"] > 0).astype(int)

    panel["active_months_count"] = (
        panel
        .groupby("customer_id")["active_month_flag"]
        .cumsum()
    )

    panel["data_sufficient_flag"] = (
        panel["active_months_count"] >= 3
    ).astype(int)

    panel[panel.columns] = panel[panel.columns].fillna(0)
    panel = panel.sort_values(["customer_id", "year_month"])

    panel["ship_rate_3m"] = (
        panel
        .groupby("customer_id")["ship_rate"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    panel["cancel_rate_3m"] = (
        panel
        .groupby("customer_id")["cancel_rate"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    rolling_sales_mean = (
        panel
        .groupby("customer_id")["total_sales"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    rolling_sales_std = (
        panel
        .groupby("customer_id")["total_sales"]
        .transform(lambda x: x.rolling(3, min_periods=1).std())
    )

    panel["sales_cv_3m"] = rolling_sales_std / rolling_sales_mean

    panel["active_ratio_3m"] = (
        panel
        .groupby("customer_id")["active_month_flag"]
        .transform(lambda x: x.rolling(3, min_periods=1).mean())
    )

    panel["outcome_score"] = (
        0.7 * panel["ship_rate_3m"].fillna(0)
        + 0.3 * (1 - panel["cancel_rate_3m"].fillna(0))
    )

    panel["consistency_score"] = np.where(
        panel["data_sufficient_flag"] == 0,
        0.5,
        1 - panel["sales_cv_3m"].clip(0, 1)
    )

    panel["engagement_score"] = panel["active_ratio_3m"].fillna(0)

    panel["trust_score_raw"] = (
        0.45 * panel["outcome_score"]
        + 0.30 * panel["consistency_score"]
        + 0.25 * panel["engagement_score"]
    )

    panel["trust_score"] = panel["trust_score_raw"]
    panel["trust_score"] = panel["trust_score"].clip(0, 1)

    panel.loc[
        panel["data_sufficient_flag"] == 0,
        "trust_score"
    ] *= 0.6

    panel["trust_level"] = pd.cut(
        panel["trust_score"],
        bins=[-1, 0.4, 0.7, 1.1],
        labels=["LOW", "MEDIUM", "HIGH"]
    )

    panel.groupby("trust_level")[
        ["ship_rate_3m", "cancel_rate_3m", "sales_cv_3m"]
    ].mean()

    panel["outcome_level"] = panel["outcome_score"].apply(score_bucket)
    panel["consistency_level"] = panel["consistency_score"].apply(score_bucket)
    panel["engagement_level"] = panel["engagement_score"].apply(score_bucket)

    # xác định yếu tố kéo trust score xuống nhiều
    panel["outcome_gap"] = panel["outcome_score"] - panel["trust_score"]
    panel["consistency_gap"] = panel["consistency_score"] - panel["trust_score"]
    panel["engagement_gap"] = panel["engagement_score"] - panel["trust_score"]

    panel["weakest_driver"] = panel[
        ["outcome_gap", "consistency_gap", "engagement_gap"]
    ].idxmin(axis=1)

    # mapping
    driver_map = {
        "outcome_gap": "OUTCOME_RELIABILITY",
        "consistency_gap": "BEHAVIORAL_CONSISTENCY",
        "engagement_gap": "ENGAGEMENT_STABILITY"
    }

    panel["weakest_driver"] = panel["weakest_driver"].map(driver_map)

    panel["trust_explanation"] = panel.apply(trust_explanation, axis=1)
    panel["trust_action_hint"] = panel.apply(trust_action_hint, axis=1)

    panel.groupby("trust_level")[
        ["outcome_score", "consistency_score", "engagement_score"]
    ].mean()

    panel["sales_trend"] = np.select(
        [
            panel["sales_3m_growth"] > 0.05,
            panel["sales_3m_growth"] < -0.05,
            panel["sales_3m_growth"].between(-0.05, 0.05),
        ],
        ["UP", "DOWN", "FLAT"],
        default="INSUFFICIENT_DATA"
    )
    panel["recommendation"] = panel.apply(recommend_action, axis=1)

    check_points = [panel.loc[
            panel["ship_rate"].notna(),
            "ship_rate"
        ].between(0,1).all(),
        (panel["ship_rate_3m"] <= 1).all(),
        panel.loc[
            panel["trust_score"].notna(),
            "trust_score"
        ].between(0,1).all(),
        panel["sales_trend"].isna().mean() < 0.05
    ]
    
    if False in check_points:
        print(check_points)
        print("error in DataProcessing.py!!!!!")
        raise ValueError("Data quality checks failed.")
    else:
        print("Done Data Processing with all checks passed.")


    try:
        save_path = os.path.join(data_path, "DataProcessed.csv")
        panel.to_csv(save_path, index=False)
        print(f"Saved DataProcessed.csv successfully at {save_path}")
    except Exception as e:
        print(f"Failed to save DataProcessed.csv: {e}")
    
    return panel
if __name__ == "__main__":
    panel = preprocess_data()
    print(len(panel.columns))
    print(panel.columns)