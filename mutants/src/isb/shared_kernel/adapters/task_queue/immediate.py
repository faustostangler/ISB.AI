import uuid
from collections.abc import Callable
from typing import Annotated, Any, ClassVar

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


class ImmediateTaskQueueAdapter(TaskQueuePort):
    """Adapter executing tasks synchronously and immediately on the calling thread.

    Useful for hermetic unit testing and local development context.
    """

    def __init__(self) -> None:
        args = []# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁImmediateTaskQueueAdapterǁ__init____mutmut_orig'), object.__getattribute__(self, 'xǁImmediateTaskQueueAdapterǁ__init____mutmut_mutants'), args, kwargs, self)

    def xǁImmediateTaskQueueAdapterǁ__init____mutmut_orig(self) -> None:
        """Initializes the synchronous task queue with an empty handler registry."""
        self._handlers: dict[str, Callable[[Any], None]] = {}

    def xǁImmediateTaskQueueAdapterǁ__init____mutmut_1(self) -> None:
        """Initializes the synchronous task queue with an empty handler registry."""
        self._handlers: dict[str, Callable[[Any], None]] = None

    xǁImmediateTaskQueueAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁImmediateTaskQueueAdapterǁ__init____mutmut_1': xǁImmediateTaskQueueAdapterǁ__init____mutmut_1
    }
    xǁImmediateTaskQueueAdapterǁ__init____mutmut_orig.__name__ = 'xǁImmediateTaskQueueAdapterǁ__init__'

    def register_handler(self, task_name: str, handler: Callable[[Any], None]) -> None:
        args = [task_name, handler]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_orig'), object.__getattribute__(self, 'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_mutants'), args, kwargs, self)

    def xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_orig(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")
        self._handlers[task_name] = handler

    def xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_1(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if not task_name and not task_name.strip():
            raise ValueError("Task name cannot be empty")
        self._handlers[task_name] = handler

    def xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_2(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")
        self._handlers[task_name] = handler

    def xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_3(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if not task_name or task_name.strip():
            raise ValueError("Task name cannot be empty")
        self._handlers[task_name] = handler

    def xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_4(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if not task_name or not task_name.strip():
            raise ValueError(None)
        self._handlers[task_name] = handler

    def xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_5(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if not task_name or not task_name.strip():
            raise ValueError("XXTask name cannot be emptyXX")
        self._handlers[task_name] = handler

    def xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_6(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if not task_name or not task_name.strip():
            raise ValueError("task name cannot be empty")
        self._handlers[task_name] = handler

    def xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_7(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if not task_name or not task_name.strip():
            raise ValueError("TASK NAME CANNOT BE EMPTY")
        self._handlers[task_name] = handler

    def xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_8(self, task_name: str, handler: Callable[[Any], None]) -> None:
        """Registers a synchronous handler for execution by name.

        Args:
            task_name: The name of the task.
            handler: The function to process the task.

        Raises:
            ValueError: If the task name is empty or whitespace.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")
        self._handlers[task_name] = None

    xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_1': xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_1,
        'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_2': xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_2,
        'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_3': xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_3,
        'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_4': xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_4,
        'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_5': xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_5,
        'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_6': xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_6,
        'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_7': xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_7,
        'xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_8': xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_8
    }
    xǁImmediateTaskQueueAdapterǁregister_handler__mutmut_orig.__name__ = 'xǁImmediateTaskQueueAdapterǁregister_handler'

    def enqueue(self, task_name: str, payload: BaseModel) -> str:
        args = [task_name, payload]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_orig'), object.__getattribute__(self, 'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_mutants'), args, kwargs, self)

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_orig(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_1(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name and not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_2(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_3(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_4(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError(None)

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_5(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("XXTask name cannot be emptyXX")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_6(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_7(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("TASK NAME CANNOT BE EMPTY")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_8(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(None) from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_9(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = None
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_10(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(None)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_11(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_12(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(None)

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_13(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = None

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_14(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(None)

        # Execute the registered task runner function inline on the calling thread
        handler(payload)

        return task_id

    def xǁImmediateTaskQueueAdapterǁenqueue__mutmut_15(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues and immediately runs a task synchronously.

        Args:
            task_name: The target task identifier.
            payload: Serializable Pydantic model parameters.

        Returns:
            str: Generated unique task ID (UUIDv4).

        Raises:
            ValueError: If the task name is empty.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        if not task_name or not task_name.strip():
            raise ValueError("Task name cannot be empty")

        try:
            # Use Pydantic V2 model_dump_json() for serialization verification
            payload.model_dump_json()
        except Exception as err:
            raise TaskSerializationError(f"Task payload serialization failed: {err}") from err

        handler = self._handlers.get(task_name)
        if not handler:
            raise TaskNotFoundError(f"No handler registered for task '{task_name}'")

        # Generate a unique task execution ID
        task_id = str(uuid.uuid4())

        # Execute the registered task runner function inline on the calling thread
        handler(None)

        return task_id

    xǁImmediateTaskQueueAdapterǁenqueue__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_1': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_1,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_2': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_2,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_3': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_3,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_4': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_4,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_5': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_5,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_6': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_6,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_7': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_7,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_8': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_8,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_9': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_9,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_10': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_10,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_11': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_11,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_12': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_12,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_13': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_13,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_14': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_14,
        'xǁImmediateTaskQueueAdapterǁenqueue__mutmut_15': xǁImmediateTaskQueueAdapterǁenqueue__mutmut_15
    }
    xǁImmediateTaskQueueAdapterǁenqueue__mutmut_orig.__name__ = 'xǁImmediateTaskQueueAdapterǁenqueue'
