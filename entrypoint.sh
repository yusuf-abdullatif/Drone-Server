#!/bin/sh

# Wait for PostgreSQL using DATABASE_URL from environment
python << END
import os
import time
import psycopg2
from psycopg2 import OperationalError

max_retries = 10
retry_delay = 2

def wait_for_db():
    for _ in range(max_retries):
        try:
            conn = psycopg2.connect(os.environ['DATABASE_URL'])
            conn.close()
            print("Database connection successful!")
            return True
        except (OperationalError, KeyError) as e:
            print(f"Database error: {str(e)}")
            print(f"Retrying in {retry_delay} seconds...")
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