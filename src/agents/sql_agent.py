from pydantic import BaseModel, Field

from src.database import DatabaseResource
from src.state import NLQState
from src.llm import sql_llm as llm
from src.prompts.sql_prompt import SQL_AGENT_SYSTEM_PROMPT


class SQLGeneration(BaseModel):
    sql: str = Field(description="DuckDB-compatible SELECT SQL query.")
    reasoning: str = Field(description="Brief reason for the SQL structure.")


def sql_agent(state: NLQState) -> dict:
    

    database = DatabaseResource()

    question = state["messages"][-1].content
    schema_context = database.get_schema()

    sql_llm = llm.with_structured_output(SQLGeneration)

    result = sql_llm.invoke([
        {
            "role": "system",
            "content": SQL_AGENT_SYSTEM_PROMPT.format(schema_context = schema_context)},
        {
            "role": "user",
            "content": question
        }
    ])

    return {
        "schema_context": schema_context,
        "generated_sql": result.sql,
        "sql_reasoning": result.reasoning,
    }