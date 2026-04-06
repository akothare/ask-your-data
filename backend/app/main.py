from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from app.ai.sql_generator import SQLGenerator
from app.db.schema_loader import SchemaLoader
from app.services.chart_service import ChartService
from app.services.query_executor import QueryExecutor
from app.services.relationship_explainer import RelationshipExplainer
from app.services.response_formatter import ResponseFormatter
from app.services.schema_selector import SchemaSelector
from app.services.session_store import SessionStore
from app.services.sql_validator import SQLValidator

app = FastAPI()

SCHEMA = SchemaLoader.load_schema()


class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"
    page: int = 1
    page_size: int = 50


def extract_tables_from_query(query: str, schema: dict):
    query = query.lower()
    return [t for t in schema if t.lower() in query]


def is_relationship_query(query: str):
    keywords = ["relationship", "related", "how are", "connection"]
    return any(k in query.lower() for k in keywords)


@app.post("/chat")
def chat(request: QueryRequest):
    user_query = request.query
    session_id = request.session_id
    page = request.page
    page_size = request.page_size

    print("\n--- NEW REQUEST ---")
    print("SESSION:", session_id)

    found_tables = extract_tables_from_query(user_query, SCHEMA)

    # Relationship query
    if is_relationship_query(user_query) and len(found_tables) >= 2:
        explanation = RelationshipExplainer.explain(
            SCHEMA,
            found_tables[0],
            found_tables[1]
        )
        return {"response": {"type": "text", "content": explanation}}

    previous_sql = SessionStore.get_last_query(session_id)

    # 🔥 NEW: schema filtering
    relevant_schema = SchemaSelector.select_relevant_tables(
        user_query,
        SCHEMA
    )

    attempts = 0
    max_attempts = 2
    last_error = None

    while attempts < max_attempts:
        try:
            sql = SQLGenerator.generate_sql(
                user_query,
                relevant_schema,
                previous_sql,
                last_error
            )

            SQLValidator.validate(sql)

            result = QueryExecutor.execute(
                sql,
                page=page,
                page_size=page_size
            )

            # Store last query
            SessionStore.set_last_query(session_id, sql)

            chart = None

            if result and isinstance(result, list) and len(result) > 0:
                chart = ChartService.analyze(result)

            formatted = ResponseFormatter.format(user_query, result)

            return {
                "response": formatted,
                "chart": chart,
                "session_id": session_id
            }

        except Exception as e:
            last_error = str(e)
            print("ERROR:", last_error)
            attempts += 1

    return {
        "error": "Failed to process query",
        "details": last_error
    }
