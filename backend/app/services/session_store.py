class SessionStore:
    _store = {}

    @classmethod
    def get_last_query(cls, session_id):
        return cls._store.get(session_id)

    @classmethod
    def set_last_query(cls, session_id, sql):
        cls._store[session_id] = sql
