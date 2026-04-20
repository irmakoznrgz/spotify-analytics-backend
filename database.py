import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

host_inf = os.getenv("DB_HOST")
port_inf = os.getenv("DB_PORT")
database_name = os.getenv("DB_NAME")
user_name = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

def get_db_connection():
    try:
        connection = psycopg2.connect(
            host=host_inf,
            port=port_inf,
            database=database_name,
            user=user_name,
            password=password
        )
        print("Successful")
        return connection
        
    except Exception as error:
        print("Error!", error)
        return None

if __name__ == "__main__":
    test_connection = get_db_connection()
    if test_connection:
        test_connection.close()