from src.state import NLQState


def error_node(state: NLQState) -> dict:
    validation_error = state.get("validation_error")
    execution_error = state.get("execution_error")
    intent = state.get("intent")

    if validation_error:
        message = f"I could not safely run the SQL query. Reason: {validation_error}"

    elif execution_error:
        message = f"The SQL query was generated, but execution failed. Reason: {execution_error}"

    elif intent == "ambiguous":
        message = "Your question is related to the NBA database, but it needs more detail before I can generate a reliable SQL query."

    elif intent == "unsafe":
        message = "I can only answer read-only analytics questions. I cannot modify or delete database records."

    else:
        message = "I could not complete the request with the available NBA database."

    return {
        "final_answer": message
    }