import os
import json
import re
import functools
import logging
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.memory import ConversationBufferMemory


# Import after module creation to avoid circular imports
# These will be imported inside functions where needed
# from menu import find_menu_item, prepare_menu_info
# from order import update_order_quantity, remove_from_order

logger = logging.getLogger(__name__)

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
                
                return default_return if default_return is not None else "I'm having trouble processing your request. Please try again."
        return wrapper
    return decorator

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

@llm_error_handler(default_return="general_question")
def classify_intent(user_message):
    """Uses LangChain to classify the intent of the user message."""
    llm = get_llm()
    if not llm:
        return "general_question"
    
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
    
    # Use modern LangChain patterns
    chain = chat_prompt | llm
    intent = chain.invoke({"input": user_message}).content.strip().lower()
    logger.info(f"LLM identified intent: {intent}")
    
    return intent

@llm_error_handler(default_return=[])
def extract_order_items_from_text(user_message):
    """
    Extract order items using text pattern matching.
    This is a direct, non-LLM approach that's faster and more reliable for simple cases.
    """
    # Import here to avoid circular imports
    from menu import find_menu_item
    
    # Look for patterns like "I would like a/an [item]" or "I want [quantity] [item]"
    direct_patterns = [
        r"(?:i|get|add|order)?\s*(?:would|want|like|need|have)?\s*(?:to)?(?:get|add|order|have)?\s*(?:an?|some|\d+)?\s*([a-zA-Z\s]+(?:burger|shake|fries|chico|dog|tea|soda|water|coffee|lemonade))",
        r"(?:i|get|add|order)?\s*(?:would|want|like|need)?\s*(\d+)\s*([a-zA-Z\s]+)",
        r"(?:add|give me|get me|get|order)\s*(?:an?|some|\d+)?\s*([a-zA-Z\s]+)"
    ]
    
    # First look for direct quantity + item match (e.g., "5 shackburgers")
    quantity_item_pattern = re.search(r'(\d+)\s+([a-zA-Z\s]+)', user_message.lower())
    if quantity_item_pattern:
        quantity = int(quantity_item_pattern.group(1))
        item_name = quantity_item_pattern.group(2).strip()
        menu_item = find_menu_item(item_name)
        if menu_item:
            return [{"name": menu_item["name"], "quantity": quantity}]
    
    extracted_items = []
    processed_items = set()  # Track which items we've already processed
    
    # Try all patterns
    for pattern in direct_patterns:
        matches = re.findall(pattern, user_message.lower())
        
        for match in matches:
            # Handle different match structures
            if isinstance(match, tuple):
                if len(match) == 2 and match[0].isdigit():  # Quantity and item
                    quantity = int(match[0])
                    item_name = match[1].strip()
                else:  # Just item
                    quantity = 1
                    item_name = match[0].strip()
            else:  # Just item
                quantity = 1
                item_name = match.strip()
            
            # Skip common words that aren't menu items
            if item_name in ["some", "a", "an", "the", "to", "for", "me", "please", "thanks"]:
                continue
            
            # Try to find corresponding menu item
            menu_item = find_menu_item(item_name)
            if menu_item and menu_item["name"] not in processed_items:
                processed_items.add(menu_item["name"])
                # Check if this item is already in our extracted list
                existing = next((i for i, item in enumerate(extracted_items) 
                                if item["name"] == menu_item["name"]), None)
                
                if existing is not None:
                    # Update quantity if already extracted
                    extracted_items[existing]["quantity"] += quantity
                else:
                    # Add new item
                    extracted_items.append({"name": menu_item["name"], "quantity": quantity})
    
    return extracted_items

@llm_error_handler(default_return=[])
def extract_order_items_using_llm(user_message):
    """Extract order items using LLM."""
    # Import here to avoid circular imports
    from menu import find_menu_item
    
    llm = get_llm()
    if not llm:
        return []
    
    # Create extraction chain with properly escaped template
    system_template = """
    You are a specialized parser for Shake Shack orders.
    Extract ALL menu items with their quantities from the following order.
    
    Format your response as a JSON object with this EXACT structure:
    {
      "items": [
        {"name": "ShackBurger", "quantity": 5},
        {"name": "Fries", "quantity": 2}
      ]
    }
    
    Ensure you match menu items EXACTLY as they appear on the menu.
    Only include the JSON object in your response, nothing else.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    # Use modern LangChain patterns
    chain = chat_prompt | llm
    response_text = chain.invoke({"input": user_message}).content.strip()
    
    # Log the result
    logger.info(f"LLM extraction result: {response_text}")
    
    # Clean up the response text to ensure it's valid JSON
    response_text = response_text.replace("```json", "").replace("```", "").strip()
    
    try:
        # Handle the case where the model might wrap the response in backticks
        if response_text.startswith("{") and response_text.endswith("}"):
            items_data = json.loads(response_text)
            if "items" in items_data and isinstance(items_data["items"], list):
                # Process the extracted items to match with actual menu items
                result_items = []
                processed_items = set()
                
                for item_data in items_data["items"]:
                    if "name" in item_data and "quantity" in item_data:
                        menu_item = find_menu_item(item_data["name"])
                        if menu_item and menu_item["name"] not in processed_items:
                            processed_items.add(menu_item["name"])
                            # Check if this item is already in our extracted list
                            existing = next((i for i, extracted in enumerate(result_items) 
                                            if extracted["name"] == menu_item["name"]), None)
                            
                            if existing is not None:
                                # Update quantity if already extracted
                                result_items[existing]["quantity"] += item_data["quantity"]
                            else:
                                # Add new item
                                result_items.append({
                                    "name": menu_item["name"],
                                    "quantity": item_data["quantity"]
                                })
                return result_items if result_items else []
    except Exception as e:
        logger.error(f"Error parsing extracted items JSON: {e}")
    
    return []

def extract_order_items(user_message):
    """
    Combined approach for extracting order items.
    First tries the faster text-based approach, falls back to LLM if needed.
    """
    # First try the text-based extraction (faster and more reliable for simple cases)
    extracted_items = extract_order_items_from_text(user_message)
    if extracted_items:
        return extracted_items
    
    # If direct extraction failed, try LLM-based extraction
    return extract_order_items_using_llm(user_message)

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
    
    Return a JSON object with this exact structure:
    {{"is_update": true, "item_name": "ItemName", "quantity": 2}}
    
    If not a quantity update, return:
    {{"is_update": false, "item_name": null, "quantity": null}}
    
    Only include the JSON object in your response, nothing else.
    """
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_message_prompt = HumanMessagePromptTemplate.from_template("{input}")
    chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
    
    # Use modern LangChain patterns
    chain = chat_prompt | llm
    result_json = chain.invoke({"input": user_message, "current_items": current_items}).content.strip()
    
    # Clean up the response text to ensure it's valid JSON
    result_json = result_json.replace("```json", "").replace("```", "").strip()
    
    try:
        if result_json.startswith("{") and result_json.endswith("}"):
            result = json.loads(result_json)
            is_update = result.get("is_update", False)
            item_name = result.get("item_name")
            quantity = result.get("quantity")
            
            return is_update, item_name, quantity
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
    
    # Use modern LangChain patterns
    chain = chat_prompt | llm
    item_name = chain.invoke({"input": user_message, "current_items": current_items}).content.strip()
    
    return item_name

@llm_error_handler(default_return=None)
def extract_price_inquiry_item(user_message):
    """Uses LangChain to extract the item name from a price inquiry."""
    # Import here to avoid circular imports
    from database import get_all_menu_items
    from menu import find_menu_item
    
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
    
    # Use modern LangChain patterns
    chain = chat_prompt | llm
    item_name = chain.invoke({"input": user_message}).content.strip()
    
    # Find the item in the menu using our improved finder
    return find_menu_item(item_name)

@llm_error_handler(default_return="I'm having trouble processing your request. Please try again.")
def general_conversation(user_message, order_str, total_price, menu_info):
    """Handles general conversation about Shake Shack."""
    llm = get_llm()
    if not llm:
        return "Please provide your OpenAI API key in the sidebar to use the chat functionality."
    
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
    
    # Use modern LangChain patterns
    chain = chat_prompt | llm
    response = chain.invoke({
        "input": user_message,
        "order": order_str,
        "total_price": total_price,
        "menu_info": menu_info
    }).content
    
    return response

@llm_error_handler(
    default_return="I'm having trouble processing your request. Please try again.", 
    error_message="I'm having trouble connecting to our systems. Please try again in a moment."
)
def process_message(user_message):
    """Processes user message and generates appropriate response."""
    # Import here to avoid circular imports
    from menu import find_menu_item, prepare_menu_info
    from order import update_order_quantity, remove_from_order, get_order_summary, add_to_order
    
    # Check for OpenAI API key
    llm = get_llm()
    if not llm:
        if os.getenv("OPENAI_API_KEY"):
            # If there's an API key in the environment but not the session
            return "Using default API key. For personalized service, you can provide your own OpenAI API key in the sidebar."
        else:
            # No API key available anywhere
            return "Please provide your OpenAI API key in the sidebar to use the chat functionality."
    
    # Special case handling for menu requests
    if "menu" in user_message.lower():
        from menu import display_formatted_menu
        return display_formatted_menu()
    
    # Classify the user's intent
    intent = classify_intent(user_message)
    logger.info(f"Classified intent: {intent}")
    
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
        # Extract items from the order request
        extracted_items = extract_order_items(user_message)
        
        if extracted_items:
            added_items = []
            
            for item_data in extracted_items:
                item_name = item_data.get("name", "")
                item_quantity = item_data.get("quantity", 1)
                
                # We can assume item_name is already a valid menu item from extract_order_items
                menu_item = find_menu_item(item_name)
                
                if menu_item:
                    # Add to order
                    add_to_order(menu_item, item_quantity)
                    added_items.append((menu_item, item_quantity))
            
            if added_items:
                # Set flag to update the sidebar since items were added
                st.session_state.update_sidebar = True
                
                # Format response consistently for orders
                response = "**Order Added Successfully**\n\n"
                response += "I've added the following to your order:\n\n"
                
                for item, quantity in added_items:
                    response += f"• {quantity}x {item['name']} — ${item['price'] * quantity:.2f}\n"
                
                response += f"\n**Your current total is ${st.session_state.total_price:.2f}**"
                return response
            
        return "I couldn't identify the menu items you want to order. Could you please try again with the exact item name from our menu?"
    
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
    # Create order summary for the context
    order_items = [
        f"{item.get('quantity', 1)}x {item['name']}" if item.get('quantity', 1) > 1 else item['name']
        for item in st.session_state.order
    ]
    order_str = ", ".join(order_items) if order_items else "None"
    
    # Use centralized menu info preparation
    menu_info = prepare_menu_info()
    
    try:
        # Using the simplified general_conversation function
        response = general_conversation(
            user_message=user_message,
            order_str=order_str,
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