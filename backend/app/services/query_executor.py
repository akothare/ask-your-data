from app.db.connection import OracleConnection


class QueryExecutor:
    MAX_ROWS = 100

    @staticmethod
    def apply_limit(sql: str):
        # Wrap query with ROWNUM filter (Oracle)
        return f"""
        SELECT * FROM (
            {sql}
        ) WHERE ROWNUM <= {QueryExecutor.MAX_ROWS}
        """

    @staticmethod
    def execute(sql):
        connection = OracleConnection.get_connection()
        cursor = connection.cursor()

        try:
            limited_sql = QueryExecutor.apply_limit(sql)

            cursor.execute(limited_sql)

            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()

            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))

            return result

        finally:
            cursor.close()
            connection.close()
