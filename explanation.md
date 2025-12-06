# NiFi Flow Explanation & Changes

## Overview

This document explains the data pipeline and the recent updates made to the logic.

### The Pipeline

1.  **Input**: Reads `airplane_crashes_ds.csv` and sends it to Kafka topic `airplane_crashes_raw`.
2.  **Processing (NiFi)**:
    - Consumes raw data.
    - **Transforms** the data using a Groovy script (cleaned, enriched, typed).
    - Publishes cleaned data to Kafka topic `produceToSpark`.
3.  **Analytics**: Spark reads from `produceToSpark`, calculates statistics, and saves to PostgreSQL.

## Recent Changes (NiFi_Flow_Final.json)

We have updated the **ScriptedTransformRecord** processor with new logic from your provided script.

### 1. Data Cleaning

- **Uppercasing**: Now converts `city`, `airline`, and `country` to UPPERCASE for consistency.
- **Trimming**: Removes extra spaces from all text fields.
- **Flight Number**: Standardizes format (removes special characters).

### 2. Enrichment

- **Risk Level**: Calculates a risk level (LOW, MEDIUM, HIGH, CRITICAL) based on fatalities and damage.
- **Safety Score**: Computes a score (0-100) for each incident.
- **Accident Category**: Classifies accidents (e.g., "WEATHER_RELATED", "HUMAN_ERROR") based on keywords in the cause.

### 3. Technical Fixes

- **Version Compatibility**: The flow is now compatible with **NiFi 1.28.0** (downgraded from 2.x bundles).
- **JSON Structure**: The script was correctly embedded into the flow definition.

## How to Use

1.  Open NiFi: [https://localhost:8443/nifi](https://localhost:8443/nifi)
2.  Import `NiFi_Flow_Final.json` (Process Group > Browse).
3.  Start the flow.
