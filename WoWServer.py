import sqlite3
import logging
from flask import Flask, request, jsonify

app = Flask(__name__)

# Suppress verbose flask logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

DB_PATH = 'wow_data.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS logs
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  raw_text TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Ingest route for combat logs
@app.route('/log', methods=['POST'])
def handle_log():
    data = request.data.decode('utf-8').strip()

    # Terminal output for monitoring
    if "DAMAGE" in data or "HEAL" in data:
        print(f"Combat event: {data}")
    else:
        print(f"System info: {data[:50]}...")

    # Persistence
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO logs (raw_text) VALUES (?)", (data,))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"DB Write Error: {e}")

    return "OK", 200

# API endpoint for dashboard visualization
@app.route('/data', methods=['GET'])
def get_data():
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        # Fetch latest 100 entries for polling
        c.execute("SELECT raw_text FROM logs ORDER BY timestamp DESC LIMIT 100")
        rows = c.fetchall()
        conn.close()
        
        return jsonify([row[0] for row in rows])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    init_db()
    print("--- Receiver active ---")
    print(f"Target DB: {DB_PATH}")
    print("Listening on port 5000...")
    app.run(host='0.0.0.0', port=5000)