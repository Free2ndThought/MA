from os import environ

if __name__ == "__main__":
    if 'RABBIT_HOST' in environ and 'RABBITMQ_PORT_CON_EXT' in environ:
        rabbit_host = str(environ['RABBIT_HOST'])  # e.g 10.10.10.2
        rabbit_port = str(environ['RABBITMQ_PORT_CON_EXT'])
    else:
        rabbit_host = 'localhost'
        rabbit_port = 5672
    if ('RABBITMQ_DEFAULT_USER' in environ) and ('RABBITMQ_DEFAULT_PASSWORD' in environ):
        rabbit_user = str(environ['RABBITMQ_DEFAULT_USER'])
        rabbit_password = str(environ['RABBITMQ_DEFAULT_PASSWORD'])
    else:
        print('missing pika credentials in environment')
        exit(10)
    import json
    import zlib
    import time
    from queue import SimpleQueue

    import pika

    from AllnetPoll import AllnetPoll
    from local_config import SETUP_NR, DEVICE_LIST, CREDENTIALS
    from pooling import blocking_delay_generator, round_robin_pooling


    print("Connecting to Allnet-Plugs ... ", )
    devices = ["strommessung_%d" % i for i in DEVICE_LIST[SETUP_NR]]
    assert len(devices)
    q_list = [SimpleQueue() for device in devices]
    thread_list = [AllnetPoll(dev, q, auth=CREDENTIALS) for dev, q in zip(devices, q_list)]
    [thread.start() for thread in thread_list]
    print("Sucessfully started all Allnet-Crawlers")

    # noinspection PyUnboundLocalVariable
    credentials = pika.PlainCredentials(rabbit_user, rabbit_password)
    for i in range(10):
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host, port=rabbit_port, credentials=credentials))
            break
        except pika.exceptions.AMQPConnectionError:
            print("Couldn't connect to RabbiMQ # ", i)
            time.sleep(2)

    print("Established Connection to RabbitMQ Server")
    channel = connection.channel()

    channel.confirm_delivery()

    channel.queue_declare(queue='task_queue', durable=True)

    prop = pika.BasicProperties(content_type='application/json',
                                content_encoding='zlib',
                                delivery_mode=2,) # Non-persistent (1) or persistent (2).

    print("Unixtime                 Power Measurements")
    for timestamp in blocking_delay_generator(10):
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
