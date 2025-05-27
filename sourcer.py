import sys
import json
from kafka import KafkaProducer
from newsapi import NewsApiClient
from datetime import datetime, timedelta
from time import sleep
import random

useDummyData = len(sys.argv) > 1 and sys.argv[1] == 'useDummyData'
KAFKA_TOPIC = 'news-articles'
KAFKA_BROKER = 'localhost:29092'
START_TIMESTAMP = datetime.now() - timedelta(days=1)
END_TIMESTAMP = datetime.now()

dummy_data = None
if (useDummyData):
    with open('dummyData.json') as json_file:
        dummy_data = json.load(json_file)
    dummy_data = dummy_data['articles']

# Setting up the Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Initialize the news api
newsapi = NewsApiClient(api_key='1339c8bf90c14fcfa1a49363c82084df')

'''
    Fetches one day's worth of news articles per fetch.
    Since there is a limit to the amount of API calls that can be done, usage of this is limited.
'''
def fetch_news():
    global START_TIMESTAMP, END_TIMESTAMP
    print("===================================================================")
    print("Pulled -> from {} to {}".format(START_TIMESTAMP, END_TIMESTAMP))
    print("===================================================================")
    startStamp, endStamp = START_TIMESTAMP.isoformat("T", "seconds"), END_TIMESTAMP.isoformat("T", "seconds")
    articles = newsapi.get_everything(language='en', 
                                      sources='the-verge, techcrunch, the-next-web, cnn, associated-press', 
                                      from_param=startStamp, 
                                      to=endStamp, 
                                      sort_by='publishedAt')
    END_TIMESTAMP = START_TIMESTAMP
    START_TIMESTAMP -= timedelta(days=1) 
    return articles

def fetch_dummy_data():
    print("===================================================================")
    print("DUMMY DATA")
    print("===================================================================")
    global dummy_data
    random_items = []
    for _ in range(5):
        random_items.append(dummy_data[random.randint(0, len(dummy_data) - 1)])
    return random_items
    
def sendToKafka():
    while True:
        if (useDummyData):
            news_articles = fetch_dummy_data()
        else:
            news_articles = fetch_news()['articles']
        for article in news_articles:
            producer.send(KAFKA_TOPIC, article['title'])
            print(f"Sent: {article['title']}")      # Sending only the headlines to run the analysis on.
        sleep(60)  # fetch every 60 seconds
    
if __name__ == '__main__':
    sendToKafka()