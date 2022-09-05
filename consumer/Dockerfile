FROM python:3.7-stretch

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

RUN useradd --create-home appuser
WORKDIR /home/appuser
USER appuser

COPY wait-for-it.sh .
COPY pika_consumer.py .
COPY .env .

#RUN ./wait-for-it.sh dmis_db:5432 -- python3 -u ./pika_consumer.py

CMD ["python3", "-u", "./pika_consumer.py"]
