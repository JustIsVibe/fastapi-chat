from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy
from datetime import datetime, timedelta
import pytz

from .database import SessionLocal, engine
from .models import Base

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Встановлюємо часовий пояс +2 години
tz = pytz.FixedOffset(120)  # +120 хвилин = UTC+2

async def get_db():
    async with SessionLocal() as session:
        yield session

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(sqlalchemy.text("SELECT * FROM messages ORDER BY created_at DESC LIMIT 20"))
    messages = result.fetchall()
    return templates.TemplateResponse("index.html", {"request": request, "messages": messages})

@app.post("/send", response_class=HTMLResponse)
async def send_message(
    request: Request,
    username: str = Form(...),
    message_text: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    created_at = datetime.now(tz)

    await db.execute(
        sqlalchemy.text("INSERT INTO messages (username, text, created_at) VALUES (:username, :text, :created_at)"),
        {"username": username, "text": message_text, "created_at": created_at}
    )
    await db.commit()

    msg = {
        "username": username,
        "text": message_text,
        # created_at потрібен лише якщо захочеш знову відображати
    }

    return templates.TemplateResponse("partials/message.html", {"request": request, "msg": msg})
