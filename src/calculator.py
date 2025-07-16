"""
Core pricing calculation logic for AWS and Databricks costs.
"""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .api_client import VantageAPIClient, DatabricksAPIClient

logger = logging.getLogger(__name__)

@dataclass
class InstanceConfig:
    """Configuration for a single instance."""
    instance_type: str
    num_instances: int
    hours_per_run: float  # Changed from hours_per_day
    region: str = "us-east-1"
    compute_type: str = "Jobs Compute"
    plan: str = "Standard"
    cloud_provider: str = "AWS"

@dataclass
class PricingResult:
    """Result of pricing calculation."""
    aws_cost_per_hour: float
    databricks_cost_per_hour: float
    total_cost_per_hour: float
    aws_cost_per_run: float
    databricks_cost_per_run: float
    total_cost_per_run: float
    total_hours_per_run: float
    instance_config: InstanceConfig
    message: str = ""  # Optional message for user feedback

class PricingCalculator:
    """Main calculator for AWS and Databricks pricing."""
    
    def __init__(self):
        self.vantage_client = VantageAPIClient()
        self.databricks_client = DatabricksAPIClient()
    
    def calculate_instance_pricing(self, config: InstanceConfig) -> Optional[PricingResult]:
        """
        Calculate pricing for a single instance configuration.
        
        Args:
            config: Instance configuration
            
        Returns:
            PricingResult with calculated costs, or None if calculation failed
        """
        try:
            # Get AWS pricing
            aws_hourly_rate = self.vantage_client.get_aws_pricing(
                config.instance_type, config.region, config.plan
            )
            
            if aws_hourly_rate is None:
                logger.warning(f"Cluster not found for AWS instance type {config.instance_type}. Returning 0 for all costs.")
                return PricingResult(
                    aws_cost_per_hour=0.0,
                    databricks_cost_per_hour=0.0,
                    total_cost_per_hour=0.0,
                    aws_cost_per_run=0.0,
                    databricks_cost_per_run=0.0,
                    total_cost_per_run=0.0,
                    total_hours_per_run=config.hours_per_run,
                    instance_config=config,
                    message="Cluster not found for AWS. All costs set to 0."
                )
            
            # Get Databricks pricing
            databricks_hourly_rate = self.databricks_client.get_instance_pricing(
                config.instance_type, config.compute_type, config.plan  , config.cloud_provider
            )
            
            if databricks_hourly_rate is None:
                logger.error(f"Could not get Databricks pricing for {config.instance_type}")
                return None
            
            # Calculate costs per hour
            aws_cost_per_hour = aws_hourly_rate * config.num_instances
            databricks_cost_per_hour = databricks_hourly_rate * config.num_instances 
            
            total_cost_per_hour = aws_cost_per_hour + databricks_cost_per_hour
            
            # Calculate costs per run
            total_hours_per_run = config.hours_per_run
            aws_cost_per_run = aws_cost_per_hour * total_hours_per_run
            databricks_cost_per_run = databricks_cost_per_hour * total_hours_per_run
            total_cost_per_run = total_cost_per_hour * total_hours_per_run
            
            return PricingResult(
                aws_cost_per_hour=aws_cost_per_hour,
                databricks_cost_per_hour=databricks_cost_per_hour,
                total_cost_per_hour=total_cost_per_hour,
                aws_cost_per_run=aws_cost_per_run,
                databricks_cost_per_run=databricks_cost_per_run,
                total_cost_per_run=total_cost_per_run,
                total_hours_per_run=total_hours_per_run,
                instance_config=config,
                message=""
            )
        
        except Exception as e:
            logger.error(f"Error calculating pricing: {e}")
            return None
    
    def calculate_multiple_instances(self, configs: List[InstanceConfig]) -> List[PricingResult]:
        """
        Calculate pricing for multiple instance configurations.
        
        Args:
            configs: List of instance configurations
            
        Returns:
            List of PricingResult objects
        """
        results = []
        
        for config in configs:
            result = self.calculate_instance_pricing(config)
            if result:
                results.append(result)
            else:
                logger.warning(f"Failed to calculate pricing for {config.instance_type}")
        
        return results
    
    def get_total_costs(self, results: List[PricingResult]) -> Dict[str, float]:
        """
        Calculate total costs across all instances.
        
        Args:
            results: List of PricingResult objects
            
        Returns:
            Dictionary with total costs
        """
        total_aws_hourly = sum(r.aws_cost_per_hour for r in results)
        total_databricks_hourly = sum(r.databricks_cost_per_hour for r in results)
        total_hourly = sum(r.total_cost_per_hour for r in results)
        
        total_aws_per_run = sum(r.aws_cost_per_run for r in results)
        total_databricks_per_run = sum(r.databricks_cost_per_run for r in results)
        total_per_run = sum(r.total_cost_per_run for r in results)
        
        return {
            "aws_hourly": total_aws_hourly,
            "databricks_hourly": total_databricks_hourly,
            "total_hourly": total_hourly,
            "aws_per_run": total_aws_per_run,
            "databricks_per_run": total_databricks_per_run,
            "total_per_run": total_per_run
        }
    
    def validate_config(self, config: InstanceConfig) -> Tuple[bool, str]:
        """
        Validate instance configuration.
        
        Args:
            config: Instance configuration to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if config.num_instances <= 0:
            return False, "Number of instances must be greater than 0"
        
        if config.hours_per_run <= 0 or config.hours_per_run > 168:  # Max 1 week
            return False, "Hours per run must be between 0 and 168 (1 week)"
        
        if not config.instance_type:
            return False, "Instance type is required"
        
        return True, "" 