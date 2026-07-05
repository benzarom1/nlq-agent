import duckdb
from pathlib import Path

DB_PATH = Path("data/nba.duckdb")


class DatabaseResource:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    def connect(self):
        return duckdb.connect(str(self.db_path), read_only=True)

    def execute_query(self, sql: str):
        with self.connect() as conn:
            return conn.execute(sql).fetchdf()

    def get_schema(self) -> str:
        with self.connect() as conn:
            tables = conn.execute("SHOW TABLES").fetchall()
            schema_parts = []
            for (table_name,) in tables:
                columns = conn.execute(f"DESCRIBE {table_name}").fetchdf()
                schema_parts.append(f"\nTable: {table_name}")
                for _, row in columns.iterrows():
                    schema_parts.append(f"- {row['column_name']}: {row['column_type']}")
            return "\n".join(schema_parts)