
from flask import Flask
import redis

from celery_config import celery_app
from modules.shared_model import model
import os
from flask import json
import pika
import whisperx




from pydub import AudioSegment


app = Flask(__name__)
app.config.from_object('celery_config')

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)







# tasks.py
from celery import shared_task


@shared_task

def transcribe_in_chunks(file_path, session_id):
    print("📥 Starting transcription task")
    chunks = split_audio(file_path)
    total_chunks = len(chunks)

    for idx, chunk in enumerate(chunks):
        try:
            audio = whisperx.load_audio(chunk)
            result = model.transcribe(audio)
            text = " ".join([seg["text"] for seg in result["segments"]])

            # ✅ Send progress to RabbitMQ with session_id
            progress = int(((idx + 1) / total_chunks) * 100)
            send_progress_to_rabbitmq({
                "progress": progress,
                "chunk": idx + 1,
                "total": total_chunks,
                "filename": os.path.basename(file_path),
                "text": text,
                "session_id": session_id
            })

            print(f"🧠 Chunk {idx + 1}/{total_chunks} Transcribed: {text}")
            print("-" * 60)

        except Exception as e:
            print(f"❌ Error transcribing chunk {idx + 1}: {e}")

        finally:
            try:
                os.remove(chunk)
                print(f"🗑️ Removed chunk: {chunk}")
            except Exception as e:
                print(f"⚠️ Failed to delete chunk {chunk}: {e}")


# 🔊 Utility: Split audio into chunks
def split_audio(file_path, chunk_duration_ms=30_000):
    audio = AudioSegment.from_file(file_path)
    chunks = []
    base, _ = os.path.splitext(file_path)
    for i in range(0, len(audio), chunk_duration_ms):
        chunk = audio[i:i+chunk_duration_ms]
        chunk_path = f"{base}_chunk_{i//chunk_duration_ms}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


# 📨 Send progress to RabbitMQ
def send_progress_to_rabbitmq(progress_data):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
        channel = connection.channel()
        channel.queue_declare(queue="transcription_progress")

        channel.basic_publish(
            exchange="",
            routing_key="transcription_progress",
            body=json.dumps(progress_data)
        )
        connection.close()

        print(f"📤 Sent progress update: {progress_data['progress']}% (Session: {progress_data['session_id']})")

    except Exception as e:
        print(f"❌ Failed to send progress to RabbitMQ: {e}")








def send_progress_to_redis(progress_data):
    try:
        redis_client.publish('transcription_progress', json.dumps(progress_data))
    except Exception as e:
        print(f"❌ Failed to send progress to Redis: {e}")
