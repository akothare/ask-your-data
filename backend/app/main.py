from fastapi import FastAPI
from pydantic import BaseModel

from app.db.schema_loader import SchemaLoader
from app.ai.sql_generator import SQLGenerator
from app.services.query_executor import QueryExecutor
from app.services.sql_validator import SQLValidator
from app.services.relationship_explainer import RelationshipExplainer

app = FastAPI()

# Load schema once
SCHEMA = SchemaLoader.load_schema()


class QueryRequest(BaseModel):
    query: str


# 🔥 NEW: Extract tables robustly
def extract_tables_from_query(query: str, schema: dict):
    query = query.lower()
    matched_tables = []

    for table in schema.keys():
        if table.lower() in query:
            matched_tables.append(table)

    return matched_tables


# 🔥 UPDATED: better detection
def is_relationship_query(query: str):
    keywords = ["relationship", "related", "how are", "connection"]
    return any(k in query.lower() for k in keywords)


@app.post("/chat")
def chat(request: QueryRequest):
    user_query = request.query

    # 🔍 DEBUG (keep for now)
    print("SCHEMA TABLES:", list(SCHEMA.keys()))
    print("USER QUERY:", user_query)

    found_tables = extract_tables_from_query(user_query, SCHEMA)
    print("MATCHED TABLES:", found_tables)

    # ✅ Step 1: Relationship explanation (BEFORE AI)
    if is_relationship_query(user_query) and len(found_tables) >= 2:
        explanation = RelationshipExplainer.explain(
            SCHEMA,
            found_tables[0],
            found_tables[1]
        )
        return {"answer": explanation}

    # ✅ Step 2: SQL flow
    attempts = 0
    max_attempts = 2
    last_error = None

    while attempts < max_attempts:
        try:
            sql = SQLGenerator.generate_sql(user_query, SCHEMA, last_error)

            print("FINAL SQL:", sql)

            SQLValidator.validate(sql)
            result = QueryExecutor.execute(sql)

            return {
                "data": result,
                "attempts": attempts + 1
            }

        except Exception as e:
            last_error = str(e)
            print("ERROR:", last_error)
            attempts += 1

    return {
        "error": "Failed to process query",
        "details": last_error
    }
