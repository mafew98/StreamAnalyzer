from __future__ import print_function

from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, explode, to_json, struct, lit, desc
from pyspark.sql.types import StringType, ArrayType
import spacy

def getNamedEntities(text):
    """Extract named entities using spaCy."""
    doc = nlp(text)
    return [ent.text.lower() for ent in doc.ents]  # Extract entity text only

if __name__ == "__main__":
    
    bootstrapServers = "kafka:9092"
    inTopic = "news-articles"
    outTopic = "named-entities"

    spark = SparkSession\
        .builder\
        .appName("NamedEntitiesFromHeadlines")\
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("ERROR")

    # Create DataSet representing the stream of input lines from kafka
    lines = spark\
        .readStream\
        .format("kafka")\
        .option("kafka.bootstrap.servers", bootstrapServers)\
        .option("subscribe", inTopic)\
        .load()\
        .selectExpr("CAST(value AS STRING)")

    nlp = spacy.load("en_core_web_sm")

    # UDF to extract entities
    ner_udf = udf(getNamedEntities, ArrayType(StringType()))

    # Assuming `lines` is the input DataFrame from Kafka
    entities_df = lines.withColumn("entities", ner_udf("value"))
    entities_exploded = entities_df.select(explode("entities").alias("entity"))

    # Count named entities
    wordCounts = entities_exploded.groupBy("entity").count()
    
    toStreamVals = wordCounts.orderBy(desc("count")).limit(10)

    # Write to console for debugging. Since the output for this is in the spark docker, attach to see debugging output in the log.
    console_query = toStreamVals.writeStream \
        .outputMode("complete") \
        .format("console") \
        .start()

    # Prepare for Kafka output: key as null, value as JSON string
    output_df = toStreamVals.withColumn("key", lit(None).cast("string")) \
                          .withColumn("value", to_json(struct("entity", "count")))

    # Write to Kafka every minute.
    kafka_query = output_df.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", bootstrapServers) \
        .option("topic", outTopic) \
        .option("checkpointLocation", "/tmp/kafka-ner-checkpoint") \
        .trigger(processingTime="1 minutes") \
        .outputMode("complete") \
        .start()

    kafka_query.awaitTermination()
    console_query.awaitTermination()
