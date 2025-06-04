from flask import Flask, request, jsonify
from cassandra.cluster import Cluster
import os
import time

app = Flask(__name__)

# Cassandra setup
CASSANDRA_HOST = os.environ.get("CASSANDRA_HOST", "localhost")
KEYSPACE = "testkeyspace"

# Retry until Cassandra is ready
for _ in range(10):
    try:
        cluster = Cluster([CASSANDRA_HOST])
        session = cluster.connect()
        break
    except Exception as e:
        print("Waiting for Cassandra...", str(e))
        time.sleep(5)

# Create keyspace and table
session.execute(f"""
    CREATE KEYSPACE IF NOT EXISTS {KEYSPACE}
    WITH replication = {{ 'class': 'SimpleStrategy', 'replication_factor': '1' }}
""")

session.set_keyspace(KEYSPACE)

session.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id UUID PRIMARY KEY,
        content TEXT
    )
""")

from uuid import uuid4

@app.route('/')
def hello():
    return "Flask + Cassandra is running!"

@app.route('/add', methods=['POST'])
def add_message():
    content = request.json.get("content")
    if not content:
        return jsonify({"error": "Content required"}), 400

    msg_id = uuid4()
    session.execute("INSERT INTO messages (id, content) VALUES (%s, %s)", (msg_id, content))
    return jsonify({"id": str(msg_id), "content": content}), 201

@app.route('/messages', methods=['GET'])
def get_messages():
    rows = session.execute("SELECT id, content FROM messages")
    return jsonify([{"id": str(row.id), "content": row.content} for row in rows])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
