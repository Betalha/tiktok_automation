# 🖼️🎵 Gerador de Vídeo com FastAPI

Este projeto é uma API desenvolvida com **FastAPI** que recebe 3 imagens e 1 arquivo de áudio (todos em formato Base64), gera um vídeo com as imagens exibidas em sequência sincronizadas com o áudio e retorna o vídeo final no formato MP4.

## ✨ Funcionalidades

- Recebe imagens e áudio via JSON codificados em Base64.
- Redimensiona e ajusta imagens automaticamente para um vídeo no formato **720x1280 (vertical)**.
- Divide o tempo de exibição de cada imagem igualmente com base na duração do áudio.
- Retorna o vídeo final como resposta binária (`video/mp4`).

---

## 🚀 Requisitos

- Python 3.8+
- [ffmpeg](https://ffmpeg.org/download.html) instalado e disponível no PATH (necessário para `moviepy` funcionar corretamente).

---

## 📦 Instalação

1. Clone o repositório:

```bash
git clone [https://github.com/Betalha/tiktok_automation.git]
