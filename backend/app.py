from flask import Flask, request, jsonify, render_template_string
import os
import psycopg2

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Fullstack App</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
        }
        input, button {
            padding: 8px;
            margin: 5px;
        }
        li {
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <h1>Full-Stack App</h1>
    <p><b>Student:</b> Madina</p>
    <p><b>ID:</b> 123456</p>

    <h2>Add item</h2>
    <input id="input" placeholder="Enter text">
    <button onclick="addItem()">Add</button>

    <h2>Items</h2>
    <ul id="list"></ul>

    <script>
        const API = "/api/data";

        async function loadItems() {
            const res = await fetch(API);
            const data = await res.json();

            const list = document.getElementById("list");
            list.innerHTML = "";

            data.forEach(item => {
                const li = document.createElement("li");
                li.innerHTML = item.name + " <button onclick='deleteItem(" + item.id + ")'>Delete</button>";
                list.appendChild(li);
            });
        }

        async function addItem() {
            const input = document.getElementById("input");

            if (!input.value.trim()) return;

            await fetch(API, {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({name: input.value})
            });

            input.value = "";
            loadItems();
        }

        async function deleteItem(id) {
            await fetch(API + "/" + id, {
                method: "DELETE"
            });

            loadItems();
        }

        loadItems();
    </script>
</body>
</html>
"""

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
    return render_template_string(HTML_PAGE)

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
