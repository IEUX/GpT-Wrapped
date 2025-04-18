from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import json
from datetime import datetime
import os
import json
from pprint import pprint
from time import strftime, localtime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
total_prompt_count = 0

ALLOWED_EXTENSIONS = {'json'}


class metrics:
    def __init__(self, total_chat_count, total_char_count, total_token_count, total_co2_emissions, total_prompt_count):
        self.total_chat_count = total_chat_count
        self.total_char_count = total_char_count
        self.total_token_count = total_token_count
        self.total_co2_emissions = total_co2_emissions
        self.total_prompt_count = total_prompt_count


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

        chatgpt_metrics = process_data(data)
        return render_template('report.html', metrics=chatgpt_metrics)

    return redirect(request.url)


def process_data(data):
    chars = get_all_GPT_character(data)
    total_chat_count = len(data)
    total_char_count = len(chars)
    total_token_count = char_to_token(len(chars))
    total_co2_emissions = co2_emission_kg(char_to_token(len(chars)))

    chatgpt_metrics = metrics(total_chat_count, total_char_count, total_token_count, total_co2_emissions, total_prompt_count)
    return chatgpt_metrics


def co2_emission_kg(tokens):
    return int(((tokens*2)/400)/1000)


def get_all_GPT_character(json_export):
    global total_prompt_count
    model_conversation_fields =['id', 'message', 'parent', 'children']
    model_message_fields = ['id', 'author', 'create_time', 'update_time', 'content', 'status', 'end_turn', 'weight', 'metadata', 'recipient', 'channel']
    all_chat_char = []
    for chat in json_export:
        chat_sum = 0
        for conversation in list(chat["mapping"].keys())[1:]:
            if list(chat["mapping"][conversation].keys()) == model_conversation_fields and chat["mapping"][conversation]["message"] != None:
                if list(chat["mapping"][conversation]["message"].keys()) == model_message_fields:
                    if chat["mapping"][conversation]["message"]['author']['role'] == "assistant":
                        if "parts" in chat["mapping"][conversation]["message"]["content"].keys():
                            messages = chat["mapping"][conversation]["message"]["content"]["parts"][0]
                            content = []
                            if type(messages) == str:
                                total_prompt_count = total_prompt_count + 1
                                for message in messages.split("\n"):
                                    for char in list(message):
                                        content.append(char)
                                        all_chat_char.append(char)
                                chat_sum = chat_sum + len(content)
    return all_chat_char


def char_to_token(chars):
    return int(chars/4)
