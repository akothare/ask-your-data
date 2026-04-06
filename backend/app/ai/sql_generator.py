from app.ai.prompt import build_prompt
from app.ai.client import AIClient
from app.config.settings import settings
import re


def clean_sql_response(response: str):
    response = response.strip()

    if response.startswith("```"):
        response = response.replace("```sql", "").replace("```", "").strip()

    if not response.lower().startswith("select"):
        raise ValueError(f"AI did not return SQL: {response}")

    return response


def normalize_string_comparisons(sql: str):
    pattern = re.compile(r"(\w+)\s*=\s*'([^']+)'", re.IGNORECASE)

    def replacer(match):
        column = match.group(1)
        value = match.group(2).upper()
        return f"UPPER({column}) = '{value}'"

    return pattern.sub(replacer, sql)


def remove_trailing_semicolon(sql: str):
    return sql.rstrip().rstrip(";")


class SQLGenerator:
    @staticmethod
    def generate_sql_only(user_query, schema):

        client = AIClient.get_client()

        prompt = f"""
    Generate ONLY a SQL query based on the user request.

    Rules:
    - DO NOT execute anything
    - DO NOT add explanation
    - Return ONLY SQL
    - Prefer SELECT queries
    - If user asks for UPDATE/DELETE, still generate SQL but DO NOT execute

    Schema:
    {schema}

    User request:
    {user_query}
    """

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        sql = response.choices[0].message.content.strip()

        if sql.startswith("```"):
            sql = sql.replace("```sql", "").replace("```", "").strip()

        return sql

    @staticmethod
    def generate_sql(user_query, schema, previous_sql=None, error_message=None):

        client = AIClient.get_client()

        prompt = build_prompt(user_query, schema)

        # 🔥 NEW: add previous context
        if previous_sql:
            prompt += f"""

Previous SQL:
{previous_sql}

User wants to modify/refine the previous query.
Generate updated SQL.
"""

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

        normalized_sql = normalize_string_comparisons(cleaned_sql)

        final_sql = remove_trailing_semicolon(normalized_sql)

        print("FINAL SQL:", final_sql)

        return final_sql
