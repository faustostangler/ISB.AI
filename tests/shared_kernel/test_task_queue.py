from typing import Any

import dramatiq
import pytest
from dramatiq.brokers.stub import StubBroker
from pydantic import BaseModel, ConfigDict

from isb.shared_kernel.adapters.task_queue.immediate import ImmediateTaskQueueAdapter
from isb.shared_kernel.adapters.task_queue.redis_dramatiq import RedisDramatiqAdapter
from isb.shared_kernel.ports.task_queue import (
    TaskNotFoundError,
    TaskSerializationError,
)


# Test Payloads
class DummyPayload(BaseModel):
    url: str


class NonSerializablePayload(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    connection: Any


# --- Unit Tests: ImmediateTaskQueueAdapter ---

def test_immediate_adapter_success() -> None:
    """Scenario 1: Verify synchronous, inline execution works correctly."""
    adapter = ImmediateTaskQueueAdapter()
    execution_record = []

    def dummy_handler(payload: DummyPayload) -> None:
        execution_record.append(payload.url)

    adapter.register_handler("test_task", dummy_handler)

    payload = DummyPayload(url="https://example.com")
    task_id = adapter.enqueue("test_task", payload)

    # Assertions
    assert task_id is not None
    assert len(task_id) > 0
    assert execution_record == ["https://example.com"]


def test_immediate_adapter_empty_task_name_raises_value_error() -> None:
    """Boundary Condition: Empty task identifier must raise ValueError."""
    adapter = ImmediateTaskQueueAdapter()
    payload = DummyPayload(url="https://example.com")

    with pytest.raises(ValueError, match="Task name cannot be empty"):
        adapter.enqueue("", payload)

    with pytest.raises(ValueError, match="Task name cannot be empty"):
        adapter.enqueue("   ", payload)


def test_immediate_adapter_unregistered_task_raises_not_found() -> None:
    """Exception Mapping: Unregistered tasks must raise TaskNotFoundError."""
    adapter = ImmediateTaskQueueAdapter()
    payload = DummyPayload(url="https://example.com")

    with pytest.raises(TaskNotFoundError, match="No handler registered for task"):
        adapter.enqueue("unregistered_task", payload)


def test_immediate_adapter_serialization_failure_raises_serialization_error() -> None:
    """Scenario 3: Non-serializable payload must raise TaskSerializationError."""
    adapter = ImmediateTaskQueueAdapter()

    # We register a dummy handler
    adapter.register_handler("test_serialization", lambda _: None)

    # Construct payload with a non-serializable object (like a complex custom class instance)
    class CustomObj:
        pass

    payload = NonSerializablePayload(connection=CustomObj())

    with pytest.raises(TaskSerializationError, match="payload serialization failed"):
        adapter.enqueue("test_serialization", payload)


# --- Integration Tests: RedisDramatiqAdapter ---

# Defining a Dramatiq actor to use in integration tests
@dramatiq.actor(actor_name="dramatiq_test_task")
def dramatiq_test_task(payload_json: str) -> None:
    # Actor processing logic
    pass


@pytest.mark.integration
def test_redis_dramatiq_adapter_success() -> None:
    """Scenario 2: Verify asynchronous broker enqueuing pushes to queue and returns task ID."""
    # Setup Dramatiq StubBroker
    broker = StubBroker()
    dramatiq.set_broker(broker)
    broker.declare_actor(dramatiq_test_task)
    dramatiq_test_task.broker = broker

    adapter = RedisDramatiqAdapter(broker=broker)
    payload = DummyPayload(url="https://example.com")

    # Enqueue should run asynchronously, push a message and return the message_id
    task_id = adapter.enqueue("dramatiq_test_task", payload)

    # Assertions
    assert task_id is not None
    assert len(task_id) > 0

    # Verify message was pushed to the queue
    assert not broker.queues["default"].empty()


@pytest.mark.integration
def test_redis_dramatiq_adapter_empty_task_name_raises_value_error() -> None:
    """Boundary Condition: Empty task identifier must raise ValueError."""
    broker = StubBroker()
    adapter = RedisDramatiqAdapter(broker=broker)
    payload = DummyPayload(url="https://example.com")

    with pytest.raises(ValueError, match="Task name cannot be empty"):
        adapter.enqueue("", payload)


@pytest.mark.integration
def test_redis_dramatiq_adapter_unregistered_actor_raises_not_found() -> None:
    """Exception Mapping: Actor not found on the broker must raise TaskNotFoundError."""
    broker = StubBroker()
    adapter = RedisDramatiqAdapter(broker=broker)
    payload = DummyPayload(url="https://example.com")

    with pytest.raises(TaskNotFoundError, match=r"actor .* not found on broker"):
        adapter.enqueue("non_existent_actor", payload)


@pytest.mark.integration
def test_redis_dramatiq_adapter_serialization_failure_raises_serialization_error() -> None:
    """Scenario 3: Non-serializable payload must raise TaskSerializationError."""
    broker = StubBroker()
    dramatiq.set_broker(broker)
    broker.declare_actor(dramatiq_test_task)
    dramatiq_test_task.broker = broker
    adapter = RedisDramatiqAdapter(broker=broker)

    class CustomObj:
        pass

    payload = NonSerializablePayload(connection=CustomObj())

    with pytest.raises(TaskSerializationError, match="payload serialization failed"):
        adapter.enqueue("dramatiq_test_task", payload)
