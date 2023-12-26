import os
import hashlib

from io import BytesIO

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import sql

from .generate import speak
from .db import SESSION_MAKER, WAVs

app = FastAPI()


class GenerateAndSaveQuery(BaseModel):
    text: str


def generate_audio_card(hash: str, text: str) -> str:
    return f"""
    <div class="my-col col-xs-6 col-md-4 col-lg-2">
        <div class="card">
            <div class="card-body">
                <h5 class="card-title">{text}</h5>
                <audio controls="true"><source src="http://$host$/wav/{hash}" type="audio/wav" preload="none"></audio>
            </div>
        </div>
    </div>
    """


@app.get("/", response_class=HTMLResponse)
def index() -> str:

    with SESSION_MAKER() as session:
        entries = session.query(WAVs).order_by(WAVs.created_at.desc()).all()
        audios = [generate_audio_card(e.hash, e.text) for e in entries]

    with open(os.path.join("web-resources", "index.html")) as f:
        return f.read().replace("{{ div_content }}", "\n".join(audios))


@app.post("/generate")
def generate_and_save(query: GenerateAndSaveQuery) -> str:

    text = query.text
    text_hash = hashlib.sha256(text.lower().encode()).hexdigest()

    with SESSION_MAKER() as session:
        if session.query(sql.exists(WAVs).where(WAVs.hash == text_hash)).scalar():
            return text_hash

    file = speak(text)

    with SESSION_MAKER() as session:
        session.add(WAVs(text_hash, text, file.read()))
        session.commit()

    return text_hash


@app.get("/wav/{hash}", response_class=StreamingResponse)
def send_wav(hash: str) -> StreamingResponse:

    with SESSION_MAKER() as session:
        if not session.query(sql.exists(WAVs).where(WAVs.hash == hash)).scalar():
            return StreamingResponse(BytesIO(), status_code=404)

        row: WAVs = session.execute(sql.select(WAVs).where(WAVs.hash == hash)).scalar()
        file = BytesIO(initial_bytes=row.binary)

    return StreamingResponse(file, media_type="audio/wav")


@app.get("/res/{file}", response_class=FileResponse)
def send_web_resource(file: str) -> str:
    return os.path.join("web-resources", file)


@app.get("/favicon.ico", response_class=FileResponse)
def send_web_resource() -> str:
    return os.path.join("web-resources", "favicon.ico")
