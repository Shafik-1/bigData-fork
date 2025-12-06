import subprocess
import sys
import os
import time
from pathlib import Path

ROOT = Path(__file__).parent
VENV = ROOT / '.venv'
REQ = ROOT / 'requirements.txt'

def ensure_venv_and_reqs():
    # Windows vs Linux/Mac paths
    if os.name == "nt":  # Windows
        pip = VENV / "Scripts" / "pip.exe"
        python_exec = VENV / "Scripts" / "python.exe"
    else:
        pip = VENV / "bin" / "pip"
        python_exec = VENV / "bin" / "python"

    if not pip.exists():
        print(f"Creating virtual environment at {VENV}...")
        import shutil
        if VENV.exists():
            shutil.rmtree(VENV)
        subprocess.check_call([sys.executable, "-m", "venv", "--system-site-packages", str(VENV)])

    # Check and install requirements manually to avoid unnecessary upgrades/downloads
    import json
    
    print("Checking installed packages...")
    try:
        # Get installed packages in JSON format
        output = subprocess.check_output([str(python_exec), "-m", "pip", "list", "--format=json"]).decode('utf-8')
        installed_packages = {pkg['name'].lower(): pkg['version'] for pkg in json.loads(output)}
    except Exception as e:
        print(f"Warning: Could not list installed packages ({e}). Proceeding with standard install.")
        installed_packages = {}

    to_install = []
    with open(REQ, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Extract package name
            import re
            match = re.match(r'^([a-zA-Z0-9_\-\.]+)', line)
            if match:
                pkg_name = match.group(1).lower()
                
                # Special handling for pyspark: check if importable even if not in pip list
                is_installed = pkg_name in installed_packages
                if not is_installed:
                    try:
                        # Map package name to import name (usually same, but handle exceptions if needed)
                        import_name = pkg_name.replace('-', '_')
                        if pkg_name == "python-dotenv": import_name = "dotenv"
                        if pkg_name == "kafka-python-ng": import_name = "kafka"
                        
                        subprocess.check_call([str(python_exec), "-c", f"import {import_name}"], 
                                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                        is_installed = True
                        print(f"  [OK] {pkg_name} found via import (system package). Skipping.")
                    except subprocess.CalledProcessError:
                        # Fallback for pyspark: check if executable exists
                        if pkg_name == "pyspark":
                            import shutil
                            if shutil.which("pyspark"):
                                is_installed = True
                                print(f"  [OK] pyspark executable found in PATH. Skipping install.")
                            else:
                                is_installed = False
                        else:
                            is_installed = False

                if is_installed:
                    if pkg_name in installed_packages:
                        print(f"  [OK] {pkg_name} is already installed ({installed_packages[pkg_name]}). Skipping.")
                else:
                    print(f"  [MISSING] {pkg_name} not found. Adding to install list.")
                    to_install.append(line)
            else:
                to_install.append(line)

    if to_install:
        print(f"Installing missing packages: {to_install}")
        subprocess.check_call([str(pip), "install"] + to_install)
    else:
        print("All requirements satisfied.")

    return python_exec


def docker_compose_up():
    subprocess.check_call(["docker", "compose", "pull"])
    subprocess.check_call(["docker", "compose", "up", "-d"])


def wait_for_kafka(host="localhost", port=9092, timeout=120):
    import socket
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("Kafka reachable")
                return True
        except Exception:
            time.sleep(1)
    raise RuntimeError("Kafka not reachable")



if __name__ == "__main__":
    python_exec = ensure_venv_and_reqs()
    docker_compose_up()

    print("Waiting for Kafka…")
    wait_for_kafka()

    print("Running KafkaProducer.py…")
    wait_for_kafka()
    subprocess.check_call([str(python_exec), str(ROOT / "KafkaProducer.py")])

