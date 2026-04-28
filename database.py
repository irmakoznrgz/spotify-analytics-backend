import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

host_inf = os.getenv("DB_HOST")
port_inf = os.getenv("DB_PORT")
database_name = os.getenv("DB_NAME")
user_name = os.getenv("DB_USER")
password = os.getenv("DB_PASS")

async def get_db_connection():
    try:
        connection = await asyncpg.connect(
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
    async def test_run():
        test_connection = await  get_db_connection()
        if test_connection:
            await test_connection.close()

    asyncio.run(test_run())