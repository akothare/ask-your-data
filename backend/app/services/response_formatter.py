from app.ai.client import AIClient
from app.config.settings import settings


class ResponseFormatter:

    @staticmethod
    def format(user_query, data):

        if not data or len(data) == 0:
            return {
                "type": "text",
                "content": "No data found for your query."
            }

        # Small dataset → summary only
        if len(data) <= 5:
            return {
                "type": "text",
                "content": ResponseFormatter.generate_summary(user_query, data)
            }

        # Medium dataset → summary + table
        if len(data) <= 50:
            return {
                "type": "mixed",
                "summary": ResponseFormatter.generate_summary(user_query, data),
                "data": data
            }

        # Large dataset → table only
        return {
            "type": "table",
            "data": data
        }

    @staticmethod
    def generate_summary(user_query, data):

        client = AIClient.get_client()

        prompt = f"""
You are a helpful assistant.

User question:
{user_query}

Data:
{data[:10]}

Generate a short, natural language summary.
Do not mention SQL.
Be concise.
"""

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        return response.choices[0].message.content.strip()
