import unittest

from src.calculator.aws_calculator import AWSCalculator 

class TestCalculation(unittest.TestCase):
    """
    
    Unit tests for AWS cost calculation
    """
    def test_aws_cost_calculation(self):
        """
        Test the AWS cost calculation for a given number of instances, hourly rate, and total hours
        """
        number_of_instances, hourly_rate, total_hours_used = 5, 0.1, 100
        
        calculator = AWSCalculator(number_of_instances, hourly_rate, total_hours_used)
        expected_price = number_of_instances * hourly_rate * total_hours_used
        self.assertEqual(calculator.calculate_price(), expected_price)
