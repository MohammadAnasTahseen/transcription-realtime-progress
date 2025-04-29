# from celery import Celery
# import logging
# # Configure the Celery app
# celery_app = Celery(
#     "transcription_tasks",
#     broker='amqp://guest:guest@localhost:5672//',  # Redis as the message broker
#     backend='rpc://' # Redis for result storageng Redis for result storage
# )


# celery_app.conf.task_routes = {
#       'tasks.transcribe_in_chunks': {'queue': 'transcription_queue'}  # Assign the task 'add' to 'test_queue'
# }


# # Celery configurations (optional)
# celery_app.conf.update(
#     task_serializer="json",
#     accept_content=["json"],
#     result_serializer="json",
#     timezone="UTC",
#     enable_utc=True,
# )

# # Configure Celery to use Python logging
# celery_app.conf.update(
#     worker_log_format='%(asctime)s - %(levelname)s - %(message)s',
#     worker_task_log_format='%(asctime)s - %(levelname)s - Task %(task_name)s [%(task_id)s] started with result: %(result)s'
# )

# # Initialize logging
# logger = logging.getLogger('celery')
# logger.setLevel(logging.INFO)
# console_handler = logging.StreamHandler()
# formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# console_handler.setFormatter(formatter)
# logger.addHandler(console_handler)

# celery_app.autodiscover_tasks(['tasks']) 


from celery import Celery
import logging

# Configure the Celery app
celery_app = Celery(
    "transcription_tasks",
    broker='amqp://guest:guest@localhost:5672//',  # RabbitMQ as the message broker
    backend=None,  # Use 'rpc://' if you still want results
)

# Optional: Configure task routes (if you need specific queue routing)
celery_app.conf.task_routes = {
    'tasks.transcribe_in_chunks': {'queue': 'transcription_queue'}  # Assign the task to 'transcription_queue'
}

# Celery configurations
celery_app.conf.update(
    task_serializer="json",  # Serialize tasks to JSON
    accept_content=["json"],  # Only accept JSON content
    result_serializer="json",  # Serialize results to JSON
    timezone="UTC",  # Timezone configuration
    enable_utc=True,  # Enable UTC time for tasks
    task_ignore_result=True,  # Ignore storing task results (to save memory)
    result_persistent=False,  # Don't persist task results
)

# Worker logging configuration
celery_app.conf.update(
    worker_log_format='%(asctime)s - %(levelname)s - %(message)s',  # Format for worker logs
    worker_task_log_format='%(asctime)s - %(levelname)s - Task %(task_name)s [%(task_id)s] started with result: %(result)s'
)

# Initialize logging for the Celery app
logger = logging.getLogger('celery')
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Automatically discover tasks in the 'tasks' module
celery_app.autodiscover_tasks(['tasks'])
