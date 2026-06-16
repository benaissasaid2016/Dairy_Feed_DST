import streamlit as st
import plotly.express as px
import pandas as pd

# --- Page Config ---
st.set_page_config(
    page_title="Belgian Dairy Farm Calculator",
    page_icon="🇧🇪",
    layout="wide"
)


# --- 1. CORRECTED CALCULATION FUNCTION ---
def calculate_margin(cow_count, avg_milk_ltrs, milk_price, feed_items, other_costs_herd):
    """
    feed_items: list of dicts with 'qty' (kg/cow/day) and 'cost' (€/kg)
    other_costs_herd: total daily variable costs for the entire herd (€/day)
    """
    # Feed cost per cow per day
    feed_cost_per_cow = sum(item["qty"] * item["cost"] for item in feed_items)

    # Total herd calculations
    total_feed_cost = feed_cost_per_cow * cow_count
    total_daily_milk = cow_count * avg_milk_ltrs
    total_daily_cost = total_feed_cost + other_costs_herd
    daily_income = total_daily_milk * milk_price

    net_margin = daily_income - total_daily_cost
    feed_cost_per_liter = total_feed_cost / total_daily_milk if total_daily_milk > 0 else 0
    breakeven_price = total_daily_cost / total_daily_milk if total_daily_milk > 0 else 0
    margin_per_cow = net_margin / cow_count if cow_count > 0 else 0
    feed_cost_as_pct = (total_feed_cost / daily_income * 100) if daily_income > 0 else 0

    return {
        "total_milk": total_daily_milk,
        "total_feed_cost": total_feed_cost,
        "total_cost": total_daily_cost,
        "daily_income": daily_income,
        "net_margin": net_margin,
        "feed_cost_per_liter": feed_cost_per_liter,
        "breakeven_price": breakeven_price,
        "margin_per_cow": margin_per_cow,
        "feed_cost_per_cow": feed_cost_per_cow,  # This is the TRUE per-cow feed cost
        "feed_cost_as_pct": feed_cost_as_pct
    }


# --- 2. SIDEBAR: USER INPUTS ---
with st.sidebar:
    st.header("🇧🇪 Farm Details")

    cow_count = st.number_input(
        "Number of Milking Cows",
        min_value=1,
        value=80,
        step=1,
        help="Average Belgian dairy herd size is ~80 cows"
    )

    avg_milk = st.number_input(
        "Avg. Liters per Cow / Day",
        min_value=0.0,
        value=28.0,
        step=0.5,
        help="Belgian average: ~28–32 liters per cow per day"
    )

    milk_price = st.number_input(
        "Milk Price (€ per Liter)",
        min_value=0.0,
        value=0.3833,
        step=0.001,
        format="%.4f",
        help="June 2026 Belgian average: €0.3833 per liter"
    )

    st.caption(f"📊 **Market context:** Belgian milk prices range from €0.335–0.40/L.")

    st.divider()
    st.subheader("🌾 Feed Ration (per cow, per day)")

    feed_items = []
    num_feeds = st.number_input("Number of feed types", min_value=1, max_value=6, value=4, step=1)

    # Realistic Belgian default values (adjusted for 2026)
    feed_suggestions = {
        0: {"name": "Grass Silage", "qty": 25, "cost": 0.12},
        1: {"name": "Corn Silage", "qty": 15, "cost": 0.14},
        2: {"name": "Concentrate", "qty": 6, "cost": 0.33},
        3: {"name": "Hay", "qty": 3, "cost": 0.15},
        4: {"name": "Protein Supplement", "qty": 2, "cost": 0.50},
        5: {"name": "Mineral Mix", "qty": 0.5, "cost": 0.60}
    }

    for i in range(int(num_feeds)):
        st.write(f"**Feed {i + 1}**")
        col1, col2 = st.columns(2)
        with col1:
            default_name = feed_suggestions.get(i, {}).get("name", f"Feed {i + 1}")
            name = st.text_input(f"Name", key=f"name_{i}", value=default_name)
        with col2:
            default_qty = feed_suggestions.get(i, {}).get("qty", 10.0)
            qty = st.number_input(
                f"Qty (kg/cow/day)",
                key=f"qty_{i}",
                min_value=0.0,
                value=float(default_qty),
                step=0.5
            )
        default_cost = feed_suggestions.get(i, {}).get("cost", 0.20)
        cost = st.number_input(
            f"Cost per kg (€)",
            key=f"cost_{i}",
            min_value=0.0,
            value=float(default_cost),
            step=0.01,
            format="%.3f"
        )
        feed_items.append({"name": name, "qty": qty, "cost": cost})

    st.divider()

    # IMPORTANT: This is now TOTAL for the HERD, not per cow
    other_costs_herd = st.number_input(
        "Other Variable Costs (€/day - TOTAL HERD)",
        min_value=0.0,
        value=100.0,
        step=10.0,
        help="Total daily cost for veterinary, breeding, electricity, water, etc. (for all cows). ~€1–2/cow/day is typical."
    )

    calculate_btn = st.button("🔄 Calculate My Margins", type="primary")

# --- 3. MAIN PAGE ---
st.title("🇧🇪 Belgian Dairy Farm Feed Cost & Margin Calculator")
st.caption("📅 Data updated: June 2026 | All values in €")

st.info(
    "💡 **Belgian Dairy Sector Snapshot:** "
    "Average milk price: **€0.38–0.40/L** (June 2026) | "
    "Herd size: **~80 cows** | "
    "Dairy farms: **5,640** (2024, -4.1% YoY)"
)

# --- 4. RESULTS ---
if calculate_btn:
    results = calculate_margin(cow_count, avg_milk, milk_price, feed_items, other_costs_herd)

    st.subheader("📊 Key Performance Indicators")

    # Color coding for margin
    margin_color = "normal"
    if results['margin_per_cow'] < 0:
        margin_color = "inverse"
    elif results['margin_per_cow'] < 1.5:
        margin_color = "off"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Feed Cost / Cow / Day", f"€{results['feed_cost_per_cow']:.2f}")  # Now shows ~€7.50
    col2.metric("Margin / Cow / Day", f"€{results['margin_per_cow']:.2f}", delta_color=margin_color)
    col3.metric("Total Daily Margin (Herd)", f"€{results['net_margin']:.2f}")
    col4.metric("Feed Cost per Liter", f"€{results['feed_cost_per_liter']:.3f}")

    st.caption("")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Daily Milk", f"{results['total_milk']:,.0f} L")
    col2.metric("Feed Cost as % of Income", f"{results['feed_cost_as_pct']:.1f}%")
    col3.metric("Break-even Milk Price", f"€{results['breakeven_price']:.3f}")

    st.divider()

    # --- Charts ---
    st.subheader("💰 Income vs Cost Breakdown (Herd Level)")
    data = {
        "Category": ["🥛 Milk Income", "🌾 Feed Cost", "🔧 Other Costs"],
        "Amount": [results['daily_income'], results['total_feed_cost'], other_costs_herd]
    }
    df = pd.DataFrame(data)
    colors = ["#2ecc71", "#e74c3c", "#f39c12"]
    fig = px.bar(df, x="Category", y="Amount", color="Category",
                 color_discrete_sequence=colors, text_auto=".2f",
                 title="Daily Income vs. Cost Breakdown (Entire Herd)")
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # --- Feed Cost Breakdown ---
    st.subheader("📦 Feed Cost Breakdown (per cow, per day)")
    feed_data = []
    for item in feed_items:
        cost_per_cow = item["qty"] * item["cost"]
        feed_data.append({"Feed": item["name"], "Cost per Cow (€)": cost_per_cow})
    feed_df = pd.DataFrame(feed_data)
    fig2 = px.pie(feed_df, values="Cost per Cow (€)", names="Feed",
                  title="Share of Feed Cost by Type", hole=0.4)
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # --- 5. WHAT-IF SIMULATOR ---
    st.subheader("🔮 What-If Scenario Simulator")
    col1, col2 = st.columns(2)
    with col1:
        new_milk_price = st.slider(
            "Adjust Milk Price (€/L)",
            min_value=0.20,
            max_value=0.60,
            value=float(milk_price),
            step=0.005,
            format="€%.3f"
        )
    with col2:
        cost_multiplier = st.slider(
            "Feed Cost Adjustment (%)",
            min_value=70,
            max_value=130,
            value=100,
            step=5,
            help="100% = current feed costs"
        )

    adjusted_feed = [
        {"name": f["name"], "qty": f["qty"], "cost": f["cost"] * (cost_multiplier / 100)}
        for f in feed_items
    ]
    new_results = calculate_margin(
        cow_count,
        avg_milk,
        new_milk_price,
        adjusted_feed,
        other_costs_herd
    )

    scen_col1, scen_col2, scen_col3 = st.columns(3)
    delta_margin = new_results['margin_per_cow'] - results['margin_per_cow']
    scen_col1.metric(
        "Projected Margin / Cow / Day",
        f"€{new_results['margin_per_cow']:.2f}",
        delta=f"{delta_margin:+.2f}",
        delta_color="normal"
    )
    scen_col2.metric(
        "Projected Feed Cost / L",
        f"€{new_results['feed_cost_per_liter']:.3f}",
        delta=f"{new_results['feed_cost_per_liter'] - results['feed_cost_per_liter']:+.3f}"
    )
    scen_col3.metric(
        "Projected Total Daily Margin",
        f"€{new_results['net_margin']:.2f}",
        delta=f"{new_results['net_margin'] - results['net_margin']:+.2f}"
    )

    st.divider()

    # --- 6. SMART RECOMMENDATIONS ---
    st.subheader("📋 Smart Recommendations")

    recommendations = []

    # Margin health
    if new_results['margin_per_cow'] < 0:
        recommendations.append(("error", "🚨 CRITICAL: You are losing money per cow!",
                                f"Margin is €{new_results['margin_per_cow']:.2f}/cow/day. "
                                f"Monthly loss ≈ €{abs(new_results['margin_per_cow'] * cow_count * 30):,.0f}."))
    elif new_results['margin_per_cow'] < 1.5:
        recommendations.append(("warning", "⚡ Caution: Very thin margin",
                                f"Margin of €{new_results['margin_per_cow']:.2f}/cow/day is below the €2.00 target."))
    else:
        recommendations.append(("success", "✅ Healthy Margin!",
                                f"Margin of €{new_results['margin_per_cow']:.2f}/cow/day is sustainable."))

    # Feed efficiency
    if new_results['feed_cost_as_pct'] > 55:
        recommendations.append(("warning", "🌾 Feed costs are very high",
                                f"Feed is {new_results['feed_cost_as_pct']:.1f}% of income (benchmark 40–50%). Optimize ration."))
    elif new_results['feed_cost_as_pct'] > 45:
        recommendations.append(("info", "📊 Feed costs at industry average",
                                f"Feed is {new_results['feed_cost_as_pct']:.1f}% of income. Look for small efficiency gains."))
    else:
        recommendations.append(("success", "🌟 Excellent feed efficiency!",
                                f"Feed is only {new_results['feed_cost_as_pct']:.1f}% of income. Well done!"))

    # Break-even check
    if new_milk_price < new_results['breakeven_price']:
        recommendations.append(("error", "📉 Milk price below break-even",
                                f"Need +€{new_results['breakeven_price'] - new_milk_price:.3f}/L to break even."))

    # Display recommendations
    for rec_type, title, detail in recommendations:
        if rec_type == "error":
            st.error(f"**{title}**\n\n{detail}")
        elif rec_type == "warning":
            st.warning(f"**{title}**\n\n{detail}")
        elif rec_type == "info":
            st.info(f"**{title}**\n\n{detail}")
        else:
            st.success(f"**{title}**\n\n{detail}")

    st.divider()

    # --- 7. BENCHMARK TABLE ---
    st.subheader("📊 Benchmark Comparison (Belgian Averages)")
    bench_data = {
        "Metric": ["Feed Cost / Cow / Day (€)", "Feed Cost / L (€)", "Margin / Cow / Day (€)", "Feed as % of Income"],
        "Your Farm": [
            f"€{new_results['feed_cost_per_cow']:.2f}",
            f"€{new_results['feed_cost_per_liter']:.3f}",
            f"€{new_results['margin_per_cow']:.2f}",
            f"{new_results['feed_cost_as_pct']:.1f}%"
        ],
        "Belgian Average": ["€7.00 – 9.00", "€0.22 – 0.28", "€1.50 – 3.00", "40 – 50%"],
        "Status": [
            "✅" if 7 <= new_results['feed_cost_per_cow'] <= 9 else "⚠️",
            "✅" if 0.22 <= new_results['feed_cost_per_liter'] <= 0.28 else "⚠️",
            "✅" if new_results['margin_per_cow'] >= 2 else "⚠️",
            "✅" if new_results['feed_cost_as_pct'] <= 50 else "⚠️"
        ]
    }
    st.table(pd.DataFrame(bench_data))
    st.caption("📌 *Averages based on 2025–2026 Belgian market data.*")

else:
    st.info("👈 Fill in your farm data and click **'Calculate My Margins'**.")
    st.markdown("""
    ### 🇧🇪 About This Tool
    - Calculates **true feed cost per cow** and per liter.
    - Compares against **Belgian averages**.
    - Runs **what-if scenarios** for price changes.
    - Gives **actionable recommendations**.
    """)