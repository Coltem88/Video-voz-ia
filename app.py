
import os
import uuid
import subprocess
from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from TTS.api import TTS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("temp", exist_ok=True)
os.makedirs("static", exist_ok=True)

VIDEO_BASE = "static/base_video.mp4"

# Crear video base si no existe
if not os.path.exists(VIDEO_BASE):
    subprocess.run([
        "ffmpeg", "-f", "lavfi", "-i", "color=c=black:s=640x480:d=10",
        "-pix_fmt", "yuv420p", VIDEO_BASE
    ])

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC", progress_bar=False, gpu=True)

@app.post("/generate-video/")
async def generate_video(text: str = Form(...)):
    audio_path = f"temp/{uuid.uuid4()}.wav"
    output_video = f"temp/{uuid.uuid4()}.mp4"

    tts.tts_to_file(text=text, file_path=audio_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", VIDEO_BASE,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_video
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    return FileResponse(output_video, media_type="video/mp4")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    with open("frontend/index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)
