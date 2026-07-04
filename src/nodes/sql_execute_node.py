# src/nodes/execution_node.py

from src.state import NLQState
from src.database import DatabaseResource


db = DatabaseResource()


def execution_node(state: NLQState) -> dict:
    sql = state.get("generated_sql")

    if not sql:
        return {
            "query_results": [],
            "row_count": 0,
            "execution_error": "No SQL query was provided.",
        }

    if state.get("is_valid_sql") is False:
        return {
            "query_results": [],
            "row_count": 0,
            "execution_error": state.get(
                "validation_error",
                "SQL validation failed."
            ),
        }

    try:
        results_df = db.execute_query(sql)

        results = results_df.to_dict(
            orient="records"
        )

        return {
            "query_results": results,
            "row_count": len(results),
            "execution_error": None,
        }

    except Exception as e:
        return {
            "query_results": [],
            "row_count": 0,
            "execution_error": str(e),
        }