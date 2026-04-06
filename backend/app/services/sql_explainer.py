import re


class SQLExplainer:

    @staticmethod
    def explain(sql: str):

        explanation = []

        sql_upper = sql.upper()

        # 🔹 TABLES
        tables = re.findall(r'FROM\s+(\w+)', sql_upper)
        joins = re.findall(r'JOIN\s+(\w+)', sql_upper)

        all_tables = list(set(tables + joins))

        if all_tables:
            explanation.append(f"Used table(s): {', '.join(all_tables)}")

        # 🔹 JOINS
        if joins:
            explanation.append(f"Joined with: {', '.join(set(joins))}")

        # 🔹 WHERE
        where_match = re.search(r'WHERE\s+(.*)', sql_upper)
        if where_match:
            where_clause = where_match.group(1)
            where_clause = re.split(r'ORDER BY|GROUP BY', where_clause)[0]
            explanation.append(f"Applied filters: {where_clause.strip()}")

        # 🔹 ORDER BY
        order_match = re.search(r'ORDER BY\s+(.*)', sql_upper)
        if order_match:
            explanation.append(f"Sorted by: {order_match.group(1).strip()}")

        # 🔹 AGGREGATION
        if any(func in sql_upper for func in ["COUNT(", "SUM(", "AVG(", "MIN(", "MAX("]):
            explanation.append("Performed aggregations")

        # 🔹 LIMIT
        if "ROWNUM" in sql_upper:
            explanation.append("Limited rows for performance")

        return explanation
