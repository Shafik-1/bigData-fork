import json
import os

# Paths
FLOW_FILE = "NiFi_Flow (23).json"
SCRIPT_FILE = "NiFi_Flow (26).json"
OUTPUT_FILE = "NiFi_Flow_Final.json"

def merge_flow():
    print(f"Reading flow from {FLOW_FILE}...")
    with open(FLOW_FILE, 'r') as f:
        flow_data = json.load(f)

    print(f"Reading script from {SCRIPT_FILE}...")
    with open(SCRIPT_FILE, 'r') as f:
        script_content = f.read()

    print("Locating ScriptedTransformRecord processor...")
    processors = flow_data['flowContents']['processors']
    updated = False
    
    for proc in processors:
        if proc['type'] == "org.apache.nifi.processors.script.ScriptedTransformRecord":
            print("Found ScriptedTransformRecord. Updating Script Body...")
            proc['properties']['Script Body'] = script_content
            updated = True
            break
    
    if not updated:
        print("ERROR: Could not find ScriptedTransformRecord processor!")
        return

    print(f"Writing merged flow to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(flow_data, f, indent=2)
    
    print("Success!")

if __name__ == "__main__":
    merge_flow()
