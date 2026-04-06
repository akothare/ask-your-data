class SchemaExplainer:

    @staticmethod
    def explain(schema, table_name=None):

        # 🔹 Specific table
        if table_name and table_name in schema:

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

        # 🔹 General schema
        tables = list(schema.keys())

        response = f"The database contains {len(tables)} tables:\n\n"

        for table in tables:
            response += f"• {table}\n"

        return response.strip()
