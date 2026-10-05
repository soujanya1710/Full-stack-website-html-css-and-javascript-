from flask import Flask, render_template, request, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_PATH = Path(__file__).with_name("snake.db")

def init_db():
    with sqlite3.connect(DB_PATH) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player TEXT NOT NULL,
                score INTEGER NOT NULL,
                level INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.commit()

@app.route("/")
def index():
    return render_template("index.html")

@app.get("/api/highscores")
def highscores():
    with sqlite3.connect(DB_PATH) as con:
        con.row_factory = sqlite3.Row
        rows = con.execute(
            "SELECT player, score, level, created_at FROM scores "
            "ORDER BY score DESC, id ASC LIMIT 10"
        ).fetchall()
    return jsonify([dict(row) for row in rows])

@app.post("/api/scores")
def save_score():
    data = request.get_json(silent=True) or {}
    player = str(data.get("player", "Player")).strip()[:20] or "Player"
    score = max(0, int(data.get("score", 0)))
    level = max(1, int(data.get("level", 1)))

    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            "INSERT INTO scores (player, score, level) VALUES (?, ?, ?)",
            (player, score, level)
        )
        con.commit()

    return jsonify({"ok": True})

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
