from flask import Flask, request, jsonify
import psycopg2
import requests
from bs4 import BeautifulSoup


load_dotenv()

app = Flask(__name__)

conn = psycopg2.connect(
    database=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT', '5432')
)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS pages (id SERIAL PRIMARY KEY, url TEXT, title TEXT, content TEXT)')
conn.commit()

@app.route('/parse')
def parse():
    url = request.args.get('url')
    if not url.startswith('http'): url = 'http://' + url
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.title.string if soup.title else 'No title'
    content = soup.get_text()[:500]
    
    cur = conn.cursor()
    cur.execute('INSERT INTO pages (url, title, content) VALUES (%s, %s, %s)', (url, title, content))
    conn.commit()
    return f'Saved: {title}'

@app.route('/data')
def get_data():
    cur = conn.cursor()
    cur.execute('SELECT id, url, title, content FROM pages')
    rows = cur.fetchall()
    return jsonify([{'id': r[0], 'url': r[1], 'title': r[2], 'content': r[3]} for r in rows])

@app.route('/')
def index():
    return '<a href="/parse?url=https://example.com">Parse example.com</a> | <a href="/data">View data</a>'

if __name__ == '__main__':
    app.run()