from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import base64
import tempfile
import shutil
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, CompositeVideoClip
import uuid
import os
import uvicorn

app = FastAPI()

class VideoRequest(BaseModel):
    image1: str  # Base64 com header (ex: "data:image/png;base64,...")
    image2: str
    image3: str
    audio: str

def decode_and_save(base64_str: str, file_type: str, temp_dir: str):
    try:
        if "," in base64_str:
            header, data = base64_str.split(",", 1)
            mime_type = header.split(":")[1].split(";")[0]
        else:
            data = base64_str
            mime_type = file_type

        extension = {
            "image/png": "png",
            "image/jpeg": "jpg",
            "audio/mpeg": "mp3",
            "audio/wav": "wav"
        }.get(mime_type, "bin")

        file_path = os.path.join(temp_dir, f"{uuid.uuid4()}.{extension}")
        decoded = base64.b64decode(data)

        with open(file_path, "wb") as f:
            f.write(decoded)

        return file_path
    except Exception as e:
        raise HTTPException(400, f"Erro ao decodificar {file_type}: {str(e)}")

@app.post("/generate-video")
async def generate_video(request: VideoRequest):
    temp_dir = tempfile.mkdtemp()
    try:
        imagens = [
            decode_and_save(request.image1, "image1", temp_dir),
            decode_and_save(request.image2, "image2", temp_dir),
            decode_and_save(request.image3, "image3", temp_dir)
        ]
        audio_path = decode_and_save(request.audio, "audio", temp_dir)

        LARGURA = 720
        ALTURA = 1280

        audio_clip = AudioFileClip(audio_path)
        duracao_total = audio_clip.duration
        duracao_por_imagem = duracao_total / 3

        clips = []
        for img_path in imagens:
            img_clip = ImageClip(img_path).set_duration(duracao_por_imagem)

            if img_clip.h > img_clip.w:
                img_clip = img_clip.resize(height=ALTURA)
            else:
                img_clip = img_clip.resize(width=LARGURA)

            final_clip = CompositeVideoClip(
                [img_clip.set_position("center")],
                size=(LARGURA, ALTURA)
            )
            clips.append(final_clip)

        video = concatenate_videoclips(clips, method="compose")
        video = video.set_audio(audio_clip)

        output_path = os.path.join(temp_dir, "output.mp4")
        video.write_videofile(
            output_path,
            codec="libx264",
            audio_codec="aac",
            fps=30,
            threads=4
        )

        with open(output_path, "rb") as video_file:
            video_base64 = base64.b64encode(video_file.read()).decode("utf-8")

        return {
            "video": f"data:video/mp4;base64,{video_base64}",
            "duration": duracao_total
        }

    except Exception as e:
        raise HTTPException(500, f"Erro na geração do vídeo: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

# Entry point para Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
