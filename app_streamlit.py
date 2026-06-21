import streamlit as st
import pandas as pd
import altair as alt
from datetime import datetime, timezone
import os
import sys

# Ensure project root is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.calculator import calculate_footprint, ELECTRICITY_REGION_FACTORS
from backend.database import init_db, save_entry, get_entries, delete_entry, clear_history
from backend.recommender import get_recommendations

# Initialize SQLite database
init_db()

# Constants
TARGET_T = 2.0
GLOBAL_AVG_T = 4.8

# Set up Streamlit page configurations
st.set_page_config(
    page_title="Ecosphere — Carbon Footprint Platform",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------------------------------
# Custom CSS Styling (Glassmorphism & Dark Green Theme Adjustments)
# --------------------------------------------------------------------------
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #060b09;
        color: #f3f4f6;
    }
    
    /* Header Area */
    .header-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: rgba(12, 22, 18, 0.6);
        border: 1px solid rgba(16, 185, 129, 0.15);
        border-radius: 16px;
        backdrop-filter: blur(12px);
    }
    .logo-badge {
        background: rgba(16, 185, 129, 0.08);
        border: 1px solid rgba(16, 185, 129, 0.25);
        padding: 0.6rem;
        border-radius: 12px;
        color: #10b981;
        font-weight: bold;
        font-size: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* Styled Glassmorphic Containers */
    .glass-card {
        background: rgba(12, 22, 18, 0.75);
        border: 1px solid rgba(16, 185, 129, 0.12);
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4);
        margin-bottom: 1.5rem;
        backdrop-filter: blur(16px);
    }
    
    /* Wizard Steps Progress indicators */
    .step-indicator {
        display: flex;
        justify-content: space-between;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid rgba(16, 185, 129, 0.12);
        padding-bottom: 0.8rem;
    }
    .step-badge {
        padding: 0.25rem 0.75rem;
        font-size: 0.75rem;
        font-weight: 800;
        border-radius: 9999px;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #9ca3af;
    }
    .step-badge.active {
        background: rgba(16, 185, 129, 0.08);
        border-color: #10b981;
        color: #10b981;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
    }
    .step-badge.completed {
        background: #10b981;
        border-color: #10b981;
        color: #020503;
    }

    /* Target Gauge Style */
    .gauge-bar-bg {
        background: rgba(255, 255, 255, 0.05);
        height: 10px;
        border-radius: 9999px;
        position: relative;
        overflow: hidden;
        margin: 10px 0;
    }
    .gauge-bar-fill {
        height: 100%;
        border-radius: 9999px;
    }
    .gauge-labels {
        display: flex;
        justify-content: space-between;
        font-size: 0.7rem;
        color: #9ca3af;
        font-weight: 600;
    }
    
    /* Table modifications */
    .category-table {
        width: 100%;
        border-collapse: collapse;
    }
    .category-table th {
        border-bottom: 1px solid rgba(16, 185, 129, 0.12);
        padding: 0.5rem 0.25rem;
        font-size: 0.7rem;
        text-transform: uppercase;
        color: #9ca3af;
        text-align: left;
    }
    .category-table td {
        padding: 0.6rem 0.25rem;
        font-size: 0.85rem;
        border-bottom: 1px dotted rgba(255, 255, 255, 0.03);
    }
    
    /* Recommendations Checklist Cards */
    .insight-card {
        background: rgba(255, 255, 255, 0.015);
        border: 1px solid rgba(16, 185, 129, 0.12);
        border-radius: 12px;
        padding: 1rem;
        margin-bottom: 0.8rem;
        transition: all 0.2s;
    }
    .insight-card:hover {
        border-color: rgba(16, 185, 129, 0.25);
    }
    .insight-badge {
        font-size: 0.65rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.15rem 0.45rem;
        border-radius: 4px;
        display: inline-block;
        margin-bottom: 0.4rem;
    }
    .insight-badge.transport { background: rgba(16, 185, 129, 0.1); color: #34d399; }
    .insight-badge.home-energy { background: rgba(59, 130, 246, 0.1); color: #60a5fa; }
    .insight-badge.diet { background: rgba(244, 63, 94, 0.1); color: #fb7185; }
    .insight-badge.goods-waste { background: rgba(245, 158, 11, 0.1); color: #fbbf24; }
    
    .savings-label {
        font-size: 0.75rem;
        font-weight: 700;
        color: #34d399;
        margin-top: 0.3rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Session State Initialization
# --------------------------------------------------------------------------
if "step" not in st.session_state:
    st.session_state.step = 1

# Initialize inputs dictionary in session state if not existing
if "inputs" not in st.session_state:
    st.session_state.inputs = {
        "car_distance": 150.0,
        "car_fuel_type": "Petrol",
        "transit_distance": 50.0,
        "short_flights": 3,
        "long_flights": 1,
        "electricity_usage": 350.0,
        "heating_type": "Natural gas",
        "household_size": 3,
        "diet_type": "Average (omnivore)",
        "shopping_habits": "Average",
        "recycling_habit": "Sometimes"
    }

if "adopted_insights" not in st.session_state:
    st.session_state.adopted_insights = {}

# --------------------------------------------------------------------------
# Sidebar Configurations
# --------------------------------------------------------------------------
st.sidebar.title("🌍 Config Panel")
st.sidebar.markdown("Configure global settings below:")

# 1. Electricity Grid Region Select
region = st.sidebar.selectbox(
    "Electricity Grid Region",
    options=list(ELECTRICITY_REGION_FACTORS.keys()),
    index=0
)

# 2. Distance Unit
distance_unit = st.sidebar.radio(
    "Distance Units",
    options=["KM", "MILE"],
    index=0,
    horizontal=True
)
unit_key = distance_unit.lower()

# --------------------------------------------------------------------------
# Calculate current results (Executed reactively at the start of every render)
# --------------------------------------------------------------------------
scaled_inputs = st.session_state.inputs.copy()
if unit_key == "mi":
    scaled_inputs["car_distance"] = scaled_inputs["car_distance"] * 1.60934
    scaled_inputs["transit_distance"] = scaled_inputs["transit_distance"] * 1.60934

breakdown = calculate_footprint(scaled_inputs, region=region)
total_kg = breakdown["totalKg"]
total_t = total_kg / 1000.0

recommendations = get_recommendations(breakdown, scaled_inputs)

simulated_savings_kg = 0
for action in recommendations:
    if st.session_state.adopted_insights.get(action["id"], False):
        simulated_savings_kg += action["saving"]

simulated_total_kg = max(0, total_kg - simulated_savings_kg)
simulated_total_t = simulated_total_kg / 1000.0

# --------------------------------------------------------------------------
# App Header
# --------------------------------------------------------------------------
st.markdown("""
<div class="header-container">
    <div class="logo-badge">🌱</div>
    <div>
        <h1 style="margin:0; font-size:1.6rem; color:#ffffff; font-weight:800;">Ecosphere</h1>
        <p style="margin:0; font-size:0.7rem; color:#10b981; text-transform:uppercase; letter-spacing:0.15em; font-weight:700;">Carbon Footprint Awareness Platform</p>
    </div>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Estimator Form Wizard Columns
# --------------------------------------------------------------------------
col_form, col_dash = st.columns([1.1, 1.0], gap="large")

with col_form:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Estimator Configurator")
    st.markdown("Walk through the steps to configure your footprint metrics.")
    
    # Render wizard progress bar
    s1 = "active" if st.session_state.step == 1 else ("completed" if st.session_state.step > 1 else "")
    s2 = "active" if st.session_state.step == 2 else ("completed" if st.session_state.step > 2 else "")
    s3 = "active" if st.session_state.step == 3 else ("completed" if st.session_state.step > 3 else "")
    s4 = "active" if st.session_state.step == 4 else ("completed" if st.session_state.step > 4 else "")
    
    st.markdown(f"""
    <div class="step-indicator">
        <span class="step-badge {s1}">1. Transport</span>
        <span class="step-badge {s2}">2. Energy</span>
        <span class="step-badge {s3}">3. Diet</span>
        <span class="step-badge {s4}">4. Goods</span>
    </div>
    """, unsafe_allow_html=True)
    
    # --------------------------------------------------------
    # STEP 1: TRANSPORT
    # --------------------------------------------------------
    if st.session_state.step == 1:
        st.markdown("<h4 style='color:#10b981; text-transform:uppercase; font-size:0.8rem; letter-spacing:0.05em;'>1. Transport Logistics</h4>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.inputs["car_distance"] = st.number_input(
                f"Car Driving / Week ({distance_unit})",
                min_value=0.0,
                value=float(st.session_state.inputs["car_distance"]),
                step=10.0
            )
        with c2:
            st.session_state.inputs["car_fuel_type"] = st.selectbox(
                "Fuel & Engine Model",
                options=["Petrol", "Diesel", "Hybrid", "Electric", "None"],
                index=["Petrol", "Diesel", "Hybrid", "Electric", "None"].index(st.session_state.inputs["car_fuel_type"])
            )
            
        st.session_state.inputs["transit_distance"] = st.number_input(
            f"Public Transit / Week ({distance_unit})",
            min_value=0.0,
            value=float(st.session_state.inputs["transit_distance"]),
            step=10.0
        )
        
        c3, c4 = st.columns(2)
        with c3:
            st.session_state.inputs["short_flights"] = st.number_input(
                "Short Flights / Year (< 1500 km)",
                min_value=0,
                value=int(st.session_state.inputs["short_flights"]),
                step=1
            )
        with c4:
            st.session_state.inputs["long_flights"] = st.number_input(
                "Long Flights / Year (>= 1500 km)",
                min_value=0,
                value=int(st.session_state.inputs["long_flights"]),
                step=1
            )
            
    # --------------------------------------------------------
    # STEP 2: HOME ENERGY
    # --------------------------------------------------------
    elif st.session_state.step == 2:
        st.markdown("<h4 style='color:#3b82f6; text-transform:uppercase; font-size:0.8rem; letter-spacing:0.05em;'>2. Home Energy</h4>", unsafe_allow_html=True)
        
        st.session_state.inputs["electricity_usage"] = st.number_input(
            "Monthly Electricity Usage (kWh)",
            min_value=0.0,
            value=float(st.session_state.inputs["electricity_usage"]),
            step=50.0
        )
        
        c1, c2 = st.columns(2)
        with c1:
            st.session_state.inputs["heating_type"] = st.selectbox(
                "Primary Heating Fuel",
                options=["Natural gas", "Electric", "Oil", "Renewable / none"],
                index=["Natural gas", "Electric", "Oil", "Renewable / none"].index(st.session_state.inputs["heating_type"])
            )
        with c2:
            st.session_state.inputs["household_size"] = st.number_input(
                "Household size (Occupants)",
                min_value=1,
                value=int(st.session_state.inputs["household_size"]),
                step=1
            )

    # --------------------------------------------------------
    # STEP 3: DIET
    # --------------------------------------------------------
    elif st.session_state.step == 3:
        st.markdown("<h4 style='color:#f43f5e; text-transform:uppercase; font-size:0.8rem; letter-spacing:0.05em;'>3. Dietary Footprint</h4>", unsafe_allow_html=True)
        
        st.write("Select your diet type:")
        
        diets = {
            "Meat heavy": "🥩 Meat Lover - Red meat or poultry consumed daily",
            "Average (omnivore)": "🥗 Omnivore - Balanced average mix of meat and plants",
            "Vegetarian": "🧀 Vegetarian - No meat, but consumes dairy and eggs",
            "Vegan": "🌱 Vegan - Purely plant-based nutrition, zero animal products"
        }
        
        st.session_state.inputs["diet_type"] = st.radio(
            "Diet Category",
            options=list(diets.keys()),
            format_func=lambda x: diets[x],
            index=list(diets.keys()).index(st.session_state.inputs["diet_type"])
        )

    # --------------------------------------------------------
    # STEP 4: GOODS & WASTE
    # --------------------------------------------------------
    elif st.session_state.step == 4:
        st.markdown("<h4 style='color:#f59e0b; text-transform:uppercase; font-size:0.8rem; letter-spacing:0.05em;'>4. Goods & Waste</h4>", unsafe_allow_html=True)
        
        st.session_state.inputs["shopping_habits"] = st.selectbox(
            "Annual Consumption & Shopping",
            options=["Low", "Average", "High"],
            index=["Low", "Average", "High"].index(st.session_state.inputs["shopping_habits"])
        )
        
        st.session_state.inputs["recycling_habit"] = st.selectbox(
            "Recycling & Waste Habits",
            options=["Always", "Sometimes", "Rarely"],
            index=["Always", "Sometimes", "Rarely"].index(st.session_state.inputs["recycling_habit"])
        )

    # Wizard buttons row
    st.write("")
    nav_prev, nav_next, nav_save = st.columns([1, 1, 2])
    
    with nav_prev:
        if st.button("⬅️ Back", disabled=(st.session_state.step == 1), use_container_width=True):
            st.session_state.step -= 1
            st.rerun()
            
    with nav_next:
        if st.session_state.step < 4:
            if st.button("Next ➡️", use_container_width=True):
                st.session_state.step += 1
                st.rerun()
                
    with nav_save:
        if st.session_state.step == 4:
            if st.button("💾 Save Entry to History", type="primary", use_container_width=True):
                # Calculate dynamic savings applied
                simulated_savings_kg = 0
                for action in recommendations:
                    if st.session_state.adopted_insights.get(action["id"], False):
                        simulated_savings_kg += action["saving"]
                        
                payload = {
                    "car_distance": st.session_state.inputs["car_distance"],
                    "car_fuel_type": st.session_state.inputs["car_fuel_type"],
                    "transit_distance": st.session_state.inputs["transit_distance"],
                    "short_flights": st.session_state.inputs["short_flights"],
                    "long_flights": st.session_state.inputs["long_flights"],
                    "electricity_usage": st.session_state.inputs["electricity_usage"],
                    "heating_type": st.session_state.inputs["heating_type"],
                    "household_size": st.session_state.inputs["household_size"],
                    "diet_type": st.session_state.inputs["diet_type"],
                    "shopping_habits": st.session_state.inputs["shopping_habits"],
                    "recycling_habit": st.session_state.inputs["recycling_habit"],
                    
                    "transport_emissions": breakdown["transportKg"],
                    "home_emissions": breakdown["homeKg"],
                    "diet_emissions": breakdown["dietKg"],
                    "goods_emissions": breakdown["goodsKg"],
                    "total_emissions": breakdown["totalKg"],
                    "simulated_savings": simulated_savings_kg,
                    "simulated_total": max(0, breakdown["totalKg"] - simulated_savings_kg)
                }
                save_entry(payload)
                st.success("Footprint entry successfully saved to local SQLite database!")
                st.rerun()
                
    st.write("")
    if st.button("🔄 Reset Inputs to Default", use_container_width=True):
        st.session_state.inputs = {
            "car_distance": 150.0,
            "car_fuel_type": "Petrol",
            "transit_distance": 50.0,
            "short_flights": 3,
            "long_flights": 1,
            "electricity_usage": 350.0,
            "heating_type": "Natural gas",
            "household_size": 3,
            "diet_type": "Average (omnivore)",
            "shopping_habits": "Average",
            "recycling_habit": "Sometimes"
        }
        st.session_state.adopted_insights = {}
        st.session_state.step = 1
        st.rerun()
        
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# COLUMN 2: Analytical Dashboard
# --------------------------------------------------------------------------
with col_dash:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.subheader("Diagnostic Dashboard")
    
    # Status level badge
    level_label = ""
    level_color = ""
    if simulated_total_t < 2.0:
        level_label, level_color = "Climate Hero 🌟", "#10b981"
    elif simulated_total_t < 4.8:
        level_label, level_color = "Eco Steward 🌱", "#60a5fa"
    elif simulated_total_t < 8.0:
        level_label, level_color = "Carbon Seeker ⚖️", "#facc15"
    else:
        level_label, level_color = "Eco Learner 🍂", "#f87171"
        
    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
        <span style="font-size:0.8rem; text-transform:uppercase; color:#9ca3af; font-weight:700;">Eco Level Rank</span>
        <span style="background:rgba(255,255,255,0.02); color:{level_color}; border:1px solid {level_color}; border-radius:9999px; padding:0.35rem 0.85rem; font-size:0.75rem; font-weight:800; font-family:sans-serif; text-transform:uppercase;">
            {level_label}
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Impact metrics columns
    m1, m2 = st.columns(2)
    with m1:
        st.metric(
            label="Current Annual Impact",
            value=f"{total_t:.2f} t CO2e",
            delta=f"{(total_t - TARGET_T):+.2f} t vs Target" if total_t > TARGET_T else "🌟 Under target limit",
            delta_color="inverse"
        )
    with m2:
        st.metric(
            label="Projected Footprint",
            value=f"{simulated_total_t:.2f} t CO2e",
            delta=f"-{simulated_savings_kg} kg savings applied" if simulated_savings_kg > 0 else "0 savings applied"
        )
        
    # Visual progress bar comparison
    fill_pct = min(100.0, (simulated_total_t / 10.0) * 100.0)
    gauge_bar_color = "#10b981" if simulated_total_t <= TARGET_T else ("#eab308" if simulated_total_t <= GLOBAL_AVG_T else "#ef4444")
    
    st.markdown(f"""
    <div class="gauge-bar-bg">
        <div class="gauge-bar-fill" style="width: {fill_pct}%; background: {gauge_bar_color};"></div>
    </div>
    <div class="gauge-labels">
        <span>0 t</span>
        <span style="color:#10b981; font-weight:700;">Target (2t)</span>
        <span style="color:#eab308; font-weight:700;">Global Avg (4.8t)</span>
        <span>10t+</span>
    </div>
    """, unsafe_allow_html=True)
    
    st.write("")
    
    # Donut Breakdown and Table Section
    c_donut, c_table = st.columns([1, 1.2])
    
    with c_donut:
        # Altair Donut Chart
        source_df = pd.DataFrame({
            'Category': ['Transport', 'Home Energy', 'Diet', 'Goods & Waste'],
            'Value': [breakdown["transportKg"], breakdown["homeKg"], breakdown["dietKg"], breakdown["goodsKg"]]
        })
        
        donut_chart = alt.Chart(source_df).mark_arc(innerRadius=45, outerRadius=65).encode(
            theta=alt.Theta(field="Value", type="quantitative"),
            color=alt.Color(field="Category", type="nominal", scale=alt.Scale(
                domain=['Transport', 'Home Energy', 'Diet', 'Goods & Waste'],
                range=['#10b981', '#3b82f6', '#f43f5e', '#f59e0b']
            ), legend=None),
            tooltip=['Category', alt.Tooltip('Value', title='Emissions (kg CO2e)')]
        ).properties(width=130, height=130).configure_view(strokeWidth=0)
        
        st.altair_chart(donut_chart, use_container_width=True)
        
    with c_table:
        denom = total_kg if total_kg > 0 else 1
        pct_t = (breakdown["transportKg"] / denom) * 100
        pct_h = (breakdown["homeKg"] / denom) * 100
        pct_d = (breakdown["dietKg"] / denom) * 100
        pct_g = (breakdown["goodsKg"] / denom) * 100
        
        st.markdown(f"""
        <table class="category-table">
            <thead>
                <tr>
                    <th>Category</th>
                    <th style="text-align:right">Impact</th>
                    <th style="text-align:right">Share</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td><span style="color:#10b981">●</span> Transport</td>
                    <td style="text-align:right; font-family:monospace; font-weight:bold;">{breakdown["transportKg"]:,} kg</td>
                    <td style="text-align:right; font-family:monospace; color:#9ca3af;">{pct_t:.0f}%</td>
                </tr>
                <tr>
                    <td><span style="color:#3b82f6">●</span> Home Energy</td>
                    <td style="text-align:right; font-family:monospace; font-weight:bold;">{breakdown["homeKg"]:,} kg</td>
                    <td style="text-align:right; font-family:monospace; color:#9ca3af;">{pct_h:.0f}%</td>
                </tr>
                <tr>
                    <td><span style="color:#f43f5e">●</span> Diet</td>
                    <td style="text-align:right; font-family:monospace; font-weight:bold;">{breakdown["dietKg"]:,} kg</td>
                    <td style="text-align:right; font-family:monospace; color:#9ca3af;">{pct_d:.0f}%</td>
                </tr>
                <tr>
                    <td><span style="color:#f59e0b">●</span> Goods & Waste</td>
                    <td style="text-align:right; font-family:monospace; font-weight:bold;">{breakdown["goodsKg"]:,} kg</td>
                    <td style="text-align:right; font-family:monospace; color:#9ca3af;">{pct_g:.0f}%</td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# AI Insights / Mitigation Checklist
# --------------------------------------------------------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("✨ Personalized Mitigation Strategies")
st.markdown("Check items below to simulate implementation and see your footprint reduction in real time:")

if len(recommendations) == 0:
    st.write("Input data to generate customized carbon offset recommendations.")
else:
    for action in recommendations:
        act_id = action["id"]
        cat_badge_class = action["category"].lower().replace(" & ", "-").replace(" ", "-")
        is_adopted_state = st.session_state.adopted_insights.get(act_id, False)
        
        # Render a Streamlit checkbox inside the styled markup
        checkbox_key = f"chk_{act_id}"
        
        # Create column layouts for recommendations details
        cb_col, text_col = st.columns([0.08, 0.92], gap="small")
        with cb_col:
            # Synchronize Streamlit checkbox state to session state
            new_checked_state = st.checkbox(
                label="Adopt mitigation",
                value=is_adopted_state,
                key=checkbox_key,
                label_visibility="collapsed"
            )
            # Re-render triggered by change
            if new_checked_state != is_adopted_state:
                st.session_state.adopted_insights[act_id] = new_checked_state
                st.rerun()
                
        with text_col:
            st.markdown(f"""
            <div style="margin-bottom:10px;">
                <span class="insight-badge {cat_badge_class}">{action["category"]}</span>
                <p style="margin:0; font-size:0.85rem; font-weight:600;">{action["advice"]}</p>
                <div class="savings-label">☘️ Saves ~{action["saving"]:,} kg CO2e / year</div>
            </div>
            """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Ledger SQLite database logs & History
# --------------------------------------------------------------------------
st.markdown('<div class="glass-card">', unsafe_allow_html=True)
st.subheader("📚 SQLite history ledger")

history_entries = get_entries(limit=15)

if len(history_entries) == 0:
    st.info("No logs committed to local database ledger yet. Go to step 4 of the Estimator form to save logs.")
else:
    # 1. Plot historical trend line chart (if 2 or more logs exist)
    if len(history_entries) >= 2:
        st.markdown("<p style='font-size:0.75rem; text-transform:uppercase; color:#9ca3af; font-weight:700; letter-spacing:0.05em;'>Chronological Emissions trend line</p>", unsafe_allow_html=True)
        
        # Format history data chronologically
        history_chart_data = []
        for idx, row in enumerate(reversed(history_entries)):
            dt = datetime.fromisoformat(row["timestamp"])
            date_str = dt.strftime("%b %d, %H:%M")
            history_chart_data.append({
                "Date": date_str,
                "Simulated Total": row["simulated_total"] / 1000.0,
                "Absolute Total": row["total_emissions"] / 1000.0
            })
            
        chart_df = pd.DataFrame(history_chart_data)
        
        # Draw Altair Line chart
        line_chart = alt.Chart(chart_df).mark_line(color="#10b981", strokeWidth=2.5, point=alt.OverlayMarkDef(color="#10b981", size=60)).encode(
            x=alt.X('Date:N', sort=None, title='Save Log Timestamp'),
            y=alt.Y('Simulated Total:Q', title='Emissions (t CO2e)'),
            tooltip=['Date', alt.Tooltip('Simulated Total', format='.2f', title='Simulated (t)'), alt.Tooltip('Absolute Total', format='.2f', title='Original (t)')]
        ).properties(height=120)
        
        # Horizontal line for 2t target
        target_rule = alt.Chart(pd.DataFrame({'y': [2.0]})).mark_rule(color="#10b981", strokeDash=[3,3]).encode(y='y:Q')
        
        st.altair_chart(line_chart + target_rule, use_container_width=True)
        st.write("")
        
    # 2. Render ledger records dataframe table
    formatted_logs = []
    for row in history_entries:
        dt = datetime.fromisoformat(row["timestamp"])
        date_str = dt.strftime("%Y-%m-%d %H:%M")
        formatted_logs.append({
            "Log ID": row["id"],
            "Timestamp": date_str,
            "Transport (kg)": f"{row['transport_emissions']:.0f}",
            "Home Energy (kg)": f"{row['home_emissions']:.0f}",
            "Diet (kg)": f"{row['diet_emissions']:.0f}",
            "Goods & Waste (kg)": f"{row['goods_emissions']:.0f}",
            "Total Footprint": f"{row['total_emissions']/1000.0:.2f} t",
            "Savings Applied": f"-{row['simulated_savings']:.0f} kg" if row['simulated_savings'] > 0 else "0",
            "Simulated Total": f"{row['simulated_total']/1000.0:.2f} t"
        })
        
    st.dataframe(pd.DataFrame(formatted_logs), use_container_width=True, hide_index=True)
    
    # 3. Actions Row: Delete single log or clear ledger
    st.write("")
    c_del, c_clear = st.columns([1, 1])
    
    with c_del:
        log_ids_to_del = [row["id"] for row in history_entries]
        del_target = st.selectbox("Select Log ID to delete", options=log_ids_to_del)
        if st.button("🗑️ Delete Selected Log", use_container_width=True):
            if delete_entry(del_target):
                st.success(f"Log ID {del_target} successfully deleted!")
                st.rerun()
                
    with c_clear:
        st.write("<div style='height:28px'></div>", unsafe_allow_html=True)
        if st.button("⚠️ Wipe History Ledger Clean", type="secondary", use_container_width=True):
            if clear_history():
                st.success("All historical logs wiped from SQLite database!")
                st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
