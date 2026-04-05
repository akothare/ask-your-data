from fastapi import FastAPI
from pydantic import BaseModel

from app.db.schema_loader import SchemaLoader
from app.ai.sql_generator import SQLGenerator
from app.services.query_executor import QueryExecutor
from app.services.sql_validator import SQLValidator
from app.services.relationship_explainer import RelationshipExplainer
from app.services.session_store import SessionStore

app = FastAPI()

SCHEMA = SchemaLoader.load_schema()


class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"   # 🔥 NEW


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

    print("\n--- NEW REQUEST ---")
    print("SESSION:", session_id)

    found_tables = extract_tables_from_query(user_query, SCHEMA)

    # ✅ Relationship handling
    if is_relationship_query(user_query) and len(found_tables) >= 2:
        explanation = RelationshipExplainer.explain(
            SCHEMA,
            found_tables[0],
            found_tables[1]
        )
        return {"answer": explanation}

    previous_sql = SessionStore.get_last_query(session_id)
    print("PREVIOUS SQL:", previous_sql)

    attempts = 0
    max_attempts = 2
    last_error = None

    while attempts < max_attempts:
        try:
            sql = SQLGenerator.generate_sql(
                user_query,
                SCHEMA,
                previous_sql,
                last_error
            )

            SQLValidator.validate(sql)

            result = QueryExecutor.execute(sql)

            # 🔥 Store for next turn
            SessionStore.set_last_query(session_id, sql)

            return {
                "data": result,
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