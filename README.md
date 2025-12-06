# Airplane Crash Analytics Project

## 1. Project Overview

This project is a **Big Data Pipeline** designed to analyze airplane crash data in real-time. It processes historical crash records, cleans and enriches them, and performs analytics to identify trends, safety scores, and risk levels.

### Key Technologies

- **Kafka**: For real-time data ingestion and streaming.
- **NiFi**: For data flow management, transformation, and cleaning.
- **Spark**: For complex analytics and aggregation.
- **PostgreSQL**: For storing the final analytical results.
- **Python**: For custom scripting and orchestration.

---

## 2. Architecture Workflow

The data flows through the system in three main stages:

### Stage 1: Ingestion (Kafka)

- **Script**: `KafkaProducer.py`
- **Action**: Reads raw data from `airplane_crashes_ds.csv` and publishes it to the Kafka topic `airplane_crashes_raw`.

### Stage 2: Processing (NiFi)

- **Tool**: Apache NiFi
- **Flow File**: `groupedFlow.json`
- **Action**:
  1.  **Consumes** raw data from Kafka.
  2.  **Transforms** the data using a Groovy script:
      - **Cleaning**: Trims whitespace, standardizes text (uppercase), fixes flight numbers.
      - **Enrichment**: Calculates `Safety Score` (0-100) and `Risk Level` (Low/High).
      - **Categorization**: Classifies accidents (e.g., "Weather Related", "Human Error").
  3.  **Publishes** the processed data to a new Kafka topic `produceToSpark`.

### Stage 3: Analytics (Spark)

- **Script**: `SparkAnalytics.py`
- **Action**:
  1.  Reads the clean data from the `produceToSpark` topic.
  2.  Performs aggregations (e.g., crashes per year, average fatalities).
  3.  Saves the results to the **PostgreSQL** database.

---

## 3. How to Run (Local Installation)

### Prerequisites

- **Java 11**: Installed and configured.
- **PostgreSQL**: Installed and running.
- **Kafka**: Downloaded and extracted.
- **NiFi**: Downloaded and extracted.

### Step 1: Start Services

We have created a helper script to start Zookeeper, Kafka, and NiFi for you.

```bash
python3 runLocal.py
```

_Wait a few minutes for NiFi to start fully._

### Step 2: Import the Flow

1.  Open NiFi at [https://localhost:8443/nifi](https://localhost:8443/nifi).
2.  Login with the credentials generated in your logs (or `admin` / `admin123456789` if you reset them).
3.  Drag a **Process Group** to the canvas.
4.  Click the **Browse** (folder icon) and select `groupedFlow.json`.
5.  Click **Add**.
6.  **Double-click** the new group to enter it.
7.  Right-click on the canvas background and select **Start**.

### Step 3: Run the Pipeline

Open two new terminal windows:

**Terminal 1 (Analytics Consumer):**

```bash
python3 SparkAnalytics.py
```

**Terminal 2 (Data Producer):**

```bash
python3 KafkaProducer.py
```

You should see data flowing in NiFi and results appearing in your PostgreSQL database.

---

## 4. File Structure

- `runLocal.py`: Script to start all local services.
- `groupedFlow.json`: The complete NiFi data flow definition.
- `KafkaProducer.py`: Sends raw data to the system.
- `SparkAnalytics.py`: Processes data and saves to DB.
- `airplane_crashes_ds.csv`: The source dataset.
