# Shake Shack Customer Support Chatbot

This project implements a Streamlit‑based AI customer service agent for Shake Shack, powered by OpenAI GPT‑4 via LangChain. Users can inquire about menu items, prices, nutritional information, and manage orders through a chat interface.

---

## 🚀 Features

- **Natural Language Chat**: Ask about menu items, prices, calories, store locations, hours, and more.
- **Order Management**:
  - Place orders by specifying items and quantities.
  - View, update, and remove items in your cart.
  - Checkout to save orders to MongoDB.
- **Dynamic Menu**:
  - Menu loaded from MongoDB, with fallback to a small hardcoded list.
  - Categorized display in chat and sidebar.
- **API Key Handling**:
  - Supports user‑provided OpenAI API key via sidebar input.
  - Falls back to environment `OPENAI_API_KEY` if set.
- **Error Handling & Logging**:
  - Centralized LLM error handler with user‑friendly messages.
  - Comprehensive logging to `shakeshack_agent.log`.
- **Session & Caching**:
  - Streamlit session state for order/cart and menu caching.
  - `st.cache_data` decorator to cache menu queries for 1 hour.

---

## 🏗️ Tech Stack

- **Python 3.8+**
- **Streamlit** for the web UI
- **LangChain** + **OpenAI GPT‑4** for NLP and intent classification
- **MongoDB** (via PyMongo) for order persistence
- **python‑dotenv** for `.env` configuration

---

## 📁 Project Structure

```
├── app.py             # Main entry point: initializes logging, UI, and requirements
├── database.py        # MongoDB connection, menu retrieval, order persistence
├── llm.py             # Intent classification, item extraction, message processing
├── menu.py            # Fuzzy menu lookup & formatted menu display
├── order.py           # Order/cart state management and checkout logic
├── ui.py              # Streamlit UI layout, sidebar, chat history
├── utils.py           # Decorators and helper functions (timing, retry, JSON, etc.)
├── requirements.txt   # Python dependencies
└── .env.example       # Example environment variables (create your own `.env`)
```

---

## ⚙️ Prerequisites

- Python 3.8 or higher
- MongoDB instance (optional: for production persistence)
- OpenAI API key (to call GPT‑4)

---

## 🔧 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/shakeshack-agent.git
   cd shakeshack-agent
   ```

2. **Create & activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # on Linux/macOS
   .\.venv\\Scripts\\activate  # on Windows
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root with:

   ```dotenv
   OPENAI_API_KEY=your_openai_api_key
   MONGODB_URI=mongodb+srv://<user>:<pass>@cluster0.mongodb.net/?retryWrites=true&w=majority
   ```

   Alternatively, configure `MONGODB_URI` in Streamlit's secrets manager when deploying.

---

## 🚀 Running the App

```bash
streamlit run app.py
```

- Open your browser at `http://localhost:8501`.
- Enter your OpenAI API key in the sidebar (unless set in `.env`).
- Start chatting!

---

## 🧩 Code Overview

### `app.py`

- Initializes logging (`shakeshack_agent.log`).
- Loads `.env` variables and writes `requirements.txt` via `update_requirements_file()`.
- Registers `cleanup()` on exit to close DB connections.
- Calls `render_ui()` from `ui.py`.

### `database.py`

- Manages MongoDB connection with `get_mongodb_client()` & `get_db()`.
- Provides:
  - `get_all_menu_items()` (with fallback hardcoded list).
  - `get_menu_by_category(category)`.
  - `save_order(order_data)`.
  - `close_connections()`.
- Uses `st.cache_data` and `st.session_state.menu_cache` for caching.

### `menu.py`

- `find_menu_item(item_name)`: fuzzy‑matches user input to menu items.
- `prepare_menu_info()`: formats menu as text for LLM prompts.
- `display_formatted_menu()`: returns a Markdown string for chat display.

### `order.py`

- Initializes session state: `order`, `total_price`, `update_sidebar`.
- `add_to_order()`, `update_order_quantity()`, `remove_from_order()`, `get_order_summary()`.
- `finalize_order()`: saves to DB and clears session order.
- `clear_order()`.

### `llm.py`

- `get_llm()`: returns a configured `ChatOpenAI` instance (session or env key).
- Intent classification and extraction functions:
  - `classify_intent()`
  - `extract_order_items_from_text()` & `..._using_llm()`
  - `process_quantity_update()`
  - `extract_item_to_remove()`, `extract_price_inquiry_item()`
- `general_conversation()`: fallback LLM handler with menu context and links.
- `process_message()`: orchestrates intent dispatch and calls menu/order/LLM functions.
- Decorator `@llm_error_handler()` wraps LLM calls for robust error handling.

### `ui.py`

- Sets up Streamlit page config and hides default header/footer.
- Sidebar for API key input and live order summary with Clear/Checkout buttons.
- Main chat area with logo, welcome text, and warning for missing API key.
- Chat history synced between Streamlit session and LangChain’s `StreamlitChatMessageHistory`.
- `render_ui()` ties everything together and triggers re-runs when state changes.
- `cleanup()` closes DB on shutdown.

### `utils.py`

- Decorators:
  - `@timeit`: logs execution time.
  - `@retry`: retry on failure with exponential backoff.
- Helpers:
  - `safe_json_loads()`, `create_directory_if_not_exists()`, `normalize_item_name()`.
  - `format_price()`, `format_currency()`, `truncate_text()`.

---

## 📋 Logging & Debugging

- All logs written to `shakeshack_agent.log`.
- Streamlit console also shows logs.
- LLM errors return user‑friendly messages in the chat.

---

## 🔄 Caching & Performance

- Menu data cached for 1 hour via `@st.cache_data(ttl=3600)`.
- Chat history stored in session state and in LangChain's history.

---
