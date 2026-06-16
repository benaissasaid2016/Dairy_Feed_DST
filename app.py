import streamlit as st
import plotly.express as px
import pandas as pd

# --- Page Config ---
st.set_page_config(page_title="Dairy Feed Calculator", layout="wide")


# --- 1. DEFINE THE CALCULATION FUNCTION (Must be before you call it!) ---
def calculate_margin(cow_count, avg_milk_ltrs, milk_price, feed_items, other_costs):
    total_daily_milk = cow_count * avg_milk_ltrs
    total_feed_cost = sum(item["qty"] * item["cost"] for item in feed_items)
    total_daily_cost = total_feed_cost + other_costs
    daily_income = total_daily_milk * milk_price

    net_margin = daily_income - total_daily_cost
    feed_cost_per_liter = total_feed_cost / total_daily_milk if total_daily_milk > 0 else 0
    breakeven_price = total_daily_cost / total_daily_milk if total_daily_milk > 0 else 0
    margin_per_cow = net_margin / cow_count if cow_count > 0 else 0

    return {
        "total_milk": total_daily_milk,
        "total_feed_cost": total_feed_cost,
        "total_cost": total_daily_cost,
        "daily_income": daily_income,
        "net_margin": net_margin,
        "feed_cost_per_liter": feed_cost_per_liter,
        "breakeven_price": breakeven_price,
        "margin_per_cow": margin_per_cow
    }


# --- 2. SIDEBAR: USER INPUTS ---
with st.sidebar:
    st.header("🐄 Farm Details")
    cow_count = st.number_input("Number of Milking Cows", min_value=1, value=50, step=1)
    avg_milk = st.number_input("Avg. Liters per Cow / Day", min_value=0.0, value=25.0, step=0.5)
    milk_price = st.number_input("Milk Price (per Liter)", min_value=0.0, value=0.45, step=0.01, format="%.2f")

    st.divider()
    st.subheader("🌾 Feed Ration")

    feed_items = []
    num_feeds = st.number_input("Number of feed types", min_value=1, max_value=6, value=3, step=1)

    for i in range(int(num_feeds)):
        st.write(f"**Feed {i + 1}**")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input(f"Name", key=f"name_{i}", value=f"Feed {i + 1}")
        with col2:
            qty = st.number_input(f"Qty (kg/day)", key=f"qty_{i}", min_value=0.0, value=10.0, step=1.0)
        cost = st.number_input(f"Cost per kg", key=f"cost_{i}", min_value=0.0, value=0.20, step=0.01)
        feed_items.append({"name": name, "qty": qty, "cost": cost})

    st.divider()
    other_costs = st.number_input("Other Variable Costs (per day)", min_value=0.0, value=10.0, step=1.0)

    # THE BUTTON - This is CRUCIAL
    calculate_btn = st.button("🔄 Calculate My Margins", type="primary")

# --- 3. MAIN PAGE: RESULTS & DASHBOARD ---
st.title("🥛 Dairy Farm Feed Cost & Margin Calculator")

# ONLY run this block IF the button is clicked
if calculate_btn:
    # Call the function safely here
    results = calculate_margin(cow_count, avg_milk, milk_price, feed_items, other_costs)

    # Display Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Feed Cost per Liter", f"${results['feed_cost_per_liter']:.2f}")
    col2.metric("Margin / Cow / Day", f"${results['margin_per_cow']:.2f}")
    col3.metric("Total Daily Margin", f"${results['net_margin']:.2f}")
    col4.metric("Break-even Milk Price", f"${results['breakeven_price']:.2f}")

    # Chart: Income vs Costs
    st.subheader("💰 Income vs Cost Breakdown")
    data = {
        "Category": ["Milk Income", "Feed Cost", "Other Costs"],
        "Amount": [results['daily_income'], results['total_feed_cost'], other_costs]
    }
    df = pd.DataFrame(data)
    fig = px.bar(df, x="Category", y="Amount", color="Category", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    # --- 4. WHAT-IF SIMULATOR ---
    st.divider()
    st.subheader("🔮 What-If Scenario Simulator")
    col1, col2 = st.columns(2)
    with col1:
        new_milk_price = st.slider("Adjust Milk Price",
                                   min_value=0.0,
                                   max_value=1.0,
                                   value=float(milk_price),
                                   step=0.01,
                                   format="$%.2f")
    with col2:
        cost_multiplier = st.slider("Feed Cost Adjustment (%)",
                                    min_value=80,
                                    max_value=120,
                                    value=100,
                                    step=5)

    adjusted_feed = [{"name": f["name"], "qty": f["qty"], "cost": f["cost"] * (cost_multiplier / 100)} for f in
                     feed_items]
    new_results = calculate_margin(cow_count, avg_milk, new_milk_price, adjusted_feed, other_costs)

    st.metric("Projected New Margin per Cow", f"${new_results['margin_per_cow']:.2f}",
              delta=f"{new_results['margin_per_cow'] - results['margin_per_cow']:.2f}")

    # Recommendations
    st.subheader("📋 Smart Recommendations")
    if new_results['margin_per_cow'] < 0:
        st.error(
            "⚠️ **Alert:** You are losing money per cow per day. Consider reducing feed costs or negotiating a higher milk price.")
    elif new_results['margin_per_cow'] < 2:
        st.warning(
            "⚡ **Caution:** Your margin is thin. Use the simulator to see how a 5% feed cost reduction improves profit.")
    else:
        st.success("✅ **Healthy Margin!** You have room to absorb small price fluctuations.")

else:
    # What to show before the button is pressed
    st.info("👈 Please fill in your farm data in the sidebar and click **'Calculate My Margins'** to see your results.")
