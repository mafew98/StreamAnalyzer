The Aim of this project is to query a source of streaming data and run analytics on it. To achieve this, kafka is used to handle the streaming data, pySpark is used to analyse the data and logstash/kibana/opensearch are used to visualize the data.

# Instructions to execute code
The code for this question is split into different parts. Since there are multiple moving components in the specification, dockers were created to isolate the components and easily manage dependencies.

The docker-compose.yaml contains all the services that are created by the project.

Steps to Execute:

1. Run the puppetteer script that orchestrates the whole execution using:
    
        ./puppeteer

        This command will NOT create the kafka topics and will not use dummy data to run the streaming. This is limited since the News API used in this project is limited to 100 API calls per day in the free version.
    
    1.1 If running the command for the first time, the kafka topics must be created before streaming. Run the following to do so:

        ./puppeteer createTopics
    
    1.2 To use dummy Data instead of the actual data from the news API (dummy data is data from the news API stored and collated), run with the following argument
    
        ./puppeteer useDummyData
    
    # NOTE: A first time run should use the following command - ./puppeteer createTopics

    This command will:
          i. Create dockers for zookeeper, kafka, spark, kibana, elasticsearch, logstash.
         ii. Create the required kafka topics (`news-articles` and `named-entities`).
        iii. Start the streaming to kafka from the source.
         iv. Start spark job to run NER on the received headlines.

2. Create visualization on elasticsearch

    2.1 Open elasticsearch on a browser at the following link - http://localhost:5601
    2.2 Go to “Stack Management” > “Kibana > Index Patterns”
	    2.2.1	Click “Create Index Pattern”
	    2.2.2	Enter the index name kafka-index (as configured in logstash.conf)
    2.3 Go to “Visualize”
	    2.3.2   Choose Bar chart
	    2.3.3.	Set the Y-axis to count and select the output as last value of the field
	    2.3.4.	Set the X-axis to the keyword field entitiy.keyword
	    2.3.5.	Use Top values to limit it to the top 10 entries

3. To stop the streaming, run

        ./puppeteer stop
