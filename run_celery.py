# import os
# import subprocess

# # Set PYTHONPATH to the current directory
# os.environ['PYTHONPATH'] = os.getcwd()

# # Run the celery command
# celery_command = ['celery', '-A', 'celery_config.celery_app', 'worker', '--loglevel=info', '-P', 'eventlet', '--concurrency=4']

# subprocess.run(celery_command)


import os
import subprocess

# Set PYTHONPATH to the current directory
os.environ['PYTHONPATH'] = os.getcwd()

# Define the Celery command
celery_command = [
    'celery', '-A', 'celery_config.celery_app', 'worker',
    '--loglevel=info', '-P', 'eventlet', '--concurrency=4'
]

# Define the command to run the Flask app
flask_command = ['python', 'app.py']

# Run both processes concurrently
try:
    # Start the Celery worker
    celery_process = subprocess.Popen(celery_command)
    
    # Start the Flask application
    flask_process = subprocess.Popen(flask_command)

    # Wait for both processes to complete
    celery_process.wait()
    flask_process.wait()
except KeyboardInterrupt:
    # Terminate both processes if interrupted
    celery_process.terminate()
    flask_process.terminate()
    print("\nProcesses terminated.")
