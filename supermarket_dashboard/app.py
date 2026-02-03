import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Supermarket Dashboard", layout="wide")

# -----------------------------
# Load data
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("supermarket.csv")
    df["Date"] = pd.to_datetime(df["Date"])  # parses 3/1/2025 style dates
    df["Revenue"] = df["Unit_Price"] * df["Quantity"]
    return df

df = load_data()

st.title("🛒 Supermarket Sales Dashboard")
st.caption("Filters on the left • Metrics + charts update automatically")

# -----------------------------
# Sidebar filters
# -----------------------------
st.sidebar.header("Filters")

min_date = df["Date"].min()
max_date = df["Date"].max()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date.date(), max_date.date()),
    min_value=min_date.date(),
    max_value=max_date.date(),
)

regions = sorted(df["Store_Region"].unique())
categories = sorted(df["Category"].unique())
customer_types = sorted(df["Customer_Type"].unique())
promo_opts = sorted(df["Promo_Applied"].unique())

region_sel = st.sidebar.multiselect("Store Region", regions, default=regions)
cat_sel = st.sidebar.multiselect("Category", categories, default=categories)
cust_sel = st.sidebar.multiselect("Customer Type", customer_types, default=customer_types)
promo_sel = st.sidebar.multiselect("Promo Applied", promo_opts, default=promo_opts)

# Apply filters
start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

f = df[
    (df["Date"] >= start_date)
    & (df["Date"] <= end_date)
    & (df["Store_Region"].isin(region_sel))
    & (df["Category"].isin(cat_sel))
    & (df["Customer_Type"].isin(cust_sel))
    & (df["Promo_Applied"].isin(promo_sel))
].copy()

# -----------------------------
# Top KPI metrics
# -----------------------------
total_revenue = f["Revenue"].sum()
num_transactions = f["Transaction_ID"].nunique()
items_sold = f["Quantity"].sum()
avg_revenue_per_txn = total_revenue / num_transactions if num_transactions else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"${total_revenue:,.2f}")
c2.metric("Transactions", f"{num_transactions:,}")
c3.metric("Items Sold", f"{items_sold:,}")
c4.metric("Avg Revenue / Transaction", f"${avg_revenue_per_txn:,.2f}")

st.divider()

# -----------------------------
# Charts
# -----------------------------
left, right = st.columns(2)

# Revenue over time
rev_by_day = (
    f.groupby("Date", as_index=False)["Revenue"]
    .sum()
    .sort_values("Date")
)
fig_line = px.line(rev_by_day, x="Date", y="Revenue", markers=True, title="Revenue Over Time")
left.plotly_chart(fig_line, use_container_width=True)

# Revenue by category
rev_by_cat = (
    f.groupby("Category", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
)
fig_bar = px.bar(rev_by_cat, x="Category", y="Revenue", title="Revenue by Category")
right.plotly_chart(fig_bar, use_container_width=True)

# Promo vs non-promo
col1, col2 = st.columns(2)

promo_split = f.groupby("Promo_Applied", as_index=False)["Revenue"].sum()
fig_promo = px.pie(promo_split, names="Promo_Applied", values="Revenue", title="Revenue Share: Promo vs No Promo")
col1.plotly_chart(fig_promo, use_container_width=True)

# Payment method
pay_split = (
    f.groupby("Payment_Method", as_index=False)["Revenue"]
    .sum()
    .sort_values("Revenue", ascending=False)
)
fig_pay = px.bar(pay_split, x="Payment_Method", y="Revenue", title="Revenue by Payment Method")
col2.plotly_chart(fig_pay, use_container_width=True)

st.divider()

# -----------------------------
# Data table
# -----------------------------
st.subheader("Filtered Data")
st.dataframe(
    f.sort_values("Date", ascending=False),
    use_container_width=True,
    hide_index=True,
)
