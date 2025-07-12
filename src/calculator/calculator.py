from abc import ABC, abstractmethod

class Calculator(ABC):
    """
    Abstract base class for calculators.
    """

    @abstractmethod
    def calculate_price(self):
        """
        Calculate the price based on the provided parameters.
        """ 
        pass