from typing import Annotated, Any, Literal, Optional, TypedDict

from langgraph.graph import add_messages
from langchain_core.messages import BaseMessage

from pydantic import BaseModel, Field

class IntentClassification(BaseModel):
    intent: Literal[
        "database_query",
        "general_conversation",
        "unsupported_query",
        "ambiguous_query",
        "unsafe_query",
    ] = Field(description="The classified intent of the user message.")

    reason: str = Field(description="Brief explanation for the classification.")

class NLQState(TypedDict, total=False):
    # User input
    question: str
    messages: Annotated[list[BaseMessage], add_messages]

    # Intent routing
    intent: Literal[
        "database_query",
        "general_conversation",
        "unsupported_query",
        "ambiguous_query",
        "unsafe_query",
    ]
    intent_reason: Optional[str]

    # Schema / SQL generation
    schema_context: Optional[str]
    generated_sql: Optional[str]
    sql_reasoning: Optional[str]

    # Validation
    is_valid_sql: Optional[bool]
    validation_error: Optional[str]
    retry_count: int

    # Execution
    query_results: Optional[list[dict[str, Any]]]
    row_count: Optional[int]
    execution_error: Optional[str]

    # Final response
    final_answer: Optional[str]