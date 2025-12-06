import json

FLOW_FILE = "groupedFlow.json"
OUTPUT_FILE = "groupedFlow.json"

def fix_flow():
    with open(FLOW_FILE, 'r') as f:
        flow = json.load(f)

    processors = flow['flowContents']['processors']
    
    for proc in processors:
        # Fix ConsumeKafka
        if "ConsumeKafka" in proc['type'] and "2_6" not in proc['type']:
            print("Fixing ConsumeKafka...")
            proc['type'] = "org.apache.nifi.processors.kafka.pubsub.ConsumeKafka_2_6"
            proc['bundle']['artifact'] = "nifi-kafka-2-6-nar"
            proc['bundle']['version'] = "1.28.0"
            
            # Update Properties
            props = proc['properties']
            # Remove 2.x properties
            if "Kafka Connection Service" in props:
                del props["Kafka Connection Service"]
            
            # Add 1.x properties
            props["bootstrap.servers"] = "localhost:9092"
            props["topic"] = "airplane_crashes_raw"
            props["group.id"] = "Nificonsumer"
            props["auto.offset.reset"] = "earliest"
            
            # Remove old property keys if they differ
            if "Topics" in props: del props["Topics"]
            if "Group ID" in props: del props["Group ID"]

        # Fix PublishKafka
        if "PublishKafka" in proc['type'] and "2_6" not in proc['type']:
            print("Fixing PublishKafka...")
            proc['type'] = "org.apache.nifi.processors.kafka.pubsub.PublishKafka_2_6"
            proc['bundle']['artifact'] = "nifi-kafka-2-6-nar"
            proc['bundle']['version'] = "1.28.0"
            
            # Update Properties
            props = proc['properties']
            # Remove 2.x properties
            if "Kafka Connection Service" in props:
                del props["Kafka Connection Service"]
            
            # Add 1.x properties
            props["bootstrap.servers"] = "localhost:9092"
            props["topic"] = "produceToSpark"
            
            # Remove old property keys if they differ
            if "Topic Name" in props: del props["Topic Name"]

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(flow, f, indent=2)
    print("Flow fixed!")

if __name__ == "__main__":
    fix_flow()
