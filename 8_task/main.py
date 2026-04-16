import os
from flask import Flask, request, jsonify
import psycopg2
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432')
    )


def init_db():
    """Создание таблицы при запуске"""
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('''
                CREATE TABLE IF NOT EXISTS pages (
                    id SERIAL PRIMARY KEY,
                    url TEXT,
                    title TEXT,
                    content TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        conn.commit()
    print("Database initialized")


@app.route('/parse')
def parse():
    url = request.args.get('url')
    if not url:
        return "URL parameter is required", 400

    if not url.startswith('http'):
        url = 'http://' + url

    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        title = soup.title.string if soup.title else 'No title'
        content = soup.get_text()[:500]

        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    'INSERT INTO pages (url, title, content) VALUES (%s, %s, %s)',
                    (url, title, content)
                )
            conn.commit()

        return f'Saved: {title}'
    except Exception as e:
        return f'Error: {str(e)}', 500


@app.route('/data')
def get_data():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT id, url, title, content, date FROM pages ORDER BY id DESC')
            rows = cur.fetchall()

    return jsonify([{
        'id': r[0],
        'url': r[1],
        'title': r[2],
        'content': r[3],
        'date': r[4].isoformat() if r[4] else None
    } for r in rows])


@app.route('/')
def index():
    return '''
        <h1>Parser App</h1>
        <a href="/parse?url=https://example.com">Parse example.com</a> |
        <a href="/data">View data</a>
    '''


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)