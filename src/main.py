"""
Main Streamlit application for the Databricks and Cloud Pricing Calculator.
This version combines the improved UI with the original application logic.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import List
import json
import logging

# --- Original Imports from your main.py ---
# Ensure your project structure has these files accessible
from .config import (
    AWS_REGIONS, DATABRICKS_COMPUTE_TYPES, DATABRICKS_PLANS,
    CLOUD_PROVIDERS, DEFAULT_REGION, DEFAULT_COMPUTE_TYPE,
    DEFAULT_PLAN, DEFAULT_CLOUD_PROVIDER, VANTAGE_API_TOKEN, INSTANCE_TYPES,
    get_instance_type_details,
    get_instance_types_by_compute_type
)
from .calculator import PricingCalculator, InstanceConfig, PricingResult
from .utils import format_currency, results_to_dataframe, get_summary_stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Cloud Cost Calculator",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a modern, clean UI
st.markdown("""
<style>
    /* General body styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }

    /* Title styling */
    h1 {
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        color: #1a1a1a;
        text-align: center;
    }

    /* Subheader styling */
     h2 {
        font-size: 1.75rem !important;
        font-weight: 600 !important;
        color: #333;
        border-bottom: 2px solid #f0f2f6;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }

    /* Metric card styling */
    [data-testid="stMetric"] {
        background-color: #F8F9FA;
        border: 1px solid #E9ECEF;
        border-radius: 8px;
        padding: 1rem;
    }
    [data-testid="stMetric"] > div:nth-child(2) {
        font-size: 2rem !important;
        font-weight: 600 !important;
    }

    /* Button styling */
    .stButton>button {
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        width: 100%;
    }
    .stDownloadButton>button {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    /* Tab styling */
    [data-baseweb="tab-list"] {
        justify-content: center;
    }
    [data-baseweb="tab"] {
        font-size: 1.1rem;
        font-weight: 600;
        padding-top: 0.75rem;
        padding-bottom: 0.75rem;
    }
    
    /* Sidebar styling - More specific selector to prevent flashing */
    [data-testid="stSidebar"] > div:first-child {
        background-color: #F8F9FA;
        border-right: 1px solid #E9ECEF;
    }
</style>
""", unsafe_allow_html=True)


def display_results(results: List[PricingResult]):
    """Display pricing results in a modern tabbed layout, using original logic."""
    if not results:
        return

    st.header("📊 Calculation Results")
    
    # Create tabs for different views of the results
    tab1, tab2, tab3 = st.tabs(["📈 Summary", "📋 Detailed Breakdown", "📤 Export & Manage"])

    with tab1:
        # --- Summary Tab ---
        stats = get_summary_stats(results)
        
        st.subheader("Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Cost per Run", format_currency(stats.get("total_per_run", 0)))
        with col2:
            st.metric("Cloud Cost (AWS)", format_currency(stats.get("aws_per_run", 0)))
        with col3:
            st.metric("Databricks Cost", format_currency(stats.get("databricks_per_run", 0)))
        with col4:
            st.metric("Total Instances", stats.get("total_instances", 0))

        st.divider()
        
        st.subheader("Cost Breakdown")
        aws_total = stats.get("aws_per_run", 0)
        db_total = stats.get("databricks_per_run", 0)
        
        if aws_total > 0 or db_total > 0:
            fig = go.Figure(data=[go.Pie(
                labels=['Cloud Cost (AWS)', 'Databricks Cost'],
                values=[aws_total, db_total],
                hole=.4,
                marker_colors=['#FF9900', '#1f77b4'],
                textinfo='percent+label',
                pull=[0.05, 0]
            )])
            fig.update_layout(
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                margin=dict(l=0, r=0, t=0, b=0)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No cost data to display in chart.")

    with tab2:
        # --- Detailed Breakdown Tab ---
        st.subheader("All Calculated Instances")
        df = results_to_dataframe(results)
        st.dataframe(df, use_container_width=True, hide_index=True)

    with tab3:
        # --- Export & Manage Tab ---
        st.subheader("Export Calculation Results")
        
        df = results_to_dataframe(st.session_state.results)
        csv_data = df.to_csv(index=False).encode('utf-8')
        
        # Original logic for JSON export
        data = []
        for result in st.session_state.results:
            config = result.instance_config
            data.append({
                "instance_type": config.instance_type,
                "num_instances": config.num_instances,
                "region": config.region,
                "compute_type": config.compute_type,
                "plan": config.plan,
                "hours_per_run": config.hours_per_run,
                "total_hours_per_run": result.total_hours_per_run,
                "aws_cost_per_hour": result.aws_cost_per_hour,
                "databricks_cost_per_hour": result.databricks_cost_per_hour,
                "total_cost_per_hour": result.total_cost_per_hour,
                "aws_cost_per_run": result.aws_cost_per_run,
                "databricks_cost_per_run": result.databricks_cost_per_run,
                "total_cost_per_run": result.total_cost_per_run,
                "message": getattr(result, "message", "")
            })
        json_data = json.dumps(data, indent=2)

        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="📄 Export to CSV",
                data=csv_data,
                file_name="pricing_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        with col2:
            st.download_button(
                label="📑 Export to JSON",
                data=json_data,
                file_name="pricing_results.json",
                mime="application/json",
                use_container_width=True
            )
        
        st.divider()
        
        st.subheader("Manage Session")
        if st.button("🗑️ Clear All Results", use_container_width=True, type="secondary"):
            st.session_state.results = []
            st.rerun()


def main():
    """Main application function."""
    
    # --- GitHub Icon moved inside main() to prevent disappearing on rerun ---
    with st.container():
        left_col, right_col = st.columns([1, 0.08]) # Adjust ratio for alignment
        with left_col:
             st.title("Databricks & Cloud Cost Calculator")
        with right_col:
            st.markdown(
                """
                <a href="https://github.com/afnan47/databricks_and_CSP_pricing_calculator" target="_blank" title="View on GitHub">
                    <svg height="32" viewBox="0 0 16 16" width="32" fill="white">
                        <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0 0 16 8c0-4.42-3.58-8-8-8z"></path>
                    </svg>
                </a>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<p style='text-align: center; font-size: 1.1rem; color: #555;'>An interactive tool to estimate your infrastructure and Databricks costs.</p>", unsafe_allow_html=True)
    
    if not VANTAGE_API_TOKEN:
        st.error("❌ Vantage API token not found. Please set VANTAGE_API_TOKEN in your environment.")
        st.stop()
    
    # Initialize session state
    if 'results' not in st.session_state:
        st.session_state.results = []

    # --- Sidebar for global configuration (using original logic) ---
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        cloud_provider = st.selectbox(
            "Cloud Provider", CLOUD_PROVIDERS, index=CLOUD_PROVIDERS.index(DEFAULT_CLOUD_PROVIDER)
        )
        region = st.selectbox(
            "AWS Region", AWS_REGIONS, index=AWS_REGIONS.index(DEFAULT_REGION)
        )
        
        # Original logic for plan filtering
        available_plans = DATABRICKS_PLANS.copy()
        if cloud_provider == "AWS":
            available_plans = [plan for plan in DATABRICKS_PLANS if plan != "Standard"]
            default_plan = "Premium" if DEFAULT_PLAN == "Standard" else DEFAULT_PLAN
        else:
            default_plan = DEFAULT_PLAN
        
        plan = st.selectbox(
            "Databricks Plan", available_plans, index=available_plans.index(default_plan) if default_plan in available_plans else 0
        )
        
        compute_type = st.selectbox(
            "Databricks Compute Type", DATABRICKS_COMPUTE_TYPES, index=DATABRICKS_COMPUTE_TYPES.index(DEFAULT_COMPUTE_TYPE)
        )

    # --- Configuration and Calculation Section (using original logic) ---
    st.header("📝 Configure and Calculate")
    with st.container(border=True):
        with st.form("instance_config"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Instance type selection with search from original code
                filtered_instance_types = get_instance_types_by_compute_type(compute_type) if compute_type else INSTANCE_TYPES
                instance_type = st.selectbox(
                    "Instance Type",
                    options=[""] + filtered_instance_types,
                    index=0,
                    help="Search and select an AWS instance type. Type to search!"
                )
                search_term = st.text_input(
                    "Search instance types",
                    placeholder="Type to filter instance types...",
                    help="Filter instance types by name"
                )
                if search_term:
                    filtered_search = [inst for inst in filtered_instance_types if search_term.lower() in inst.lower()]
                    if filtered_search:
                        st.write(f"**Found {len(filtered_search)} matching instances:**")
                        st.caption(", ".join(filtered_search[:10]) + ("..." if len(filtered_search) > 10 else ""))
                    else:
                        st.warning("No instance types found matching your search term.")

                if instance_type:
                    details = get_instance_type_details(instance_type)
                    if details:
                        with st.expander("View Instance Details", expanded=False):
                            st.success(f"**vCPU:** {details.get('vcpu', 'N/A')} | **Memory:** {details.get('memory', 'N/A')} | **Storage:** {details.get('storage', 'N/A')}")

            with col2:
                num_instances = st.number_input("Number of Instances", min_value=1, value=1)
                hours_per_run = st.number_input("Hours per Run", min_value=0.1, max_value=168.0, value=1.0, step=0.1)

            submitted = st.form_submit_button("🚀 Add to Calculation", use_container_width=True, type="primary")

    # --- Form Submission Logic (original logic) ---
    if submitted:
        if not instance_type or instance_type.strip() == "":
            st.error("❌ Instance type is required")
        else:
            config = InstanceConfig(
                instance_type=instance_type,
                num_instances=num_instances,
                hours_per_run=hours_per_run,
                region=region,
                compute_type=compute_type,
                plan=plan,
                cloud_provider=cloud_provider
            )
            
            calculator = PricingCalculator()
            is_valid, error_msg = calculator.validate_config(config)
            
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                with st.spinner("🔍 Calculating pricing..."):
                    try:
                        result = calculator.calculate_instance_pricing(config)
                        st.session_state.results.append(result)
                        st.success(f"✅ Calculation for **{config.instance_type}** added successfully!")
                    except Exception as e:
                        st.error(f"❌ An error occurred during calculation: {e}")
                        logger.error(f"Calculation error: {e}")

    # --- Display Results Section ---
    if st.session_state.results:
        display_results(st.session_state.results)
    else:
        st.info("Your calculation results will appear here once you add an instance configuration.", icon="ℹ️")


if __name__ == "__main__":
    main()
