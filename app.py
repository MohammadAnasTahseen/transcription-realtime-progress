from uuid import uuid4
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from celery import Celery, uuid
from werkzeug.utils import secure_filename
import os
import threading
import pika
import json
from tasks import transcribe_in_chunks
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['CELERY_BROKER_URL'] = 'amqp://guest:guest@localhost:5672//'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'

# Celery instance
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# SocketIO setup (use eventlet or gevent for production)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/transcribe', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('audio')
        if not file or file.filename == '':
            flash('No file selected')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # 🔥 Generate a session ID
        session_id = str(uuid4())

        print(f"with session ID #################{session_id}")

        # Start transcription task and pass session_id
        transcribe_in_chunks.delay(file_path, session_id)

        flash("✅ File uploaded! Transcription started.")
        return redirect(url_for('index', session_id=session_id))

    # If GET, grab session_id from query params
    session_id = request.args.get('session_id', str(uuid4()))


    print(f"Session ID##############: {session_id}")
    return render_template('index.html',session_id=session_id)






# Listen to RabbitMQ messages and emit via WebSocket
def rabbitmq_listener():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue='transcription_progress')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        session_id = data.get("session_id")
        print(f"📡 Received progress update for session {session_id}: {data}")

        if session_id:
            socketio.emit('progress_update', data, room=session_id)

    channel.basic_consume(queue='transcription_progress', on_message_callback=callback, auto_ack=True)
    print("🚀 WebSocket listener started.")
    channel.start_consuming()

@app.before_first_request
def start_background_listener():
    threading.Thread(target=rabbitmq_listener, daemon=True).start()


@socketio.on('connect')
def handle_connect():
    print("✅ Client connected")



from flask_socketio import join_room

@socketio.on('join')
def on_join(data):
    session_id = data.get('session_id')
    if session_id:
        join_room(session_id)
        print(f"🧩 Client joined room {session_id}")


# Run app
if __name__ == '__main__':
    socketio.run(app, port=5155)
