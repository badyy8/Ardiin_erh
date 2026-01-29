import streamlit as st
import pandas as pd

@st.cache_data(show_spinner=True)
def load_data():
    df = pd.read_parquet(
        "ardiin_erh_code_grouped_2024_2025.pqt"
    )

    df["TXN_DATE"] = pd.to_datetime(df["TXN_DATE"], errors="coerce")
    df = df[df["TXN_DATE"].notna()].copy()

    df["year_month"] = df["TXN_DATE"].dt.to_period("M").astype(str)
    df["year"] = df["TXN_DATE"].dt.year
    df["CUST_CODE"] = df["CUST_CODE"].astype("category")
    df["MONTH_NUM"] = df["MONTH_NUM"].astype("int16")
    df["TXN_AMOUNT"] = pd.to_numeric(df["TXN_AMOUNT"], errors="coerce")


    return df

@st.cache_data(show_spinner=False)
def get_lookup():

    lookup_df = pd.read_csv("loyalty_lookup_2.csv")
    loyal_code_to_desc = dict(
        zip(lookup_df["LOYAL_CODE"], lookup_df["TXN_DESC"].str.capitalize())
    )
    return loyal_code_to_desc

@st.cache_data(show_spinner=True)
def load_precomputed_page1():
    user_level_stat_monthly = pd.read_parquet("data/page1/precomputed_user_level_stat_monthly.pqt", engine="pyarrow")
    monthly_reward_stat = pd.read_parquet("data/page1/precomputed_monthly_reward_stat.pqt", engine="pyarrow")
    point_cutoff = pd.read_parquet("data/page1/precomputed_point_cutoff.pqt", engine="pyarrow")

    return user_level_stat_monthly, monthly_reward_stat, point_cutoff


# ------------------- PAGE 2 DATA ----------------------------

@st.cache_data(show_spinner=True)
def load_precomputed_page2():
    grouped_reward = pd.read_parquet("data/page2/precomputed_grouped_reward.pqt", engine="pyarrow")
    transaction_summary = pd.read_parquet("data/page2/precomputed_transaction_summary.pqt", engine="pyarrow")
    transaction_summary_with_pad = pd.read_parquet("data/page2/precomputed_transaction_summary_with_pad.pqt", engine="pyarrow")
    return grouped_reward, transaction_summary, transaction_summary_with_pad

@st.cache_data(show_spinner=False)
def load_page2_codegroup_map():
    return pd.read_parquet("data/page2/precomputed_codegroup_loyalcode_map.pqt", engine="pyarrow")

@st.cache_data(show_spinner=False)
def load_page2_movers_monthly():
    return pd.read_parquet("data/page2/precomputed_movers_monthly.pqt", engine="pyarrow")


#------------------ PAGE 4 ---------------------


@st.cache_data(show_spinner=False)
def filter_df_by_year(df: pd.DataFrame, year: int) -> pd.DataFrame:
    df = df.copy()
    return df[df["year"] == year].copy()


@st.cache_data(show_spinner=True)
def load_precomputed_page4():
    users_agg_df = pd.read_parquet("data/page4/users_agg_df.pqt", engine="pyarrow")
    thresholds_df = pd.read_parquet("data/page4/thresholds.pqt", engine="pyarrow")
    user_segment_monthly_df = pd.read_parquet("data/page4/user_segment_monthly_df.pqt", engine="pyarrow")
    segment_loyal_summary = pd.read_parquet("data/page4/segment_loyal_summary.pqt", engine="pyarrow")

    return users_agg_df, thresholds_df, user_segment_monthly_df, segment_loyal_summary


@st.cache_data(show_spinner=False)
def get_most_growing_loyal_code_from_monthly(movers_monthly: pd.DataFrame, year: int):
    df = movers_monthly[movers_monthly["year"] == year].copy()

    # Enforce > 6 active months
    df = df.groupby("LOYAL_CODE", observed=True).filter(lambda x: x["MONTH_NUM"].nunique() > 6)

    stats = df.groupby("LOYAL_CODE", observed=True)["TXN_AMOUNT"].agg(first="first", last="last")
    stats = stats[stats["first"] > 0]

    stats["PCT_INCREASE"] = ((stats["last"] - stats["first"]) / stats["first"]) * 100

    movers_df = (
        stats[(stats["PCT_INCREASE"] > 20) & (stats["last"] > 100_000)]
        .sort_values("PCT_INCREASE", ascending=False)
        .head(4)
        .reset_index()
    )

    return movers_df["LOYAL_CODE"], movers_df




# -------------------- PAGE 5 ----------------------

@st.cache_data(show_spinner=False)
def get_monthly_customer_points(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per customer per month: Total monthly points.
    Used in tab5 (distribution / bins).
    """
    out = (
        df.groupby(["MONTH_NUM", "MONTH_NAME", "CUST_CODE"], observed=True)["TXN_AMOUNT"]
        .sum()
        .reset_index()
        .rename(columns={"TXN_AMOUNT": "Total_Points"})
    )
    return out


@st.cache_data(show_spinner=False)
def get_users_agg_by_monthnum(df: pd.DataFrame) -> pd.DataFrame:
    """
    One row per customer per month_num (aggregated).
    Used throughout Page 5.
    """
    users_agg_df = (
        df.groupby(["CUST_CODE", "MONTH_NUM"], observed=True)
        .agg(
            Total_Points=("TXN_AMOUNT", "sum"),
            Transaction_Count=("JRNO", "count"),
            Unique_Loyal_Codes=("LOYAL_CODE", "nunique"),
            Active_Days=("TXN_DATE", "nunique"),
        )
        .reset_index()
    )

    users_agg_df["Reached_1000_Flag"] = (users_agg_df["Total_Points"] >= 1000).astype(int)
    users_agg_df["Inactive"] = (users_agg_df["Transaction_Count"] <= 1).astype(int)

    return users_agg_df


@st.cache_data(show_spinner=False)
def get_page5_thresholds(users_agg_df: pd.DataFrame) -> dict:
    """
    Percentile thresholds used for segmentation (Page 5).
    """
    user_under_1000 = users_agg_df[(users_agg_df["Reached_1000_Flag"] == 0) & (users_agg_df["Inactive"] == 0)]
    user_reached_1000 = users_agg_df[users_agg_df["Reached_1000_Flag"] == 1]

    return {
        "txn_q25": user_under_1000["Transaction_Count"].quantile(0.25),
        "txn_q75": user_under_1000["Transaction_Count"].quantile(0.75),
        "days_q25": user_under_1000["Active_Days"].quantile(0.25),
        "days_q75": user_under_1000["Active_Days"].quantile(0.75),
        "points_q25": user_under_1000["Total_Points"].quantile(0.25),
        "points_q75": user_under_1000["Total_Points"].quantile(0.75),
        "achievers_txn_q25": user_reached_1000["Transaction_Count"].quantile(0.25),
    }


@st.cache_data(show_spinner=False)
def assign_page5_segments(users_agg_df: pd.DataFrame, thresholds: dict) -> pd.DataFrame:
    """
    Vectorized segmentation (fast).
    Mongolian labels to match your page.
    """
    out = users_agg_df.copy()

    txn_q75 = thresholds["txn_q75"]
    days_q75 = thresholds["days_q75"]
    achievers_txn_q25 = thresholds["achievers_txn_q25"]

    out["User_Segment"] = "Тогтмол_бус_оролцогч"

    out.loc[(out["Transaction_Count"] >= txn_q75) & (out["Active_Days"] > days_q75), "User_Segment"] = "Тогтвортой"
    out.loc[(out["Transaction_Count"] < txn_q75) & (out["Active_Days"] <= days_q75), "User_Segment"] = "Туршигч"
    out.loc[out["Transaction_Count"] >= achievers_txn_q25, "User_Segment"] = "Их_чармайлттай"
    out.loc[out["Reached_1000_Flag"] == 1, "User_Segment"] = "Амжилттай"
    out.loc[out["Inactive"] == 1, "User_Segment"] = "Идэвхгүй"

    return out


@st.cache_data(show_spinner=False)
def get_page5_user_milestone_counts(users_agg_df: pd.DataFrame) -> pd.DataFrame:
    """
    For tab2: how many times each user reached 1000.
    """
    reached = users_agg_df[(users_agg_df["Reached_1000_Flag"] == 1)]

    user_milestone_counts = (
        reached.groupby("CUST_CODE", observed=True)
        .size()
        .reset_index(name="Times_Reached_1000")
        .sort_values("Times_Reached_1000", ascending=False)
    )

    reach_frequency = (
        user_milestone_counts.groupby("Times_Reached_1000", observed=True)["CUST_CODE"]
        .size()
        .reset_index(name="Number_of_Users")
    )
    reach_frequency["Total"] = reach_frequency["Times_Reached_1000"] * reach_frequency["Number_of_Users"]

    return reach_frequency


@st.cache_data(show_spinner=False)
def get_page5_loyal_normalized_profile(df: pd.DataFrame, users_agg_df: pd.DataFrame) -> pd.DataFrame:
    """
    For tab3: build normalized points per loyal code among months where total >= 1000.
    """
    monthly_totals = (
        df.groupby(["CUST_CODE", "MONTH_NUM"], observed=True)["TXN_AMOUNT"]
        .sum()
        .reset_index(name="True_Monthly_Total")
    )

    loyal_code_agg = (
        df.groupby(["CUST_CODE", "LOYAL_CODE", "MONTH_NUM"], observed=True)["TXN_AMOUNT"]
        .sum()
        .reset_index()
    )

    segment_map = users_agg_df[["CUST_CODE", "MONTH_NUM", "User_Segment"]].copy()

    total_loyal_df = (
        loyal_code_agg
        .merge(segment_map, on=["CUST_CODE", "MONTH_NUM"], how="inner")
        .merge(monthly_totals, on=["CUST_CODE", "MONTH_NUM"], how="left")
    )

    final_df = total_loyal_df[total_loyal_df["True_Monthly_Total"] >= 1000].copy()

    # Business cleaning
    final_df = final_df[final_df["LOYAL_CODE"].notna()]
    #final_df = final_df[final_df["LOYAL_CODE"] != "None"]
    final_df = final_df[final_df["LOYAL_CODE"] != "10K_PURCH_INSUR"]

    final_df["Normalized_Points"] = (final_df["TXN_AMOUNT"] / final_df["True_Monthly_Total"]) * 1000

    user_month_profile = (
        final_df.groupby(["CUST_CODE", "MONTH_NUM", "LOYAL_CODE"], observed=True)["Normalized_Points"]
        .sum()
        .reset_index()
    )

    return user_month_profile

@st.cache_data(show_spinner=False)
def get_page5_bundle(df: pd.DataFrame, year: int) -> dict:
    df_year = df[df["year"] == year].copy()

    monthly_customer_points = get_monthly_customer_points(df_year)

    users_agg_df = get_users_agg_by_monthnum(df_year)
    thresholds = get_page5_thresholds(users_agg_df)
    users_agg_df = assign_page5_segments(users_agg_df, thresholds)

    reach_frequency = get_page5_user_milestone_counts(users_agg_df)

    # ✅ Tab3 heavy profile (only for achievers)
    user_month_profile = get_page5_loyal_normalized_profile(df_year, users_agg_df)

    return {
        "df_year": df_year,
        "monthly_customer_points": monthly_customer_points,
        "users_agg_df": users_agg_df,
        "thresholds": thresholds,
        "reach_frequency": reach_frequency,
        "user_month_profile": user_month_profile,
    }


# ------------------- PAGE MISC ----------------------

@st.cache_data(show_spinner=False)
def load_precomputed_page_misc_counts():
    return pd.read_parquet("data/page_misc/precomputed_monthly_bucket_counts.pqt", engine="pyarrow")

@st.cache_data(show_spinner=False)
def load_precomputed_page_misc_loyal_avg():
    return pd.read_parquet("data/page_misc/precomputed_loyal_avg_by_year.pqt", engine="pyarrow")

@st.cache_data(show_spinner=False)
def load_precomputed_page_misc_reach_frequency():
    return pd.read_parquet("data/page_misc/precomputed_reach_frequency_by_year.pqt", engine="pyarrow")
