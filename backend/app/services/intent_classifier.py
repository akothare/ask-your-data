from app.ai.client import AIClient
from app.config.settings import settings


class IntentClassifier:

    @staticmethod
    def classify(user_query: str):

        query = user_query.lower().strip()

        # 🔥 FAST RULES
        if len(query) <= 3:
            return "conversational"

        if any(word in query for word in ["sql", "query", "write query", "generate query"]):
            return "sql_generation"

        simple_ack = ["ok", "okay", "thanks", "thank you", "cool", "great"]
        if query in simple_ack:
            return "conversational"

        # 🔥 AI FALLBACK
        client = AIClient.get_client()

        prompt = f"""
Classify the user query into ONE of these categories:

1. conversational
2. schema
3. relationship
4. data
5. sql_generation

User query:
"{user_query}"

Respond with ONLY one word.
"""

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        intent = response.choices[0].message.content.strip().lower()

        if intent not in ["conversational", "schema", "relationship", "data", "sql_generation"]:
            return "data"

        return intent
