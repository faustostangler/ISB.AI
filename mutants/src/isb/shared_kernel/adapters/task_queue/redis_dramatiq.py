from collections.abc import Callable
from typing import Annotated, ClassVar

import dramatiq
from pydantic import BaseModel

from isb.shared_kernel.ports.task_queue import (
    TaskNotFoundError,
    TaskQueuePort,
    TaskSerializationError,
)

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os  # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException  # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit  # type: ignore
        record_trampoline_hit(orig.__module__ + '.' + orig.__name__) # type: ignore
        # (for class methods, orig is bound and thus does not need the explicit self argument)
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    prefix = orig.__module__ + '.' + orig.__name__ + '__mutmut_' # type: ignore
    if not mutant_under_test.startswith(prefix): # type: ignore
        result = orig(*call_args, **call_kwargs) # type: ignore
        return result # type: ignore
    mutant_name = mutant_under_test.rpartition('.')[-1] # type: ignore
    if self_arg is not None: # type: ignore
        # call to a class method where self is not bound
        result = mutants[mutant_name](self_arg, *call_args, **call_kwargs) # type: ignore
    else:
        result = mutants[mutant_name](*call_args, **call_kwargs) # type: ignore
    return result # type: ignore


class RedisDramatiqAdapter(TaskQueuePort):
    """Adapter enqueuing tasks into a Redis broker using Dramatiq."""

    def __init__(self, broker: dramatiq.Broker | None = None) -> None:
        args = [broker]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁRedisDramatiqAdapterǁ__init____mutmut_orig'), object.__getattribute__(self, 'xǁRedisDramatiqAdapterǁ__init____mutmut_mutants'), args, kwargs, self)

    def xǁRedisDramatiqAdapterǁ__init____mutmut_orig(self, broker: dramatiq.Broker | None = None) -> None:
        """Initializes the Dramatiq task queue adapter.

        Args:
            broker: The Dramatiq broker instance. If None, resolves to the default global broker.
        """
        self._broker = broker or dramatiq.get_broker()

    def xǁRedisDramatiqAdapterǁ__init____mutmut_1(self, broker: dramatiq.Broker | None = None) -> None:
        """Initializes the Dramatiq task queue adapter.

        Args:
            broker: The Dramatiq broker instance. If None, resolves to the default global broker.
        """
        self._broker = None

    def xǁRedisDramatiqAdapterǁ__init____mutmut_2(self, broker: dramatiq.Broker | None = None) -> None:
        """Initializes the Dramatiq task queue adapter.

        Args:
            broker: The Dramatiq broker instance. If None, resolves to the default global broker.
        """
        self._broker = broker and dramatiq.get_broker()

    xǁRedisDramatiqAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁRedisDramatiqAdapterǁ__init____mutmut_1': xǁRedisDramatiqAdapterǁ__init____mutmut_1,
        'xǁRedisDramatiqAdapterǁ__init____mutmut_2': xǁRedisDramatiqAdapterǁ__init____mutmut_2
    }
    xǁRedisDramatiqAdapterǁ__init____mutmut_orig.__name__ = 'xǁRedisDramatiqAdapterǁ__init__'

    def enqueue(self, task_name: str, payload: BaseModel) -> str:
        args = [task_name, payload]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁRedisDramatiqAdapterǁenqueue__mutmut_orig'), object.__getattribute__(self, 'xǁRedisDramatiqAdapterǁenqueue__mutmut_mutants'), args, kwargs, self)

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_orig(self, task_name: str, payload: BaseModel) -> str:
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

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_1(self, task_name: str, payload: BaseModel) -> str:
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
        if not task_name and not task_name.strip():
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

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_2(self, task_name: str, payload: BaseModel) -> str:
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
        if task_name or not task_name.strip():
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

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_3(self, task_name: str, payload: BaseModel) -> str:
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
        if not task_name or task_name.strip():
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

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_4(self, task_name: str, payload: BaseModel) -> str:
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
            raise ValueError(None)

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

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_5(self, task_name: str, payload: BaseModel) -> str:
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
            raise ValueError("XXTask name cannot be emptyXX")

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

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_6(self, task_name: str, payload: BaseModel) -> str:
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
            raise ValueError("task name cannot be empty")

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

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_7(self, task_name: str, payload: BaseModel) -> str:
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
            raise ValueError("TASK NAME CANNOT BE EMPTY")

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

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_8(self, task_name: str, payload: BaseModel) -> str:
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
            payload_json = None
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        try:
            actor = self._broker.get_actor(task_name)
        except dramatiq.ActorNotFound as err:
            raise TaskNotFoundError(f"Dramatiq actor '{task_name}' not found on broker") from err

        # Dispatch the task asynchronously using send
        message = actor.send(payload_json)
        return message.message_id

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_9(self, task_name: str, payload: BaseModel) -> str:
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
            raise TaskSerializationError(None) from err

        try:
            actor = self._broker.get_actor(task_name)
        except dramatiq.ActorNotFound as err:
            raise TaskNotFoundError(f"Dramatiq actor '{task_name}' not found on broker") from err

        # Dispatch the task asynchronously using send
        message = actor.send(payload_json)
        return message.message_id

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_10(self, task_name: str, payload: BaseModel) -> str:
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
            actor = None
        except dramatiq.ActorNotFound as err:
            raise TaskNotFoundError(f"Dramatiq actor '{task_name}' not found on broker") from err

        # Dispatch the task asynchronously using send
        message = actor.send(payload_json)
        return message.message_id

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_11(self, task_name: str, payload: BaseModel) -> str:
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
            actor = self._broker.get_actor(None)
        except dramatiq.ActorNotFound as err:
            raise TaskNotFoundError(f"Dramatiq actor '{task_name}' not found on broker") from err

        # Dispatch the task asynchronously using send
        message = actor.send(payload_json)
        return message.message_id

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_12(self, task_name: str, payload: BaseModel) -> str:
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
            raise TaskNotFoundError(None) from err

        # Dispatch the task asynchronously using send
        message = actor.send(payload_json)
        return message.message_id

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_13(self, task_name: str, payload: BaseModel) -> str:
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
        message = None
        return message.message_id

    def xǁRedisDramatiqAdapterǁenqueue__mutmut_14(self, task_name: str, payload: BaseModel) -> str:
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
        message = actor.send(None)
        return message.message_id

    xǁRedisDramatiqAdapterǁenqueue__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁRedisDramatiqAdapterǁenqueue__mutmut_1': xǁRedisDramatiqAdapterǁenqueue__mutmut_1,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_2': xǁRedisDramatiqAdapterǁenqueue__mutmut_2,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_3': xǁRedisDramatiqAdapterǁenqueue__mutmut_3,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_4': xǁRedisDramatiqAdapterǁenqueue__mutmut_4,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_5': xǁRedisDramatiqAdapterǁenqueue__mutmut_5,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_6': xǁRedisDramatiqAdapterǁenqueue__mutmut_6,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_7': xǁRedisDramatiqAdapterǁenqueue__mutmut_7,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_8': xǁRedisDramatiqAdapterǁenqueue__mutmut_8,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_9': xǁRedisDramatiqAdapterǁenqueue__mutmut_9,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_10': xǁRedisDramatiqAdapterǁenqueue__mutmut_10,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_11': xǁRedisDramatiqAdapterǁenqueue__mutmut_11,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_12': xǁRedisDramatiqAdapterǁenqueue__mutmut_12,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_13': xǁRedisDramatiqAdapterǁenqueue__mutmut_13,
        'xǁRedisDramatiqAdapterǁenqueue__mutmut_14': xǁRedisDramatiqAdapterǁenqueue__mutmut_14
    }
    xǁRedisDramatiqAdapterǁenqueue__mutmut_orig.__name__ = 'xǁRedisDramatiqAdapterǁenqueue'
