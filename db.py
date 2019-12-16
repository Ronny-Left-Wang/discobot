import psycopg2

try:
    conn = psycopg2.connect(
            user = "wang",
            password = "password",
            host = "127.0.0.1",
            port = "5432",
            database = "botdb")

    cur = conn.cursor()
    # Print PostgreSQL Connection properties
    print (conn.get_dsn_parameters(),"\n")

    # Print PostgreSQL version
    cur.execute("""
    CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        discord_id BIGINT UNIQUE NOT NULL,
        exp BIGINT NOT NULL,
        level INTEGER NOT NULL,
        gold BIGINT NOT NULL,
        stage INTEGER NOT NULL
    )""")
    conn.commit()
    #record = cursor.fetchone()
    #print("You are connected to - ", record,"\n")
except Exception as e:
    print("gay:", e)
finally:
    if(conn):
        cur.close()
        conn.close()
        print("PostgreSQL conn closed")
