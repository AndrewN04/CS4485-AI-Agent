import streamlit as st
import logging
from menu import find_menu_item
from database import save_order

logger = logging.getLogger(__name__)

def initialize_order_state():
    """Initialize order-related session state variables."""
    if 'order' not in st.session_state:
        st.session_state.order = []
    
    if 'total_price' not in st.session_state:
        st.session_state.total_price = 0.0
    
    if 'update_sidebar' not in st.session_state:
        st.session_state.update_sidebar = False

def add_to_order(menu_item, quantity=1):
    """
    Adds an item to the order.
    
    Args:
        menu_item: The menu item dictionary to add
        quantity: Quantity to add (default: 1)
        
    Returns:
        Boolean indicating success
    """
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
    
    Args:
        item_name: Name of the item to update
        new_quantity: New quantity to set
        
    Returns:
        Response message confirming the update
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
    """
    Removes an item from the order.
    
    Args:
        item_name: Name of the item to remove
        
    Returns:
        Response message confirming the removal
    """
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

def get_order_summary():
    """
    Generates summary of current order.
    
    Returns:
        Formatted order summary string
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

def clear_order():
    """Clear the current order."""
    st.session_state.order = []
    st.session_state.total_price = 0.0
    st.session_state.update_sidebar = True
    return "Your order has been cleared."

def finalize_order():
    """
    Save the order to database and clear local state.
    
    Returns:
        Order confirmation ID or error message
    """
    if not st.session_state.order:
        return "Cannot finalize an empty order."
    
    order_data = {
        "items": st.session_state.order,
        "total_price": st.session_state.total_price,
        "status": "pending"
    }
    
    order_id = save_order(order_data)
    if order_id:
        # Clear current order after successful save
        clear_order()
        return f"Thank you for your order! Your order ID is: {order_id}"
    else:
        return "Sorry, there was a problem saving your order. Please try again."