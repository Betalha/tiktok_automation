from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
import shutil
import os
import uuid
import subprocess

app = FastAPI()

@app.post("/merge-media")
async def merge_media(
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    image3: UploadFile = File(...),
    audio: UploadFile = File(...)
):
    session_id = str(uuid.uuid4())
    folder = f"temp/{session_id}"
    os.makedirs(folder, exist_ok=True)

    def save_file(file: UploadFile, filename: str):
        path = f"{folder}/{filename}"
        with open(path, "wb") as f:
            shutil.copyfileobj(file.file, f)
        return path

    img1 = save_file(image1, "1.png")
    img2 = save_file(image2, "2.png")
    img3 = save_file(image3, "3.png")
    audio_path = save_file(audio, "audio.mp3")

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
