import streamlit as st
import sqlite3
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from difflib import get_close_matches
from contextlib import contextmanager

# Load environment variables once
load_dotenv()

# Initialize OpenAI client once
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Constants
MENU_CATEGORIES = ["Burgers", "Chicken", "Fries", "Milkshakes", "Drinks"]

# Initialize session state variables
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

# Database functions
@contextmanager
def get_db_connection():
    """Create a connection to the SQLite database using context manager"""
    conn = sqlite3.connect('shakeshack.db')
    try:
        yield conn
    finally:
        conn.close()

def get_all_menu_items():
    """Get all menu items from all category tables with caching"""
    # Return cached menu if available
    if st.session_state.menu_cache is not None:
        return st.session_state.menu_cache
    
    all_items = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
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
                # Table might not exist yet
                pass
    
    # Cache the menu
    st.session_state.menu_cache = all_items
    return all_items

def get_menu_by_category(category):
    """Get menu items for a specific category"""
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
            # Table might not exist yet
            return []

def find_menu_item(item_name):
    """Find a specific menu item by name across all categories using enhanced fuzzy matching"""
    all_items = get_all_menu_items()
    
    if not item_name or not isinstance(item_name, str):
        return None
    
    # Handle common plurals and prepare item name for matching
    search_names = [item_name.lower()]
    if item_name.lower().endswith('s') and not item_name.lower().endswith('fries'):
        singular_item_name = item_name[:-1]
        search_names.append(singular_item_name.lower())
    
    # Add common variations with more comprehensive handling
    normalized_search_names = list(search_names)
    for name in search_names:
        # Enhanced substitutions
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
    
    # Remove duplicates and empty strings
    normalized_search_names = list(set(filter(None, normalized_search_names)))
    
    # Direct match first - enhanced with better partial matching
    for item in all_items:
        item_lower = item["name"].lower()
        
        for search_name in normalized_search_names:
            # Exact match
            if search_name == item_lower:
                return item
            
            # Substring match in either direction
            if search_name in item_lower or item_lower in search_name:
                return item
    
    # Enhanced keyword match with more categories
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
    
    # Check if any keywords from the item name appear in menu items
    for search_name in normalized_search_names:
        for category, keywords in common_keywords.items():
            if any(keyword in search_name for keyword in keywords):
                # Find items in this category
                matching_items = [item for item in all_items 
                                 if any(keyword in item["name"].lower() for keyword in keywords)]
                if matching_items:
                    # Get the most similar item
                    menu_item_names = [item["name"].lower() for item in matching_items]
                    closest_matches = get_close_matches(search_name, menu_item_names, n=1, cutoff=0.1)
                    if closest_matches:
                        closest_match = closest_matches[0]
                        for item in matching_items:
                            if item["name"].lower() == closest_match:
                                return item
                    else:
                        # If no close match, return the first item in that category
                        return matching_items[0]
    
    # No match found
    return None

def get_menu_categories():
    """Get all available menu categories"""
    categories = []
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        for table in MENU_CATEGORIES:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                if cursor.fetchone()[0] > 0:
                    categories.append(table)
            except sqlite3.OperationalError:
                # Table might not exist yet
                pass
    
    return categories

def extract_quantity(text):
    """Extract quantity from text like '2 vanilla shakes'"""
    quantity_pattern = r'\b(\d+)\s+'
    match = re.search(quantity_pattern, text.lower())
    if match:
        return int(match.group(1)), text[match.end():]
    
    # Handle textual numbers like "two", "a", etc.
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
    """Generic intent checker for various keyword sets"""
    return any(keyword in user_message.lower() for keyword in keywords)

def check_cart_inquiry(user_message):
    """Check if the user is asking about their cart/order"""
    cart_keywords = [
        "cart", "order", "basket", "what's in my order", "what is in my order", 
        "what have i ordered", "view my order", "view order", "check order",
        "what's in my cart", "what is in my cart", "check my order", "show me my order",
        "show order", "current order", "see my order", "see order"
    ]
    return check_intent(user_message, cart_keywords)

def check_for_order_intent(user_message):
    """Check if the user is trying to place an order"""
    order_keywords = [
        "order", "get", "want", "like", "have", "give me", 
        "i'd like", "i would like", "can i get", "can i have", 
        "may i have", "i want", "i'll have", "gimme", "add"
    ]
    return check_intent(user_message, order_keywords)

def check_price_inquiry(user_message):
    """Determine if the user is asking about a menu item's price"""
    price_keywords = ["how much", "price", "cost", "how many", "what is the price", "what's the price"]
    
    # Check if this is a price-related query
    if not check_intent(user_message, price_keywords):
        return None
    
    # Check which menu item is being referenced
    menu_items = get_all_menu_items()
    for item in menu_items:
        if item["name"].lower() in user_message.lower():
            return item
    
    # If we can't determine the exact item, try extracting it with OpenAI
    try:
        item_extraction_response = client.chat.completions.create(
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
    """Generate a formatted order summary"""
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
    """Add an item to the order with given quantity"""
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
    """Remove an item from the order by name"""
    for i, item in enumerate(st.session_state.order):
        if item_name.lower() in item["name"].lower():
            removed_item = st.session_state.order.pop(i)
            quantity = removed_item.get("quantity", 1)
            st.session_state.total_price -= removed_item["price"] * quantity
            
            quantity_text = f"{quantity}x " if quantity > 1 else ""
            response = f"**Removed from your order:**  \n- {quantity_text}{removed_item['name']}  \n  \n**Your total is now ${st.session_state.total_price:.2f}**"
            
            # Create a placeholder for rerun after rendering response
            st.session_state.last_response = response
            st.rerun()
            return response
    
    return f"I couldn't find '{item_name}' in your current order."

def extract_order_items(user_message):
    """Extract menu items and quantities from an order message using OpenAI"""
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
        
        import json
        extracted_text = extraction_response.choices[0].message.content.strip()
        items_data = json.loads(extracted_text)
        
        if "items" in items_data and len(items_data["items"]) > 0:
            return items_data["items"]
        
    except Exception as e:
        print(f"Error extracting order items: {e}")
    
    # Fallback to basic extraction
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

# Process user message with OpenAI API
def process_message(user_message):
    try:
        # Check if user is asking about their cart/order
        if check_cart_inquiry(user_message):
            return get_order_summary()
        
        # Check for ordering intent
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
                    response = "**Added to your order:**  \n"
                    for item, quantity in added_items:
                        response += f"- {quantity}x {item['name']} — ${item['price'] * quantity:.2f}  \n"
                    
                    response += f"  \n**Your total is now ${st.session_state.total_price:.2f}**"
                    
                    if not_found_items:
                        response += f"  \n\nI couldn't find the following items on our menu: {', '.join(not_found_items)}"
                    
                    return response
                else:
                    return "I couldn't find any of the requested items on our menu. Please check the menu and try again."
        
        # Check if this is a price inquiry
        price_item = check_price_inquiry(user_message)
        if price_item:
            return f"The {price_item['name']} costs ${price_item['price']:.2f} and contains {price_item['calories']} calories."
        
        # Check if user wants to remove an item
        if "remove" in user_message.lower():
            try:
                item_extraction_response = client.chat.completions.create(
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
        
        # Check for general information queries about hours, locations, etc.
        general_info_keywords = {
            "hours": ["hours", "open time", "close time", "opening time", "closing time", "when do you open", "when do you close", "operating hours", "business hours"],
            "locations": ["locations", "where are you", "address", "find a location", "near me", "closest", "nearest", "where is", "where can i find"],
            "contact": ["contact", "phone number", "email", "customer service", "support", "how to contact", "reach out", "get in touch"],
            "allergens": ["allergen", "allergies", "gluten", "dairy", "nuts", "soy", "vegetarian", "vegan", "dietary", "celiac"],
            "nutrition": ["nutrition", "nutritional", "calories", "protein", "fat", "carbs", "sodium", "sugar", "ingredients"],
            "catering": ["catering", "large order", "event", "party", "group order"],
            "app": ["app", "mobile app", "rewards", "shack app", "loyalty", "points"],
            "covid": ["covid", "coronavirus", "safety measures", "safety protocol", "mask", "vaccination"]
        }
        
        # Check if message contains general info keywords
        for category, keywords in general_info_keywords.items():
            if any(keyword in user_message.lower() for keyword in keywords):
                if category == "hours":
                    return "Shake Shack's hours vary by location. To find the specific hours for your nearest Shake Shack, please visit the official website: [Shake Shack Locations](https://www.shakeshack.com/locations/)"
                
                elif category == "locations":
                    return "To find your nearest Shake Shack location, please visit the location finder on the official website: [Shake Shack Locations](https://www.shakeshack.com/locations/). You can search by city, state, or zip code to find Shake Shack restaurants near you."
                
                elif category == "contact":
                    return "For customer service inquiries, you can reach Shake Shack through their [Contact Page](https://www.shakeshack.com/contact-us/). For immediate assistance, you can also visit your local Shake Shack or call their customer service line available on their website."
                
                elif category == "allergens":
                    return "Shake Shack provides detailed allergen and nutritional information for all menu items. For the most up-to-date and accurate allergen information, please visit: [Shake Shack Allergen Information](https://www.shakeshack.com/allergies-nutrition/)"
                
                elif category == "nutrition":
                    return "Detailed nutritional information for all Shake Shack menu items can be found on their official website. For accurate nutritional content, please visit: [Shake Shack Nutritional Information](https://www.shakeshack.com/allergies-nutrition/)"
                
                elif category == "catering":
                    return "Shake Shack offers catering options for events and large groups. For more information about catering services and to place a catering order, please visit: [Shake Shack Catering](https://www.shakeshack.com/catering/)"
                
                elif category == "app":
                    return "The Shake Shack app allows you to order ahead, save favorites, and earn rewards. Download the app from the [App Store](https://apps.apple.com/us/app/shake-shack/id1406960590) or [Google Play](https://play.google.com/store/apps/details?id=com.shakeshack.android), or learn more on the [Shake Shack website](https://www.shakeshack.com/app/)"
                
                elif category == "covid":
                    return "For the latest information on Shake Shack's health and safety protocols, please visit their official website: [Shake Shack Safety Measures](https://www.shakeshack.com/)"
        
        # Check if the message is Shake Shack related
        menu_items = get_all_menu_items()
        contains_menu_item = any(item["name"].lower() in user_message.lower() for item in menu_items)
        
        is_relevant = True
        if not contains_menu_item:
            try:
                check_relevance_response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are a classifier that determines if a question is related to Shake Shack or not. Answer with only 'Yes' or 'No'."},
                        {"role": "user", "content": f"Is this question related to Shake Shack? Question: {user_message}"}
                    ],
                    max_tokens=10
                )
                
                is_relevant = "yes" in check_relevance_response.choices[0].message.content.strip().lower()
            except Exception as e:
                print(f"Error checking relevance: {e}")
                # Assume relevant on error
                is_relevant = True
        
        if not is_relevant:
            return "I'm a Shake Shack customer service agent. Please ask me questions about Shake Shack's menu, locations, or services."
        
        # Prepare menu information to provide to the AI
        menu_info = "Shake Shack Menu Information:\n"
        
        # Group items by category
        menu_by_category = {}
        for item in menu_items:
            if item["category"] not in menu_by_category:
                menu_by_category[item["category"]] = []
            menu_by_category[item["category"]].append(item)
        
        # Format menu information
        for category, items in menu_by_category.items():
            menu_info += f"\n{category}:\n"
            for item in items:
                menu_info += f"- {item['name']}: ${item['price']:.2f}, {item['calories']} calories\n"
        
        # Format current order for context
        order_items = []
        for item in st.session_state.order:
            quantity = item.get("quantity", 1)
            quantity_str = f"{quantity}x " if quantity > 1 else ""
            order_items.append(f"{quantity_str}{item['name']}")
        
        order_str = ", ".join(order_items) if st.session_state.order else "None"
        
        # For general questions about Shake Shack
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
                    Shake Shack website where they can find accurate information rather than guessing.
                    
                    If the user asks to view their cart or order, always show them their current order items and total.
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

# Streamlit UI
def main():
    st.set_page_config(page_title="Shake Shack Customer Support", page_icon="🍔")
    
    # Sidebar with order information
    st.sidebar.title("Order Summary")
    
    # Current order display in sidebar
    if st.session_state.order:
        for item in st.session_state.order:
            quantity = item.get("quantity", 1)
            quantity_str = f"({quantity}x) " if quantity > 1 else ""
            st.sidebar.write(f"- {quantity_str}{item['name']} — ${item['price'] * quantity:.2f}")
        st.sidebar.write(f"**Total: ${st.session_state.total_price:.2f}**")
        
        if st.sidebar.button("Clear Order"):
            st.session_state.order = []
            st.session_state.total_price = 0.0
            st.rerun()
    else:
        st.sidebar.write("Your order is empty.")
    
    # Main chat interface
    st.title("Shake Shack Customer Support Chat")
    st.write("Welcome to Shake Shack! Ask me about our menu, place an order, or get help with anything Shake Shack related.")
    
    # Display chat history with consistent formatting
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Check if we need to display a stored response (from a rerun)
    if st.session_state.last_response:
        response = st.session_state.last_response
        st.session_state.last_response = None  # Clear it after use
        
        # Add bot response to chat history if it's not already there
        last_message = st.session_state.chat_history[-1] if st.session_state.chat_history else None
        if not last_message or last_message["role"] != "assistant" or last_message["content"] != response:
            st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Display bot response with consistent formatting
        with st.chat_message("assistant"):
            st.markdown(response)
    
    # Chat input
    user_message = st.chat_input("Type your message here...")
    if user_message:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_message})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_message)
        
        # Get bot response
        with st.spinner("Thinking..."):
            response = process_message(user_message)
        
        # Add bot response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Display bot response with consistent formatting
        with st.chat_message("assistant"):
            st.markdown(response)

if __name__ == "__main__":
    main()