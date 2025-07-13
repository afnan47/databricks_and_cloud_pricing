"""
Main Streamlit application for the Databricks and Cloud Pricing Calculator.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Any
import logging
import json

from .config import (
    AWS_REGIONS, DATABRICKS_COMPUTE_TYPES, DATABRICKS_PLANS,
    CLOUD_PROVIDERS, DEFAULT_REGION, DEFAULT_COMPUTE_TYPE,
    DEFAULT_PLAN, DEFAULT_CLOUD_PROVIDER, VANTAGE_API_TOKEN, INSTANCE_TYPES,
    get_instance_type_categories, get_instance_type_details
)
from .calculator import PricingCalculator, InstanceConfig, PricingResult
from .utils import format_currency, results_to_dataframe, export_to_csv, export_to_json, get_summary_stats

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Databricks & Cloud Pricing Calculator",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .stAlert {
        border-radius: 0.5rem;
    }
    .instance-type-dropdown {
        font-size: 1.1rem;
    }
    .search-highlight {
        background-color: #ffeb3b;
        padding: 2px 4px;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """Main application function."""
    
    # Header
    st.markdown('<h1 class="main-header">💰 Databricks & Cloud Pricing Calculator</h1>', unsafe_allow_html=True)
    
    # Check if Vantage API token is configured
    if not VANTAGE_API_TOKEN:
        st.error("❌ Vantage API token not found. Please set VANTAGE_API_TOKEN in your .env file.")
        st.stop()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Cloud Provider Selection
        cloud_provider = st.selectbox(
            "Cloud Provider",
            CLOUD_PROVIDERS,
            index=CLOUD_PROVIDERS.index(DEFAULT_CLOUD_PROVIDER)
        )
        
        # Region Selection
        region = st.selectbox(
            "AWS Region",
            AWS_REGIONS,
            index=AWS_REGIONS.index(DEFAULT_REGION)
        )
        
        # Databricks Plan - Filter based on cloud provider
        available_plans = DATABRICKS_PLANS.copy()
        if cloud_provider == "AWS":
            # Remove Standard plan for AWS (only Premium and Enterprise available)
            available_plans = [plan for plan in DATABRICKS_PLANS if plan != "Standard"]
            # Update default plan if Standard was selected
            if DEFAULT_PLAN == "Standard":
                default_plan = "Premium"
            else:
                default_plan = DEFAULT_PLAN
        else:
            default_plan = DEFAULT_PLAN
        
        plan = st.selectbox(
            "Databricks Plan",
            available_plans,
            index=available_plans.index(default_plan) if default_plan in available_plans else 0
        )
        
        # Compute Type
        compute_type = st.selectbox(
            "Databricks Compute Type",
            DATABRICKS_COMPUTE_TYPES,
            index=DATABRICKS_COMPUTE_TYPES.index(DEFAULT_COMPUTE_TYPE)
        )
        
        # API Status
        st.subheader("🔑 API Status")
        if VANTAGE_API_TOKEN:
            st.success("✅ Vantage API token configured")
        else:
            st.error("❌ Vantage API token missing")
        
        # Export Options
        st.subheader("📊 Export Options")
        export_format = st.selectbox(
            "Export Format",
            ["CSV", "JSON"]
        )
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📋 Instance Configuration")
        
        # Instance configuration form
        with st.form("instance_config"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Instance type selection with search
                if INSTANCE_TYPES:
                    # Create a more organized dropdown with categories
                    instance_type = st.selectbox(
                        "Instance Type",
                        options=[""] + INSTANCE_TYPES,
                        index=0,
                        help="Search and select an AWS instance type from the available options. Type to search!"
                    )
                    
                    # Add search filter
                    search_term = st.text_input(
                        "Search instance types",
                        placeholder="Type to filter instance types...",
                        help="Filter instance types by name"
                    )
                    
                    if search_term:
                        filtered_instances = [inst for inst in INSTANCE_TYPES if search_term.lower() in inst.lower()]
                        if filtered_instances:
                            st.write(f"**Found {len(filtered_instances)} matching instances:**")
                            st.caption(", ".join(filtered_instances[:10]) + ("..." if len(filtered_instances) > 10 else ""))
                        else:
                            st.warning("No instance types found matching your search term.")
                    
                    # Show instance details if selected
                    if instance_type and instance_type.strip():
                        details = get_instance_type_details(instance_type)
                        if details:
                            st.success(f"✅ Selected: {instance_type}")
                            with st.expander("📋 Instance Details"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.write(f"**Region:** {details.get('region', 'N/A')}")
                                    st.write(f"**Compute:** {details.get('compute_label', 'N/A')}")
                                    st.write(f"**Plan:** {details.get('plan', 'N/A')}")
                                    st.write(f"**vCPU:** {details.get('vcpu', 'N/A')}")
                                with col2:
                                    st.write(f"**Memory:** {details.get('memory', 'N/A')}")
                                    st.write(f"**Storage:** {details.get('storage', 'N/A')}")
                                    st.write(f"**Model:** {details.get('model', 'N/A')}")
                                    st.write(f"**Hour Rate:** {details.get('hourrate', 'N/A')}")
                        else:
                            st.info(f"ℹ️ Instance type '{instance_type}' selected (details not available)")
                else:
                    instance_type = st.text_input(
                        "Instance Type",
                        placeholder="e.g., m5d.8xlarge",
                        help="AWS instance type (e.g., m5d.8xlarge, c6id.xlarge)"
                    )
                
                num_instances = st.number_input(
                    "Number of Instances",
                    min_value=1,
                    value=1,
                    help="Number of instances to run"
                )
                
                hours_per_run = st.number_input(
                    "Hours per Run",
                    min_value=0.1,
                    max_value=168.0,
                    value=1.0,
                    step=0.1,
                    help="Hours per run (max 168 hours = 1 week)"
                )
            
            with col2:
                # Display calculated total hours
                st.metric("Total Hours per Run", f"{hours_per_run:.1f}")
                
                # Show estimated cost range
                if instance_type:
                    st.info("💡 Cost estimates will be calculated when you submit")
            
            submitted = st.form_submit_button("🚀 Calculate Pricing", use_container_width=True)
    
    with col2:
        st.header("📈 Quick Stats")
        
        # Placeholder for summary metrics
        if 'results' in st.session_state and st.session_state.results:
            stats = get_summary_stats(st.session_state.results)
            
            st.metric("Total Instances", stats.get("total_instances", 0))
            st.metric("Total Hours/Run", f"{stats.get('total_hours_per_run', 0):.1f}")
            st.metric("Total Cost per Run", format_currency(stats.get("total_per_run", 0)))
        else:
            st.info("Configure and calculate pricing to see stats")
    
    # Handle form submission
    if submitted:
        if not instance_type or instance_type.strip() == "":
            st.error("❌ Instance type is required")
            return
        
        # Create instance configuration
        config = InstanceConfig(
            instance_type=instance_type,
            num_instances=num_instances,
            hours_per_run=hours_per_run,
            region=region,
            compute_type=compute_type,
            plan=plan,
            cloud_provider=cloud_provider
        )
        
        # Initialize calculator
        calculator = PricingCalculator()
        
        # Validate configuration
        is_valid, error_msg = calculator.validate_config(config)
        if not is_valid:
            st.error(f"❌ {error_msg}")
            return
        
        # Show loading spinner
        with st.spinner("🔄 Calculating pricing..."):
            try:
                # Calculate pricing
                result = calculator.calculate_instance_pricing(config)
                
                if result:
                    # Store results in session state
                    if 'results' not in st.session_state:
                        st.session_state.results = []
                    st.session_state.results.append(result)
                    
                    st.success("✅ Pricing calculated successfully!")
                    
                    # Display results
                    display_results(st.session_state.results)
                    
                else:
                    st.error("❌ Failed to calculate pricing. Please check your configuration and API token.")
                    
            except Exception as e:
                st.error(f"❌ Error during calculation: {str(e)}")
                logger.error(f"Calculation error: {e}")
    
    # Display existing results if any
    if 'results' in st.session_state and st.session_state.results:
        display_results(st.session_state.results)
        
        # Export options
        st.header("📤 Export Results")
        col1, col2 = st.columns(2)
        
        with col1:
            df = results_to_dataframe(st.session_state.results)
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📊 Export to CSV",
                data=csv_data,
                file_name="pricing_results.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            # Convert results to JSON string
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
                    "total_cost_per_run": result.total_cost_per_run
                })
            json_data = json.dumps(data, indent=2)
            st.download_button(
                label="📄 Export to JSON",
                data=json_data,
                file_name="pricing_results.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Clear results
        if st.button("🗑️ Clear Results", use_container_width=True):
            st.session_state.results = []
            st.rerun()

def display_results(results: List[PricingResult]):
    """Display pricing results in a formatted way."""
    
    if not results:
        return
    
    # Summary metrics
    stats = get_summary_stats(results)
    
    # Create metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cost per Run", format_currency(stats["total_per_run"]))
    
    with col2:
        st.metric("AWS Cost per Run", format_currency(stats["aws_per_run"]))
    
    with col3:
        st.metric("Databricks Cost per Run", format_currency(stats["databricks_per_run"]))
    
    with col4:
        st.metric("Total Instances", stats["total_instances"])
    

    
    # Detailed results table
    st.subheader("📋 Detailed Results")
    
    df = results_to_dataframe(results)
    st.dataframe(df, use_container_width=True)
    


if __name__ == "__main__":
    main() 