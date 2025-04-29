import pika

# Connect to RabbitMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

# Declare a queue
channel.queue_declare(queue='test_queue')

# Publish a message
channel.basic_publish(exchange='', routing_key='test_queue', body='Hello, RabbitMQ!')
print(" [x] Sent 'Hello, RabbitMQ!'")

# Close the connection
connection.close()
