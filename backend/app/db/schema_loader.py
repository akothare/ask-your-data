from app.db.connection import OracleConnection


class SchemaLoader:

    @staticmethod
    def load_schema():
        connection = OracleConnection.get_connection()
        cursor = connection.cursor()

        schema = {}

        # Get tables
        # For production
        cursor.execute("""
            SELECT table_name
            FROM user_tables
        """)

        tables = [row[0] for row in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM user_tab_columns
                WHERE table_name = '{table}'
            """)

            columns = cursor.fetchall()

            schema[table] = [
                {"column": col[0], "type": col[1]} for col in columns
            ]

        cursor.close()
        connection.close()

        return schema
