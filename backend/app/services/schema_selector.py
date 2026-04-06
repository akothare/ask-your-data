class SchemaSelector:

    @staticmethod
    def select_relevant_tables(user_query, schema):

        query = user_query.lower()
        relevant = {}

        for table, details in schema.items():
            if table.lower() in query:
                relevant[table] = details

        # Fallback (avoid empty schema)
        if not relevant:
            for i, (k, v) in enumerate(schema.items()):
                if i >= 5:
                    break
                relevant[k] = v

        return relevant
