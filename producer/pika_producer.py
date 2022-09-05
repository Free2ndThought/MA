from os import environ
# usage of environment variables to configure the rabbitmq server, see docker-compose.yml
"""
Creates a list of device queues which are taken in round robin scheduling fashion
"""
if __name__ == "__main__":
    if ('RABBIT_HOST' in environ):
        rabbit_host = str(environ['RABBIT_HOST'])  # e.g 10.10.10.2
    else:
        rabbit_host = 'localhost'
    import json
    import zlib
    import time
    from queue import SimpleQueue

    import pika

    from AllnetPoll import AllnetPoll
    from local_config import SETUP_NR, DEVICE_LIST
    from pooling import blocking_delay_generator, round_robin_pooling


    print("Connecting to Allnet-Plugs ... ", )
    devices = ["BLADL_0%d_0%02d" % (SETUP_NR, i) for i in DEVICE_LIST[SETUP_NR]]
    assert len(devices)
    q_list = [SimpleQueue() for device in devices]
    thread_list = [AllnetPoll(dev, q) for dev, q in zip(devices, q_list)]
    [thread.start() for thread in thread_list]
    print("Sucessfully started all Allnet-Crawlers")


    credentials = pika.PlainCredentials('rabbitmq', 'rabbitmq')
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=5672, credentials=credentials))
            break
        except pika.exceptions.AMQPConnectionError: # quit if no connection is possible
            print("Couldn't connect to RabbiMQ # ", i)
            time.sleep(2)

    print("Established Connection to RabbitMQ Server")
    channel = connection.channel() # create a channel

    channel.confirm_delivery() # confirm delivery of messages

    channel.queue_declare(queue='task_queue', durable=True) # create a queue to publish messages to

    prop = pika.BasicProperties(content_type='application/json',
                                content_encoding='zlib',
                                delivery_mode=2,) # Non-persistent (1) or persistent (2).

    print("Unixtime                 Power Measurements")
    for timestamp in blocking_delay_generator(10): # in regular intervals publish existing measurements to rabbitmq channel
        messages = round_robin_pooling(q_list)
        messages = list(messages)
        if len(messages) > 0:
            body = json.dumps(messages, ensure_ascii=False)
            body = body.encode('utf-8')
            body = zlib.compress(body)
            channel.basic_publish(exchange='', routing_key='task_queue',
                                  body=body, properties=prop, mandatory=True)

        print(timestamp, '\t', len(messages))

    assert False
