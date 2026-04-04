from fastapi import FastAPI
from pydantic import BaseModel

from app.db.schema_loader import SchemaLoader
from app.ai.sql_generator import SQLGenerator
from app.services.query_executor import QueryExecutor
from app.services.sql_validator import SQLValidator

app = FastAPI()

SCHEMA = SchemaLoader.load_schema()


class QueryRequest(BaseModel):
    query: str


@app.post("/chat")
def chat(request: QueryRequest):
    user_query = request.query

    attempts = 0
    max_attempts = 2
    last_error = None

    while attempts < max_attempts:
        try:
            # Step 1: Generate SQL
            sql = SQLGenerator.generate_sql(user_query, SCHEMA, last_error)

            # Step 2: Validate SQL
            SQLValidator.validate(sql)

            # Step 3: Execute
            result = QueryExecutor.execute(sql)

            return {
                "data": result,
                "attempts": attempts + 1
            }

        except Exception as e:
            last_error = str(e)
            attempts += 1

    return {
        "error": "Failed to process query",
        "details": last_error
    }
