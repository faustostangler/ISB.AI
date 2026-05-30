import dramatiq
from pydantic import BaseModel

from isb.shared_kernel.ports.task_queue import (
    TaskNotFoundError,
    TaskQueuePort,
    TaskSerializationError,
)


class RedisDramatiqAdapter(TaskQueuePort):
    """Adapter enqueuing tasks into a Redis broker using Dramatiq."""

    def __init__(self, broker: dramatiq.Broker | None = None) -> None:
        """Initializes the Dramatiq task queue adapter.

        Args:
            broker: The Dramatiq broker instance. If None, resolves to the default global broker.
        """
        self._broker = broker or dramatiq.get_broker()

    def enqueue(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues a task asynchronously using Dramatiq's messaging broker.

        Args:
            task_name: The name of the registered actor to trigger.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: The enqueued task execution message ID.

        Raises:
            ValueError: If the task name is empty or whitespace.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the actor is not found on the registered broker.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload_json = payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        try:
            actor = self._broker.get_actor(task_name)
        except dramatiq.ActorNotFound as err:
            raise TaskNotFoundError(f"Dramatiq actor '{task_name}' not found on broker") from err

        # Dispatch the task asynchronously using send
        message = actor.send(payload_json)
        return message.message_id
