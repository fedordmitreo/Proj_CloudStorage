import asyncpg

HOST = "10.0.0.102"
PASSWORD = "postgres"
PORT = "5432"
USER = "postgres"
DB_NAME = "postgres"

h = "kva@raika.g"
g = "Ertyuiop123456789"

async def g(h, g):
    conn = await asyncpg.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DB_NAME,
        port=PORT
    )
    await conn.fetch("insert table values ('$1', '$2')", h, g)

