import os
import oracledb
from dotenv import load_dotenv

load_dotenv()


class OracleConnection:

    @staticmethod
    def get_connection():
        try:
            connection = oracledb.connect(
                user=os.getenv("ORACLE_USER"),
                password=os.getenv("ORACLE_PASSWORD"),
                dsn=os.getenv("ORACLE_DSN")
            )
            return connection
        except Exception as e:
            raise RuntimeError(f"Error connecting to Oracle DB: {str(e)}")
