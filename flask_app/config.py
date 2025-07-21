import os

DB_CONFIG = {
    "host": "db.ynmlhxhpvqupdwiptyrn.supabase.co",
    "dbname": "postgres",
    "user": "postgres", 
    "password": os.getenv("SUPABASE_PASSWORD"),
    "port": 5432,
    "sslmode": "require",
    "connect_timeout": 30
}
