import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


load_dotenv()

LOW_COST_MODEL = "gpt-4.1-mini"
HIGH_COST_MODEL = "gpt-4.1"
API_KEY = os.getenv("OPENAI_API_KEY")

intent_llm = ChatOpenAI(
    model= LOW_COST_MODEL,
    temperature=0,
    api_key= API_KEY
)

sql_llm = ChatOpenAI(
    model= HIGH_COST_MODEL,
    temperature= 0,
    api_key= API_KEY
)

insight_llm = ChatOpenAI(
    model= HIGH_COST_MODEL,
    temperature= 0.3,
    api_key= API_KEY
)