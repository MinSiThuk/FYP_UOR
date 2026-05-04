from flask import Flask, render_template, request, jsonify, redirect, url_for
import googletrans
from googletrans import Translator
import PyPDF2
import docx
import io
import sqlite3
import datetime
import asyncio
import inspect

app = Flask(__name__)

def sync_translate(*args, **kwargs):
    translator = Translator(service_urls=['translate.googleapis.com', 'translate.google.com', 'translate.google.cn'])
    result = translator.translate(*args, **kwargs)
    if inspect.isawaitable(result):
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(result)
        finally:
            loop.close()
    return result

def init_db():
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY,
        original_text TEXT,
        translated_text TEXT,
        lang TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/text')
def text_translation():
    langs = googletrans.LANGUAGES
    return render_template('text.html', langs=langs)

@app.route('/file')
def file_translation():
    langs = googletrans.LANGUAGES
    return render_template('file.html', langs=langs)

@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.get_json()
    text = data['text']
    dest = data['lang']
    try:
        translated = sync_translate(text, dest=dest)
        conn = sqlite3.connect('translations.db')
        c = conn.cursor()
        c.execute("INSERT INTO history (original_text, translated_text, lang) VALUES (?, ?, ?)", (text, translated.text, dest))
        conn.commit()
        conn.close()
        return jsonify({'translated': translated.text})
    except Exception as e:
        app.logger.exception('Translation failed')
        message = str(e)
        if 'getaddrinfo failed' in message or 'Failed to establish' in message:
            message = 'Translation service is unreachable. Check your internet connection or try again later.'
        return jsonify({'error': message})

@app.route('/upload', methods=['POST'])
def upload_document():
    file = request.files['file']
    lang = request.form['lang']
    if file.filename.lower().endswith('.pdf'):
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file.read()))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
    elif file.filename.lower().endswith('.docx'):
        doc = docx.Document(io.BytesIO(file.read()))
        text = '\n'.join([para.text for para in doc.paragraphs])
    else:
        return jsonify({'error': 'Unsupported file type. Please upload PDF or DOCX.'})
    
    try:
        translated = sync_translate(text, dest=lang)
        conn = sqlite3.connect('translations.db')
        c = conn.cursor()
        c.execute("INSERT INTO history (original_text, translated_text, lang) VALUES (?, ?, ?)", (text[:500], translated.text, lang))  # limit original to 500 chars
        conn.commit()
        conn.close()
        return jsonify({'translated': translated.text})
    except Exception as e:
        app.logger.exception('File translation failed')
        message = str(e)
        if 'getaddrinfo failed' in message or 'Failed to establish' in message:
            message = 'Translation service is unreachable. Check your internet connection or try again later.'
        return jsonify({'error': message})

@app.route('/history')
def history():
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return render_template('history.html', history=rows)

@app.route('/clear_history', methods=['POST'])
def clear_history():
    conn = sqlite3.connect('translations.db')
    c = conn.cursor()
    c.execute("DELETE FROM history")
    conn.commit()
    conn.close()
    from flask import redirect, url_for
    return redirect(url_for('history'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)