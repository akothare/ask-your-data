from app.db.connection import OracleConnection


class QueryExecutor:
    MAX_ROWS = 100

    @staticmethod
    def enforce_limit(sql: str):

        if "rownum" in sql.lower():
            return sql

        return f"""
        SELECT * FROM (
            {sql}
        ) WHERE ROWNUM <= {QueryExecutor.MAX_ROWS}
        """

    @staticmethod
    def apply_pagination(sql, page, page_size):

        offset = (page - 1) * page_size

        return f"""
        SELECT * FROM (
            SELECT a.*, ROWNUM rnum FROM (
                {sql}
            ) a
            WHERE ROWNUM <= {offset + page_size}
        )
        WHERE rnum > {offset}
        """

    @staticmethod
    def execute(sql, page=1, page_size=50):

        connection = OracleConnection.get_connection()
        cursor = connection.cursor()

        try:
            # Apply limit first (safety)
            limited_sql = QueryExecutor.enforce_limit(sql)

            # Apply pagination
            paginated_sql = QueryExecutor.apply_pagination(
                limited_sql,
                page,
                page_size
            )

            print("EXECUTING SQL:", paginated_sql)

            cursor.execute(paginated_sql)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return result

        finally:
            cursor.close()
            connection.close()
