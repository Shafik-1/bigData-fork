import psycopg2
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Parse DB name from URL or use default
# POSTGRES_URL=jdbc:postgresql://postgres:5432/airplane_analytics
pg_url = os.getenv("POSTGRES_URL", "jdbc:postgresql://localhost:5432/airplane_analytics")
default_db_name = pg_url.split("/")[-1]

DB_NAME = os.getenv("POSTGRES_DB", default_db_name)
DB_USER = os.getenv("POSTGRES_USER", "postgres")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def check_db():
    print(f"Connecting to database '{DB_NAME}' at {DB_HOST}:{DB_PORT}...")
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        
        # List all tables
        print("Checking for ANY tables in the database...")
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public';
        """)
        tables = cur.fetchall()
        
        if not tables:
            print("❌ No tables found in 'public' schema.")
            print("   Spark has not written any data yet.")
            return
            
        print(f"✅ Found tables: {[t[0] for t in tables]}")

        # Check specifically for crashes_by_country
        if ('crashes_by_country',) in tables:
            cur.execute("SELECT count(*) FROM crashes_by_country;")
            count = cur.fetchone()[0]
            print(f"✅ 'crashes_by_country' has {count} rows.")
            
            if count > 0:
                print("\nTop 5 entries:")
                cur.execute("SELECT * FROM crashes_by_country ORDER BY crash_count DESC LIMIT 5;")
                for row in cur.fetchall():
                    print(row)
        else:
            print("⚠️ 'crashes_by_country' is missing, but other tables exist.")

        # Count rows
        cur.execute("SELECT count(*) FROM crashes_by_country;")
        count = cur.fetchone()[0]
        print(f"✅ Found {count} rows in 'crashes_by_country' table.")
        
        if count > 0:
            print("\nTop 5 entries (Country, Count, Fatalities):")
            cur.execute("SELECT * FROM crashes_by_country ORDER BY crash_count DESC LIMIT 5;")
            rows = cur.fetchall()
            for row in rows:
                print(row)
        else:
            print("   Waiting for data...")

        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        print("Ensure PostgreSQL is running and credentials in .env are correct.")

if __name__ == "__main__":
    check_db()
