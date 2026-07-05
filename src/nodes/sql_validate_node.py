
from src.state import NLQState

INVALID_OPERATIONS = [
    "INSERT",
    "UPDATE",
    "DELETE",
    "ALTER",
    "DROP",
    "CREATE",
    "TRUNCATE",
]
def validation_node(state: NLQState) -> dict:
    sql = state.get("generated_sql")

    if not sql:
        return {
            "is_valid_sql": False,
            "validation_error": "No SQL query was provided.",
        }

    normalized_sql = sql.strip().upper()

    if not (
        normalized_sql.startswith("SELECT")
        or normalized_sql.startswith("WITH")
    ):
        return {
            "is_valid_sql": False,
            "validation_error": "Only read-only queries are allowed.",
        }

    for operation in INVALID_OPERATIONS:
        if operation in normalized_sql:
            return {
                "is_valid_sql": False,
                "validation_error": f"Generated SQL contains invalid operation: {operation}",
            }
    
    if ";" in normalized_sql.rstrip(";"):
        return {
            "is_valid_sql": False,
            "validation_error": "Multiple SQL statements are not allowed.",
        }
    return {
        "is_valid_sql": True,
        "validation_error": None,
    }
    
    
