import streamlit as st
import plotly.graph_objects as go
import numpy as np

# --- Sidebar Inputs ---
st.sidebar.title("Configuration")

lp_base_tokens = st.sidebar.number_input("Initial LP Base Token Allocation", min_value=1, value=35714285, step=1000000)
gp_mgmt_tokens = st.sidebar.number_input("GP Management Fee Tokens", min_value=0, value=5000000, step=500000)
total_tokens = st.sidebar.number_input("Total Tokens in SPV", min_value=1, value=76452599, step=1000000)
lp_investment = st.sidebar.number_input("LP Total Investment ($)", min_value=1, value=10000000, step=500000)
target_moic_for_gps = st.sidebar.number_input("LP MOIC Threshold Before GP", min_value=1.0, value=2.5, step=0.1)
cliff_months = st.sidebar.number_input("Cliff Period (Months)", min_value=0, value=24, step=1)
vesting_months = st.sidebar.number_input("Vesting Duration After Cliff (Months)", min_value=1, value=18, step=1)

# --- Token Inputs ---
token_price = st.slider("Token Price ($)", min_value=0.01, max_value=1.00, value=0.28, step=0.01)
month = st.slider("Month Since TGE", min_value=0, max_value=cliff_months + vesting_months, value=24)

# --- Derived Values ---
bonus_reserve = total_tokens - lp_base_tokens - gp_mgmt_tokens
monthly_vest_lp = lp_base_tokens / vesting_months
monthly_vest_bonus = bonus_reserve / vesting_months
monthly_vest_gp_mgmt = gp_mgmt_tokens / vesting_months

# --- Vesting Logic ---
if month < cliff_months:
    lp_vested = 0
    bonus_vested = 0
    gp_mgmt_vested = 0
else:
    lp_vested = min(lp_base_tokens, (month - cliff_months) * monthly_vest_lp)
    bonus_vested = min(bonus_reserve, (month - cliff_months) * monthly_vest_bonus)
    gp_mgmt_vested = min(gp_mgmt_tokens, (month - cliff_months) * monthly_vest_gp_mgmt)

# --- Value Calculations ---
lp_total_tokens = lp_base_tokens
lp_total_value = lp_total_tokens * token_price
moic = lp_total_value / lp_investment
bonus_remaining = bonus_reserve - bonus_vested

# --- Display Top Metrics ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("LP Token Price", f"${token_price:.2f}")
col2.metric("Vested LP Tokens", f"{int(lp_vested):,}")
col3.metric("Vested Bonus Tokens", f"{int(bonus_vested):,}")
col4.metric("MOIC", f"{moic:.2f}x")

# --- Token Bucket Visualization ---
labels = ["LP Vested", "Bonus Used", "Bonus Remaining", "GP Mgmt", "GP"]
values = [lp_vested, bonus_vested, bonus_remaining, gp_mgmt_vested, 0]
colors = ["#2a9d8f", "#f4a261", "#a8dadc", "#e76f51", "#b5838d"]

fig = go.Figure(data=[
    go.Bar(
        x=labels,
        y=values,
        marker_color=colors,
        text=[f"{int(v):,}" for v in values],
        textposition="auto"
    )
])
fig.update_layout(
    title="Token Allocation Buckets",
    yaxis_title="Tokens",
    xaxis_title="Category",
    height=500,
    template="plotly_dark"
)
st.plotly_chart(fig, use_container_width=True)
