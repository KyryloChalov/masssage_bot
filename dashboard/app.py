from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="dashboard/templates")

DB_PATH = "database.db"


def get_stats():
    with sqlite3.connect(DB_PATH) as conn:
        total_messages = conn.execute(
            "SELECT COUNT(*) FROM gpt_messages"
        ).fetchone()[0]

        total_users = conn.execute(
            "SELECT COUNT(DISTINCT user_id) FROM gpt_messages"
        ).fetchone()[0]

    return total_messages, total_users


def get_users():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT DISTINCT user_id FROM gpt_messages"
        ).fetchall()
    return [r[0] for r in rows]


def get_user_history(user_id):
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            """
            SELECT role, content, created_at
            FROM gpt_messages
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 50
            """,
            (user_id,),
        ).fetchall()

    return rows


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    total_messages, total_users = get_stats()
    users = get_users()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "total_messages": total_messages,
            "total_users": total_users,
            "users": users,
        },
    )


@app.get("/user/{user_id}", response_class=HTMLResponse)
async def user_view(request: Request, user_id: int):
    history = get_user_history(user_id)

    return templates.TemplateResponse(
        "user.html",
        {
            "request": request,
            "user_id": user_id,
            "history": history,
        },
    )