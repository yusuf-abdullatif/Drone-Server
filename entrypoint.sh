#!/bin/sh

# Wait for PostgreSQL using Python (better alternative)
python << END
import os
import time
import psycopg2
from psycopg2 import OperationalError

max_retries = 10
retry_delay = 2

def wait_for_db():
    conn = None
    for _ in range(max_retries):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv('POSTGRES_DB', 'dronedb'),
                user=os.getenv('POSTGRES_USER', 'user'),
                password=os.getenv('POSTGRES_PASSWORD', 'password'),
                host=os.getenv('POSTGRES_HOST', 'db'),
                port=os.getenv('POSTGRES_PORT', '5432')
            )
            conn.close()
            print("Database connection successful!")
            return True
        except OperationalError:
            print(f"Database not ready, retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
    return False

if not wait_for_db():
    exit(1)
END

# Initialize database
flask db init
flask db migrate
flask db upgrade

# Start application
exec gunicorn --bind 0.0.0.0:5000 "app:create_app()"