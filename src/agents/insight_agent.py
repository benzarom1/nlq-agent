from pydantic import BaseModel, Field

from src.prompts.insight_prompt import INSIGHT_AGENT_SYSTEM_PROMPT, INSIGHT_AGENT_USER_PROMPT
from src.llm import insight_llm as llm

from src.state import NLQState



class InsightResponse(BaseModel):
    answer: str = Field(
        description="A concise business-friendly answer based on the SQL results."
    )


def insight_agent(state: NLQState) -> dict:
    question = state["messages"][-1].content
    generated_sql = state.get("generated_sql", "")
    query_results = state.get("query_results", [])
    row_count = state.get("row_count", 0)

    insight_llm = llm.with_structured_output(InsightResponse)

    result = insight_llm.invoke([
        {
            "role": "system",
            "content": INSIGHT_AGENT_SYSTEM_PROMPT
            },
            {
    "role": "user",
    "content": INSIGHT_AGENT_USER_PROMPT.format(question = question, generated_sql = generated_sql, query_results = query_results, row_count = row_count)
            }

        ])

    final_answer = f"""
    {result.answer}
    """

    return {
        "final_answer": final_answer
    }