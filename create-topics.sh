#!/bin/bash

# Kafka container's bootstrap server address
KAFKA_BROKER="kafka:9092"  # Use internal Docker network address
echo "Kafka broker address: $KAFKA_BROKER"

# Wait for Kafka to fully initialize
echo "Waiting for Kafka to fully initialize..."
sleep 10  # Adjust the sleep time if needed

# List of topics to create
TOPICS=("news-articles" "named-entities")

# Loop through and create topics
for TOPIC in "${TOPICS[@]}"
do
  echo "Creating topic: $TOPIC"
  kafka-topics.sh --create --topic "$TOPIC" --bootstrap-server $KAFKA_BROKER --replication-factor 1 --partitions 1
  if [ $? -eq 0 ]; then
    echo "Successfully created topic: $TOPIC"
  else
    echo "Failed to create topic: $TOPIC"
  fi
done

# Ensure Kafka runs after the script execution
exec /etc/confluent/docker/run