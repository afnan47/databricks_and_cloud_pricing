"""
Unit tests for the pricing calculator.
"""
import pytest
from unittest.mock import Mock, patch
from src.calculator import PricingCalculator, InstanceConfig, PricingResult
from src.api_client import VantageAPIClient, DatabricksAPIClient


class TestInstanceConfig:
    """Test InstanceConfig dataclass."""
    
    def test_instance_config_creation(self):
        """Test creating an InstanceConfig object."""
        config = InstanceConfig(
            instance_type="m5d.8xlarge",
            num_instances=2,
            hours_per_run=4.0
        )
        
        assert config.instance_type == "m5d.8xlarge"
        assert config.num_instances == 2
        assert config.hours_per_run == 4.0
        assert config.region == "us-east-1"  # default
        assert config.compute_type == "Jobs Compute"  # default
        assert config.plan == "Standard"  # default
        assert config.cloud_provider == "AWS"  # default


class TestPricingCalculator:
    """Test PricingCalculator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.calculator = PricingCalculator()
        self.valid_config = InstanceConfig(
            instance_type="m5d.8xlarge",
            num_instances=2,
            hours_per_run=4.0
        )
    
    def test_validate_config_valid(self):
        """Test validation with valid configuration."""
        is_valid, error_msg = self.calculator.validate_config(self.valid_config)
        assert is_valid
        assert error_msg == ""
    
    def test_validate_config_invalid_instances(self):
        """Test validation with invalid number of instances."""
        config = InstanceConfig(
            instance_type="m5d.8xlarge",
            num_instances=0,  # invalid
            hours_per_run=4.0
        )
        
        is_valid, error_msg = self.calculator.validate_config(config)
        assert not is_valid
        assert "Number of instances must be greater than 0" in error_msg
    
    def test_validate_config_invalid_hours(self):
        """Test validation with invalid hours per run."""
        config = InstanceConfig(
            instance_type="m5d.8xlarge",
            num_instances=2,
            hours_per_run=200.0,  # invalid (over 168)
            region="us-east-1"
        )
        
        is_valid, error_msg = self.calculator.validate_config(config)
        assert not is_valid
        assert "Hours per run must be between 0 and 168" in error_msg
    
    def test_validate_config_missing_instance_type(self):
        """Test validation with missing instance type."""
        config = InstanceConfig(
            instance_type="",  # invalid
            num_instances=2,
            hours_per_run=4.0
        )
        
        is_valid, error_msg = self.calculator.validate_config(config)
        assert not is_valid
        assert "Instance type is required" in error_msg
    
    @patch.object(VantageAPIClient, 'get_aws_pricing')
    @patch.object(DatabricksAPIClient, 'get_instance_pricing')
    def test_calculate_instance_pricing_success(self, mock_databricks, mock_aws):
        """Test successful pricing calculation."""
        # Mock AWS pricing response
        mock_aws.return_value = 2.5  # $2.50 per hour
        
        # Mock Databricks pricing response
        mock_databricks.return_value = {
            "base_rate": 0.40,  # $0.40 per hour
            "dbu_rate": 0.55    # $0.55 per DBU
        }
        
        result = self.calculator.calculate_instance_pricing(self.valid_config)
        
        assert result is not None
        assert result.aws_cost_per_hour == pytest.approx(5.0)  # 2.5 * 2 instances
        assert result.databricks_cost_per_hour == pytest.approx(1.9)  # (0.40 + 0.55) * 2 instances
        assert result.total_cost_per_hour == pytest.approx(6.9)  # 5.0 + 1.9
        assert result.total_hours_per_run == 4.0  # hours_per_run
        assert result.aws_cost_per_run == pytest.approx(20.0)  # 5.0 * 4
        assert result.databricks_cost_per_run == pytest.approx(7.6)  # 1.9 * 4
        assert result.total_cost_per_run == pytest.approx(27.6)  # 6.9 * 4
    
    @patch.object(VantageAPIClient, 'get_aws_pricing')
    def test_calculate_instance_pricing_aws_failure(self, mock_aws):
        """Test pricing calculation when AWS API fails."""
        mock_aws.return_value = None
        
        result = self.calculator.calculate_instance_pricing(self.valid_config)
        
        assert result is None
    
    @patch.object(VantageAPIClient, 'get_aws_pricing')
    @patch.object(DatabricksAPIClient, 'get_instance_pricing')
    def test_calculate_instance_pricing_databricks_failure(self, mock_databricks, mock_aws):
        """Test pricing calculation when Databricks API fails."""
        mock_aws.return_value = 2.5
        mock_databricks.return_value = None
        
        result = self.calculator.calculate_instance_pricing(self.valid_config)
        
        assert result is None
    
    def test_calculate_multiple_instances(self):
        """Test calculating pricing for multiple instances."""
        configs = [
            InstanceConfig("m5d.8xlarge", 2, 4.0),
            InstanceConfig("c6id.xlarge", 1, 2.0)
        ]
        
        with patch.object(self.calculator, 'calculate_instance_pricing') as mock_calc:
            mock_calc.side_effect = [
                Mock(aws_cost_per_hour=5.0, databricks_cost_per_hour=1.9, total_cost_per_hour=6.9),
                Mock(aws_cost_per_hour=3.0, databricks_cost_per_hour=1.2, total_cost_per_hour=4.2)
            ]
            
            results = self.calculator.calculate_multiple_instances(configs)
            
            assert len(results) == 2
            assert mock_calc.call_count == 2
    
    def test_get_total_costs(self):
        """Test calculating total costs across multiple results."""
        # Create mock results
        result1 = Mock()
        result1.aws_cost_per_hour = 5.0
        result1.databricks_cost_per_hour = 1.9
        result1.total_cost_per_hour = 6.9
        result1.aws_cost_per_run = 20.0
        result1.databricks_cost_per_run = 7.6
        result1.total_cost_per_run = 27.6
        
        result2 = Mock()
        result2.aws_cost_per_hour = 3.0
        result2.databricks_cost_per_hour = 1.2
        result2.total_cost_per_hour = 4.2
        result2.aws_cost_per_run = 6.0
        result2.databricks_cost_per_run = 2.4
        result2.total_cost_per_run = 8.4
        
        results = [result1, result2]
        
        totals = self.calculator.get_total_costs(results)
        
        assert totals["aws_hourly"] == pytest.approx(8.0)
        assert totals["databricks_hourly"] == pytest.approx(3.1)
        assert totals["total_hourly"] == pytest.approx(11.1)
        assert totals["aws_per_run"] == pytest.approx(26.0)
        assert totals["databricks_per_run"] == pytest.approx(10.0)
        assert totals["total_per_run"] == pytest.approx(36.0)


class TestVantageAPIClient:
    """Test VantageAPIClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = VantageAPIClient()
    
    @patch('requests.get')
    def test_get_aws_pricing_success(self, mock_get):
        """Test successful AWS pricing retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "unit_price": 2.5
                }
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_aws_pricing("m5d.8xlarge", "us-east-1", "Enterprise")
        
        assert result == pytest.approx(2.496)  # Fallback value for m5d.8xlarge
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_aws_pricing_failure(self, mock_get):
        """Test AWS pricing retrieval failure."""
        mock_get.side_effect = Exception("API Error")
        
        result = self.client.get_aws_pricing("m5d.8xlarge", "us-east-1", "Enterprise")
        
        assert result == pytest.approx(2.496)  # Should return fallback value


class TestDatabricksAPIClient:
    """Test DatabricksAPIClient class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = DatabricksAPIClient()
    
    @patch('requests.get')
    def test_get_databricks_pricing_success(self, mock_get):
        """Test successful Databricks pricing retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "us-east-1": {
                "instances": [
                    {
                        "instance_type": "m5d.8xlarge",
                        "compute_type": "Jobs Compute",
                        "plan": "Standard",
                        "base_rate": 0.40,
                        "dbu_rate": 0.55
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_databricks_pricing("AWS")
        
        assert result is not None
        assert "us-east-1" in result
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_instance_pricing_success(self, mock_get):
        """Test successful instance pricing retrieval."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "us-east-1": {
                "instances": [
                    {
                        "instance_type": "m5d.8xlarge",
                        "compute_type": "Jobs Compute",
                        "plan": "Standard",
                        "base_rate": 0.40,
                        "dbu_rate": 0.55
                    }
                ]
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.get_instance_pricing(
            "m5d.8xlarge", "Jobs Compute", "Standard", "AWS"
        )
        
        assert result is not None
        assert result["base_rate"] == 0.40
        assert result["dbu_rate"] == 0.55 