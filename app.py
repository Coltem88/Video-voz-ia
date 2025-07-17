from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

class TextInput(BaseModel):
    text: str

@app.get("/")
async def read_index():
    return FileResponse("frontend/index.html")

@app.post("/generate")
async def generate_audio(input: TextInput):
    text = input.text
    output_path = "output.mp3"
    os.system(f'gtts-cli "{text}" --output {output_path}')
    return JSONResponse({"audio_url": f"/{output_path}"})

@app.get("/output.mp3")
async def get_audio():
    return FileResponse("output.mp3", media_type="audio/mpeg")
