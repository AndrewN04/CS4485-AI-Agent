import streamlit as st
import os
import logging
from langchain_community.chat_message_histories import StreamlitChatMessageHistory

# Setup logging
logger = logging.getLogger(__name__)

# UI Initialization
def initialize_ui():
    """Initialize the UI components and styles."""
    # Set page title and icon
    st.set_page_config(page_title="Shake Shack Customer Support", page_icon="🍔")

    # Hide default header/footer
    st.markdown(
        """<style>header {visibility: hidden;} footer {visibility: hidden;}</style>""",
        unsafe_allow_html=True
    )

# Sidebar Components
def setup_sidebar():
    """Set up the sidebar with API key input and order summary."""
    # Import here to avoid circular imports
    from order import clear_order
    
    # --- Sidebar: API Key Input ---
    st.sidebar.header("OpenAI API Key")
    
    # Check if we have an environment API key
    has_env_key = bool(os.getenv("OPENAI_API_KEY"))
    
    # API key input text
    api_key_label = "Enter your OpenAI API Key (ENV Key found)" if has_env_key else "Enter your OpenAI API Key"
    
    # API key input widget
    api_key_input = st.sidebar.text_input(api_key_label, type="password")
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
        
        # Add checkout button
        col1, col2 = st.sidebar.columns(2)
        with col1:
            if st.button("Clear Order"):
                clear_order()
                st.rerun()
        with col2:
            if st.button("Checkout"):
                from order import finalize_order
                result = finalize_order()
                st.session_state.last_response = result
                st.rerun()
    else:
        st.sidebar.write("Your order is empty.")

# Main Content Components
def setup_main_content():
    """Set up the main content area with chat interface."""
    # Use simple path for logo
    try:
        st.image("assets/Shake-Shack-Logo.png")
    except:
        # Fallback if logo isn't available
        st.title("Shake Shack Customer Support")
        
    st.write("Welcome to Shake Shack! Ask me about our menu, place an order, or get help with anything Shake Shack related.")

    # API key warning (only if no key is available anywhere)
    if not os.getenv("OPENAI_API_KEY") and not st.session_state.get("openai_api_key"):
        st.warning("⚠️ Please enter your OpenAI API key in the sidebar to use the chat functionality.")

# Chat History Management
def initialize_chat_history():
    """Initialize and synchronize chat history."""
    # Initialize chat history if not already done
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
        
    # Initialize last_response if not already done
    if "last_response" not in st.session_state:
        st.session_state.last_response = None
        
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
        
    return msgs

def display_chat_history():
    """Display the chat history."""
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
            msgs = StreamlitChatMessageHistory(key="langchain_messages")
            msgs.add_ai_message(response)
        
        with st.chat_message("assistant"):
            st.markdown(response)

def handle_user_input(msgs):
    """Handle user input and process messages."""
    # Import here to avoid circular imports
    from llm import process_message
    
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

# Quick actions have been removed as they are not necessary

# Main UI function
def render_ui():
    """Main function to render the complete UI."""
    # Initialize UI components
    initialize_ui()
    
    # Initialize order state (imported here to avoid circular imports)
    from order import initialize_order_state
    initialize_order_state()
    
    # Setup sidebar
    setup_sidebar()
    
    # Setup main content area
    setup_main_content()
    
    # Initialize and display chat history
    msgs = initialize_chat_history()
    display_chat_history()
    
    # Handle user input
    handle_user_input(msgs)
    
    # Check if sidebar needs updating and rerun if needed
    if st.session_state.get('update_sidebar', False):
        st.session_state.update_sidebar = False
        st.rerun()

# Cleanup function to be called on app shutdown
def cleanup():
    """Clean up resources when the app shuts down."""
    # Import here to avoid circular imports
    from database import close_connections
    
    # Close database connections
    close_connections()
    
    logger.info("Application shutting down, resources cleaned up")