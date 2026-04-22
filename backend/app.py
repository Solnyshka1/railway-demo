from flask import Flask, request, jsonify
import os
import psycopg2

app = Flask(__name__)

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    return psycopg2.connect(database_url)

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    cur.close()
    conn.close()

@app.route('/')
def home():
    return '<h1>Backend works!</h1><p>API is running on Railway.</p>'

@app.route('/api/data', methods=['GET'])
def get_data():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = [{"id": row[0], "name": row[1]} for row in rows]
    return jsonify(data)

@app.route('/api/data', methods=['POST'])
def add_data():
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Name is required"}), 400

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO items (name) VALUES (%s) RETURNING id, name", (name,))
    row = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": row[0], "name": row[1]}), 201

@app.route('/api/data/<int:item_id>', methods=['DELETE'])
def delete_data(item_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM items WHERE id = %s RETURNING id", (item_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if deleted:
        return jsonify({"message": "Deleted successfully"})
    return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    init_db()
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
