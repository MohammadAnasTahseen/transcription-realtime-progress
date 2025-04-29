import sys
import whisperx

model = None

def load_transcription_models():
    global model
    # MODEL_PATH = r"models\models--Systran--faster-whisper-large-v2\snapshots\f0fe81560cb8b68660e564f55dd99207059c092e"
    # MODEL_DEVICE = "cuda"

    print("📥 Loading WhisperX model...")
    # model = whisperx.load_model(MODEL_PATH, device=MODEL_DEVICE)
        
    model = whisperx.load_model(
        r"D:\Media_Github\media_live\media_content_analysis\models\models--Systran--faster-whisper-large-v2\snapshots\f0fe81560cb8b68660e564f55dd99207059c092e",
        device="cuda"
    )
    print("✅ WhisperX model loaded successfully!")

def is_celery_worker():
    return "celery" in sys.argv[0] or "worker" in sys.argv

# Only load the model if this is a Celery worker process
if is_celery_worker():
    load_transcription_models()
else:
    print("🚫 Skipping model loading: Not a Celery worker.")


