from app.ai.client import AIClient
from app.config.settings import settings


class IntentClassifier:

    @staticmethod
    def classify(user_query: str):

        query = user_query.lower().strip()

        # 🔥 Step 1: Fast rule-based (cheap)
        if len(query) <= 3:
            return "conversational"

        simple_ack = ["ok", "okay", "thanks", "thank you", "cool", "great"]
        if query in simple_ack:
            return "conversational"

        # 🔥 Step 2: AI-based classification
        client = AIClient.get_client()

        prompt = f"""
Classify the user query into ONE of these categories:

1. conversational → greetings, acknowledgements, casual replies
2. schema → asking about tables, columns, structure
3. relationship → asking how tables are related
4. data → asking for actual data or metrics

User query:
"{user_query}"

Respond with ONLY one word:
conversational OR schema OR relationship OR data
"""

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        intent = response.choices[0].message.content.strip().lower()

        # Safety fallback
        if intent not in ["conversational", "schema", "relationship", "data"]:
            return "data"

        return intent
