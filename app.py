import streamlit as st
import os
import re
from openai import OpenAI
from difflib import get_close_matches
from contextlib import contextmanager
import json
import random
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

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
# Helper: OpenAI Client Getter
# -----------------------------------------------------------------------------
def get_client():
    """
    Returns an instance of the OpenAI client.
    Priority:
    1. User-provided API key (via the UI)
    2. API key from environment variables or .env file
    """
    # First check if user provided an API key through the UI
    key = st.session_state.get("openai_api_key")
    if key:
        return OpenAI(api_key=key)
    
    # Otherwise, try to get the API key from environment variables (.env)
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return OpenAI(api_key=env_key)
    
    # If neither is available, show a warning
    st.warning("Please provide an OpenAI API key to use the chat functionality.")
    return None

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
        st.error(f"Error retrieving menu items: {e}")
        return []

def get_menu_by_category(category):
    """Retrieves menu items for a specific category."""
    try:
        with get_db_connection() as db:
            return list(db.menu_items.find({"category": category}, {"_id": 0}))
    except Exception:
        return []

def find_menu_item(item_name):
    """Finds a menu item by name with progressive matching strategies."""
    if not item_name or not isinstance(item_name, str):
        return None
    
    search_name = item_name.lower()
    words = search_name.split()
    
    try:
        with get_db_connection() as db:
            # Strategy 1: Exact match (case insensitive)
            item = db.menu_items.find_one(
                {"name": {"$regex": f"^{search_name}$", "$options": "i"}}, 
                {"_id": 0}
            )
            if item:
                return item
            
            # Strategy 2: Sequential word match (for multi-word items)
            if len(words) > 1:
                regex_pattern = ".*".join([re.escape(word) for word in words])
                item = db.menu_items.find_one(
                    {"name": {"$regex": f".*{regex_pattern}.*", "$options": "i"}}, 
                    {"_id": 0}
                )
                if item:
                    return item
            
            # Strategy 3: Partial match
            item = db.menu_items.find_one(
                {"name": {"$regex": search_name, "$options": "i"}}, 
                {"_id": 0}
            )
            if item:
                return item
            
            # Strategy 4: Text search if available
            try:
                item = db.menu_items.find_one(
                    {"$text": {"$search": search_name}},
                    {"_id": 0, "score": {"$meta": "textScore"}}
                )
                if item:
                    return item
            except pymongo.errors.OperationFailure:
                pass
    except Exception as e:
        st.error(f"Database error while finding menu item: {e}")
        return None
                
    # Strategy 5: Advanced matching with all menu items
    all_items = get_all_menu_items()
    
    # Check for all words in item name (unordered)
    for item in all_items:
        item_lower = item["name"].lower()
        if all(word in item_lower for word in words):
            return item
            
    # Strategy 6: Most words match
    if len(words) > 1:
        matches = []
        for item in all_items:
            item_lower = item["name"].lower()
            match_count = sum(1 for word in words if word in item_lower)
            if match_count > 0:
                matches.append((item, match_count))
        
        if matches:
            matches.sort(key=lambda x: x[1], reverse=True)
            return matches[0][0]
            
    # Strategy 7: Keyword matching
    keyword_categories = {
        "burger": ["burger", "hamburger", "cheeseburger", "shackburger"],
        "shake": ["shake", "milkshake", "custard"],
        "fries": ["fries", "fry", "crinkle"],
        "chicken": ["chicken", "chick", "bird"],
        "lemonade": ["lemonade", "shackmade"],
        "tea": ["tea", "iced tea", "ice tea", "organic"],
        "hot dog": ["hot dog", "hotdog", "dog"],
        "drink": ["drink", "soda", "beverage", "tea", "lemonade"]
    }
    
    for category, keywords in keyword_categories.items():
        if any(keyword in search_name for keyword in keywords):
            matching_items = [item for item in all_items if any(keyword in item["name"].lower() for keyword in keywords)]
            if matching_items:
                menu_item_names = [item["name"].lower() for item in matching_items]
                closest_matches = get_close_matches(search_name, menu_item_names, n=1, cutoff=0.1)
                if closest_matches:
                    closest_match = closest_matches[0]
                    for item in matching_items:
                        if item["name"].lower() == closest_match:
                            return item
                return matching_items[0]
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
# Message & Order Handling Functions
# -----------------------------------------------------------------------------
def extract_quantity(text):
    """Extracts quantity from text."""
    # Number pattern (e.g., "2 burgers")
    quantity_pattern = r'\b(\d+)\s+'
    match = re.search(quantity_pattern, text.lower())
    if match:
        return int(match.group(1)), text[match.end():]

    # Text number pattern (e.g., "two burgers")
    text_lower = text.lower()
    text_number_map = {
        "a ": 1, "an ": 1, "one ": 1, "two ": 2, "three ": 3, "four ": 4, "five ": 5,
        "six ": 6, "seven ": 7, "eight ": 8, "nine ": 9, "ten ": 10
    }
    for text_num, value in text_number_map.items():
        if text_lower.startswith(text_num):
            return value, text_lower[len(text_num):]
    return 1, text

def check_intent(user_message, keywords):
    """Checks if user message contains any keywords."""
    return any(keyword in user_message.lower() for keyword in keywords)

def check_cart_inquiry(user_message):
    """Checks if user is asking about their order/cart."""
    cart_keywords = [
        "cart", "order", "basket", "what's in my order", "what is in my order",
        "what have i ordered", "view my order", "view order", "check order",
        "what's in my cart", "what is in my cart", "check my order", "show me my order",
        "show order", "current order", "see my order", "see order", "total"
    ]
    return check_intent(user_message, cart_keywords)

def check_for_order_intent(user_message):
    """Checks if user wants to place an order."""
    order_keywords = [
        "order", "get", "want", "give me", "like",
        "i'd like", "i would like", "can i get", "can i have",
        "may i have", "i want", "i'll have", "gimme", "add"
    ]
    return check_intent(user_message, order_keywords)

def check_price_inquiry(user_message):
    """Checks if user is asking about item price."""
    price_keywords = ["how much", "price", "cost", "how many", "what is the price", "what's the price"]
    if not check_intent(user_message, price_keywords):
        return None

    # Direct item match in message
    menu_items = get_all_menu_items()
    for item in menu_items:
        if item["name"].lower() in user_message.lower():
            return item

    # Use OpenAI to extract item name
    client = get_client()
    if not client:
        return None
        
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract the name of the Shake Shack menu item the user is asking about. Return only the item name."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=50
        )
        item_name = response.choices[0].message.content.strip()
        return find_menu_item(item_name)
    except Exception as e:
        print(f"Error extracting item name: {e}")
        return None

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
            st.session_state.last_response = response
            st.session_state.update_sidebar = True
            st.rerun()
            return response
    return f"I couldn't find '{item_name}' in your current order."

def extract_order_items(user_message):
    """Extracts menu items and quantities from user message."""
    # Check for OpenAI API key
    client = get_client()
    if not client:
        return []
        
    # Try OpenAI JSON extraction
    try:
        extraction_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": """
You are a specialized parser for Shake Shack orders.
Extract ALL menu items with their quantities from the following order.
Use the EXACT names as in the menu: for example, "Shackmade Lemonade", "Organic Ice Tea", "Hot Dog", "ShackBurger", etc.
Return only a JSON object in the following format (do not include any additional text):
{"items": [{"name": "Shackmade Lemonade", "quantity": 2}, {"name": "Organic Ice Tea", "quantity": 1}, {"name": "Hot Dog", "quantity": 1}, {"name": "ShackBurger", "quantity": 1}]}
"""},            
                {"role": "user", "content": user_message}
            ],
            max_tokens=300
        )
        extracted_text = extraction_response.choices[0].message.content.strip()
        items_data = json.loads(extracted_text)
        if "items" in items_data and len(items_data["items"]) > 0:
            return items_data["items"]
    except Exception as e:
        print(f"Error extracting order items: {e}")

    # Fallback extraction
    try:
        quantity, remaining_text = extract_quantity(user_message)
        item_extraction_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract the name of the Shake Shack menu item the user wants to order. Return only the item name."},
                {"role": "user", "content": remaining_text}
            ],
            max_tokens=50
        )
        item_name = item_extraction_response.choices[0].message.content.strip()
        return [{"name": item_name, "quantity": quantity}]
    except Exception as e:
        print(f"Error in fallback extraction: {e}")
        return []

def check_for_quantity_update(user_message):
    """
    Checks if the user message is a request to update item quantity.
    Returns a tuple of (True/False, item_name, new_quantity) if detected.
    """
    # Keywords that might indicate quantity update
    quantity_update_keywords = ["make", "change", "update", "only", "just", "instead", "reduce", "increase"]
    
    # Check if any keyword is present
    has_update_keyword = any(keyword in user_message.lower() for keyword in quantity_update_keywords)
    
    # If no keyword is found, return False
    if not has_update_keyword:
        return False, None, None
        
    # Extract quantity
    quantity_pattern = r'\b([1-9][0-9]?)\b'  # Match numbers 1-99
    match = re.search(quantity_pattern, user_message)
    if not match:
        return False, None, None
        
    new_quantity = int(match.group(1))
    
    # If we have only one item in the order, it's likely this item
    if len(st.session_state.order) == 1:
        return True, st.session_state.order[0]["name"], new_quantity
    
    # Otherwise, try to extract the item name
    client = get_client()
    if client:
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "The user is changing the quantity of a menu item at Shake Shack. Extract the name of the item. Return only the item name."},
                    {"role": "user", "content": user_message + "\n\nCurrent order: " + ", ".join([item["name"] for item in st.session_state.order])}
                ],
                max_tokens=50
            )
            item_name = response.choices[0].message.content.strip()
            return True, item_name, new_quantity
        except Exception as e:
            print(f"Error extracting item name for quantity update: {e}")
    
    # If we couldn't determine the item, return True but with None for item_name
    return True, None, new_quantity

def process_message(user_message):
    """Processes user message and generates appropriate response."""
    # Check for OpenAI API key in session or environment
    client = get_client()
    if not client:
        if os.getenv("OPENAI_API_KEY"):
            # If there's an API key in the environment but not the session
            return "Using default API key. For personalized service, you can provide your own OpenAI API key in the sidebar."
        else:
            # No API key available anywhere
            return "Please provide your OpenAI API key in the sidebar to use the chat functionality."
        
    try:
        # Cart inquiry
        if check_cart_inquiry(user_message):
            return get_order_summary()

        # Check for quantity update request
        is_quantity_update, item_name, new_quantity = check_for_quantity_update(user_message)
        if is_quantity_update and st.session_state.order:
            if item_name:
                # We have identified both the item and quantity
                return update_order_quantity(item_name, new_quantity)
            elif len(st.session_state.order) == 1:
                # Only one item in the order, so update that
                return update_order_quantity(st.session_state.order[0]["name"], new_quantity)
            else:
                # Multiple items but couldn't identify which one
                return "I'm not sure which item you want to change. Please specify the item name."

        # Order placement
        if check_for_order_intent(user_message):
            extracted_items = extract_order_items(user_message)
            if extracted_items:
                added_items = []
                not_found_items = []
                
                for item_data in extracted_items:
                    item_name = item_data.get("name", "")
                    item_quantity = item_data.get("quantity", 1)
                    menu_item = find_menu_item(item_name)
                    
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

        # Price inquiry
        price_item = check_price_inquiry(user_message)
        if price_item:
            return f"The {price_item['name']} costs ${price_item['price']:.2f} and contains {price_item['calories']} calories."

        # Remove item
        if "remove" in user_message.lower():
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Extract the name of the Shake Shack menu item the user wants to remove. Return only the item name."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=50
                )
                item_name = response.choices[0].message.content.strip()
                return remove_from_order(item_name)
            except Exception as e:
                print(f"Error in remove item: {e}")
                return "I'm having trouble understanding which item you want to remove. Could you please specify the exact item name?"

        # General conversation with OpenAI
        # Prepare menu information
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

        # Current order summary
        order_items = [
            f"{item.get('quantity', 1)}x {item['name']}" if item.get('quantity', 1) > 1 else item['name']
            for item in st.session_state.order
        ]
        order_str = ", ".join(order_items) if order_items else "None"

        # Generate response with OpenAI
        try:
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"""
You are a helpful and knowledgeable customer service agent for Shake Shack. You answer questions about Shake Shack's menu, 
locations, ordering process, and general information about Shake Shack. If the user asks about anything 
not related to Shake Shack, politely redirect them to ask questions about Shake Shack instead.

Current User Order: {order_str}
Total Price: ${st.session_state.total_price:.2f}

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
"""}, 
                    {"role": "user", "content": user_message}
                ]
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error in general conversation: {e}")
            return "I'm having trouble processing your request. Please try again."
    except Exception as e:
        return f"I'm having trouble processing your request. Please try again. Error details: {str(e)}"

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
    st.image("assets/Shake-Shack-Logo.png")
    st.write("Welcome to Shake Shack! Ask me about our menu, place an order, or get help with anything Shake Shack related.")

    # API key warning (only if no key is available anywhere)
    if not os.getenv("OPENAI_API_KEY") and not st.session_state.get("openai_api_key"):
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to use the chat functionality.")

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
        
        with st.chat_message("assistant"):
            st.markdown(response)

    # Chat input for user messages
    user_message = st.chat_input("Type your message here...")
    if user_message:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)
        
        # Process message and generate response
        with st.spinner("Thinking..."):
            response = process_message(user_message)
        
        # Add response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Check if sidebar needs updating and rerun if needed
    if st.session_state.get('update_sidebar', False):
        st.session_state.update_sidebar = False
        st.rerun()

if __name__ == "__main__":
    main()