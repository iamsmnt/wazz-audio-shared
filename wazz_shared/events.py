"""
Event infrastructure for publishing domain events to RabbitMQ.

Provides event payload models and a synchronous EventPublisher
that publishes to a topic exchange. Designed to be used by the
backend (sync FastAPI endpoints) to emit domain events that are
consumed by decoupled services (e.g. the email service).
"""

import json
import logging
from datetime import datetime
from typing import Optional

import pika
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Event routing keys (used as RabbitMQ routing keys on the topic exchange)
# ---------------------------------------------------------------------------
USER_REGISTERED = "user.registered"
USER_VERIFIED = "user.verified"
USER_PASSWORD_RESET_REQUESTED = "user.password_reset_requested"

# ---------------------------------------------------------------------------
# Event payload models
# ---------------------------------------------------------------------------


class BaseEvent(BaseModel):
    """Base event with common metadata."""

    event_type: str
    timestamp: datetime


class UserRegisteredEvent(BaseEvent):
    """Published when a new user signs up."""

    event_type: str = USER_REGISTERED
    user_id: int
    email: EmailStr
    username: str
    verification_token: str
    verification_token_expires: datetime
    frontend_url: str


class UserVerifiedEvent(BaseEvent):
    """Published when a user verifies their email."""

    event_type: str = USER_VERIFIED
    user_id: int
    email: EmailStr
    username: str
    frontend_url: str


class UserPasswordResetRequestedEvent(BaseEvent):
    """Published when a user requests a password reset."""

    event_type: str = USER_PASSWORD_RESET_REQUESTED
    user_id: int
    email: EmailStr
    username: str
    reset_token: str
    reset_token_expires: datetime
    frontend_url: str


# ---------------------------------------------------------------------------
# EventPublisher — synchronous, uses pika
# ---------------------------------------------------------------------------


class EventPublisher:
    """
    Synchronous event publisher using pika.

    Publishes JSON-serialized Pydantic event models to a RabbitMQ
    topic exchange named ``user_events``.

    Usage::

        publisher = EventPublisher(rabbitmq_url)
        publisher.connect()
        publisher.publish(event)
        publisher.close()
    """

    EXCHANGE_NAME = "user_events"
    EXCHANGE_TYPE = "topic"

    def __init__(self, rabbitmq_url: str):
        self._rabbitmq_url = rabbitmq_url
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[pika.channel.Channel] = None

    def connect(self):
        """Establish connection and declare the topic exchange."""
        params = pika.URLParameters(self._rabbitmq_url)
        self._connection = pika.BlockingConnection(params)
        self._channel = self._connection.channel()
        self._channel.exchange_declare(
            exchange=self.EXCHANGE_NAME,
            exchange_type=self.EXCHANGE_TYPE,
            durable=True,
        )
        logger.info("EventPublisher connected to RabbitMQ")

    def publish(self, event: BaseEvent):
        """
        Publish an event to the topic exchange.

        Uses ``event.event_type`` as the routing key. Messages are
        persistent (delivery_mode=2). Automatically reconnects if
        the channel has been closed.
        """
        if not self._channel or self._channel.is_closed:
            self.connect()

        body = event.model_dump_json()
        self._channel.basic_publish(
            exchange=self.EXCHANGE_NAME,
            routing_key=event.event_type,
            body=body,
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json",
            ),
        )
        logger.info(f"Published event: {event.event_type}")

    def close(self):
        """Close the RabbitMQ connection."""
        if self._connection and not self._connection.is_closed:
            self._connection.close()
            logger.info("EventPublisher disconnected from RabbitMQ")
