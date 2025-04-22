import streamlit as st
import os
import re
from contextlib import contextmanager
import json
import random
import functools
import logging
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

# LangChain imports
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate
from langchain.chains import LLMChain
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# Load environment variables from .env file if it exists
load_dotenv()

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

# -----------------------------------------------------------------------------
# Configuration & Environment Variables
# -----------------------------------------------------------------------------
# Set page title and icon
st.set_page_config(page_title="Shake Shack Customer Support", page_icon="🍔")

# Hide default header/footer
st.markdown(
    """<style>header {visibility: hidden;} footer {visibility: hidden;}</style>""",
    unsafe_allow_html=True
)

# Decorator for LLM error handling
def llm_error_handler(default_return=None, error_message=None):
    """Decorator for handling LLM chain errors consistently."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_type = type(e).__name__
                error_details = str(e)
                logger.error(f"Error in {func.__name__}: {error_type} - {error_details}")
                
                # Provide specific user-friendly messages based on error type
                if "Unauthorized" in error_details:
                    return "There seems to be an issue with the API key. Please check that your API key is valid."
                elif "Connection" in error_details or "Timeout" in error_details:
                    return "I'm having trouble connecting to the language model service. Please check your internet connection and try again."
                elif "JSON" in error_type or "parsing" in error_details.lower():
                    return "I had trouble processing the response format. Please try rephrasing your request."
                
                # Use the provided error message if available
                if error_message:
                    return error_message
                
                # Use the default return value if provided
                if isinstance(default_return, str):
                    return f"I'm having trouble processing your request. {default_return}"
                
                return default_return
        return wrapper
    return decorator

# MongoDB connection string from Streamlit secrets or environment variables
def get_mongodb_uri():
    # In development: use local .env if available
    if os.getenv("MONGODB_URI"):
        return os.getenv("MONGODB_URI")
    # In production: use Streamlit secrets
    try:
        return st.secrets["MONGODB_URI"]
    except KeyError:
        st.error("MongoDB connection string not found. Please check your configuration.")
        return None

# -----------------------------------------------------------------------------
# Helper: LangChain Chat Model Getter
# -----------------------------------------------------------------------------
def get_llm():
    """
    Returns an instance of the LangChain ChatOpenAI model.
    Priority:
    1. User-provided API key (via the UI)
    2. API key from environment variables or .env file
    """
    # First check if user provided an API key through the UI
    key = st.session_state.get("openai_api_key")
    if key:
        return ChatOpenAI(api_key=key, model_name="gpt-4", temperature=0.5)
    
    # Otherwise, try to get the API key from environment variables (.env)
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return ChatOpenAI(api_key=env_key, model_name="gpt-4", temperature=0.5)
    
    # If neither is available, return None
    return None

# Get or create conversation memory
def get_conversation_memory():
    """Get or create a conversation memory object from session state."""
    if "conversation_memory" not in st.session_state:
        st.session_state.conversation_memory = ConversationBufferMemory(memory_key="chat_history")
    return st.session_state.conversation_memory

# -----------------------------------------------------------------------------
# Global Constants & Session State Initialization
# -----------------------------------------------------------------------------
# List of menu categories
MENU_CATEGORIES = ["Burgers", "Chicken", "Fries", "Milkshakes", "Drinks"]

# Initialize session state variables
for state_var in ['order', 'total_price', 'chat_history', 'menu_cache', 'last_response', 'openai_api_key', 'update_sidebar']:
    if state_var not in st.session_state:
        st.session_state[state_var] = [] if state_var in ['order', 'chat_history'] else (
            0.0 if state_var == 'total_price' else (
                False if state_var == 'update_sidebar' else None))

# -----------------------------------------------------------------------------
# Database Functions
# -----------------------------------------------------------------------------
@contextmanager
def get_db_connection():
    """Context manager for MongoDB connection."""
    mongodb_uri = get_mongodb_uri()
    if not mongodb_uri:
        raise Exception("MongoDB connection string not available")
    
    client = MongoClient(mongodb_uri)
    try:
        yield client["shakeshack"]  # database name
    finally:
        client.close()

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_all_menu_items():
    """Retrieves all menu items from MongoDB with caching."""
    if st.session_state.menu_cache is not None:
        return st.session_state.menu_cache

    try:
        with get_db_connection() as db:
            all_items = list(db.menu_items.find({}, {"_id": 0}))
            st.session_state.menu_cache = all_items
            return all_items
    except Exception as e:
        logger.error(f"Error retrieving menu items: {e}")
        st.error(f"Error retrieving menu items: {e}")
        return []

def get_menu_by_category(category):
    """Retrieves menu items for a specific category."""
    try:
        with get_db_connection() as db:
            return list(db.menu_items.find({"category": category}, {"_id": 0}))
    except Exception as e:
        logger.error(f"Error retrieving menu items by category: {e}")
        return []
    
def display_formatted_menu():
    """
    Returns a nicely formatted menu for display to the user.
    This is separate from prepare_menu_info which is for LLM prompts.
    """
    menu_items = get_all_menu_items()
    menu_by_category = {}
    for item in menu_items:
        category = item["category"]
        if category not in menu_by_category:
            menu_by_category[category] = []
        menu_by_category[category].append(item)
    
    formatted_menu = "# Shake Shack Menu\n\n"
    for category, items in menu_by_category.items():
        formatted_menu += f"## {category}\n\n"
        for item in items:
            formatted_menu += f"- **{item['name']}** — ${item['price']:.2f} ({item['calories']} calories)\n"
        formatted_menu += "\n"
    
    return formatted_menu

def prepare_menu_info():
    """Prepare formatted menu information for prompts."""
    menu_items = get_all_menu_items()
    menu_by_category = {}
    for item in menu_items:
        category = item["category"]
        if category not in menu_by_category:
            menu_by_category[category] = []
        menu_by_category[category].append(item)
    
    menu_info = "Shake Shack Menu Information:\n"
    for category, items in menu_by_category.items():
        menu_info += f"\n{category}:\n"
        for item in items:
            menu_info += f"- {item['name']}: ${item['price']:.2f}, {item['calories']} calories\n"
    
    return menu_info

@llm_error_handler(default_return=None)
def find_menu_item_langchain(item_description):
    """Uses LangChain to find the most likely menu item match."""
    llm = get_llm()
    if not llm:
        return None
    
    # Get all menu items for context
    all_items = get_all_menu_items()
    menu_json = json.dumps([{"name": item["name"], "category": item["category"]} for item in all_items])
    
    system_template = """
    You are given a user's description of a menu item at Shake Shack and a list of actual menu items.
    Find the menu item that best matches the user's description.
    
    Available menu items:
    {menu_items}
    
    Return ONLY the exact name of the matching menu item. If no good match is found, return "NO_MATCH".
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    matched_name = chain.run(input=item_description, menu_items=menu_json).strip()
    
    if matched_name == "NO_MATCH":
        return None
    
    # Find the full item details from the matched name
    for item in all_items:
        if item["name"].lower() == matched_name.lower():
            return item
    
    return None

def get_menu_categories():
    """Returns a list of available menu categories."""
    try:
        with get_db_connection() as db:
            results = db.menu_items.aggregate([
                {"$group": {"_id": "$category"}},
                {"$sort": {"_id": 1}}
            ])
            return [doc["_id"] for doc in results]
    except Exception:
        # Fallback to default categories if database query fails
        return MENU_CATEGORIES

# -----------------------------------------------------------------------------
# Order Management Functions
# -----------------------------------------------------------------------------
def get_order_summary():
    """Generates summary of current order."""
    if not st.session_state.order:
        return "Your order is currently empty."

    order_summary = "**Your current order:**  \n"
    for item in st.session_state.order:
        quantity = item.get("quantity", 1)
        quantity_str = f"({quantity}x) " if quantity > 1 else ""
        order_summary += f"- {quantity_str}{item['name']} — ${item['price'] * quantity:.2f}  \n"
    order_summary += f"  \n**Total: ${st.session_state.total_price:.2f}**"
    return order_summary

def add_to_order(menu_item, quantity=1):
    """Adds an item to the order."""
    if not menu_item:
        return False
    
    # Check if this item is already in the order
    for i, item in enumerate(st.session_state.order):
        if item["name"].lower() == menu_item["name"].lower():
            # Update the quantity instead of adding a new item
            old_quantity = item.get("quantity", 1)
            new_quantity = old_quantity + quantity
            st.session_state.order[i]["quantity"] = new_quantity
            st.session_state.total_price += menu_item["price"] * quantity
            st.session_state.update_sidebar = True
            return True
        
    # Item not in order, add it as new
    st.session_state.order.append({
        "name": menu_item["name"],
        "price": menu_item["price"],
        "category": menu_item["category"],
        "quantity": quantity
    })
    st.session_state.total_price += menu_item["price"] * quantity
    
    # Set flag to update the sidebar
    st.session_state.update_sidebar = True
    
    return True

def update_order_quantity(item_name, new_quantity):
    """
    Updates the quantity of an item already in the order.
    Returns a message confirming the update.
    """
    for i, item in enumerate(st.session_state.order):
        if item_name.lower() in item["name"].lower():
            # Store old quantity for price adjustment
            old_quantity = item.get("quantity", 1)
            
            # Calculate price difference
            price_change = item["price"] * (new_quantity - old_quantity)
            
            # Update quantity or remove if quantity is zero
            if new_quantity <= 0:
                removed_item = st.session_state.order.pop(i)
                st.session_state.total_price -= removed_item["price"] * old_quantity
                response = f"**I've removed {removed_item['name']} from your order.**  \n  \n**Your total is now ${st.session_state.total_price:.2f}**"
            else:
                st.session_state.order[i]["quantity"] = new_quantity
                st.session_state.total_price += price_change
                item_name = st.session_state.order[i]["name"]
                response = f"**I've updated your order:**  \n- Now {new_quantity}x {item_name} — ${item['price'] * new_quantity:.2f}  \n  \n**Your total is now ${st.session_state.total_price:.2f}**"
            
            # Set flag to update the sidebar
            st.session_state.update_sidebar = True
            
            return response
            
    return f"I couldn't find '{item_name}' in your current order."

def remove_from_order(item_name):
    """Removes an item from the order."""
    for i, item in enumerate(st.session_state.order):
        if item_name.lower() in item["name"].lower():
            removed_item = st.session_state.order.pop(i)
            quantity = removed_item.get("quantity", 1)
            st.session_state.total_price -= removed_item["price"] * quantity
            quantity_text = f"{quantity}x " if quantity > 1 else ""
            response = f"**Removed from your order:**  \n- {quantity_text}{removed_item['name']}  \n  \n**Your total is now ${st.session_state.total_price:.2f}**"
            st.session_state.update_sidebar = True
            return response
    return f"I couldn't find '{item_name}' in your current order."

# -----------------------------------------------------------------------------
# LangChain Intent Classification
# -----------------------------------------------------------------------------
@llm_error_handler(default_return="unknown")
def classify_intent(user_message):
    """Uses LangChain to classify the intent of the user message."""
    llm = get_llm()
    if not llm:
        return "unknown"
    
    system_template = """
    Classify the user's message into ONE of the following intents:
    - cart_inquiry: User is asking about their current order/cart
    - order_placement: User wants to place or add to an order
    - quantity_update: User wants to change the quantity of an item
    - price_inquiry: User is asking about the price of an item
    - remove_item: User wants to remove an item from their order
    - general_question: User is asking a general question about Shake Shack
    
    Return ONLY the intent label, nothing else.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    intent = chain.run(input=user_message).strip().lower()
    
    return intent

# -----------------------------------------------------------------------------
# LangChain Item Extraction
# -----------------------------------------------------------------------------
@llm_error_handler(default_return=[])
def extract_order_items(user_message):
    """Extracts menu items and quantities from user message using LangChain."""
    llm = get_llm()
    if not llm:
        return []
        
    # Create extraction chain
    system_template = """
    You are a specialized parser for Shake Shack orders.
    Extract ALL menu items with their quantities from the following order.
    Use the EXACT names as in the menu: for example, "Shackmade Lemonade", "Organic Ice Tea", "Hot Dog", "ShackBurger", etc.
    Return only a JSON object in the following format (do not include any additional text):
    {"items": [{"name": "Shackmade Lemonade", "quantity": 2}, {"name": "Organic Ice Tea", "quantity": 1}, {"name": "Hot Dog", "quantity": 1}, {"name": "ShackBurger", "quantity": 1}]}
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    extracted_text = chain.run(input=user_message).strip()
    
    try:
        items_data = json.loads(extracted_text)
        if "items" in items_data and len(items_data["items"]) > 0:
            return items_data["items"]
    except Exception as e:
        logger.error(f"Error parsing extracted items JSON: {e}")
    
    return []

@llm_error_handler(default_return=(False, None, None))
def process_quantity_update(user_message):
    """Uses LangChain to process quantity update requests."""
    llm = get_llm()
    if not llm:
        return False, None, None
    
    # Create a list of current order items for context
    current_items = ", ".join([item["name"] for item in st.session_state.order])
    
    system_template = """
    Determine if the user is trying to update the quantity of an item in their order.
    
    Current order items: {current_items}
    
    If the user is updating a quantity, extract:
    1. The item name they want to update
    2. The new quantity
    
    Return in JSON format:
    {"is_update": true/false, "item_name": "item name", "quantity": number}
    
    If not a quantity update, return:
    {"is_update": false, "item_name": null, "quantity": null}
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    result_json = chain.run(input=user_message, current_items=current_items).strip()
    
    try:
        result = json.loads(result_json)
        return result["is_update"], result["item_name"], result["quantity"]
    except Exception as e:
        logger.error(f"Error parsing quantity update JSON: {e}")
        return False, None, None

@llm_error_handler(default_return=None)
def extract_item_to_remove(user_message):
    """Uses LangChain to extract the item to remove from an order."""
    llm = get_llm()
    if not llm:
        return None
    
    # Create a list of current order items for context
    current_items = ", ".join([item["name"] for item in st.session_state.order])
    
    system_template = """
    The user wants to remove an item from their Shake Shack order.
    Extract the name of the item they want to remove.
    
    Current order items: {current_items}
    
    Return ONLY the name of the item to remove, nothing else.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    item_name = chain.run(input=user_message, current_items=current_items).strip()
    
    return item_name

@llm_error_handler(default_return=None)
def extract_price_inquiry_item(user_message):
    """Uses LangChain to extract the item name from a price inquiry."""
    llm = get_llm()
    if not llm:
        return None
    
    # Direct item match in message
    menu_items = get_all_menu_items()
    for item in menu_items:
        if item["name"].lower() in user_message.lower():
            return item
    
    # Create item extraction chain
    system_template = """
    Extract the name of the Shake Shack menu item the user is asking about the price of.
    Return ONLY the item name, nothing else.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    chain = LLMChain(llm=llm, prompt=chat_prompt)
    item_name = chain.run(input=user_message).strip()
    
    # Find the item in the menu
    return find_menu_item_langchain(item_name)

# -----------------------------------------------------------------------------
# LangChain Conversation
# -----------------------------------------------------------------------------
def create_shake_shack_chain():
    """Creates a LangChain chain for general Shake Shack conversations."""
    llm = get_llm()
    if not llm:
        return None
    
    # Use centralized menu info preparation
    menu_info = prepare_menu_info()

    # Create system template with menu and order info
    system_template = """
    You are a helpful and knowledgeable customer service agent for Shake Shack. You answer questions about Shake Shack's menu, 
    locations, ordering process, and general information about Shake Shack. If the user asks about anything 
    not related to Shake Shack, politely redirect them to ask questions about Shake Shack instead.

    Current User Order: {order}
    Total Price: ${total_price:.2f}

    When answering questions about menu items, prices, or nutritional information, use ONLY the following 
    accurate menu information from the database:

    {menu_info}

    Do not make up prices or nutritional information. If the user asks about an item not listed above,
    tell them you don't have information about that specific item.

    For general information that's not in the menu database:
    - If asked about store hours, direct users to: https://www.shakeshack.com/locations/
    - If asked about locations or finding nearby stores: https://www.shakeshack.com/locations/
    - If asked about allergens or nutritional information beyond calories: https://www.shakeshack.com/allergies-nutrition/
    - If asked about catering or large orders: https://www.shakeshack.com/catering/
    - For customer service or contact information: https://www.shakeshack.com/contact-us/
    - For app or rewards program questions: https://www.shakeshack.com/app/

    Be friendly and helpful. If you don't know specific information, it's better to provide a link to the official
    Shake Shack website rather than guessing.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    # Use persistent memory from session state
    memory = get_conversation_memory()
    
    return LLMChain(
        llm=llm, 
        prompt=chat_prompt,
        memory=memory,
        verbose=True
    )
    
# -----------------------------------------------------------------------------
# Main Message Processing
# -----------------------------------------------------------------------------
@llm_error_handler(
    default_return="I'm having trouble processing your request. Please try again.", 
    error_message="I'm having trouble connecting to our systems. Please try again in a moment."
)
def process_message(user_message):
    """Processes user message and generates appropriate response using LangChain intent classification."""
    # Check for OpenAI API key
    llm = get_llm()
    if not llm:
        if os.getenv("OPENAI_API_KEY"):
            # If there's an API key in the environment but not the session
            return "Using default API key. For personalized service, you can provide your own OpenAI API key in the sidebar."
        else:
            # No API key available anywhere
            return "Please provide your OpenAI API key in the sidebar to use the chat functionality."
    
    # Classify the user's intent
    intent = classify_intent(user_message)
    logger.info(f"Classified intent: {intent}")
    
    # Special case handling for menu requests
    if "menu" in user_message.lower():
        return f"Here's our current menu:\n\n{prepare_menu_info()}"
    
    # Handle based on intent
    if intent == "cart_inquiry":
        return get_order_summary()
    
    elif intent == "quantity_update":
        is_update, item_name, new_quantity = process_quantity_update(user_message)
        if is_update and new_quantity is not None:
            if item_name:
                # We have identified both the item and quantity
                return update_order_quantity(item_name, new_quantity)
            elif len(st.session_state.order) == 1:
                # Only one item in the order, so update that
                return update_order_quantity(st.session_state.order[0]["name"], new_quantity)
            else:
                # Multiple items but couldn't identify which one
                return "I'm not sure which item you want to change. Please specify the item name."
    
    elif intent == "order_placement":
        extracted_items = extract_order_items(user_message)
        if extracted_items:
            added_items = []
            not_found_items = []
            
            for item_data in extracted_items:
                item_name = item_data.get("name", "")
                item_quantity = item_data.get("quantity", 1)
                menu_item = find_menu_item_langchain(item_name)
                
                if menu_item:
                    add_to_order(menu_item, item_quantity)
                    added_items.append((menu_item, item_quantity))
                else:
                    not_found_items.append(item_name)
            
            if added_items:
                # Set flag to update the sidebar since items were added
                st.session_state.update_sidebar = True
                
                intro_line = random.choice([
                    "Fantastic! I've just added those items to your order:",
                    "Excellent choice! Your items have been added:",
                    "Great decision! I've updated your order with the following items:",
                    "Awesome! I've included those items in your order:"
                ])
                
                response = f"\"{intro_line}\"\n\n"
                for item, quantity in added_items:
                    response += f"- {quantity}x {item['name']} — ${item['price'] * quantity:.2f}\n"
                
                response += f"\nYour current total is now ${st.session_state.total_price:.2f}."
                response += "\n\nAnything else you'd like to adjust?"
                
                if not_found_items:
                    response += f"\n\nI couldn't find these items on our menu: {', '.join(not_found_items)}."
                
                return response
            else:
                return "I couldn't find any of the requested items on our menu. Please check the menu and try again."
    
    elif intent == "price_inquiry":
        price_item = extract_price_inquiry_item(user_message)
        if price_item:
            return f"The {price_item['name']} costs ${price_item['price']:.2f} and contains {price_item['calories']} calories."
        return "I'm not sure which item you're asking about. Could you please specify the name of the menu item?"
    
    elif intent == "remove_item":
        item_name = extract_item_to_remove(user_message)
        if item_name:
            return remove_from_order(item_name)
        return "I'm not sure which item you want to remove. Could you please specify the exact item name?"
    
    # General conversation (default fallback)
    shake_shack_chain = create_shake_shack_chain()
    
    # Create order summary for the chain context
    order_items = [
        f"{item.get('quantity', 1)}x {item['name']}" if item.get('quantity', 1) > 1 else item['name']
        for item in st.session_state.order
    ]
    order_str = ", ".join(order_items) if order_items else "None"
    
    # Use centralized menu info preparation
    menu_info = prepare_menu_info()
    
    # Run the general conversation chain
    try:
        # Make sure we have the correct input variables that match the prompt template
        response = shake_shack_chain.run(
            input=user_message,
            order=order_str,
            total_price=st.session_state.total_price,
            menu_info=menu_info
        )
        return response
    except Exception as e:
        logger.error(f"Error in general conversation: {e}")
        
        # If there's an error with the chain, handle common requests directly
        if "menu" in user_message.lower():
            return f"Here's our menu:\n\n{menu_info}"
        
        return "I'm having trouble processing your request. Please try again."

# -----------------------------------------------------------------------------
# Main Application UI
# -----------------------------------------------------------------------------
def main():
    """Main application function."""
    # --- Sidebar: API Key Input ---
    st.sidebar.header("OpenAI API Key")
    
    # Check if we have an environment API key
    has_env_key = bool(os.getenv("OPENAI_API_KEY"))
    
    # API key input
    api_key_input = st.sidebar.text_input("Enter your OpenAI API Key (ENV Key found)" if has_env_key else "Enter your OpenAI API Key", 
                                        type="password")
    if api_key_input:
        st.session_state.openai_api_key = api_key_input
        
    # --- Sidebar: Order Summary ---
    st.sidebar.title("Order Summary")
    if st.session_state.order:
        # Display order items
        for item in st.session_state.order:
            quantity = item.get("quantity", 1)
            quantity_str = f"({quantity}x) " if quantity > 1 else ""
            st.sidebar.write(f"- {quantity_str}{item['name']} — ${item['price'] * quantity:.2f}")
        
        # Display total and clear button
        st.sidebar.write(f"**Total: ${st.session_state.total_price:.2f}**")
        if st.sidebar.button("Clear Order"):
            st.session_state.order = []
            st.session_state.total_price = 0.0
            st.rerun()
    else:
        st.sidebar.write("Your order is empty.")

    # --- Main Chat Interface ---
    # Use simple path for logo
    st.image("assets/Shake-Shack-Logo.png")
    st.write("Welcome to Shake Shack! Ask me about our menu, place an order, or get help with anything Shake Shack related.")

    # API key warning (only if no key is available anywhere)
    if not os.getenv("OPENAI_API_KEY") and not st.session_state.get("openai_api_key"):
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to use the chat functionality.")

    # Initialize chat message history for LangChain integration
    msgs = StreamlitChatMessageHistory(key="langchain_messages")
    
    # If our session state is empty but LangChain history exists, sync them
    if not st.session_state.chat_history and msgs.messages:
        for msg in msgs.messages:
            st.session_state.chat_history.append({
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content
            })
    
    # If we have a welcome message in session state but not in LangChain history
    elif st.session_state.chat_history and not msgs.messages:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                msgs.add_user_message(msg["content"])
            else:
                msgs.add_ai_message(msg["content"])
    
    # If both are empty, initialize with welcome message
    elif not st.session_state.chat_history and not msgs.messages:
        welcome_msg = "Welcome to Shake Shack! How can I help you today?"
        msgs.add_ai_message(welcome_msg)
        st.session_state.chat_history.append({"role": "assistant", "content": welcome_msg})

    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Display last response if any
    if st.session_state.last_response:
        response = st.session_state.last_response
        st.session_state.last_response = None
        
        # Avoid duplicate responses
        last_message = st.session_state.chat_history[-1] if st.session_state.chat_history else None
        if not last_message or last_message["role"] != "assistant" or last_message["content"] != response:
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            # Also add to LangChain history
            msgs.add_ai_message(response)
        
        with st.chat_message("assistant"):
            st.markdown(response)

    # Chat input for user messages
    user_message = st.chat_input("Type your message here...")
    if user_message:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        # Also add to LangChain history
        msgs.add_user_message(user_message)
        
        with st.chat_message("user"):
            st.markdown(user_message)
        
        # Process message and generate response
        with st.spinner("Thinking..."):
            response = process_message(user_message)
        
        # Add response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        # Also add to LangChain history
        msgs.add_ai_message(response)
        
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Check if sidebar needs updating and rerun if needed
    if st.session_state.get('update_sidebar', False):
        st.session_state.update_sidebar = False
        st.rerun()

if __name__ == "__main__":
    main()