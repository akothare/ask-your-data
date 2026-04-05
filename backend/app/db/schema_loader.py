from app.db.connection import OracleConnection


class SchemaLoader:

    @staticmethod
    def load_schema():
        connection = OracleConnection.get_connection()
        cursor = connection.cursor()

        schema = {}

        # Step 1: Tables
        cursor.execute("SELECT table_name FROM user_tables")
        tables = [row[0] for row in cursor.fetchall()]

        # Step 2: Columns
        for table in tables:
            cursor.execute(f"""
                SELECT column_name, data_type
                FROM user_tab_columns
                WHERE table_name = '{table}'
            """)

            columns = cursor.fetchall()

            schema[table] = {
                "columns": [
                    {"name": col[0], "type": col[1]} for col in columns
                ],
                "relationships": []
            }

        # Step 3: Foreign Keys (RELATIONSHIPS)
        cursor.execute("""
            SELECT
                a.table_name,
                a.column_name,
                c_pk.table_name AS referenced_table,
                b.column_name AS referenced_column
            FROM user_cons_columns a
            JOIN user_constraints c ON a.constraint_name = c.constraint_name
            JOIN user_constraints c_pk ON c.r_constraint_name = c_pk.constraint_name
            JOIN user_cons_columns b ON c_pk.constraint_name = b.constraint_name
            WHERE c.constraint_type = 'R'
        """)

        relationships = cursor.fetchall()

        for row in relationships:
            table, column, ref_table, ref_column = row

            if table in schema:
                schema[table]["relationships"].append({
                    "column": column,
                    "ref_table": ref_table,
                    "ref_column": ref_column
                })

        cursor.close()
        connection.close()

        return schema
