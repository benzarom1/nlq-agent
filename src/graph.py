from langgraph.graph import END, START, StateGraph

from src.agents.insight_agent import insight_agent
from src.agents.intent_agent import intent_agent
from src.agents.sql_agent import sql_agent
from src.nodes.non_database_response_node import non_database_response_node
from src.nodes.error_node import error_node
from src.nodes.sql_execute_node import execution_node
from src.nodes.sql_validate_node import validation_node

from src.state import NLQState


def _route_after_intent(state: NLQState):

    intent = state.get('intent')
    if intent == "database_query":
        return "sql_generate"
    else: 
        return "non_database_response"

def _route_after_validate(state: NLQState):

    is_valid_sql = state.get('is_valid_sql')
    if is_valid_sql:
        return "sql_execute"
    else:
        return "error"
    
def _route_after_execute(state: NLQState):

    execution_error = state.get('execution_error')
    if not execution_error:
        return "insight"
    else: 
        return "error"

def build_graph():
    graph = StateGraph(NLQState)

    graph.add_node("intent", intent_agent)
    graph.add_node("sql_generate", sql_agent)
    graph.add_node("insight", insight_agent)

    graph.add_node("non_database_response", non_database_response_node)
    graph.add_node("sql_execute", execution_node)
    graph.add_node("sql_validate", validation_node)
    graph.add_node("error", error_node)



    graph.set_entry_point("intent")

    graph.add_conditional_edges("intent", _route_after_intent, {
        "sql_generate",
        "non_database_response"
    })
    graph.add_edge("sql_generate","sql_validate")

    graph.add_conditional_edges("sql_validate", _route_after_validate,{"sql_execute", "error"})

    graph.add_conditional_edges(
        "sql_execute",
        _route_after_execute,
        {
            "insight": "insight",
            "error": "error",
        }
    )
    graph.add_edge("insight", END)
    graph.add_edge("non_database_response", END)
    graph.add_edge("error", END)

    return graph.compile()









