from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from celery import Celery
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
    print("from index")
    if request.method == 'POST':
        print("from post")
        file = request.files.get('audio')
        if not file or file.filename == '':
            print("no file")
            flash('No file selected')
            return redirect(request.url)

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Start transcription
        print("calling transcribe_in_chunks")
        
        transcribe_in_chunks.delay(file_path)

        flash("✅ File uploaded! Transcription started.")
        return redirect(url_for('index'))

    return render_template('index.html')


# Listen to RabbitMQ messages and emit via WebSocket
def rabbitmq_listener():
    connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
    channel = connection.channel()
    channel.queue_declare(queue='transcription_progress')

    def callback(ch, method, properties, body):
        data = json.loads(body)
        print(f"📡 Received progress update: {data}")
        socketio.emit('progress_update', data)

    channel.basic_consume(queue='transcription_progress', on_message_callback=callback, auto_ack=True)
    print("🚀 WebSocket listener started.")
    channel.start_consuming()

@app.before_first_request
def start_background_listener():
    threading.Thread(target=rabbitmq_listener, daemon=True).start()


@socketio.on('connect')
def handle_connect():
    print("✅ Client connected")


# Run app
if __name__ == '__main__':
    socketio.run(app, port=5155)
