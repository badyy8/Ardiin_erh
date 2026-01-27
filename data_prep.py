import pandas as pd
import numpy as np

INPUT_PARQUET = "ardiin_erh.pqt"
LOOKUP_CSV = "loyalty_lookup_2.csv"
OUTPUT_PARQUET = "ardiin_erh_code_grouped_all_years.pqt"


# -----------------------------
# 1) Load
# -----------------------------
df = pd.read_parquet(INPUT_PARQUET)
loyal_code_df = pd.read_csv(LOOKUP_CSV)


# -----------------------------
# 2) Remove test / invalid records (robust)
# -----------------------------
df = df.copy()

# Remove explicit test description
df = df[df["TXN_DESC"].fillna("").str.strip() != "Тест"]

# Remove specific test loyalty code
df = df[df["LOYAL_CODE"].fillna("") != "LUNAR_RDXQR"]

# Fill missing loyalty codes
df["LOYAL_CODE"] = df["LOYAL_CODE"].fillna("None").astype(str)


# -----------------------------
# 3) Parse dates safely (works for 2026+)
# -----------------------------
# TXN_DATE can come in different string formats; try coerce safely
df["TXN_DATE"] = pd.to_datetime(df["TXN_DATE"], errors="coerce")
df["POST_DATE"] = pd.to_datetime(df["POST_DATE"], errors="coerce")

# Drop rows with missing transaction date (optional but recommended)
df = df[df["TXN_DATE"].notna()].copy()


# -----------------------------
# 4) Time features (year-safe)
# -----------------------------
df["YEAR"] = df["TXN_DATE"].dt.year
df["MONTH_NUM"] = df["TXN_DATE"].dt.month
df["MONTH_NAME"] = df["TXN_DATE"].dt.strftime("%b").str.upper()
df["year_month"] = df["TXN_DATE"].dt.to_period("M").astype(str)


# -----------------------------
# 5) TXN_DESC cleaning (safe)
# -----------------------------
df["TXN_DESC"] = df["TXN_DESC"].fillna("").astype(str).str.strip()

df["TXN_DESC"] = (
    df["TXN_DESC"]
    .str.replace("Крипто Вик", "Crypto Week", regex=False)
    .str.replace("Кривто Вик", "Crypto Week", regex=False)
    .str.replace(".", "", regex=False)
    .str.lower()
)


# -----------------------------
# 6) Loyalty code grouping (your logic, with small safety improvements)
# -----------------------------
GEO_CODES = {
    "BAGANUUR", "BULGAN", "DARKHAN", "ERDENET",
    "KHENTII", "CHOIR", "SAINSHAND", "SELENGE"
}

def map_group_fixed(code: str) -> str:
    if pd.isna(code):
        return "Financial Transactions"

    code = str(code)

    if code in GEO_CODES:
        return "Geographic Campaigns"

    if (
        code.startswith("10K_OPEN")
        or code in {"ARD_SEC", "ARD_SEC1", "ARD_SEC100", "10K_KIDS61"}
        or code.endswith("UTSD")
        or "TETDANS" in code
    ):
        return "Account Opening"

    if (
        "TRANSACTION" in code
        or "CHARGE" in code
        or "CCA" in code
        or "AFFILIATE" in code
        or code in {"LOYALTY_LIMIT", "ACO", "ZEEL_TULULT", "10K_TULBUR_TSES"}
    ):
        return "Financial Transactions"

    if "INSUR" in code or "DAATGAL" in code:
        return "Insurance"

    if (
        code.startswith(("MARAL", "MARAN"))
        or "KRYPTOS" in code
        or "PNP" in code
        or "LOTTO" in code
        or code == "10K_GAME"
    ):
        return "Merchant & Lifestyle"

    if (
        "SOCIAL" in code
        or "FACEBOOK" in code
        or "SELFIE" in code
        or "MEDEE" in code
        or "TUUH" in code
    ):
        return "Social & Engagement"

    if (
        code.startswith("10K_BUY")
        or code.startswith("ARD_BIT")
        or code.startswith("ARD_IDAX")
        or code.startswith("ARD_UBX")
        or "1072" in code
        or "HOS" in code
        or "HOUS" in code
    ):
        return "Investments & Securities"

    # Campaigns/events: make this future-proof by allowing ARD_/INVESTORWEEK/SMART/HURUNGU
    if code.startswith(("ARD_", "INVESTORWEEK", "TVMEN", "SMART", "HURUNGU", "PENSION_SURGALT", "CREDIT_SURGALT", "CREDIT_ZEEL", "ARDCOIN", "CREDIT_AIRDROP")):
        return "Campaigns & Events"

    # NEW: Let future yearly campaign codes still go here (INF2025, INF2026, etc.)
    if code.startswith("INF") and code[3:7].isdigit():
        return "Campaigns & Events"

    return "Other"


df["CODE_GROUP"] = df["LOYAL_CODE"].apply(map_group_fixed)


# -----------------------------
# 7) Save (future-proof output name)
# -----------------------------
df.to_parquet(OUTPUT_PARQUET, index=False)

print("Saved:", OUTPUT_PARQUET)
print("Years included:", sorted(df["YEAR"].unique()))
print("Rows:", len(df))
