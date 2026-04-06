from app.ai.client import AIClient
from app.config.settings import settings


class IntentClassifier:

    @staticmethod
    def classify(user_query: str):

        query = user_query.lower().strip()

        # 🔥 STRICT SQL detection (EXPLICIT ONLY)
        sql_keywords = [
            "give me sql",
            "write sql",
            "generate sql",
            "sql query",
            "write query",
            "generate query"
        ]

        if any(k in query for k in sql_keywords):
            return "sql_generation"

        # 🔹 conversational
        simple_ack = ["ok", "okay", "thanks", "thank you", "cool", "great"]
        if query in simple_ack:
            return "conversational"

        # 🔹 schema hints
        if any(k in query for k in ["schema", "structure", "columns", "table details"]):
            return "schema"

        # 🔹 relationship hints
        if "relationship" in query or "how are" in query:
            return "relationship"

        # 🔥 DEFAULT → DATA
        return "data"
