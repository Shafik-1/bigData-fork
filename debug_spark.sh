#!/bin/bash
echo "Running Spark Analytics in Debug Mode..."
echo "Logs will be saved to spark_debug.log"

# Ensure we use the same python as the current shell (venv)
export PYSPARK_PYTHON=$(which python3)
export PYSPARK_DRIVER_PYTHON=$(which python3)

spark-submit \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.postgresql:postgresql:42.6.0 \
  SparkAnalytics.py > spark_debug.log 2>&1

echo "Spark finished (or crashed). Check spark_debug.log for details."
