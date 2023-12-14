FROM python:3.10-bookworm

RUN apt update && apt install ffmpeg -y

RUN apt clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "main.py"]
