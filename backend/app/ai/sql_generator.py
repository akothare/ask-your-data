import re
from app.ai.prompt import build_prompt
from app.ai.client import AIClient
from app.config.settings import settings


class SQLGenerator:

    @staticmethod
    def clean_sql(sql: str) -> str:
        # Remove markdown ```sql ``` blocks
        sql = re.sub(r"```sql|```", "", sql, flags=re.IGNORECASE)

        # Remove extra text before SELECT
        match = re.search(r"(select .*?)$", sql, re.IGNORECASE | re.DOTALL)
        if match:
            sql = match.group(1)

        # Remove trailing semicolon
        sql = sql.strip().rstrip(";")

        return sql.strip()

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

        cleaned_sql = SQLGenerator.clean_sql(raw_sql)

        print("RAW SQL:", raw_sql)
        print("CLEANED SQL:", cleaned_sql)

        return cleaned_sql
