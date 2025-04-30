#!/bin/sh

# Wait using both methods for redundancy
python << END
import os
import time
import psycopg2
from psycopg2 import OperationalError

max_retries = 20  # Increased retries
retry_delay = 3

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

# Secondary check using pg_isready
until pg_isready -h db -U droneuser -d dronedb; do
  echo "PostgreSQL check via pg_isready..."
  sleep 2
done

# Initialize database
if [ ! -f "/app/migrations/alembic.ini" ]; then
  flask db init
fi

flask db migrate
flask db upgrade

exec gunicorn --bind 0.0.0.0:5000 "app:create_app()"