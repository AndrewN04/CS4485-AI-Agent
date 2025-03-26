import streamlit as st
import sqlite3
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from difflib import get_close_matches
from contextlib import contextmanager
import json
import random

# Load environment variables from a .env file (if available)
load_dotenv()

# -----------------------------------------------------------------------------
# Helper: OpenAI Client Getter
# -----------------------------------------------------------------------------
def get_client():
    """
    Returns an instance of the OpenAI client.
    It first checks if an API key is provided by the user via the sidebar (stored in session_state).
    If not, it falls back to the API key set in the environment variables.
    """
    key = st.session_state.get("openai_api_key")
    if key:
        return OpenAI(api_key=key)
    else:
        return OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------------------------------------------------------
# Global Constants & Session State Initialization
# -----------------------------------------------------------------------------
# List of menu categories (each assumed to be a table in the SQLite database)
MENU_CATEGORIES = ["Burgers", "Chicken", "Fries", "Milkshakes", "Drinks"]

# Initialize session state variables to track the user's order, total price, chat history, etc.
if 'order' not in st.session_state:
    st.session_state.order = []
if 'total_price' not in st.session_state:
    st.session_state.total_price = 0.0
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'menu_cache' not in st.session_state:
    st.session_state.menu_cache = None
if 'last_response' not in st.session_state:
    st.session_state.last_response = None

# -----------------------------------------------------------------------------
# Database Functions
# -----------------------------------------------------------------------------
@contextmanager
def get_db_connection():
    """
    Context manager for creating a connection to the SQLite database.
    Ensures that the connection is closed after the operations are completed.
    """
    conn = sqlite3.connect('shakeshack.db')
    try:
        yield conn
    finally:
        conn.close()

def get_all_menu_items():
    """
    Retrieves all menu items from all category tables.
    Uses caching (in session_state) to avoid querying the database repeatedly.
    Returns a list of dictionaries containing menu item details.
    """
    if st.session_state.menu_cache is not None:
        return st.session_state.menu_cache

    all_items = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # Loop through each category table to fetch items
        for category in MENU_CATEGORIES:
            try:
                cursor.execute(f"SELECT name, price, calories FROM {category}")
                items = cursor.fetchall()
                for item in items:
                    all_items.append({
                        "name": item[0],
                        "price": item[1],
                        "calories": item[2],
                        "category": category
                    })
            except sqlite3.OperationalError:
                # If the table doesn't exist yet, skip it
                pass
    st.session_state.menu_cache = all_items
    return all_items

def get_menu_by_category(category):
    """
    Retrieves menu items for a specific category from the database.
    Returns a list of dictionaries with item details.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(f"SELECT name, price, calories FROM {category}")
            items = cursor.fetchall()
            return [
                {
                    "name": item[0],
                    "price": item[1],
                    "calories": item[2],
                    "category": category
                }
                for item in items
            ]
        except sqlite3.OperationalError:
            return []
        

def find_menu_item(item_name):
    """
    Attempts to find a menu item by its name using fuzzy matching.
    First, it handles direct and plural matching. Then, it performs keyword matching.
    Returns the menu item as a dictionary if found; otherwise, None.
    """
    all_items = get_all_menu_items()

    if not item_name or not isinstance(item_name, str):
        return None

    # Prepare potential search names (handle plural forms)
    search_names = [item_name.lower()]
    if item_name.lower().endswith('s') and not item_name.lower().endswith('fries'):
        singular_item_name = item_name[:-1]
        search_names.append(singular_item_name.lower())

    # Add variations for common items (e.g., iced tea, hot dog, etc.)
    normalized_search_names = list(search_names)
    for name in search_names:
        if "ice tea" in name or "iced tea" in name:
            normalized_search_names.extend([
                name.replace("ice tea", "iced tea"),
                name.replace("iced tea", "ice tea"),
                "iced tea", "ice tea"
            ])
        if "hot dog" in name or "hotdog" in name:
            normalized_search_names.extend(["hot dog", "hotdog", "dog"])
        if "shackmade" in name and "lemonade" in name:
            normalized_search_names.extend([
                "shackmade lemonade",
                "lemonade",
                "shack lemonade",
                "shake shack lemonade"
            ])
        if "organic" in name:
            normalized_search_names.append(name.replace("organic", "").strip())
            normalized_search_names.append(name.replace("organic", "organic iced").strip())

    normalized_search_names = list(set(filter(None, normalized_search_names)))

    # Direct match attempt (exact or substring match)
    for item in all_items:
        item_lower = item["name"].lower()
        for search_name in normalized_search_names:
            if search_name == item_lower:
                return item
            if search_name in item_lower or item_lower in search_name:
                return item

    # Fuzzy matching using common keywords
    common_keywords = {
        "burger": ["burger", "hamburger", "cheeseburger", "shackburger"],
        "shake": ["shake", "milkshake", "custard"],
        "fries": ["fries", "fry", "crinkle"],
        "chicken": ["chicken", "chick", "bird"],
        "lemonade": ["lemonade", "shackmade"],
        "tea": ["tea", "iced tea", "ice tea", "organic"],
        "hot dog": ["hot dog", "hotdog", "dog"],
        "drink": ["drink", "soda", "beverage", "tea", "lemonade"]
    }
    for search_name in normalized_search_names:
        for category, keywords in common_keywords.items():
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
                    else:
                        return matching_items[0]
    return None

def get_menu_categories():
    """
    Checks each menu category table to determine if it has any items.
    Returns a list of category names that contain menu items.
    """
    categories = []
    with get_db_connection() as conn:
        cursor = conn.cursor()
        for table in MENU_CATEGORIES:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                if cursor.fetchone()[0] > 0:
                    categories.append(table)
            except sqlite3.OperationalError:
                pass
    return categories

# -----------------------------------------------------------------------------
# Message & Order Handling Functions
# -----------------------------------------------------------------------------
def extract_quantity(text):
    """
    Extracts a quantity number from the beginning of a text string.
    Returns a tuple: (quantity, remaining_text). Defaults to 1 if not found.
    """
    quantity_pattern = r'\b(\d+)\s+'
    match = re.search(quantity_pattern, text.lower())
    if match:
        return int(match.group(1)), text[match.end():]

    # Handle textual numbers (e.g., "two", "one", etc.)
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
    """
    Checks if any of the specified keywords are present in the user_message, make sure it is associated with ShakeShack.
    Returns True if at least one keyword is found, otherwise False.
    """
    return any(keyword in user_message.lower() for keyword in keywords)

def check_cart_inquiry(user_message):
    """
    Determines if the user is asking about their current order/cart.
    Returns True if cart-related keywords are found.
    """
    cart_keywords = [
        "cart", "order", "basket", "what's in my order", "what is in my order",
        "what have i ordered", "view my order", "view order", "check order",
        "what's in my cart", "what is in my cart", "check my order", "show me my order",
        "show order", "current order", "see my order", "see order"
    ]
    return check_intent(user_message, cart_keywords)

def check_for_order_intent(user_message):
    """
    Determines if the user's message indicates an intent to place an order.
    Returns True if order-related keywords are found with a food associated in the menu
    """
    order_keywords = [
        "order", "get", "want", "give me", "like",
        "i'd like", "i would like", "can i get", "can i have",
        "may i have", "i want", "i'll have", "gimme", "add"
    ]
    return check_intent(user_message, order_keywords)

def check_price_inquiry(user_message):
    """
    Checks if the user's message is inquiring about the price of a menu item.
    Returns the corresponding menu item if found; otherwise, None.
    """
    price_keywords = ["how much", "price", "cost", "how many", "what is the price", "what's the price"]
    if not check_intent(user_message, price_keywords):
        return None

    menu_items = get_all_menu_items()
    for item in menu_items:
        if item["name"].lower() in user_message.lower():
            return item

    # Use OpenAI to extract the item name if not found directly
    try:
        item_extraction_response = get_client().chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Extract the name of the Shake Shack menu item the user is asking about. Return only the item name."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=50
        )
        item_name = item_extraction_response.choices[0].message.content.strip()
        return find_menu_item(item_name)
    except Exception as e:
        print(f"Error extracting item name: {e}")
        return None

def get_order_summary():
    """
    Generates a formatted string summarizing the current order and total price.
    """
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
    """
    Adds a menu item to the user's order with the specified quantity.
    Updates the total price accordingly.
    Returns True if the item was successfully added.
    """
    if not menu_item:
        return False
    st.session_state.order.append({
        "name": menu_item["name"],
        "price": menu_item["price"],
        "category": menu_item["category"],
        "quantity": quantity
    })
    st.session_state.total_price += menu_item["price"] * quantity
    return True

def remove_from_order(item_name):
    """
    Removes an item from the user's order based on a partial name match.
    Updates the total price and returns a confirmation message.
    """
    for i, item in enumerate(st.session_state.order):
        if item_name.lower() in item["name"].lower():
            removed_item = st.session_state.order.pop(i)
            quantity = removed_item.get("quantity", 1)
            st.session_state.total_price -= removed_item["price"] * quantity
            quantity_text = f"{quantity}x " if quantity > 1 else ""
            response = f"**Removed from your order:**  \n- {quantity_text}{removed_item['name']}  \n  \n**Your total is now ${st.session_state.total_price:.2f}**"
            st.session_state.last_response = response
            st.rerun()
            return response
    return f"I couldn't find '{item_name}' in your current order."

def extract_order_items(user_message):
    """
    Uses OpenAI to parse the user's message and extract menu items with their quantities.
    Returns a list of dictionaries with the format: {"name": item_name, "quantity": quantity}.
    If parsing fails, a fallback extraction method is attempted.
    """
    try:
        extraction_response = get_client().chat.completions.create(
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

    # Fallback extraction: attempt to extract a quantity and then use OpenAI to extract the item name
    try:
        quantity, remaining_text = extract_quantity(user_message)
        item_extraction_response = get_client().chat.completions.create(
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

def process_message(user_message):
    """
    Main processing function for user messages.
    Determines the intent (cart inquiry, order placement, price inquiry, removal, or general query) and responds accordingly.
    Returns a response string.
    """
    try:
        # Check if the user is asking about their cart/order
        if check_cart_inquiry(user_message):
            return get_order_summary()

        # Check if the user intends to place an order
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
                    positive_intros = [
                        "Fantastic! I've just added those items to your order:",
                        "Excellent choice! Your items have been added:",
                        "Great decision! I've updated your order with the following items:",
                        "Awesome! I've included those items in your order:"
                    ]
                    intro_line = random.choice(positive_intros)
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

        # Check if the message is inquiring about the price of a menu item
        price_item = check_price_inquiry(user_message)
        if price_item:
            return f"The {price_item['name']} costs ${price_item['price']:.2f} and contains {price_item['calories']} calories."

        # Check if the user wants to remove an item from their order
        if "remove" in user_message.lower():
            try:
                item_extraction_response = get_client().chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Extract the name of the Shake Shack menu item the user wants to remove. Return only the item name."},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=50
                )
                item_name = item_extraction_response.choices[0].message.content.strip()
                return remove_from_order(item_name)
            except Exception as e:
                print(f"Error in remove item: {e}")

        # Check if the query is related to Shake Shack by looking for menu items in the message
        menu_items = get_all_menu_items()
        contains_menu_item = any(item["name"].lower() in user_message.lower() for item in menu_items)

        # Prepare menu information for context to provide accurate responses
        menu_info = "Shake Shack Menu Information:\n"
        menu_by_category = {}
        for item in menu_items:
            if item["category"] not in menu_by_category:
                menu_by_category[item["category"]] = []
            menu_by_category[item["category"]].append(item)
        for category, items in menu_by_category.items():
            menu_info += f"\n{category}:\n"
            for item in items:
                menu_info += f"- {item['name']}: ${item['price']:.2f}, {item['calories']} calories\n"

        # Summarize the current order for additional context
        order_items = []
        for item in st.session_state.order:
            quantity = item.get("quantity", 1)
            quantity_str = f"{quantity}x " if quantity > 1 else ""
            order_items.append(f"{quantity_str}{item['name']}")
        order_str = ", ".join(order_items) if st.session_state.order else "None"

        # Use OpenAI to generate a general response based on the provided context
        try:
            completion = get_client().chat.completions.create(
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
    """
    Sets up the Streamlit user interface:
    - Displays a sidebar for API key input and order summary.
    - Provides a chat interface for the user to interact with the Shake Shack support agent.
    """
    st.set_page_config(page_title="Shake Shack Customer Support", page_icon="🍔")
    
    st.markdown(
    """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)
    
    # --- Sidebar: API Key Input ---
    st.sidebar.header("API Key")
    # Provide a password input field for users to enter their OpenAI API key.
    api_key_input = st.sidebar.text_input("Enter your OpenAI API Key", type="password")
    if api_key_input:
        st.session_state.openai_api_key = api_key_input

    # --- Sidebar: Order Summary ---
    st.sidebar.title("Order Summary")
    if st.session_state.order:
        # Display each item in the current order with quantity and price
        for item in st.session_state.order:
            quantity = item.get("quantity", 1)
            quantity_str = f"({quantity}x) " if quantity > 1 else ""
            st.sidebar.write(f"- {quantity_str}{item['name']} — ${item['price'] * quantity:.2f}")
        st.sidebar.write(f"**Total: ${st.session_state.total_price:.2f}**")
        # Button to clear the order; resets order and total price when clicked
        if st.sidebar.button("Clear Order"):
            st.session_state.order = []
            st.session_state.total_price = 0.0
            st.rerun()
    else:
        st.sidebar.write("Your order is empty.")

    # --- Main Chat Interface ---
    st.image("assets/Shake-Shack-Logo.png")
    st.write("Welcome to Shake Shack! Ask me about our menu, place an order, or get help with anything Shake Shack related.")

    # Display the chat history using Streamlit's chat_message for consistent formatting
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Display any stored response (e.g., after removing an item) from session_state
    if st.session_state.last_response:
        response = st.session_state.last_response
        st.session_state.last_response = None
        last_message = st.session_state.chat_history[-1] if st.session_state.chat_history else None
        if not last_message or last_message["role"] != "assistant" or last_message["content"] != response:
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

    # Chat input for user messages
    user_message = st.chat_input("Type your message here...")
    if user_message:
        # Add user message to chat history and display it
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)
        # Process the user's message and generate a response
        with st.spinner("Thinking..."):
            response = process_message(user_message)
        # Append the agent's response to chat history and display it
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()

