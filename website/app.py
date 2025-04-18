from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = 'your_secret_key_here'

ALLOWED_EXTENSIONS = {'json'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)


@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Process data
        with open(filepath) as f:
            data = json.load(f)

        metrics = process_data(data)
        return render_template('report.html', metrics=metrics)

    return redirect(request.url)


def process_data(data):
    metrics = 1
    metrics.total_messages = 10
    metrics.longest_convo.length = 5
    metrics.total_energy_wh = 40
    return metrics
