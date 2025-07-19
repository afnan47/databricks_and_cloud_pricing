"""
API client for fetching pricing data from Vantage and Databricks.
"""
import requests
import json
import logging
from typing import Dict, List, Optional, Any
from .config import (
    VANTAGE_API_TOKEN, VANTAGE_API_BASE_URL,
    DATABRICKS_AWS_PRICING_URL, DATABRICKS_GCP_PRICING_URL,
)

logger = logging.getLogger(__name__)

class VantageAPIClient:
    """Client for interacting with Vantage API to get AWS pricing."""
    
    def __init__(self):
        self.api_token = VANTAGE_API_TOKEN
        self.base_url = VANTAGE_API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def get_aws_pricing(self, instance_type: str, region: str = "us-east-1", plan: str = "Enterprise") -> Optional[float]:
        """
        Get AWS pricing for a specific instance type and region.
        
        Args:
            instance_type: AWS instance type (e.g., "m5d.8xlarge")
            region: AWS region (e.g., "us-east-1")
            plan: Databricks plan (Standard, Premium, Enterprise)
            
        Returns:
            Hourly price in USD, or None if not found
        """
        try:
            # Get the product by querying on instance_type
            products_url = f"{self.base_url}/v2/products?name={instance_type}"
            products_response = requests.get(products_url, headers=self.headers)
            products_response.raise_for_status()
            products_data = products_response.json()
            
            if not products_data:
                logger.error("Could not find AWS EC2 product in Vantage API")
            
            # Extract the product id from the products_data dictionary
            products = products_data.get("products", [])
            product_id = products[0]["id"] if products and "id" in products[0] else None
            
            if not product_id:
                logger.error(f"Could not find product ID for instance type {instance_type}")
                return 0
            

            instance_id = f"{product_id}-{region.replace('-', '_')}-on_demand-linux"
            
            # Get pricing for the specific instance type
            pricing_url = f"{self.base_url}/v2/products/{product_id}/prices/{instance_id}"
            
            response = requests.get(pricing_url, headers=self.headers)
            response.raise_for_status()
            
            data = response.json()            
            return data.get('amount', None)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching AWS pricing: {e}")
            return 0
        except Exception as e:
            logger.error(f"Unexpected error in AWS pricing: {e}")
            return 0
    
    
    def get_available_instances(self, region: str = "us-east-1") -> List[str]:
        """
        Get list of available AWS instance types.
        
        Args:
            region: AWS region
            
        Returns:
            List of available instance types
        """
        try:
            # Get all products first
            products_url = f"{self.base_url}/v2/products"
            products_response = requests.get(products_url, headers=self.headers)
            products_response.raise_for_status()
            products_data = products_response.json()
            
            # Find AWS EC2 product
            aws_ec2_product = None
            for product in products_data.get("data", []):
                if product.get("name") == "Amazon EC2" or "ec2" in product.get("name", "").lower():
                    aws_ec2_product = product
                    break
            
            if not aws_ec2_product:
                return None
            
            product_id = aws_ec2_product.get("id")
            
            # Get all prices for this product
            pricing_url = f"{self.base_url}/v2/products/{product_id}/prices"
            params = {"filter[region]": region}
            
            response = requests.get(pricing_url, headers=self.headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract unique instance types
            instance_types = set()
            for price_item in data.get("data", []):
                instance_type = price_item.get("instance_type")
                if instance_type:
                    instance_types.add(instance_type)
            
            # If no instances found from API, return fallback list
            if not instance_types:
                return None
            
            return list(instance_types)
            
        except Exception as e:
            logger.error(f"Error fetching available instances: {e}")
            return None


class DatabricksAPIClient:
    """Client for fetching Databricks pricing data."""
    
    def __init__(self):
        self.aws_pricing_url = DATABRICKS_AWS_PRICING_URL
        self.gcp_pricing_url = DATABRICKS_GCP_PRICING_URL
    
    def get_databricks_pricing(self, cloud_provider: str = "AWS") -> List[Dict[str, Any]]:
        """
        Get Databricks pricing data for the specified cloud provider.
        
        Args:
            cloud_provider: Cloud provider ("AWS" or "GCP")
            
        Returns:
            Dictionary containing Databricks pricing data
        """
        try:
            url = self.aws_pricing_url if cloud_provider == "AWS" else self.gcp_pricing_url
            
            response = requests.get(url)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Databricks pricing: {e}")
            return {}
        except Exception as e:
            logger.error(f"Unexpected error in Databricks pricing: {e}")
            return {}
    
    def get_instance_pricing(self, instance_type: str, compute_type: str, 
                           plan: str, cloud_provider: str = "AWS") -> float:
        """
        Get Databricks pricing for a specific instance type and configuration.
        
        Args:
            instance_type: Instance type (e.g., "m5d.8xlarge")
            compute_type: Databricks compute type
            plan: Databricks plan (Standard, Premium, Enterprise)
            cloud_provider: Cloud provider
            
        Returns:
            Hourly price in USD, or None if not found
        """
        try:
            pricing_data = self.get_databricks_pricing(cloud_provider)
            
            # Search for the specific instance and configuration
            # This is a simplified example - actual data structure may vary
            # The pricing_data is a list of dicts, each representing an instance pricing entry.
            for entry in pricing_data:
                if (
                    entry.get("instance") == instance_type and
                    entry.get("compute") == compute_type and
                    entry.get("plan") == plan
                ):
                    logger.info(f"Found instance pricing entry: {entry}")
                    # Parse baserate and dburate as floats, fallback to 0.0 if missing or not convertible
                    try:
                        hour_rate = float(entry.get("hourrate", 0.0))
                    except (TypeError, ValueError):
                        hour_rate = 0.0
                    return hour_rate
            
            # If not found in API data, return fallback            
        except Exception as e:
            logger.error(f"Error getting instance pricing: {e}")
            return 0.0