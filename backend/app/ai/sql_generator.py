import re

from app.ai.prompt import build_prompt
from app.ai.client import AIClient
from app.config.settings import settings


def clean_sql_response(response: str):
    response = response.strip()

    # Remove markdown formatting if present
    if response.startswith("```"):
        response = response.replace("```sql", "").replace("```", "").strip()

    # Reject non-SQL responses
    if not response.lower().startswith("select"):
        raise ValueError(f"AI did not return SQL: {response}")

    return response


class SQLGenerator:

    @staticmethod
    def generate_sql(user_query, schema, error_message=None):
        client = AIClient.get_client()

        prompt = build_prompt(user_query, schema)

        if error_message:
            prompt += f"""

Previous query failed with error:
{error_message}

Fix the SQL query.
"""

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        raw_sql = response.choices[0].message.content.strip()

        print("RAW SQL:", raw_sql)

        cleaned_sql = clean_sql_response(raw_sql)

        print("CLEANED SQL:", cleaned_sql)

        normalized_sql = normalize_string_comparisons(cleaned_sql)

        print("NORMALIZED SQL:", normalized_sql)

        return normalized_sql


def normalize_string_comparisons(sql: str):
    # Convert: column = 'value' → UPPER(column) = 'VALUE'
    pattern = re.compile(r"(\w+)\s*=\s*'([^']+)'", re.IGNORECASE)

    def replacer(match):
        column = match.group(1)
        value = match.group(2).upper()
        return f"UPPER({column}) = '{value}'"

    return pattern.sub(replacer, sql)
