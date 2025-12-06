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
    python_path = sys.executable
    
    print(f"Launching SparkAnalytics.py (Consumer) using spark-submit...")
    # Open in new terminal and keep open
    try:
        # Use spark-submit for the Spark script
        # We include the Kafka SQL package for Spark 3.5.x
        spark_cmd = (
            f"export PYSPARK_PYTHON={python_path} && "
            f"export PYSPARK_DRIVER_PYTHON={python_path} && "
            "spark-submit "
            "--packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.6.0 "
            "SparkAnalytics.py"
        )
        cmd = f"bash -c '{spark_cmd}; exec bash'"
        subprocess.Popen(["x-terminal-emulator", "-e", cmd])
    except FileNotFoundError:
        print("Could not open new terminal. Running in background.")
        subprocess.Popen(spark_cmd.split())

    time.sleep(5) # Give Spark a moment

    print(f"Launching KafkaProducer.py (Producer) using {python_path}...")
    try:
        # Quote the python path to handle spaces in directory names
        cmd = f"bash -c '\"{python_path}\" KafkaProducer.py; exec bash'"
        subprocess.Popen(["x-terminal-emulator", "-e", cmd])
    except FileNotFoundError:
        print("Could not open new terminal. Running in background.")
        subprocess.Popen([python_path, "KafkaProducer.py"])

def check_dependencies():
    print("Checking dependencies...")
    
    # 1. Check PySpark (Don't auto-install, it's huge)
    try:
        import pyspark
        print("✅ Found pyspark")
    except ImportError:
        print("⚠️  WARNING: 'pyspark' not found.")
        print("   If you have it installed globally, ensure you are running with access to system packages.")
        print("   Otherwise, install it manually: pip install pyspark")

    # 2. Check other libs (Auto-install if missing and possible)
    required_libs = {
        "kafka": "kafka-python-ng",
        "psycopg2": "psycopg2-binary",
        "pandas": "pandas",
        "dotenv": "python-dotenv"
    }
    
    for module, package in required_libs.items():
        try:
            __import__(module)
            print(f"✅ Found {package}")
        except ImportError:
            print(f"❌ Missing {package}. Attempting to install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"   Installed {package}")
            except subprocess.CalledProcessError:
                print(f"   FAILED to install {package}.")
                print("   Hint: If you are on Kali Linux globally, try 'sudo apt install python3-xyz' or use a venv.")

def main():
    check_dependencies()

    start_services()
    
    print("\nWaiting 60 seconds for NiFi to initialize before running scripts...")
    # Optional: You can skip this wait if NiFi is already running
    time.sleep(10) 
    
    run_analytics()
    print("\nAll systems go! Check the opened terminals.")

if __name__ == "__main__":
    main()
