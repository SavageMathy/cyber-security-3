"""Aplicación segura para la evaluación OCY1102 EV3."""

import os
import sqlite3
from pathlib import Path
from markupsafe import escape  # Para sanitizar XSS

from flask import Flask, abort, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


def create_app(database_path=None):
    app = Flask(__name__)
    # VULN 1 CORREGIDA: Se elimina el valor por defecto inseguro. Si no hay SECRET_KEY, la app falla al iniciar.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    if not app.config["SECRET_KEY"]:
        raise ValueError("La variable de entorno SECRET_KEY es obligatoria para iniciar la aplicación.")
    
    app.config["DATABASE_PATH"] = str(
        database_path or os.getenv("DATABASE_PATH", str(Path(__file__).with_name("securedev.db")))
    )

    def db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE_PATH"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error):
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()

    with app.app_context():
        Path(app.config["DATABASE_PATH"]).parent.mkdir(parents=True, exist_ok=True)
        connection = db()
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS tickets (
                id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                body TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY,
                ticket_id INTEGER NOT NULL,
                author_id INTEGER NOT NULL,
                body TEXT NOT NULL
            );
            """
        )
        if connection.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            connection.executemany(
                "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                [
                    (1, "ana", generate_password_hash("ana123")),
                    (2, "bruno", generate_password_hash("bruno123")),
                ],
            )
            connection.executemany(
                "INSERT INTO tickets (id, owner_id, title, body) VALUES (?, ?, ?, ?)",
                [
                    (1, 1, "Revisión de despliegue", "Preparar evidencias de CI/CD."),
                    (2, 2, "Acceso al panel", "Revisar registros de acceso."),
                ],
            )
        connection.commit()

    def current_user():
        return session.get("user_id")

    @app.route("/")
    def index():
        if not current_user():
            return redirect(url_for("login"))
        tickets = db().execute(
            "SELECT id, title FROM tickets WHERE owner_id = ? ORDER BY id", (current_user(),)
        ).fetchall()
        return render_template("index.html", tickets=tickets)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        error = None
        if request.method == "POST":
            username = request.form.get("username", "")
            password = request.form.get("password", "")
            user = db().execute(
                "SELECT id, username, password_hash FROM users WHERE username = ?", (username,)
            ).fetchone()
            if user and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("index"))
            error = "Credenciales inválidas"
        return render_template("login.html", error=error)

    @app.post("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.get("/tickets/<int:ticket_id>")
    def ticket(ticket_id):
        if not current_user():
            return redirect(url_for("login"))
        # VULN 2 CORREGIDA (IDOR): Se agrega owner_id = ? para verificar que el ticket pertenece al usuario
        item = db().execute(
            "SELECT id, owner_id, title, body FROM tickets WHERE id = ? AND owner_id = ?", 
            (ticket_id, current_user())
        ).fetchone()
        if item is None:
            abort(404) # No revelamos si el ticket existe o no (evita enumeración)
        comments = db().execute(
            "SELECT body FROM comments WHERE ticket_id = ? ORDER BY id", (ticket_id,)
        ).fetchall()
        return render_template("ticket.html", ticket=item, comments=comments)

    @app.post("/tickets/<int:ticket_id>/comments")
    def add_comment(ticket_id):
        if not current_user():
            return redirect(url_for("login"))
        # Verificación de propiedad antes de permitir comentar
        if db().execute("SELECT id FROM tickets WHERE id = ? AND owner_id = ?", (ticket_id, current_user())).fetchone() is None:
            abort(404)
        body = request.form.get("body", "")
        # VULN 3 CORREGIDA (XSS): Sanitizamos el input antes de guardarlo
        safe_body = str(escape(body))
        db().execute(
            "INSERT INTO comments (ticket_id, author_id, body) VALUES (?, ?, ?)",
            (ticket_id, current_user(), safe_body),
        )
        db().commit()
        return redirect(url_for("ticket", ticket_id=ticket_id))

    @app.get("/search")
    def search():
        if not current_user():
            return redirect(url_for("login"))
        query = request.args.get("q", "")
        # VULN 4 CORREGIDA (SQLi): Se usan consultas parametrizadas (?) en lugar de f-strings
        sql = "SELECT id, title FROM tickets WHERE title LIKE ? ORDER BY id"
        search_term = f"%{query}%"
        tickets = db().execute(sql, (search_term,)).fetchall()
        return render_template("search.html", tickets=tickets, query=query)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


if __name__ == "__main__":
    # Se recomienda usar un servidor WSGI como gunicorn en producción, no el debug de Flask
    create_app().run(host="0.0.0.0", port=8000)