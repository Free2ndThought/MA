FROM python:3.7-stretch

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY device_name_mapping.py .
COPY AllnetPoll.py .
COPY pooling.py .
COPY pika_producer.py .
COPY local_config.py . 
COPY .k.ey .
COPY .credentials.auth .
#COPY wait-for-it.sh .

#CMD ["./wait-for-it.sh", "dbrabbit-container:5672", "--", "python3", "-u", "./pika_producer.py"]
#CMD ["./wait-for-it.sh", "--strict", "dbrabbit-container:5672", "--", "echo", "SATAN"]
CMD ["python3", "-u", "./pika_producer.py"]
