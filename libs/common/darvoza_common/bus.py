"""Kafka producer/consumer wrapper with retries and a dead-letter queue."""

import asyncio
import logging
from collections.abc import Awaitable, Callable

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from aiokafka.errors import KafkaConnectionError

from .envelope import Envelope, Topics
from .settings import get_settings

log = logging.getLogger("bus")

Handler = Callable[[Envelope], Awaitable[None]]


class Bus:
    def __init__(self, client_id: str):
        self.client_id = client_id
        self.settings = get_settings()
        self.producer: AIOKafkaProducer | None = None
        self._consumers: list[AIOKafkaConsumer] = []

    async def start(self) -> None:
        for attempt in range(30):
            try:
                self.producer = AIOKafkaProducer(
                    bootstrap_servers=self.settings.kafka_bootstrap,
                    client_id=self.client_id,
                    acks="all",
                    enable_idempotence=True,
                )
                await self.producer.start()
                return
            except KafkaConnectionError:
                log.warning("kafka not ready (attempt %s), retrying", attempt + 1)
                await asyncio.sleep(2)
        raise RuntimeError("could not connect to Kafka")

    async def stop(self) -> None:
        for c in self._consumers:
            await c.stop()
        if self.producer:
            await self.producer.stop()

    async def publish(self, topic: str, env: Envelope, key: str | None = None) -> None:
        assert self.producer, "bus not started"
        k = (key or env.session_id or env.message_id).encode()
        await self.producer.send_and_wait(topic, env.to_bytes(), key=k)

    async def consume(self, topics: list[str], group: str, handler: Handler, from_latest: bool = False) -> None:
        """Run forever. A failing message is retried, then sent to the DLQ."""
        consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.settings.kafka_bootstrap,
            group_id=group,
            client_id=self.client_id,
            auto_offset_reset="latest" if from_latest else "earliest",
            enable_auto_commit=True,
        )
        for attempt in range(30):
            try:
                await consumer.start()
                break
            except KafkaConnectionError:
                log.warning("consumer waiting for kafka (attempt %s)", attempt + 1)
                await asyncio.sleep(2)
        self._consumers.append(consumer)
        async for msg in consumer:
            try:
                env = Envelope.from_bytes(msg.value)
            except Exception:
                log.exception("bad message on %s", msg.topic)
                continue
            for i in range(3):
                try:
                    await handler(env)
                    break
                except Exception as e:
                    log.exception("handler failed (try %s) for %s", i + 1, env.message_id)
                    if i == 2:
                        await self.publish(
                            Topics.DLQ,
                            env.child(type="event", source_agent=self.client_id,
                                      payload={"error": str(e), "original": env.model_dump(mode="json")}),
                        )
                    else:
                        await asyncio.sleep(0.5 * (i + 1))
