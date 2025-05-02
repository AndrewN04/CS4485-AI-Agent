import os
import json
import re
import random
import functools
import logging
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.memory import ConversationBufferMemory
from menu import find_menu_item, display_formatted_menu, prepare_menu_info
from order import update_order_quantity, remove_from_order, get_order_summary, add_to_order
from database import get_all_menu_items

logger = logging.getLogger(__name__)

# ——————————— Pre‑compiled Regex Patterns ———————————
# Strip leading “I’d like…”, “Can I get…”, etc. (handles both ’ and ')
PREFIX_RE = re.compile(
    r"^(?:(?:i(?:'|’)?d like(?: a)?|i would like|i want)|can i (?:get|have)|give me|may i have)\b",
    re.IGNORECASE
)
# Pull off a leading integer quantity
QTY_RE = re.compile(r"^(\d+)\s+", re.IGNORECASE)

# Dynamic item‑name matcher built from the current menu
_menu_items = get_all_menu_items()
_item_names = sorted([item["name"] for item in _menu_items], key=len, reverse=True)
ITEM_RE = re.compile(r"\b(" + "|".join(map(re.escape, _item_names)) + r")\b", re.IGNORECASE)


def llm_error_handler(default_return=None, error_message=None):
    """Decorator for handling LLM chain errors consistently."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {type(e).__name__} - {e}")
                msg = str(e)
                if "Unauthorized" in msg:
                    return "There seems to be an issue with the API key. Please check that it's valid."
                if "Connection" in msg or "Timeout" in msg:
                    return "I'm having trouble connecting to the language model. Please check your connection and try again."
                if error_message:
                    return error_message
                if isinstance(default_return, str):
                    return f"I'm having trouble processing your request. {default_return}"
                return default_return
        return wrapper
    return decorator


def get_llm():
    """Return a ChatOpenAI instance, preferring session‑state key over environment."""
    key = st.session_state.get("openai_api_key")
    if key:
        return ChatOpenAI(api_key=key, model_name="gpt-4", temperature=0.5)
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return ChatOpenAI(api_key=env_key, model_name="gpt-4", temperature=0.5)
    return None


def get_conversation_memory():
    """Get or create a ConversationBufferMemory in session state."""
    if "conversation_memory" not in st.session_state:
        st.session_state.conversation_memory = ConversationBufferMemory(memory_key="chat_history")
    return st.session_state.conversation_memory


@llm_error_handler(default_return="general_question")
def classify_intent(user_message):
    """Classify user intent via LLM into one of our known intents."""
    llm = get_llm()
    if not llm:
        return "general_question"
    system = SystemMessagePromptTemplate.from_template("""
        Classify the user's message into ONE of:
        - cart_inquiry
        - order_placement
        - quantity_update
        - price_inquiry
        - remove_item
        - general_question
        Return ONLY the intent label.
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    intent = chain.invoke({"input": user_message}).content.strip().lower()
    logger.info(f"Intent: {intent}")
    return intent


@llm_error_handler(default_return=[])
def extract_order_items_from_text(user_message):
    """
    Text‑based extraction using dynamic ITEM_RE:
      1) Strip ordering prefixes.
      2) Find all menu‑name matches.
      3) For each, pull an integer immediately to its left (if any).
    """
    raw = user_message.strip().lower()
    raw = PREFIX_RE.sub("", raw).strip()

    items = []
    seen = set()
    for match in ITEM_RE.finditer(raw):
        fragment = match.group(1)
        menu_item = find_menu_item(fragment)
        if not menu_item or menu_item["name"] in seen:
            continue
        seen.add(menu_item["name"])
        prefix = raw[: match.start()]
        m = re.search(r"(\d+)\s*$", prefix)
        qty = int(m.group(1)) if m else 1
        items.append({"name": menu_item["name"], "quantity": qty})

    return items


@llm_error_handler(default_return=[])
def extract_order_items_using_llm(user_message):
    """LLM‑based fallback extraction (returns list of {"name","quantity"})."""
    llm = get_llm()
    if not llm:
        return []
    system = SystemMessagePromptTemplate.from_template("""
        You are a parser for Shake Shack orders.
        Extract ALL menu items with their quantities.
        Respond ONLY as JSON: {"items":[{"name":"ShackBurger","quantity":2},...]}
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    raw = chain.invoke({"input": user_message}).content.strip()
    raw = raw.replace("```json", "").replace("```", "")
    try:
        data = json.loads(raw)
        result, seen = [], set()
        for it in data.get("items", []):
            mi = find_menu_item(it.get("name", ""))
            if mi and mi["name"] not in seen:
                seen.add(mi["name"])
                result.append({"name": mi["name"], "quantity": it.get("quantity", 1)})
        return result
    except Exception as e:
        logger.error(f"Failed LLM extraction JSON parse: {e}")
        return []


def extract_order_items(user_message):
    """Combined extractor: try text‑based first, then LLM fallback."""
    items = extract_order_items_from_text(user_message)
    return items or extract_order_items_using_llm(user_message)


@llm_error_handler(default_return=(False, None, None))
def process_quantity_update(user_message):
    """LLM‑driven quantity‑update detection (returns is_update, name, qty)."""
    llm = get_llm()
    if not llm:
        return False, None, None
    current = ", ".join([i["name"] for i in st.session_state.order])
    system = SystemMessagePromptTemplate.from_template(f"""
        Current order items: {current}
        If updating quantity, return JSON:
        {{"is_update": true, "item_name":"Name", "quantity":2}}
        Else: {{"is_update": false, "item_name": null, "quantity": null}}
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    raw = chain.invoke({"input": user_message}).content.strip()
    raw = raw.replace("```json", "").replace("```", "")
    try:
        result = json.loads(raw)
        return result.get("is_update", False), result.get("item_name"), result.get("quantity")
    except Exception as e:
        logger.error(f"Qty update JSON parse error: {e}")
        return False, None, None


@llm_error_handler(default_return=None)
def extract_item_to_remove(user_message):
    """LLM‑based extraction of a single item name to remove."""
    llm = get_llm()
    if not llm:
        return None
    current = ", ".join([i["name"] for i in st.session_state.order])
    system = SystemMessagePromptTemplate.from_template(f"""
        Current order items: {current}
        Extract ONLY the name of the item to remove.
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    return chain.invoke({"input": user_message}).content.strip()


@llm_error_handler(default_return=None)
def extract_price_inquiry_item(user_message):
    """Extract menu item for a price inquiry, direct or via LLM fallback."""
    for it in get_all_menu_items():
        if it["name"].lower() in user_message.lower():
            return it
    llm = get_llm()
    if not llm:
        return None
    system = SystemMessagePromptTemplate.from_template("""
        Extract ONLY the name of the menu item whose price is asked.
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    name = chain.invoke({"input": user_message}).content.strip()
    return find_menu_item(name)


@llm_error_handler(default_return="I'm having trouble processing your request. Please try again.")
def general_conversation(user_message, order_str, total_price, menu_info):
    """Handle general Shake Shack Q&A via LLM prompts."""
    llm = get_llm()
    if not llm:
        return "Please provide your OpenAI API key in the sidebar."
    system = SystemMessagePromptTemplate.from_template(f"""
        You are a knowledgeable Shake Shack customer support agent.
        You only answer questions related to Shake Shack menu, orders, prices, ingredients, or recommendations.
        If a user asks something unrelated to Shake Shack, politely redirect them: "I'm here to help with Shake Shack-related questions—menu, orders, and recommendations. Please ask me something related to Shake Shack."
        Order: {order_str} | Total: ${total_price:.2f}
        Menu Info:
        {menu_info}
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    return chain.invoke({"input": user_message}).content


@llm_error_handler(default_return="I'm having trouble processing your request. Please try again.",
                   error_message="I'm having trouble connecting to our systems. Please try again in a moment.")
def process_message(user_message):
    """Main routing for user messages to specific handlers or custom logic."""
    llm = get_llm()
    if not llm:
        return "Please provide your OpenAI API key in the sidebar."
    if "menu" in user_message.lower():
        return display_formatted_menu()

    # Pre‑intent overrides
    user_lower = user_message.lower()
    # Recommendation requests
    if any(kw in user_lower for kw in ("recommend", "suggest", "what should i", "what's good", "best")):
        items = get_all_menu_items()
        burgers = [i for i in items if i["category"].lower() == "burgers"]
        chicken = [i for i in items if "chicken" in i["name"].lower()]
        choices = []
        if chicken: choices.append(random.choice(chicken))
        if burgers: choices.append(random.choice(burgers))
        if not choices: choices = items
        rec = random.choice(choices)
        return f"I'd recommend our **{rec['name']}** — priced at ${rec['price']:.2f} with about {rec['calories']} calories. It's one of our popular {rec['category']}!"
    # Ingredient info requests
    if any(kw in user_lower for kw in ("ingredient", "ingredients", "contain", "contains", "allergen")):
        items = get_all_menu_items()
        mi = next((i for i in items if i["name"].lower() in user_lower), None)
        if mi:
            if "ingredients" in mi:
                return f"The {mi['name']} contains: {', '.join(mi['ingredients'])}."
            else:
                return f"Sorry, I don't have detailed ingredient info for **{mi['name']}**, but it's made fresh with high-quality ingredients."
        return "Which Shake Shack item would you like ingredient information for?"

    # Intent‑based handling
    intent = classify_intent(user_message)
    logger.info(f"Intent: {intent}")

    if intent == "cart_inquiry":
        return get_order_summary()

    if intent == "quantity_update":
        is_upd, name, qty = process_quantity_update(user_message)
        if is_upd and qty is not None:
            if name:
                return update_order_quantity(name, qty)
            if len(st.session_state.order) == 1:
                return update_order_quantity(st.session_state.order[0]["name"], qty)
        return "I couldn't identify which item to update. Please specify."

    if intent == "order_placement":
        extracted = extract_order_items(user_message)
        if extracted:
            added = []
            for it in extracted:
                mi = find_menu_item(it["name"])
                if mi:
                    add_to_order(mi, it["quantity"])
                    added.append((mi, it["quantity"]))
            if added:
                st.session_state.update_sidebar = True
                resp = "**Order Added Successfully**\n\nI've added:\n"
                for mi, q in added:
                    resp += f"- {q}x {mi['name']} — ${mi['price'] * q:.2f}  \n"
                resp += f"\n**Your current total is ${st.session_state.total_price:.2f}**"
                return resp
        return "I couldn't identify any items to add. Please use exact menu names."

    if intent == "price_inquiry":
        pi = extract_price_inquiry_item(user_message)
        if pi:
            return f"{pi['name']} costs ${pi['price']:.2f}, {pi['calories']} calories."
        return "Which item price would you like to know?"

    if intent == "remove_item":
        items_to_remove = extract_order_items(user_message)
        responses = []
        for it in items_to_remove:
            name, qty = it["name"], it["quantity"]
            current = next((i for i in st.session_state.order if i["name"] == name), None)
            if current:
                if qty < current["quantity"]:
                    new_qty = current["quantity"] - qty
                    responses.append(update_order_quantity(name, new_qty))
                else:
                    responses.append(remove_from_order(name))
        return "\n\n".join(responses) if responses else "I couldn't find those items in your order."

    # Fallback: direct shack‑related general questions, else redirect
    order_items = [
        f"{i.get('quantity',1)}x {i['name']}" if i.get('quantity',1) > 1 else i['name']
        for i in st.session_state.order
    ]
    order_str = ", ".join(order_items) if order_items else "None"
    menu_info = prepare_menu_info()
    if ITEM_RE.search(user_lower):
        return general_conversation(user_message, order_str, st.session_state.total_price, menu_info)
    return "I'm here to help with Shake Shack-related questions—menu, orders, ingredients, and recommendations. How can I assist you?"
