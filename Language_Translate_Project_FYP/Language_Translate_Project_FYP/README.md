# Language Translator Web App

A full-stack translator app built with Flask (backend) and HTML/CSS/JS (frontend) for my FYP.

## Features
- Text translation using Google Translate API (via googletrans library).
- Document upload and translation (PDF/DOCX).
- Modern glassmorphism UI with dark mode.

## Setup
1. Clone the repo: `git clone https://github.com/MinSiThuk/FYP_UOR.git`
2. Create virtual environment: `python -m venv .venv`
3. Activate it: `.venv\Scripts\activate` (Windows)
4. Install dependencies: `pip install -r requirements.txt`
5. Run the app: `python app.py`
6. Open `http://127.0.0.1:8000`

## Tech Stack
- Backend: Python, Flask
- Frontend: HTML, Tailwind CSS, Vanilla JS
- Translation: googletrans (no API key needed)

## Notes
- .venv is excluded from Git—recreate it locally.
- For production, use a WSGI server like Gunicorn.