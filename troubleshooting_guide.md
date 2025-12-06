# Project Troubleshooting & Fixes Guide

This document summarizes the key technical issues encountered during the migration to a local environment and how they were resolved. Use this to replicate the setup on another machine.

## 1. NiFi Flow Compatibility ("Invalid Processor" / "Validation Errors")

**The Issue:**
When importing the flow into NiFi 1.28, multiple validation errors appeared:

- `'Record Reader' is invalid because must be a known Kafka client configuration property`
- `Kafka3ConnectionService` is invalid.
- Processors were missing or invalid.

**The Cause:**
The original flow was likely exported from a different NiFi version or had a mix of NiFi 2.x and 1.x configurations.

1.  It used generic `ConsumeKafka` processors but configured them with Record Readers (which requires `ConsumeKafkaRecord`).
2.  It used "Display Names" (e.g., "Record Reader") for properties instead of "Internal Names" (e.g., `record-reader`), causing NiFi to treat them as dynamic properties.
3.  It included `Kafka3ConnectionService` which is not used by the standard NiFi 1.x Kafka processors.

**The Solution:**
We programmatically "surgically" fixed the `groupedFlow.json` file:

1.  **Switched Processors:** Changed `ConsumeKafka` → `ConsumeKafkaRecord_2_6` (and same for Publish).
2.  **Fixed Property Keys:** Renamed `"Record Reader"` → `"record-reader"` and `"Record Writer"` → `"record-writer"`.
3.  **Removed Invalid Service:** Deleted the `Kafka3ConnectionService` reference.
4.  **Cleaned Properties:** Removed invalid Kafka 2.x properties like `Header Encoding` and `Topic Format`.

---

## 2. Kafka "UnrecognizedBrokerVersion" Error

**The Issue:**
The Python producer (`KafkaProducer.py`) failed with:
`kafka.errors.UnrecognizedBrokerVersion: UnrecognizedBrokerVersion`

**The Cause:**
The `kafka-python` library sometimes fails to automatically negotiate the API version with newer Kafka brokers (or specific local setups).

**The Solution:**
Explicitly set the API version in `KafkaProducer.py`:

```python
producer = KafkaProducer(
    ...
    api_version=(2, 8, 1),  # Explicitly set version
    ...
)
```

---

## 3. Spark "ModuleNotFoundError: pyspark"

**The Issue:**
Running `python3 runAll.py` failed because it tried to run `SparkAnalytics.py` using the virtual environment's Python, which didn't have `pyspark` installed (to save space). The user wanted to use the global Spark installation.

**The Solution:**
Modified `runAll.py` to launch the Spark script using `spark-submit` instead of `python3`.

- **Command:** `spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1 SparkAnalytics.py`
- This uses the global Spark engine and automatically downloads the necessary Kafka connector JARs.

---

## 4. "No such file or directory" (Path Spaces)

**The Issue:**
The project path contained spaces (`.../Level 3/1st term/...`). When `runAll.py` tried to open a new terminal using `bash -c`, it interpreted the spaces as separate arguments.

**The Solution:**
Wrapped the path in escaped quotes in `runAll.py`:

```python
# BEFORE
cmd = f"bash -c '{python_path} script.py ...'"

# AFTER
cmd = f"bash -c '\"{python_path}\" script.py ...'"
```
