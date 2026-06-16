import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="Belgian Dairy Farm Calculator",
    page_icon="🇧🇪",
    layout="wide"
)

# --- 1. CALCULATION FUNCTION ---
def calculate_margin(cow_count, avg_milk_ltrs, milk_price, feed_items, other_costs):
    total_daily_milk = cow_count * avg_milk_ltrs
    total_feed_cost = sum(item["qty"] * item["cost"] for item in feed_items)
    total_daily_cost = total_feed_cost + other_costs
    daily_income = total_daily_milk * milk_price

    net_margin = daily_income - total_daily_cost
    feed_cost_per_liter = total_feed_cost / total_daily_milk if total_daily_milk > 0 else 0
    breakeven_price = total_daily_cost / total_daily_milk if total_daily_milk > 0 else 0
    margin_per_cow = net_margin / cow_count if cow_count > 0 else 0
    feed_cost_per_cow = total_feed_cost / cow_count if cow_count > 0 else 0
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
        "feed_cost_per_cow": feed_cost_per_cow,
        "feed_cost_as_pct": feed_cost_as_pct
    }

# --- 2. SIDEBAR: USER INPUTS ---
with st.sidebar:
    st.header("🇧🇪 Farm Details")

    # Herd info with Belgian typical values
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
        help="Belgian average: ~28-32 liters per cow per day"
    )

    # Milk price with Belgian market context
    milk_price = st.number_input(
        "Milk Price (€ per Liter)",
        min_value=0.0,
        value=0.3833,
        step=0.001,
        format="%.4f",
        help="June 2026 Belgian average: €0.3833 per liter (€38.33/100L)[reference:0]"
    )

    st.caption(f"📊 **Market context:** Belgian milk prices range from €0.335 – 0.40/L. LDA paid €0.48/kg avg in 2025[reference:1][reference:2]")

    st.divider()
    st.subheader("🌾 Feed Ration")

    feed_items = []
    num_feeds = st.number_input("Number of feed types", min_value=1, max_value=6, value=4, step=1)

    # Pre-filled feed suggestions with realistic Belgian prices
    feed_suggestions = {
        0: {"name": "Grass Silage", "qty": 35, "cost": 0.14},
        1: {"name": "Corn Silage", "qty": 20, "cost": 0.16},
        2: {"name": "Concentrate", "qty": 8, "cost": 0.35},
        3: {"name": "Hay", "qty": 5, "cost": 0.20},
        4: {"name": "Protein Supplement", "qty": 3, "cost": 0.50},
        5: {"name": "Mineral Mix", "qty": 1, "cost": 0.60}
    }

    for i in range(int(num_feeds)):
        st.write(f"**Feed {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            default_name = feed_suggestions.get(i, {}).get("name", f"Feed {i+1}")
            name = st.text_input(f"Name", key=f"name_{i}", value=default_name)
        with col2:
            default_qty = feed_suggestions.get(i, {}).get("qty", 10.0)
            qty = st.number_input(f"Qty (kg/cow/day)", key=f"qty_{i}", min_value=0.0, value=float(default_qty), step=0.5)
        default_cost = feed_suggestions.get(i, {}).get("cost", 0.20)
        cost = st.number_input(f"Cost per kg (€)", key=f"cost_{i}", min_value=0.0, value=float(default_cost), step=0.01, format="%.3f")
        feed_items.append({"name": name, "qty": qty, "cost": cost})

    st.divider()

    other_costs = st.number_input(
        "Other Variable Costs (€/day)",
        min_value=0.0,
        value=15.0,
        step=1.0,
        help="Veterinary, breeding, electricity, water, etc."
    )

    calculate_btn = st.button("🔄 Calculate My Margins", type="primary")

# --- 3. MAIN PAGE: HEADER ---
st.title("🇧🇪 Belgian Dairy Farm Feed Cost & Margin Calculator")

# Display last updated
st.caption(f"📅 Data updated: June 2026 | All values in €")

# Belgian sector context banner
st.info(
    "💡 **Belgian Dairy Sector Snapshot:** "
    "Average milk price: **€0.38 – 0.40/L** (June 2026)[reference:3] | "
    "Herd size: **~80 cows** | "
    "Sector net margin: **~1.2%** (2024)[reference:4][reference:5] | "
    "Dairy farms: **5,640** (2024, -4.1% YoY)[reference:6]"
)

# --- 4. RESULTS DASHBOARD ---
if calculate_btn:
    results = calculate_margin(cow_count, avg_milk, milk_price, feed_items, other_costs)

    # --- Key Metrics Row ---
    st.subheader("📊 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    # Color coding for margins
    margin_color = "normal"
    if results['margin_per_cow'] < 0:
        margin_color = "inverse"
    elif results['margin_per_cow'] < 1.5:
        margin_color = "off"

    col1.metric("Feed Cost per Liter", f"€{results['feed_cost_per_liter']:.3f}")
    col2.metric("Margin / Cow / Day", f"€{results['margin_per_cow']:.2f}", delta_color=margin_color)
    col3.metric("Total Daily Margin", f"€{results['net_margin']:.2f}")
    col4.metric("Break-even Milk Price", f"€{results['breakeven_price']:.3f}")

    # Additional metrics row
    st.caption("")
    col1, col2, col3 = st.columns(3)
    col1.metric("Feed Cost / Cow / Day", f"€{results['feed_cost_per_cow']:.2f}")
    col2.metric("Total Daily Milk", f"{results['total_milk']:,.0f} L")
    col3.metric("Feed Cost as % of Income", f"{results['feed_cost_as_pct']:.1f}%")

    st.divider()

    # --- Chart: Income vs Cost Breakdown ---
    st.subheader("💰 Income vs Cost Breakdown")
    data = {
        "Category": ["🥛 Milk Income", "🌾 Feed Cost", "🔧 Other Costs"],
        "Amount": [results['daily_income'], results['total_feed_cost'], other_costs]
    }
    df = pd.DataFrame(data)

    # Color coding
    colors = ["#2ecc71", "#e74c3c", "#f39c12"]
    fig = px.bar(
        df,
        x="Category",
        y="Amount",
        color="Category",
        color_discrete_sequence=colors,
        text_auto=".2f",
        title="Daily Income vs. Cost Breakdown"
    )
    fig.update_layout(showlegend=False, height=400)
    st.plotly_chart(fig, use_container_width=True)

    # --- Feed Cost Breakdown Chart ---
    st.subheader("📦 Feed Cost Breakdown")
    feed_data = []
    for item in feed_items:
        cost = item["qty"] * item["cost"] * cow_count
        feed_data.append({"Feed": item["name"], "Daily Cost (€)": cost})

    feed_df = pd.DataFrame(feed_data)
    fig2 = px.pie(
        feed_df,
        values="Daily Cost (€)",
        names="Feed",
        title="Share of Total Feed Cost by Feed Type",
        hole=0.4
    )
    fig2.update_traces(textposition="inside", textinfo="percent+label")
    st.plotly_chart(fig2, use_container_width=True)

    st.divider()

    # --- 5. WHAT-IF SIMULATOR ---
    st.subheader("🔮 What-If Scenario Simulator")
    st.caption("Adjust prices below to see how changes affect your margin instantly")

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
        # Market context
        if new_milk_price < 0.35:
            st.warning("⚠️ Below Belgian average (€0.38–0.40/L)[reference:7]")
        elif new_milk_price > 0.45:
            st.success("✅ Above Belgian average — strong market position")

    with col2:
        cost_multiplier = st.slider(
            "Feed Cost Adjustment (%)",
            min_value=70,
            max_value=130,
            value=100,
            step=5,
            help="100% = current feed costs"
        )

    # Recalculate with adjusted values
    adjusted_feed = [
        {"name": f["name"], "qty": f["qty"], "cost": f["cost"] * (cost_multiplier / 100)}
        for f in feed_items
    ]
    new_results = calculate_margin(
        cow_count,
        avg_milk,
        new_milk_price,
        adjusted_feed,
        other_costs
    )

    # Scenario results
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

    # --- 6. SMART RECOMMENDATIONS ENGINE ---
    st.subheader("📋 Smart Recommendations")

    recommendations = []

    # 1. Margin health check
    if new_results['margin_per_cow'] < 0:
        recommendations.append({
            "type": "error",
            "title": "🚨 CRITICAL: You are losing money per cow per day!",
            "detail": f"Your current margin is €{new_results['margin_per_cow']:.2f} per cow per day. "
                       f"At this rate, you're losing approximately €{abs(new_results['margin_per_cow'] * cow_count * 30):,.0f} per month."
        })
    elif new_results['margin_per_cow'] < 1.5:
        recommendations.append({
            "type": "warning",
            "title": "⚡ Caution: Very thin margin",
            "detail": f"Your margin of €{new_results['margin_per_cow']:.2f}/cow/day is below the recommended €2.00+ target. "
                       "Any small drop in milk price or rise in feed costs could push you into loss."
        })
    else:
        recommendations.append({
            "type": "success",
            "title": "✅ Healthy Margin!",
            "detail": f"Your margin of €{new_results['margin_per_cow']:.2f}/cow/day is sustainable. "
                       "You have room to absorb moderate market fluctuations."
        })

    # 2. Feed cost as % of income
    if new_results['feed_cost_as_pct'] > 55:
        recommendations.append({
            "type": "warning",
            "title": "🌾 Feed costs are very high",
            "detail": f"Feed represents {new_results['feed_cost_as_pct']:.1f}% of your milk income. "
                       "The industry benchmark is 40–50%[reference:8]. Consider ration optimization or negotiating bulk discounts."
        })
    elif new_results['feed_cost_as_pct'] > 45:
        recommendations.append({
            "type": "info",
            "title": "📊 Feed costs are at industry average",
            "detail": f"Feed represents {new_results['feed_cost_as_pct']:.1f}% of your milk income, "
                       "which is within the typical Belgian range of 40–50%. Look for small efficiency gains."
        })
    else:
        recommendations.append({
            "type": "success",
            "title": "🌟 Excellent feed efficiency!",
            "detail": f"Feed represents only {new_results['feed_cost_as_pct']:.1f}% of your milk income — "
                       "below the industry average. Well done!"
        })

    # 3. Milk price vs break-even
    if new_milk_price < new_results['breakeven_price']:
        recommendations.append({
            "type": "error",
            "title": "📉 Milk price below break-even",
            "detail": f"Your break-even price is €{new_results['breakeven_price']:.3f}/L, "
                       f"but you're receiving only €{new_milk_price:.3f}/L. "
                       f"You need a price increase of €{new_results['breakeven_price'] - new_milk_price:.3f}/L to break even."
        })
    elif new_milk_price - new_results['breakeven_price'] < 0.05:
        recommendations.append({
            "type": "warning",
            "title": "📊 Milk price close to break-even",
            "detail": f"Your margin buffer is only €{new_milk_price - new_results['breakeven_price']:.3f}/L. "
                       "Consider hedging or diversifying income streams."
        })

    # 4. Belgian sector context
    if new_results['margin_per_cow'] < 2:
        recommendations.append({
            "type": "info",
            "title": "🇧🇪 Belgian sector context",
            "detail": "The Belgian dairy sector's net margin was only 1.23% in 2024[reference:9]. "
                       "With 5,640 farms and declining numbers (-4.1% YoY)[reference:10], "
                       "efficiency is critical for survival. This tool helps you identify where to improve."
        })

    # 5. Feed cost per liter benchmark
    if new_results['feed_cost_per_liter'] > 0.20:
        recommendations.append({
            "type": "warning",
            "title": "📈 Feed cost per liter above benchmark",
            "detail": f"Your feed cost of €{new_results['feed_cost_per_liter']:.3f}/L is above the "
                       "typical Belgian benchmark of €0.15–0.20/L. Review your ration composition."
        })

    # Display recommendations
    for rec in recommendations:
        if rec["type"] == "error":
            st.error(f"**{rec['title']}**\n\n{rec['detail']}")
        elif rec["type"] == "warning":
            st.warning(f"**{rec['title']}**\n\n{rec['detail']}")
        elif rec["type"] == "info":
            st.info(f"**{rec['title']}**\n\n{rec['detail']}")
        else:
            st.success(f"**{rec['title']}**\n\n{rec['detail']}")

    st.divider()

    # --- 7. BENCHMARK COMPARISON ---
    st.subheader("📊 Benchmark Comparison (Belgian Averages)")

    bench_data = {
        "Metric": [
            "Milk Price (€/L)",
            "Feed Cost / L (€)",
            "Margin / Cow / Day (€)",
            "Feed as % of Income"
        ],
        "Your Farm": [
            f"€{new_milk_price:.3f}",
            f"€{new_results['feed_cost_per_liter']:.3f}",
            f"€{new_results['margin_per_cow']:.2f}",
            f"{new_results['feed_cost_as_pct']:.1f}%"
        ],
        "Belgian Average": [
            "€0.38 – 0.40[reference:11]",
            "€0.15 – 0.20",
            "€1.50 – 3.00",
            "40 – 50%"
        ],
        "Status": []
    }

    # Add status indicators
    statuses = []
    # Milk price
    if new_milk_price >= 0.38:
        statuses.append("✅ On par or above")
    else:
        statuses.append("⚠️ Below average")
    # Feed cost
    if new_results['feed_cost_per_liter'] <= 0.20:
        statuses.append("✅ Good")
    else:
        statuses.append("⚠️ Above average")
    # Margin
    if new_results['margin_per_cow'] >= 2.0:
        statuses.append("✅ Strong")
    elif new_results['margin_per_cow'] >= 1.0:
        statuses.append("⚠️ Moderate")
    else:
        statuses.append("🔴 Weak")
    # Feed %
    if new_results['feed_cost_as_pct'] <= 50:
        statuses.append("✅ Good")
    else:
        statuses.append("⚠️ High")

    bench_data["Status"] = statuses

    bench_df = pd.DataFrame(bench_data)
    st.table(bench_df)

    st.caption("📌 *Belgian averages are estimates based on 2025–2026 market data. Your actual performance may vary.*")

else:
    # --- What to show before calculation ---
    st.info("👈 Please fill in your farm data in the sidebar and click **'Calculate My Margins'** to get started.")

    st.markdown("""
    ### 🇧🇪 About This Tool

    This decision support tool helps Belgian dairy farmers analyze their feed costs and profitability using **realistic market data** for the Belgian dairy sector.

    **Key features:**
    - 📊 Calculate feed cost per liter and daily margins
    - 🔮 Run "what-if" scenarios for milk price and feed cost changes
    - 📋 Get smart, actionable recommendations
    - 📈 Compare your performance against Belgian averages

    **Belgian sector context (2025–2026):**
    - Average milk price: **€0.38–0.40 per liter**[reference:12]
    - Average herd size: **~80 cows**
    - Number of dairy farms: **5,640** (declining -4.1% YoY)[reference:13]
    - Sector net margin: **~1.23%**[reference:14]
    - Total milk production: **4.376 billion liters** (2025)[reference:15]

    ---
    *Data sources: Boerenbusiness, BCZ, Vilt.be, CLAL, IndexBox*
    """)