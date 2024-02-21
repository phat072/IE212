
import streamlit as st
from PIL import Image
import pickle as pkl
import numpy as np

class_list = {'0': 'Clean', '1': 'Hate', '2': 'Offensive'}
st.title("Sentiment analysis from Vietnamese students’ feedback")


image = Image.open('vsfc.jpg')
st.image(image)


image = Image.open('vsfc.jpg')
st.image(image)
# Đảm bảo file lstm_encoder.pkl tồn tại
try:
    with open('lstm_encoder.pkl', 'rb') as input_ec:
        encoder = pkl.load(input_ec)
except FileNotFoundError:
    st.error("Error: 'lstm_encoder.pkl' not found. Please check the file path.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred while loading 'lstm_encoder.pkl': {e}")
    st.stop()
# Đảm bảo file model.pkl tồn tại
try:
    with open('lstm.pkl', 'rb') as input_md:
        model = pkl.load(input_md)
except FileNotFoundError:
    st.error("Error: 'lstm.pkl' not found. Please check the file path.")
    st.stop()
except Exception as e:
    st.error(f"An error occurred while loading 'lstm.pkl': {e}")
    st.stop()

st.header('Write a feedback')
txt = st.text_area(label='', placeholder='Enter your feedback here:')

if txt != '':
    feature_vector = encoder.transform([txt])
    prediction_result = model.predict(feature_vector)

    st.header('Result')
    st.text(class_list[str(prediction_result[0])])
