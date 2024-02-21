# app.py

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

data = {}

@app.route('/', methods=['GET', 'POST'])
def home():
    global data
    
    if request.method == 'POST':
        req = request.json
        
        text = req['text']
        label = req['label']
        
        if label not in data:
            data[label] = []
        
        data[label].append(text)
    
    return render_template('index.html', predictions=data)

if __name__ == '__main__':
    app.run(debug=True)
