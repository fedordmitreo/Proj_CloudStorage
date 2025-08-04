import psycopg2

HOST = "10.0.0.102"
PASSWORD = "postgres"
PORT = "5432"
USER = "postgres"
DB_NAME = "postgres"



def gtr(h, g):
    conn = psycopg2.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=DB_NAME,
        port=PORT
    )
    cur = conn.cursor()
    cur.execute(f"insert into tble values ('{h}', '{g}')")

h = "kva@raika.g"
g = "Ertyuiop123456789"

gtr(h, g)