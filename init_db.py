import os
import psycopg2
from config import Config


try:
    with psycopg2.connect(Config.DATABASE_URI) as con:
        with con.cursor() as cur:
            cur.execute("""create schema if not exists rest_api; """
                        )
            cur.execute("""CREATE TABLE IF NOT EXISTS rest_app.users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(80) UNIQUE NOT NULL,
                password VARCHAR(120) NOT NULL,
                role VARCHAR(50) NOT NULL
            );
            """)
            cur.execute("""CREATE TABLE IF NOT EXISTS rest_app.articles (
                id SERIAL PRIMARY KEY,
                title VARCHAR(80) UNIQUE NOT NULL,
                value VARCHAR(1000) NOT NULL,
                privacy VARCHAR(10) NOT NULL,
                insered_by int,
                CONSTRAINT fk_insered FOREIGN KEY (insered_by) 
                REFERENCES rest_app.users(id) 
            );
            """)
        con.commit()
finally:
        con.close()
