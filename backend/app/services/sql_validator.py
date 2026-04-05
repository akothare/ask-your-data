import re


class SQLValidator:
    FORBIDDEN_KEYWORDS = [
        "insert", "update", "delete", "drop",
        "truncate", "alter", "merge", "grant"
    ]

    @staticmethod
    def validate(sql: str):
        sql_lower = sql.lower()

        # Only SELECT allowed
        if not sql_lower.strip().startswith("select"):
            raise ValueError("Only SELECT queries are allowed")

        # Block dangerous keywords
        for keyword in SQLValidator.FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{keyword}\b", sql_lower):
                raise ValueError(f"Forbidden keyword detected: {keyword}")

        return True
