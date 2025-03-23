import pika
import json

from app.config import RABBITMQ_HOST, EXCHANGE_NAME

def get_rabbitmq_channel():
    '''
       connect to the rabbitmq and return the channel
    '''
    connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
    channel = connection.channel()
    
    # Declare the fanout exchange
    channel.exchange_declare(exchange=EXCHANGE_NAME, exchange_type='fanout')
    
    return channel

def publish_task(task: dict):
    '''
        publish the task to the rabbitmq
    '''
    channel = get_rabbitmq_channel()
    channel.basic_publish(exchange=EXCHANGE_NAME, routing_key='', body=json.dumps(task))
    print(f" [x] Sent {task}")
    channel.close()