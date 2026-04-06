class SchemaExplainer:

    @staticmethod
    def explain(schema, table_name=None):

        # 🔹 If specific table requested
        if table_name and table_name in schema:

            table = schema[table_name]

            columns = table.get("columns", [])
            foreign_keys = table.get("foreign_keys", [])

            response = f"The {table_name} table contains the following columns:\n\n"

            # Columns
            for col in columns:
                response += f"- {col}\n"

            # Relationships (if any)
            if foreign_keys:
                response += "\nRelationships:\n"
                for fk in foreign_keys:
                    response += f"- {fk['column']} → {fk['ref_table']}.{fk['ref_column']}\n"

            return response

        # 🔹 General schema overview
        tables = list(schema.keys())

        response = f"The database contains {len(tables)} tables:\n\n"

        for table in tables:
            response += f"- {table}\n"

        return response
