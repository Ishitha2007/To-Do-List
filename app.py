from flask import Flask, redirect, render_template, request, url_for
import sqlite3
from pathlib import Path

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "tasks.db"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()


@app.route("/", methods=["GET"])
def index():
    with get_db_connection() as conn:
        tasks = conn.execute(
            "SELECT id, title, completed FROM tasks ORDER BY id DESC"
        ).fetchall()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title", "").strip()
    if title:
        with get_db_connection() as conn:
            conn.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
            conn.commit()
    return redirect(url_for("index"))


@app.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id: int):
    with get_db_connection() as conn:
        task = conn.execute(
            "SELECT completed FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if task is not None:
            new_value = 0 if task["completed"] else 1
            conn.execute(
                "UPDATE tasks SET completed = ? WHERE id = ?", (new_value, task_id)
            )
            conn.commit()
    return redirect(url_for("index"))


@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id: int):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
