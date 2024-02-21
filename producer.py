from time import sleep
from json import dumps
import random
import pandas as pd

from river import datasets
from kafka import KafkaProducer

# create a kafka product that connects to Kafka on port 9092
producer = KafkaProducer(
    bootstrap_servers=["localhost:9092"],
    value_serializer=lambda x: dumps(x).encode("utf-8"),
)

# Initialize the River phishing dataset.
# This dataset contains features from web pages 
# that are classified as phishing or not.
# Path to the CSV file
csv_file_path = 'data/room_1/test1.csv'

# Read the CSV file using pandas
dataset = pd.read_csv(csv_file_path)

# Iterate over rows of the dataset and send observations to the Kafka topic
for index, row in dataset.iterrows():
    text = row['free_text']  # Assuming 'x' is the feature column name
    label = row['label_id']  # Assuming 'y' is the label column name
    
    print(f"Sending: {text, label}")
    data = {"text": text, "label": label}
    producer.send("training_data", value=data)
    sleep(random.random())