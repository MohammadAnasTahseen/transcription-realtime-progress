# import os
# from flask import json
# import pika
# import whisperx

# from .shared_model import model

# # model = whisperx.load_model(
# #     r"D:\Media_Github\media_live\media_content_analysis\models\models--Systran--faster-whisper-large-v2\snapshots\f0fe81560cb8b68660e564f55dd99207059c092e",
# #     device="cuda"
# # )
# from pydub import AudioSegment


# def split_audio(file_path, chunk_duration_ms=30_000):
#     audio = AudioSegment.from_file(file_path)
#     chunks = []
#     base, _ = os.path.splitext(file_path)
#     for i in range(0, len(audio), chunk_duration_ms):
#         chunk = audio[i:i+chunk_duration_ms]
#         chunk_path = f"{base}_chunk_{i//chunk_duration_ms}.wav"
#         chunk.export(chunk_path, format="wav")
#         chunks.append(chunk_path)
#     return chunks






# # def transcribe_in_chunks(file_path):
# #     chunks = split_audio(file_path)

# #    # Or globally load for performance

# #     for idx, chunk in enumerate(chunks):
# #         try:
# #             audio = whisperx.load_audio(chunk)
# #             result = model.transcribe(audio)

# #             text = " ".join([seg["text"] for seg in result["segments"]])


       
            
# #             print("🧠 Chunk Transcription:")
# #             print(text)
# #             print("-" * 60)

# #         except Exception as e:
# #             print(f"❌ Error transcribing {chunk}: {e}")

# #         finally:
# #             try:
# #                 os.remove(chunk)
# #                 print(f"🗑️ Removed chunk: {chunk}")
# #             except Exception as e:
# #                 print(f"⚠️ Failed to delete {chunk}: {e}")


# def transcribe_in_chunks(file_path):
#     chunks = split_audio(file_path)
#     total_chunks = len(chunks)

#     for idx, chunk in enumerate(chunks):
#         try:
#             audio = whisperx.load_audio(chunk)
#             result = model.transcribe(audio)
#             text = " ".join([seg["text"] for seg in result["segments"]])

#             # Send progress to RabbitMQ
#             progress = int(((idx + 1) / total_chunks) * 100)
#             send_progress_to_rabbitmq({
#                 "progress": progress,
#                 "chunk": idx + 1,
#                 "total": total_chunks,
#                 "filename": os.path.basename(file_path)
#             })

#             print("🧠 Chunk Transcription:")
#             print(text)
#             print("-" * 60)

#         except Exception as e:
#             print(f"❌ Error transcribing {chunk}: {e}")

#         finally:
#             try:
#                 os.remove(chunk)
#                 print(f"🗑️ Removed chunk: {chunk}")
#             except Exception as e:
#                 print(f"⚠️ Failed to delete {chunk}: {e}")






# def send_progress_to_rabbitmq(progress_data):
#     try:
#         connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
#         channel = connection.channel()
#         channel.queue_declare(queue='transcription_progress')
#         channel.basic_publish(
#             exchange='',
#             routing_key='transcription_progress',
#             body=json.dumps(progress_data)
#         )
#         connection.close()
#     except Exception as e:
#         print(f"❌ Failed to send progress to RabbitMQ: {e}")
