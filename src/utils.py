"""
Utility functions for data export and formatting.
"""
import pandas as pd
import json
from typing import List, Dict, Any
from .calculator import PricingResult

def format_currency(amount: float) -> str:
    """Format amount as currency string."""
    return f"${amount:,.2f}"

def results_to_dataframe(results: List[PricingResult]) -> pd.DataFrame:
    """
    Convert pricing results to a pandas DataFrame.
    
    Args:
        results: List of PricingResult objects
        
    Returns:
        DataFrame with pricing data
    """
    data = []
    
    for result in results:
        config = result.instance_config
        data.append({
            "Instance Type": config.instance_type,
            "Number of Instances": config.num_instances,
            "Region": config.region,
            "Compute Type": config.compute_type,
            "Plan": config.plan,
            "Hours per Run": config.hours_per_run,
            "AWS Cost per Run": format_currency(result.aws_cost_per_run),
            "Databricks Cost per Run": format_currency(result.databricks_cost_per_run),
            "Total Cost per Run": format_currency(result.total_cost_per_run)
        })
    
    return pd.DataFrame(data)

def export_to_csv(results: List[PricingResult], filename: str = "pricing_results.csv") -> str:
    """
    Export pricing results to CSV file.
    
    Args:
        results: List of PricingResult objects
        filename: Output filename
        
    Returns:
        Path to the exported file
    """
    df = results_to_dataframe(results)
    df.to_csv(filename, index=False)
    return filename

def export_to_json(results: List[PricingResult], filename: str = "pricing_results.json") -> str:
    """
    Export pricing results to JSON file.
    
    Args:
        results: List of PricingResult objects
        filename: Output filename
        
    Returns:
        Path to the exported file
    """
    data = []
    
    for result in results:
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
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    
    return filename

def get_summary_stats(results: List[PricingResult]) -> Dict[str, Any]:
    """
    Get summary statistics for pricing results.
    
    Args:
        results: List of PricingResult objects
        
    Returns:
        Dictionary with summary statistics
    """
    if not results:
        return {}
    
    total_aws_hourly = sum(r.aws_cost_per_hour for r in results)
    total_databricks_hourly = sum(r.databricks_cost_per_hour for r in results)
    total_hourly = sum(r.total_cost_per_hour for r in results)
    
    total_aws_per_run = sum(r.aws_cost_per_run for r in results)
    total_databricks_per_run = sum(r.databricks_cost_per_run for r in results)
    total_per_run = sum(r.total_cost_per_run for r in results)
    
    total_instances = sum(r.instance_config.num_instances for r in results)
    total_hours = sum(r.total_hours_per_run for r in results)
    
    return {
        "total_instances": total_instances,
        "total_hours_per_run": total_hours,
        "aws_hourly": total_aws_hourly,
        "databricks_hourly": total_databricks_hourly,
        "total_hourly": total_hourly,
        "aws_per_run": total_aws_per_run,
        "databricks_per_run": total_databricks_per_run,
        "total_per_run": total_per_run,
        "aws_percentage": (total_aws_per_run / total_per_run * 100) if total_per_run > 0 else 0,
        "databricks_percentage": (total_databricks_per_run / total_per_run * 100) if total_per_run > 0 else 0
    } 