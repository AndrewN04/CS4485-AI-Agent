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
PREFIX_RE = re.compile(
    r"^(?:(?:i(?:'|’)?d like(?: a)?|i would like|i want)|can i (?:get|have)|give me|may i have)\b",
    re.IGNORECASE
)
QTY_RE = re.compile(r"^(\d+)\s+", re.IGNORECASE)

# Dynamic item‑name matcher
_menu_items = get_all_menu_items()
_item_names = sorted([item["name"] for item in _menu_items], key=len, reverse=True)
ITEM_RE = re.compile(r"\b(" + "|".join(map(re.escape, _item_names)) + r")\b", re.IGNORECASE)


def llm_error_handler(default_return=None, error_message=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e}")
                if error_message:
                    return error_message
                if isinstance(default_return, str):
                    return default_return
                return default_return
        return wrapper
    return decorator


def get_llm():
    key = st.session_state.get("openai_api_key")
    if key:
        return ChatOpenAI(api_key=key, model_name="gpt-4", temperature=0.5)
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return ChatOpenAI(api_key=env_key, model_name="gpt-4", temperature=0.5)
    return None


def get_conversation_memory():
    if "conversation_memory" not in st.session_state:
        st.session_state.conversation_memory = ConversationBufferMemory(memory_key="chat_history")
    return st.session_state.conversation_memory


@llm_error_handler(default_return="general_question")
def classify_intent(user_message):
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
    return chain.invoke({"input": user_message}).content.strip().lower()


@llm_error_handler(default_return=[])
def extract_order_items_from_text(user_message):
    raw = user_message.strip().lower()
    raw = PREFIX_RE.sub("", raw).strip()
    items, seen = [], set()
    for match in ITEM_RE.finditer(raw):
        fragment = match.group(1)
        mi = find_menu_item(fragment)
        if mi and mi["name"] not in seen:
            seen.add(mi["name"])
            prefix = raw[:match.start()]
            m = re.search(r"(\d+)\s*$", prefix)
            qty = int(m.group(1)) if m else 1
            items.append({"name": mi["name"], "quantity": qty})
    return items


@llm_error_handler(default_return=[])
def extract_order_items_using_llm(user_message):
    llm = get_llm()
    if not llm:
        return []
    system = SystemMessagePromptTemplate.from_template("""
        You are a parser for Shake Shack orders.
        Extract ALL menu items and quantities as JSON.
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    raw = chain.invoke({"input": user_message}).content
    try:
        data = json.loads(raw)
        items, seen = [], set()
        for it in data.get("items", []):
            mi = find_menu_item(it.get("name", ""))
            if mi and mi["name"] not in seen:
                seen.add(mi["name"])
                items.append({"name": mi["name"], "quantity": it.get("quantity", 1)})
        return items
    except:
        return []


def extract_order_items(user_message):
    items = extract_order_items_from_text(user_message)
    return items or extract_order_items_using_llm(user_message)


@llm_error_handler(default_return=(False, None, None))
def process_quantity_update(user_message):
    llm = get_llm()
    if not llm:
        return False, None, None
    current = ", ".join([i["name"] for i in st.session_state.order])
    system = SystemMessagePromptTemplate.from_template(f"""
        Current order: {current}
        If updating quantity, return JSON with is_update, item_name, quantity.
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    raw = chain.invoke({"input": user_message}).content
    try:
        res = json.loads(raw)
        return res.get("is_update", False), res.get("item_name"), res.get("quantity")
    except:
        return False, None, None


@llm_error_handler(default_return=None)
def extract_item_to_remove(user_message):
    llm = get_llm()
    if not llm:
        return None
    current = ", ".join([i["name"] for i in st.session_state.order])
    system = SystemMessagePromptTemplate.from_template(f"""
        Current order: {current}
        Extract only the name of the item to remove.
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    return chain.invoke({"input": user_message}).content.strip()


@llm_error_handler(default_return=None)
def extract_price_inquiry_item(user_message):
    # direct lookup
    for it in get_all_menu_items():
        if it["name"].lower() in user_message.lower():
            return it
    llm = get_llm()
    if not llm:
        return None
    system = SystemMessagePromptTemplate.from_template("""
        Extract ONLY the name of the menu item being asked about for price inquiry.
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    name = chain.invoke({"input": user_message}).content.strip()
    return find_menu_item(name)


@llm_error_handler(default_return="I'm having trouble processing your request.")
def general_conversation(user_message, order_str, total_price, menu_info):
    llm = get_llm()
    if not llm:
        return "Please provide your API key."
    system = SystemMessagePromptTemplate.from_template(f"""
        You are a knowledgeable Shake Shack customer support agent.
        Answer only Shake Shack-related questions about the menu, orders, prices, or recommendations, if not related, politely redirect to the customer to ask about one of those options.
        If asked about store hours, locations, nutrition/allergens, catering, contact, or app/rewards,
        provide the appropriate Shake Shack URL:
        - Store hours & locations: https://www.shakeshack.com/locations/
        - Allergies & nutrition: https://www.shakeshack.com/allergies-nutrition/
        - Catering & large orders: https://www.shakeshack.com/catering/
        - Customer service: https://www.shakeshack.com/contact-us/
        - App & rewards program: https://www.shakeshack.com/app/
        Order: {order_str} | Total: ${total_price:.2f}
        Menu Info:
        {menu_info}
    """)
    human = HumanMessagePromptTemplate.from_template("{input}")
    chain = ChatPromptTemplate.from_messages([system, human]) | llm
    return chain.invoke({"input": user_message}).content


@llm_error_handler(default_return="I'm having trouble processing your request.", error_message="Connection issue.")
def process_message(user_message):
    llm = get_llm()
    if not llm:
        return "Please provide your OpenAI API key."
    if "menu" in user_message.lower():
        return display_formatted_menu()

    user_lower = user_message.lower()
    # Recommendation requests
    if any(kw in user_lower for kw in ("recommend", "suggest", "what should i", "best")):
        items = get_all_menu_items()
        burgers = [i for i in items if i["category"].lower() == "burgers"]
        chicken = [i for i in items if "chicken" in i["name"].lower()]
        choices = []
        if chicken:
            choices.append(random.choice(chicken))
        if burgers:
            choices.append(random.choice(burgers))
        rec = random.choice(choices) if choices else random.choice(items)
        return f"I'd recommend our **{rec['name']}** — ${rec['price']:.2f}, about {rec['calories']} cal."

    # Intent-based handling
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
                    resp += f"- {q}x {mi['name']} — ${mi['price']*q:.2f}  \n"
                resp += f"\n**Total: ${st.session_state.total_price:.2f}**"
                return resp
        return "I couldn't identify any items to add. Please use exact menu names."

    if intent == "price_inquiry":
        pi = extract_price_inquiry_item(user_message)
        if pi:
            return f"{pi['name']} costs ${pi['price']:.2f}, {pi['calories']} cal."
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

    # Fallback to general conversation
    order_items = [
        f"{i.get('quantity',1)}x {i['name']}" if i.get('quantity',1)>1 else i['name']
        for i in st.session_state.order
    ]
    order_str = ", ".join(order_items) if order_items else "None"
    menu_info = prepare_menu_info()
    return general_conversation(user_message, order_str, st.session_state.total_price, menu_info)
