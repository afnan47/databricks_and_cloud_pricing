"""
Streamlit app entry point for the pricing calculator.
Run this with: streamlit run src/streamlit_app.py
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.main import main

if __name__ == "__main__":
    main() 