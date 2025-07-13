"""
Configuration settings for the pricing calculator.
"""
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Vantage API Configuration
VANTAGE_API_TOKEN = os.getenv("VANTAGE_API_TOKEN", "")
VANTAGE_API_BASE_URL = "https://api.vantage.sh"

# Databricks Pricing URLs
DATABRICKS_AWS_PRICING_URL = "https://www.databricks.com/en-pricing-assets/data/pricing/AWS.json"
# TODO: Add later
DATABRICKS_GCP_PRICING_URL = "https://www.databricks.com/en-pricing-assets/data/pricing/GCP.json"

# AWS Regions
AWS_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "eu-west-1", "eu-central-1", "ap-southeast-1", "ap-northeast-1"
]

# Databricks Compute Types
DATABRICKS_COMPUTE_TYPES = [
    "Jobs Compute",
    "All-Purpose Compute", 
    "SQL Compute",
    "ML Runtime"
]

# Databricks Plans
DATABRICKS_PLANS = [
    "Standard",
    "Premium", 
    "Enterprise"
]

# Cloud Providers
CLOUD_PROVIDERS = ["AWS"]  # GCP, Azure for future

# Default settings
DEFAULT_REGION = "us-east-1"
DEFAULT_COMPUTE_TYPE = "Jobs Compute"
DEFAULT_PLAN = "Standard"
DEFAULT_CLOUD_PROVIDER = "AWS"

def load_instance_types_from_file():
    """
    Load instance types from the instance_types.txt file.
    Returns a list of unique instance types.
    """
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        instance_types_path = os.path.join(current_dir, "instance_types.txt")
        if not os.path.exists(instance_types_path):
            print(f"Warning: instance_types.txt file not found at {instance_types_path}")
            return []
        with open(instance_types_path, "r", encoding="utf-8") as f:
            instance_types = [line.strip() for line in f if line.strip()]

        return instance_types
    except Exception as e:
        print(f"Error loading instance types from file: {e}")
        return []

def get_instance_type_categories():
    """
    Categorize instance types for better organization.
    Returns a dictionary with categories.
    """
    instance_types = load_instance_types_from_file()
    
    categories = {
        "General Purpose": [],
        "Compute Optimized": [],
        "Memory Optimized": [],
        "Storage Optimized": [],
        "GPU Instances": [],
        "Other": []
    }
    
    for instance in instance_types:
        instance_lower = instance.lower()
        
        if any(gpu in instance_lower for gpu in ['gpu', 'p3', 'p4', 'g4', 'g5']):
            categories["GPU Instances"].append(instance)
        elif any(comp in instance_lower for comp in ['c5', 'c6', 'c7', 'compute']):
            categories["Compute Optimized"].append(instance)
        elif any(mem in instance_lower for mem in ['r5', 'r6', 'r7', 'x1', 'x2', 'memory']):
            categories["Memory Optimized"].append(instance)
        elif any(storage in instance_lower for storage in ['d2', 'd3', 'h1', 'i3', 'storage']):
            categories["Storage Optimized"].append(instance)
        elif any(general in instance_lower for general in ['m5', 'm6', 'm7', 't3', 't4']):
            categories["General Purpose"].append(instance)
        else:
            categories["Other"].append(instance)
    
    return categories

def get_instance_type_details(instance_name):
    """
    Get detailed information about a specific instance type from the JSON data.
    Returns a dictionary with instance details.
    """
    try:
        # Get the path to the aws.json file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        aws_json_path = os.path.join(current_dir, "aws.json")
        
        if not os.path.exists(aws_json_path):
            return None
        
        with open(aws_json_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        # Find matching instances
        matching_instances = []
        for item in data:
            if isinstance(item, dict) and item.get('instance') == instance_name:
                matching_instances.append(item)
        
        if not matching_instances:
            return None
        
        # Return the first match with all available details
        instance_info = matching_instances[0]
        return {
            'instance': instance_info.get('instance'),
            'cloud': instance_info.get('cloud'),
            'region': instance_info.get('region'),
            'compute': instance_info.get('compute'),
            'compute_label': instance_info.get('compute_label'),
            'plan': instance_info.get('plan'),
            'vcpu': instance_info.get('vcpu'),
            'memory': instance_info.get('memory'),
            'baserate': instance_info.get('baserate'),
            'dburate': instance_info.get('dburate'),
            'hourrate': instance_info.get('hourrate'),
            'storage': instance_info.get('storage'),
            'model': instance_info.get('model'),
            'token_input_price': instance_info.get('token_input_price'),
            'token_output_price': instance_info.get('token_output_price'),
            'dbu_input': instance_info.get('dbu_input'),
            'dbu_output': instance_info.get('dbu_output')
        }
    
    except Exception as e:
        print(f"Error getting instance details: {e}")
        return None

# Load instance types
INSTANCE_TYPES = load_instance_types_from_file() 