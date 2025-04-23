import os
import logging
import pymongo
from pymongo import MongoClient
import streamlit as st
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Define a fallback menu for testing if the database is not available
FALLBACK_MENU = [
    {"name": "ShackBurger", "price": 6.99, "calories": 500, "category": "Burgers"},
    {"name": "Cheeseburger", "price": 6.49, "calories": 440, "category": "Burgers"},
    {"name": "Hamburger", "price": 6.49, "calories": 370, "category": "Burgers"},
    {"name": "Avocado Bacon Burger", "price": 9.49, "calories": 610, "category": "Burgers"},
    {"name": "SmokeShack", "price": 8.49, "calories": 570, "category": "Burgers"},
    {"name": "Bacon Cheeseburger", "price": 11.49, "calories": 760, "category": "Burgers"},
    {"name": "Fries", "price": 3.99, "calories": 470, "category": "Fries"},
    {"name": "Vanilla Shake", "price": 5.99, "calories": 680, "category": "Milkshakes"},
    {"name": "Chocolate Shake", "price": 5.99, "calories": 750, "category": "Milkshakes"},
    {"name": "Strawberry Shake", "price": 5.99, "calories": 690, "category": "Milkshakes"},
    {"name": "Topo Chico", "price": 3.49, "calories": 0, "category": "Drinks"},
]

# MongoDB connection string getter
def get_mongodb_uri():
    """Get MongoDB connection string from environment variables or Streamlit secrets."""
    # In development: use local .env if available
    if os.getenv("MONGODB_URI"):
        return os.getenv("MONGODB_URI")
    # In production: use Streamlit secrets
    try:
        return st.secrets["MONGODB_URI"]
    except KeyError:
        logger.error("MongoDB connection string not found")
        return None

# Global connection pool
_mongodb_client = None

def get_mongodb_client():
    """Get or create a MongoDB client."""
    global _mongodb_client
    
    if _mongodb_client is None:
        mongodb_uri = get_mongodb_uri()
        if not mongodb_uri:
            return None
        
        try:
            _mongodb_client = MongoClient(mongodb_uri)
            # Test the connection
            _mongodb_client.admin.command('ping')
            logger.info("MongoDB connection established")
        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")
            _mongodb_client = None
    
    return _mongodb_client

def get_db():
    """Get the Shake Shack database."""
    client = get_mongodb_client()
    if client:
        return client["shakeshack"]
    return None

def close_connections():
    """Close all database connections."""
    global _mongodb_client
    if _mongodb_client:
        _mongodb_client.close()
        _mongodb_client = None
        logger.info("MongoDB connections closed")

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_all_menu_items():
    """Retrieves all menu items with improved connection handling and caching."""
    # Check if we have a cached version in session state
    if "menu_cache" in st.session_state and st.session_state.menu_cache:
        return st.session_state.menu_cache

    try:
        db = get_db()
        if db is not None:
            all_items = list(db.menu_items.find({}, {"_id": 0}))
            if all_items:
                # Cache the results
                st.session_state.menu_cache = all_items
                return all_items
        
        # Fallback to hardcoded menu
        logger.info("Using fallback menu data (no DB connection or empty result)")
        st.session_state.menu_cache = FALLBACK_MENU
        return FALLBACK_MENU
    except Exception as e:
        logger.error(f"Error retrieving menu items: {e}")
        st.session_state.menu_cache = FALLBACK_MENU
        return FALLBACK_MENU

def get_menu_by_category(category):
    """Retrieves menu items for a specific category."""
    try:
        db = get_db()
        if db:
            items = list(db.menu_items.find({"category": category}, {"_id": 0}))
            if items:
                return items
        
        # Fallback to filtered hardcoded menu
        return [item for item in FALLBACK_MENU if item["category"] == category]
    except Exception as e:
        logger.error(f"Error retrieving menu items by category: {e}")
        return [item for item in FALLBACK_MENU if item["category"] == category]

def save_order(order_data):
    """Save an order to the database."""
    try:
        db = get_db()
        if db:
            result = db.orders.insert_one(order_data)
            return str(result.inserted_id)
        return None
    except Exception as e:
        logger.error(f"Error saving order: {e}")
        return None