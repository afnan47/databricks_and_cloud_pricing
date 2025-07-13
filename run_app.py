#!/usr/bin/env python3
"""
Simple script to run the Streamlit pricing calculator app.
"""
import subprocess
import sys
import os

def main():
    """Run the Streamlit application."""
    try:
        # Check if streamlit is available
        subprocess.run([sys.executable, "-m", "streamlit", "--version"], 
                      check=True, capture_output=True)
        
        # Run the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/streamlit_app.py", "--server.port", "8501"
        ])
        
    except subprocess.CalledProcessError:
        print("❌ Streamlit is not installed. Please install it first:")
        print("   uv add streamlit")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 