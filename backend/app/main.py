from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

from app.db.schema_loader import SchemaLoader
from app.ai.sql_generator import SQLGenerator
from app.services.query_executor import QueryExecutor
from app.services.sql_validator import SQLValidator
from app.services.relationship_explainer import RelationshipExplainer
from app.services.session_store import SessionStore
from app.services.chart_service import ChartService
from app.services.response_formatter import ResponseFormatter
from app.services.schema_selector import SchemaSelector
from app.services.schema_explainer import SchemaExplainer
from app.services.intent_classifier import IntentClassifier

# 🔥 NEW IMPORTS
from app.services.sql_explainer import SQLExplainer
from app.services.explanation_builder import ExplanationBuilder

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SCHEMA = SchemaLoader.load_schema()


class QueryRequest(BaseModel):
    query: str
    session_id: str = "default"
    page: int = 1
    page_size: int = 50


def extract_tables_from_query(query: str, schema: dict):
    query = query.lower()
    return [t for t in schema if t.lower() in query]


@app.post("/chat")
def chat(request: QueryRequest):
    user_query = request.query
    session_id = request.session_id

    print("\n--- NEW REQUEST ---")
    print("SESSION:", session_id)

    intent = IntentClassifier.classify(user_query)
    print("INTENT:", intent)

    # =========================================================
    # 🔹 SQL GENERATION ONLY
    # =========================================================
    if intent == "sql_generation":
        relevant_schema = SchemaSelector.select_relevant_tables(
            user_query,
            SCHEMA
        )

        sql = SQLGenerator.generate_sql_only(
            user_query,
            relevant_schema
        )

        return {
            "response": {
                "type": "sql",
                "text": "Here is the SQL query:",
                "sql": sql
            }
        }

    # =========================================================
    # 🔹 SCHEMA
    # =========================================================
    if intent == "schema":
        found_tables = extract_tables_from_query(user_query, SCHEMA)
        table = found_tables[0] if found_tables else None

        explanation = SchemaExplainer.explain(SCHEMA, table)

        return {
            "response": {
                "type": "text",
                "content": explanation
            }
        }

    # =========================================================
    # 🔹 RELATIONSHIP
    # =========================================================
    if intent == "relationship":

        found_tables = extract_tables_from_query(user_query, SCHEMA)

        if len(found_tables) >= 2:
            explanation = RelationshipExplainer.explain(
                SCHEMA,
                found_tables[0],
                found_tables[1]
            )

            return {
                "response": {
                    "type": "text",
                    "content": explanation
                }
            }

    # =========================================================
    # 🔹 CONVERSATIONAL
    # =========================================================
    if intent == "conversational":
        return {
            "response": {
                "type": "text",
                "content": "Glad that helped! Let me know if you need anything else."
            }
        }

    # =========================================================
    # 🔹 DATA QUERY + EXPLANATION
    # =========================================================

    previous_sql = SessionStore.get_last_query(session_id)

    relevant_schema = SchemaSelector.select_relevant_tables(
        user_query,
        SCHEMA
    )

    sql = SQLGenerator.generate_sql(
        user_query,
        relevant_schema,
        previous_sql,
        None
    )

    SQLValidator.validate(sql)

    result = QueryExecutor.execute(sql)

    SessionStore.set_last_query(session_id, sql)

    chart = None
    if result and isinstance(result, list) and len(result) > 0:
        chart = ChartService.analyze(result)

    formatted = ResponseFormatter.format(user_query, result)

    # 🔥 EXPLANATION
    steps = SQLExplainer.explain(sql)

    if formatted["type"] == "text":
        explanation_text = ExplanationBuilder.build(
            formatted.get("content"),
            steps
        )
    else:
        explanation_text = ExplanationBuilder.build(
            formatted.get("summary"),
            steps
        )

    return {
        "response": {
            "type": formatted["type"],
            "content": formatted.get("data"),
            "summary": explanation_text,
            "text": explanation_text
        },
        "chart": chart,
        "session_id": session_id
    }
