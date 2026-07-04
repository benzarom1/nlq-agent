def non_database_response_node(state):
    intent = state["intent"]

    if intent == "general_conversation":
        final_answer = "Hi! I can answer questions about NBA games, attendance, and player statistics."

    elif intent == "unsafe_query":
        final_answer = "This app only supports read-only analytical questions."

    elif intent == "ambiguous_query":
        final_answer = "Your question is related to the NBA database, but it needs more detail before I can generate a reliable SQL query."

    elif intent == "unsupported_query":
        final_answer = "I can only answer questions about the NBA database available in this application."

    else:
        final_answer = "I could not classify your request."

    return {"final_answer": final_answer}