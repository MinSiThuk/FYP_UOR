from flask import Flask, render_template, request, jsonify
import googletrans
from googletrans import Translator
import PyPDF2
import docx
import io

app = Flask(__name__)
translator = Translator()

@app.route('/')
def index():
    langs = googletrans.LANGUAGES
    return render_template('index.html', langs=langs)

@app.route('/translate', methods=['POST'])
async def translate_text():
    data = request.get_json()
    text = data['text']
    dest = data['lang']
    try:
        translated = await translator.translate(text, dest=dest)
        return jsonify({'translated': translated.text})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/upload', methods=['POST'])
async def upload_document():
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
        translated = await translator.translate(text, dest=lang)
        return jsonify({'translated': translated.text})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)