from . import calculator

class AWSCalculator(calculator.Calculator):
    """
        Price Calculator for AWS instances.
    """

    def __init__(self, number_of_instances, hourly_rate, total_hours_used):
        """
        Initialize the AWSCalculator with instance type, hourly rate, and total hours used.
        
        :param number_of_instances: Total number of instances.
        :param hourly_rate: Hourly rate for the instance type.
        :param total_hours_used: Total hours the instance was used.
        """
        self.number_of_instances = number_of_instances
        self.hourly_rate = hourly_rate
        self.total_hours_used = total_hours_used

    def calculate_price(self):
        """
        Calculate the price for AWS instances based on the instance type, hourly rate, and total hours used.
        
        :return: Calculated price.
        """
        return self.number_of_instances * self.hourly_rate * self.total_hours_used