import os
import subprocess
import time
import sys
from pathlib import Path

# Reuse logic from runLocal.py (importing it would be cleaner, but let's make this standalone for simplicity)
HOME = Path(os.path.expanduser("~"))
DOWNLOADS = HOME / "Downloads"
KAFKA_DIR = DOWNLOADS / "kafka_2.12-2.8.2"
NIFI_DIR = DOWNLOADS / "nifi-1.28.0" / "nifi-1.28.0"

def start_services():
    print("=== Starting Infrastructure ===")
    # 1. Postgres
    try:
        subprocess.check_call(["systemctl", "is-active", "--quiet", "postgresql"])
        print("PostgreSQL is running.")
    except:
        print("Starting PostgreSQL...")
        subprocess.run(["sudo", "systemctl", "start", "postgresql"])

    # 2. Zookeeper & Kafka
    log_dir = Path("/tmp/bigdata_logs")
    log_dir.mkdir(exist_ok=True)
    
    print("Starting Zookeeper...")
    zk_log = open(log_dir / "zookeeper.log", "w")
    subprocess.Popen([str(KAFKA_DIR / "bin/zookeeper-server-start.sh"), 
                      str(KAFKA_DIR / "config/zookeeper.properties")], 
                     stdout=zk_log, stderr=zk_log, cwd=KAFKA_DIR)
    time.sleep(5)

    print("Starting Kafka...")
    kafka_log = open(log_dir / "kafka.log", "w")
    subprocess.Popen([str(KAFKA_DIR / "bin/kafka-server-start.sh"), 
                      str(KAFKA_DIR / "config/server.properties")], 
                     stdout=kafka_log, stderr=kafka_log, cwd=KAFKA_DIR)
    time.sleep(5)

    # 3. NiFi
    print("Starting NiFi...")
    env = os.environ.copy()
    env["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64/"
    subprocess.run([str(NIFI_DIR / "bin/nifi.sh"), "start"], env=env)
    print("NiFi started (background).")

def run_analytics():
    print("\n=== Starting Analytics & Producer ===")
    print("Launching SparkAnalytics.py (Consumer)...")
    # Open in new terminal if possible, else background
    try:
        subprocess.Popen(["x-terminal-emulator", "-e", "python3 SparkAnalytics.py"])
    except FileNotFoundError:
        print("Could not open new terminal. Running in background.")
        subprocess.Popen(["python3", "SparkAnalytics.py"])

    time.sleep(5) # Give Spark a moment

    print("Launching KafkaProducer.py (Producer)...")
    try:
        subprocess.Popen(["x-terminal-emulator", "-e", "python3 KafkaProducer.py"])
    except FileNotFoundError:
        print("Could not open new terminal. Running in background.")
        subprocess.Popen(["python3", "KafkaProducer.py"])

def main():
    start_services()
    
    print("\nWaiting 60 seconds for NiFi to initialize before running scripts...")
    # Optional: You can skip this wait if NiFi is already running
    time.sleep(10) 
    
    run_analytics()
    print("\nAll systems go! Check the opened terminals.")

if __name__ == "__main__":
    main()
