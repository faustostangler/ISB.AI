from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Annotated

from pydantic import BaseModel

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


class TaskQueueError(Exception):
    """Base exception class for all task queue related errors."""
    pass


class TaskSerializationError(TaskQueueError):
    """Exception raised when a task payload fails serialization validation."""
    pass


class TaskNotFoundError(TaskQueueError):
    """Exception raised when a requested task handler or actor is not registered."""
    pass


class TaskQueuePort(ABC):
    """Abstract port defining the interface for scheduling background tasks.

    This port allows the domain/application layer to schedule tasks asynchronously
    without being coupled to the underlying message broker or execution engine.
    """

    @abstractmethod
    def enqueue(self, task_name: str, payload: BaseModel) -> str:
        """Enqueues a task to run asynchronously.

        Args:
            task_name: The unique string identifier of the task (e.g., actor name).
            payload: A Pydantic BaseModel containing the serializable parameters.

        Returns:
            str: A unique task execution identifier (message ID).

        Raises:
            ValueError: If task_name is empty or invalid.
            TaskSerializationError: If the payload cannot be serialized to JSON.
            TaskNotFoundError: If the task name is not registered.
        """
        # Step-by-step implementation walkthrough in adapters:
        # 1. Validate that the task_name is not empty or whitespace.
        # 2. Assert that the payload is serializable via model_dump_json().
        # 3. Retrieve the execution entity (handler/actor) by task_name.
        # 4. Dispatch the payload and return a unique identifier.
        raise NotImplementedError("Subclasses must implement the enqueue method")
