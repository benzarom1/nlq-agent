from typing import Literal

from pydantic import BaseModel, Field

from src.prompts.intent_prompt import INTENT_AGENT_SYSTEM_PROMPT
from src.llm import intent_llm as llm
from src.state import IntentClassification, NLQState




def intent_agent(state: NLQState):
    messages = state.get("messages", [])

    if messages:
        user_content = messages[-1].content
    else:
        user_content = state.get("question")

    if not user_content:
        return {
            "intent": "unsupported_query",
            "intent_reason": "No user message or question was provided."
        }

    classifier_llm = llm.with_structured_output(IntentClassification)

    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": INTENT_AGENT_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_content
        }
    ])

    return {
        "intent": result.intent,
        "intent_reason": result.reason
    }