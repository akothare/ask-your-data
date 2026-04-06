class SchemaExplainer:

    @staticmethod
    def explain(schema, table_name=None):

        # 🔒 If specific table requested but not found
        if table_name and table_name not in schema:
            return f"Table '{table_name}' does not exist or you do not have access."

        # 🔹 Specific table
        if table_name:

            table = schema[table_name]
            columns = table.get("columns", [])
            foreign_keys = table.get("foreign_keys", [])

            response = f"The {table_name} table contains the following columns:\n\n"

            for col in columns:
                if isinstance(col, dict):
                    name = col.get("name", "")
                    dtype = col.get("type", "")
                    response += f"• {name} ({dtype})\n"
                else:
                    response += f"• {col}\n"

            if foreign_keys:
                response += "\nRelationships:\n"
                for fk in foreign_keys:
                    response += f"• {fk['column']} → {fk['ref_table']}.{fk['ref_column']}\n"

            return response.strip()

        # 🔒 DO NOT expose all tables by default
        return "Please specify a table name to view its structure."
