import os
import subprocess
import time
import sys
import shutil
from pathlib import Path

# --- Configuration ---
HOME = Path(os.path.expanduser("~"))
DOWNLOADS = HOME / "Downloads"

# Paths to services (Adjust if needed)
KAFKA_DIR = DOWNLOADS / "kafka_2.12-2.8.2"
NIFI_DIR = DOWNLOADS / "nifi-1.28.0" / "nifi-1.28.0"

# Postgres Config
PG_USER = "postgres"
PG_DB = "airplane_analytics"
PG_PASS = "postgres"

def check_path(path, name):
    if not path.exists():
        print(f"[ERROR] {name} not found at {path}")
        return False
    return True

def start_postgres():
    print("--- Starting PostgreSQL ---")
    try:
        # Check if service is running
        subprocess.check_call(["systemctl", "is-active", "--quiet", "postgresql"])
        print("PostgreSQL service is running.")
    except subprocess.CalledProcessError:
        print("Starting PostgreSQL service (requires sudo)...")
        subprocess.check_call(["sudo", "systemctl", "start", "postgresql"])

    # Setup DB and User
    print("Configuring Database...")
    try:
        # Create user
        subprocess.run(["sudo", "-u", "postgres", "psql", "-c", 
                        f"CREATE USER {PG_USER} WITH PASSWORD '{PG_PASS}';"], 
                       stderr=subprocess.DEVNULL)
        # Create DB
        subprocess.run(["sudo", "-u", "postgres", "psql", "-c", 
                        f"CREATE DATABASE {PG_DB} OWNER {PG_USER};"], 
                       stderr=subprocess.DEVNULL)
        print("Database configured.")
    except Exception as e:
        print(f"Database setup warning (might already exist): {e}")

def start_zookeeper_kafka():
    print("--- Starting Zookeeper & Kafka ---")
    if not check_path(KAFKA_DIR, "Kafka"):
        sys.exit(1)

    # Start Zookeeper
    print("Starting Zookeeper...")
    zk_log = open("zookeeper.log", "w")
    subprocess.Popen([str(KAFKA_DIR / "bin/zookeeper-server-start.sh"), 
                      str(KAFKA_DIR / "config/zookeeper.properties")], 
                     stdout=zk_log, stderr=zk_log, cwd=KAFKA_DIR)
    time.sleep(5) # Wait for ZK

    # Start Kafka
    print("Starting Kafka...")
    kafka_log = open("kafka.log", "w")
    subprocess.Popen([str(KAFKA_DIR / "bin/kafka-server-start.sh"), 
                      str(KAFKA_DIR / "config/server.properties")], 
                     stdout=kafka_log, stderr=kafka_log, cwd=KAFKA_DIR)
    time.sleep(5) # Wait for Kafka
    print("Kafka started.")

def start_nifi():
    print("--- Starting NiFi ---")
    if not check_path(NIFI_DIR, "NiFi"):
        print("Please download NiFi 1.28.0 and extract it to Downloads.")
        sys.exit(1)
    
    nifi_bin = NIFI_DIR / "bin/nifi.sh"
    
    # Set JAVA_HOME explicitly
    env = os.environ.copy()
    env["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64/"
    
    subprocess.check_call([str(nifi_bin), "start"], env=env)
    print("NiFi started (background). It may take a few minutes to become available at https://localhost:8443/nifi")

def main():
    print("=== Local Deployment Script ===")
    
    start_postgres()
    start_zookeeper_kafka()
    start_nifi()
    
    print("\n=== All Services Started ===")
    print(f"Kafka: {KAFKA_DIR}")
    print(f"NiFi: {NIFI_DIR}")
    print("Postgres: System Service")
    print("\nYou can now run your python scripts (Producer/Spark).")
    print("To stop services:")
    print(f"  {NIFI_DIR}/bin/nifi.sh stop")
    print(f"  {KAFKA_DIR}/bin/kafka-server-stop.sh")
    print(f"  {KAFKA_DIR}/bin/zookeeper-server-stop.sh")

if __name__ == "__main__":
    main()
