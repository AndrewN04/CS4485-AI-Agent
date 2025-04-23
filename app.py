import os
import logging
import atexit
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("shakeshack_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file if it exists
load_dotenv()

# Update requirements file with the correct dependencies
def update_requirements_file():
    """Creates or updates requirements.txt with the correct dependencies."""
    with open("requirements.txt", "w") as f:
        f.write("""streamlit>=1.28.0
openai>=1.1.0
python-dotenv>=1.0.0
langchain>=0.0.335
langchain_openai>=0.0.1
langchain_community>=0.0.13
pymongo>=4.5.0
""")

def main():
    """Main entry point for the Shake Shack Customer Support application."""
    try:
        # Import UI components
        from ui import render_ui, cleanup
        
        # Register cleanup function to run on exit
        atexit.register(cleanup)
        
        # Render the UI
        render_ui()
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        import streamlit as st
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error("Please check the logs for more information or contact support.")

if __name__ == "__main__":
    # Update requirements file with the correct dependencies
    update_requirements_file()
    main()