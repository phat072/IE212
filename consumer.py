
from json import loads
from time import sleep
import numpy as np
from kafka import KafkaConsumer

from river import linear_model
from river import compose
from river import preprocessing
from tensorflow.keras.models import load_model
from river import base, optim, metrics
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences


# Load the Keras model
keras_model = tf.keras.models.load_model('lstm.h5')


from river import metrics

# use rocauc as the metric for evaluation
metric = metrics.ROCAUC()

def send_record_to_server(record):
    url = "http://127.0.0.1:5000/"
    try:
        response = requests.post(url, json=record)
        print("Response:", response.text)
    except Exception as e:
        print("Error sending record:", e)

import emoji
from pyvi import ViTokenizer

def deEmojify(text):
    return emoji.demojize(str(text))

def tokenize_with_pyvi(text):
    return ViTokenizer.tokenize(text).split()

def lower_remove_punct(text):
    # Chuyển đổi văn bản thành lowercase
    tokens_lower = [token.lower() for token in text]

    # Loại bỏ dấu câu
    tokens_no_punctuation = [token.strip(".,") for token in tokens_lower]

    # Loại bỏ ký tự đặc biệt
    def remove_special_characters(tokens):
        return [token.replace(':', '').replace('=', '').replace('[', '').replace(']', '').replace(',', '').replace(';', '').replace(')', '').replace('(', '') for token in tokens]

    # Áp dụng hàm loại bỏ ký tự đặc biệt
    tokens_no_special = remove_special_characters(tokens_no_punctuation)

    return tokens_no_special
STOPWORDS = 'vietnamese-stopwords.txt'
with open(STOPWORDS, "r") as ins:
    stopwords = []
    for line in ins:
        dd = line.strip('\n')
        stopwords.append(dd)
    stopwords = set(stopwords)

def filter_stop_words(text, stop_words):
    new_sent = [word for word in text.split() if word not in stop_words]
    text = ' '.join(new_sent)

    return text
def replace_abbreviations(tokens):
    result = []
    for token in tokens:
        for full_word, abbreviations in abbreviations_dict.items():
            if token in abbreviations:
                result.append(full_word)
                break
        else:
            result.append(token)
    return result

abbreviations_dict = {
    'rồi': ['r'],
    'bạn': ['b'],
    'sao': ['s'],
    'được': ['đc'],
    'đéo': ['đ'],
    'không': ['k', 'ko', 'kh', 'kg'],
    'vãi lồn': ['vl', 'vlol'],
    'lồn': ['l', 'lol', 'lz'],
    'cái lồn má': ['clm'],
    'cặc': ['c'],
    'con cặc': ['cc'],
    'cái lồn': ['cl'],
    'vãi cả lồn': ['vcl'],
    'vãi cả cặc': ['vcc'],
    'mày': ['m'],
    "địt mẹ": ['dm', 'đm', 'đme', 'duma'],
    'anh': ['a'],
    'việt nam': ['vn', 'vnam'],
    'vậy': ['v'],
    'em': ['e'],
    'tao': ['t'],
    'con mẹ nó': ['cmn'],
    'người': ['ng'],
    'với': ['vs']
}
def preprocess(text):
    # Xử lý các bước trước
    text = deEmojify(text)
    tokens = tokenize_with_pyvi(text)
    tokens_cleaned = lower_remove_punct(tokens)
    filtered_text = filter_stop_words(" ".join(tokens_cleaned), stopwords)
    final_tokens = replace_abbreviations(filtered_text.split())

    return final_tokens

tokenizer = Tokenizer(oov_token="<OOV>")
max_length = 200
# use each event to update our model and print the metrics

clean_count = 0
offensive_count = 0
hate_count = 0
total_count = 0

def kafka_consumer():
    # create our Kafka consumer
    consumer = KafkaConsumer(
        "training_data",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="my-group-id",
        value_deserializer=lambda x: loads(x.decode("utf-8")),
    )
    try:
        for event in consumer:
            event_data = event.value
            try:
                x = preprocess(event_data["text"])
                print(event_data["text"])
                y = event_data["label"]
                if not x:
                    print("Empty input data. Skipping...")
                    continue
                tokenizer = Tokenizer(oov_token="<OOV>")
                tokenizer.fit_on_texts(x)
                X_sequences = tokenizer.texts_to_sequences(x)
                X_padded = pad_sequences(X_sequences, maxlen=max_length)

                # Check if X_padded is empty
                if not X_padded.any():
                    print("Empty padded sequence. Skipping...")
                    continue

                # Dự đoán
                predictions = keras_model.predict(X_padded)
                predicted_classes = np.argmax(predictions, axis=-1)
                labels = np.array(['CLEAN', 'OFFENSIVE', 'HATE'])
                predicted_labels = labels[predicted_classes]

                unique_labels, counts = np.unique(predicted_labels, return_counts=True)
                percentages = counts / len(predicted_labels) * 100

                # In ra kết quả
                # for label, percentage in zip(unique_labels, percentages):
                #     print(event_data["x"])
                #     if percentage == 100:
                #         print( f"Label: {label}")
                #     else:
                #         print(f"Label: {label}, Phần trăm: {percentage:.2f}%")
                highest_percentage = 0
                highest_label = ""

                for label, percentage in zip(unique_labels, percentages):
                    if percentage != 100 and percentage > highest_percentage:
                        print(f"Label: {label}, Phần trăm: {percentage:.2f}%")
                        highest_percentage = percentage
                        highest_label = label
                    elif percentage == 100:
                        print(f"Label: {label}")
                        highest_percentage = percentage
                        highest_label = label
                        break
                if highest_label == "CLEAN":
                    y_pred = 0
                elif highest_label == "OFFENSIVE":
                    y_pred = 1 
                elif highest_label == "HATE":
                    y_pred = 2 
                metric.update(y, y_pred)
                print(metric)
                # clean_count += np.sum(predicted_labels == 'CLEAN')
                # offensive_count += np.sum(predicted_labels == 'OFFENSIVE')
                # hate_count += np.sum(predicted_labels == 'HATE')
                # total_count += len(predicted_labels)
            except:
                # Clean up resources (e.g., close Kafka consumer)
                consumer.close()
                print("Exiting gracefully...")
                print("Processing bad data...")

    except KeyboardInterrupt:
        print("Kafka consumer interrupted. Calculating overall predicted percentage...")

# Calculate the overall percentages
# overall_percentage = (clean_count + offensive_count + hate_count) / total_count * 100

# print(f"Overall Predicted Percentage: {overall_percentage:.2f}%")
if __name__ == '__main__':
    kafka_consumer()