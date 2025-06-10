from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import shutil
import os
import uuid
import subprocess

app = FastAPI()

class MediaRequest(BaseModel):
    image1: str  # Base64 string
    image2: str
    image3: str
    audio: str

def decode_base64(data: str, file_type: str) -> bytes:
    try:
        # Remove header se presente (ex: "data:image/png;base64,")
        if "," in data:
            data = data.split(",")[1]
        return base64.b64decode(data)
    except Exception as e:
        raise HTTPException(400, f"Invalid {file_type} Base64 data: {str(e)}")

@app.post("/merge-media")
async def merge_media(request: MediaRequest):
    session_id = str(uuid.uuid4())
    folder = f"temp/{session_id}"
    os.makedirs(folder, exist_ok=True)

    # Decodificar e salvar arquivos
    def save_file(data: str, filename: str, file_type: str):
        path = f"{folder}/{filename}"
        decoded = decode_base64(data, file_type)
        with open(path, "wb") as f:
            f.write(decoded)
        return path

    try:
        img1 = save_file(request.image1, "1.png", "image1")
        img2 = save_file(request.image2, "2.png", "image2")
        img3 = save_file(request.image3, "3.png", "image3")
        audio_path = save_file(request.audio, "audio.mp3", "audio")

        # Resto do código permanece igual...
        txt_list_path = f"{folder}/list.txt"
        with open(txt_list_path, "w") as f:
            f.write(f"file '{img1}'\nduration 3\n")
            f.write(f"file '{img2}'\nduration 3\n")
            f.write(f"file '{img3}'\nduration 3\n")

        video_path = f"{folder}/video.mp4"
        subprocess.run([
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", txt_list_path,
            "-vsync", "vfr",
            "-pix_fmt", "yuv420p",
            video_path
        ], check=True)

        final_video_path = f"{folder}/final_video.mp4"
        subprocess.run([
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            final_video_path
        ], check=True)

        return FileResponse(final_video_path, media_type="video/mp4", filename="video.mp4")

    except Exception as e:
        shutil.rmtree(folder, ignore_errors=True)
        raise HTTPException(500, f"Processing error: {str(e)}")
