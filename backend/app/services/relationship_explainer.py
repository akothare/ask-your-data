class RelationshipExplainer:

    @staticmethod
    def explain(schema, table1, table2):

        # Normalize
        table1 = table1.upper()
        table2 = table2.upper()

        if table1 not in schema or table2 not in schema:
            return "No information available for given tables."

        # 🔥 Check table1 → table2
        for rel in schema[table1]["relationships"]:
            if rel["ref_table"] == table2:
                return (
                    f"{table1} is related to {table2} via "
                    f"{table1}.{rel['column']} = "
                    f"{table2}.{rel['ref_column']}"
                )

        # 🔥 Check table2 → table1 (IMPORTANT FIX)
        for rel in schema[table2]["relationships"]:
            if rel["ref_table"] == table1:
                return (
                    f"{table2} is related to {table1} via "
                    f"{table2}.{rel['column']} = "
                    f"{table1}.{rel['ref_column']}"
                )

        return f"No direct relationship found between {table1} and {table2}."
