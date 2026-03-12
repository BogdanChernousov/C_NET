# main.py
from flask import Flask, request, jsonify
import psycopg2
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)

# Функция для подключения к БД
def get_db_connection():
    return psycopg2.connect(
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432')
    )

# Инициализация БД
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS pages (
        id SERIAL PRIMARY KEY, 
        url TEXT, 
        title TEXT, 
        content TEXT,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()

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
        
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('INSERT INTO pages (url, title, content) VALUES (%s, %s, %s)', (url, title, content))
        conn.commit()
        conn.close()
        
        return f'Saved: {title}'
    except Exception as e:
        return f'Error: {str(e)}', 500

@app.route('/data')
def get_data():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, url, title, content, date FROM pages ORDER BY id DESC')
    rows = cur.fetchall()
    conn.close()
    
    return jsonify([{
        'id': r[0], 
        'url': r[1], 
        'title': r[2], 
        'content': r[3],
        'date': r[4]
    } for r in rows])

@app.route('/')
def index():
    return '''
        <h1>Parser App</h1>
        <a href="/parse?url=https://example.com">Parse example.com</a> | 
        <a href="/data">View data</a>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)