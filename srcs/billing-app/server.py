import json
import os
import time

import pika
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column


dotenv_path = "/vagrant/.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()


class Base(DeclarativeBase):
    pass


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(nullable=False)
    number_of_items: Mapped[str] = mapped_column(nullable=False)
    total_amount: Mapped[str] = mapped_column(nullable=False)


DB_USER = os.getenv("BILLING_DB_USER")
DB_PASS = os.getenv("BILLING_DB_PASSWORD")
DB_HOST = os.getenv("BILLING_DB_HOST")
DB_PORT = os.getenv("BILLING_DB_PORT")
DB_NAME = os.getenv("BILLING_DB_NAME")

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST", "/")
RABBITMQ_USER = os.getenv("RABBITMQ_USER")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASSWORD")
BILLING_QUEUE = os.getenv("BILLING_QUEUE", "billing_queue")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
Base.metadata.create_all(engine)


def save_order(payload):
    required_fields = ("user_id", "number_of_items", "total_amount")
    missing_fields = [field for field in required_fields if field not in payload]
    if missing_fields:
        raise ValueError(f"Missing fields: {', '.join(missing_fields)}")

    order = Order(
        user_id=str(payload["user_id"]),
        number_of_items=str(payload["number_of_items"]),
        total_amount=str(payload["total_amount"]),
    )

    with Session(engine) as session:
        session.add(order)
        session.commit()


def connect_to_rabbitmq():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        virtual_host=RABBITMQ_VHOST,
        credentials=credentials,
        heartbeat=60,
        blocked_connection_timeout=30,
    )

    while True:
        try:
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError as error:
            print(f"RabbitMQ unavailable: {error}. Retrying in 5 seconds...", flush=True)
            time.sleep(5)


def handle_message(channel, method, properties, body):
    try:
        payload = json.loads(body.decode("utf-8"))
        save_order(payload)
        channel.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Processed billing order: {payload}", flush=True)
    except (json.JSONDecodeError, ValueError) as error:
        print(f"Discarding invalid billing message: {error}", flush=True)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as error:
        print(f"Failed to process billing message: {error}", flush=True)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        time.sleep(5)


def main():
    connection = connect_to_rabbitmq()
    channel = connection.channel()
    channel.queue_declare(queue=BILLING_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=BILLING_QUEUE, on_message_callback=handle_message)

    print(f"Billing consumer waiting for messages on {BILLING_QUEUE}", flush=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
