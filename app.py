
import os
import time
import mysql.connector
from flask import Flask, request, redirect, render_template, abort

app = Flask(__name__)

def get_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "db"),
        user=os.getenv("DB_USER", "taskuser"),
        password=os.getenv("DB_PASSWORD", "taskpass123"),
        database=os.getenv("DB_NAME", "taskmanager")
    )

def initialize_database():
    for attempt in range(30):
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    priority VARCHAR(20) NOT NULL DEFAULT 'Medium',
                    due_date DATE NULL,
                    completed BOOLEAN NOT NULL DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            db.commit()
            cursor.close()
            db.close()
            return
        except mysql.connector.Error:
            if attempt == 29:
                raise
            time.sleep(2)

def get_task(task_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    cursor.close()
    db.close()

    if task is None:
        abort(404)

    return task

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date") or None

        if not title or len(title) > 200:
            return "Title is required and must be 200 characters or fewer.", 400

        if priority not in ["Low", "Medium", "High"]:
            return "Invalid priority.", 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO tasks (title, description, priority, due_date)
            VALUES (%s, %s, %s, %s)
        """, (title, description, priority, due_date))
        db.commit()
        cursor.close()
        db.close()

        return redirect("/")

    search = request.args.get("q", "").strip()
    status = request.args.get("status", "all")

    db = get_db()
    cursor = db.cursor(dictionary=True)

    query = "SELECT * FROM tasks WHERE title LIKE %s"
    params = ["%" + search + "%"]

    if status == "pending":
        query += " AND completed = FALSE"
    elif status == "completed":
        query += " AND completed = TRUE"

    query += " ORDER BY id DESC"
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    cursor.close()
    db.close()

    return render_template(
        "index.html",
        tasks=tasks,
        search=search,
        status=status
    )

@app.route("/tasks/<int:task_id>/edit", methods=["GET", "POST"])
def edit_task(task_id):
    task = get_task(task_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        priority = request.form.get("priority", "Medium")
        due_date = request.form.get("due_date") or None

        if not title or len(title) > 200:
            return "Title is required and must be 200 characters or fewer.", 400

        if priority not in ["Low", "Medium", "High"]:
            return "Invalid priority.", 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE tasks
            SET title = %s, description = %s,
                priority = %s, due_date = %s
            WHERE id = %s
        """, (title, description, priority, due_date, task_id))
        db.commit()
        cursor.close()
        db.close()

        return redirect("/")

    return render_template("edit.html", task=task)

@app.route("/tasks/<int:task_id>/toggle", methods=["POST"])
def toggle_task(task_id):
    task = get_task(task_id)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE tasks SET completed = %s WHERE id = %s",
        (not task["completed"], task_id)
    )
    db.commit()
    cursor.close()
    db.close()

    return redirect("/")

@app.route("/tasks/<int:task_id>/delete", methods=["POST"])
def delete_task(task_id):
    get_task(task_id)

    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
    db.commit()
    cursor.close()
    db.close()

    return redirect("/")

if __name__ == "__main__":
    initialize_database()
    app.run(host="0.0.0.0", port=5000)

