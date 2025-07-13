import unittest
from unittest.mock import Mock, patch

from src.calculator import PricingCalculator, InstanceConfig

class TestCalculation(unittest.TestCase):
    """
    Unit tests for pricing calculation
    """
    
    def test_aws_cost_calculation(self):
        """
        Test the AWS cost calculation for a given number of instances, hourly rate, and total hours
        """
        # Create a test configuration
        config = InstanceConfig(
            instance_type="m5d.8xlarge",
            num_instances=5,
            hours_per_run=3.0
        )
        
        # Mock the API clients
        calculator = PricingCalculator()
        with patch.object(calculator.vantage_client, 'get_aws_pricing') as mock_vantage, \
             patch.object(calculator.databricks_client, 'get_instance_pricing') as mock_databricks:
            
            # Mock AWS pricing
            mock_vantage.get_aws_pricing.return_value = 0.1
            
            # Mock Databricks pricing
            mock_databricks.get_instance_pricing.return_value = {
                "base_rate": 0.05,
                "dbu_rate": 0.03
            }
            
            result = calculator.calculate_instance_pricing(config)
            
            # Verify the calculation
            expected_aws_hourly = 5 * 0.1  # num_instances * hourly_rate
            expected_databricks_hourly = 5 * (0.05 + 0.03)  # num_instances * (base_rate + dbu_rate)
            expected_total_hourly = expected_aws_hourly + expected_databricks_hourly
            
            self.assertIsNotNone(result)
            self.assertAlmostEqual(result.aws_cost_per_hour, expected_aws_hourly, places=10)
            self.assertAlmostEqual(result.databricks_cost_per_hour, expected_databricks_hourly, places=10)
            self.assertAlmostEqual(result.total_cost_per_hour, expected_total_hourly, places=10)
    
    def test_total_hours_calculation(self):
        """
        Test the total hours calculation
        """
        config = InstanceConfig(
            instance_type="m5d.8xlarge",
            num_instances=2,
            hours_per_run=4.0
        )
        
        expected_total_hours = 4.0  # hours_per_run
        actual_total_hours = config.hours_per_run
        
        self.assertEqual(actual_total_hours, expected_total_hours)
        self.assertEqual(actual_total_hours, 4.0)
