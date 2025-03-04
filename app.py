import streamlit as st
from pathlib import Path
from langchain.llms.openai import OpenAI
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine, inspect
import sqlite3
from langchain.prompts import PromptTemplate
import re

st.set_page_config(page_title="Shake Shack AI Customer Agent", page_icon="🍔")

st.markdown(
    """
    <style>
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

logo_path = Path(__file__).parent / "assets" / "Shake-Shack-Logo.png"
st.image(str(logo_path), use_container_width=True)

LOCALDB = "USE_LOCALDB"
# Always use local database
db_uri = LOCALDB

openai_api_key = st.sidebar.text_input(
    label="OpenAI API Key",
    type="password",
)

st.sidebar.markdown("### Frameworks in Use")
st.sidebar.markdown("- [Streamlit Frontend Framework](https://docs.streamlit.io/)")
st.sidebar.markdown("- [LangChain App Framework](https://python.langchain.com/docs/introduction/)")
st.sidebar.markdown("- [OpenAI LLM Model](https://platform.openai.com/docs/)")

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.")
    st.stop()

# Setup the LLM agent
llm = OpenAI(openai_api_key=openai_api_key, temperature=0, streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri):
    if db_uri == LOCALDB:
        db_filepath = (Path(__file__).parent / "shakeshack.db").absolute()
        creator = lambda: sqlite3.connect(f"file:{db_filepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    return SQLDatabase.from_uri(database_uri=db_uri)

db = configure_db(db_uri)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

custom_template = """
You are a helpful SQL expert. Always provide your answers in clear, complete sentences.
When generating SQL queries or explanations, please ensure your response is detailed and uses full sentences.
User Query: {input}
"""
custom_prompt = PromptTemplate(template=custom_template, input_variables=["input"])

agent = create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    agent_kwargs={"prompt": custom_prompt}
)

if "messages" not in st.session_state or st.sidebar.button("Clear message history"):
    inspector = inspect(db._engine)
    table_names = inspector.get_table_names()
    menu = "\n".join([f"- {table}" for table in table_names])
    welcome_message = f"Welcome! Take a look at the Shake Shack Menu!\n{menu}"
    st.session_state["messages"] = [{"role": "assistant", "content": welcome_message}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query = st.chat_input(placeholder="Ask me anything!")

def clean_text(text):
    return re.sub(r"[,(){}\[\]]", "", text).strip()

if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container())
        response = agent.run(user_query, callbacks=[st_cb])
        st.session_state.messages.append({"role": "assistant", "content": response})

        if "\n" in response:
            items = response.splitlines()
        else:
            items = response.split(')')

        clean_items = [item for item in [clean_text(it) for it in items] if item]
        list_output = "\n".join([f"- {item}" for item in clean_items])
        st.markdown(list_output)