from abc import ABC, abstractmethod

#: Default confidence level (1 - alpha) used when no explicit value is provided.
#: Guarantees the true category appears in the prediction set >= 90% of the time.
DEFAULT_CONFIDENCE_LEVEL: float = 0.90
from typing import Annotated
from typing import Callable
from typing import ClassVar

MutantDict = Annotated[dict[str, Callable], "Mutant"] # type: ignore


def _mutmut_trampoline(orig, mutants, call_args, call_kwargs, self_arg = None): # type: ignore
    """Forward call to original or mutated function, depending on the environment"""
    import os # type: ignore
    mutant_under_test = os.environ['MUTANT_UNDER_TEST'] # type: ignore
    if mutant_under_test == 'fail': # type: ignore
        from mutmut.__main__ import MutmutProgrammaticFailException # type: ignore
        raise MutmutProgrammaticFailException('Failed programmatically')       # type: ignore
    elif mutant_under_test == 'stats': # type: ignore
        from mutmut.__main__ import record_trampoline_hit # type: ignore
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


class PredictionCalibratorPort(ABC):
    """Port interface for prediction calibration using statistical conformal intervals."""

    def calibrate(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        args = [raw_scores, confidence_level]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁPredictionCalibratorPortǁcalibrate__mutmut_orig'), object.__getattribute__(self, 'xǁPredictionCalibratorPortǁcalibrate__mutmut_mutants'), args, kwargs, self)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_orig(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_1(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_2(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (1.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_3(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 <= confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_4(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level <= 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_5(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 2.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_6(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError(None)

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_7(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("XXConfidence level must be strictly between 0.0 and 1.0XX")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_8(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_9(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("CONFIDENCE LEVEL MUST BE STRICTLY BETWEEN 0.0 AND 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_10(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_11(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError(None)

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_12(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("XXRaw scores dictionary cannot be emptyXX")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_13(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_14(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("RAW SCORES DICTIONARY CANNOT BE EMPTY")

        return self._calibrate(raw_scores, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_15(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(None, confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_16(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, None)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_17(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(confidence_level)

    def xǁPredictionCalibratorPortǁcalibrate__mutmut_18(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
        """Validates inputs and delegates to the concrete calibration algorithm.

        Args:
            raw_scores: Dictionary mapping category names to their raw model output scores.
            confidence_level: Target confidence level (1 - alpha), must be strictly in (0.0, 1.0).

        Returns:
            A set of categories that are statistically valid at the given confidence level.

        Raises:
            ValueError: If confidence_level is out of bounds or raw_scores is empty.
        """
        if not (0.0 < confidence_level < 1.0):
            raise ValueError("Confidence level must be strictly between 0.0 and 1.0")

        if not raw_scores:
            raise ValueError("Raw scores dictionary cannot be empty")

        return self._calibrate(raw_scores, )
    
    xǁPredictionCalibratorPortǁcalibrate__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁPredictionCalibratorPortǁcalibrate__mutmut_1': xǁPredictionCalibratorPortǁcalibrate__mutmut_1, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_2': xǁPredictionCalibratorPortǁcalibrate__mutmut_2, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_3': xǁPredictionCalibratorPortǁcalibrate__mutmut_3, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_4': xǁPredictionCalibratorPortǁcalibrate__mutmut_4, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_5': xǁPredictionCalibratorPortǁcalibrate__mutmut_5, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_6': xǁPredictionCalibratorPortǁcalibrate__mutmut_6, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_7': xǁPredictionCalibratorPortǁcalibrate__mutmut_7, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_8': xǁPredictionCalibratorPortǁcalibrate__mutmut_8, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_9': xǁPredictionCalibratorPortǁcalibrate__mutmut_9, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_10': xǁPredictionCalibratorPortǁcalibrate__mutmut_10, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_11': xǁPredictionCalibratorPortǁcalibrate__mutmut_11, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_12': xǁPredictionCalibratorPortǁcalibrate__mutmut_12, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_13': xǁPredictionCalibratorPortǁcalibrate__mutmut_13, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_14': xǁPredictionCalibratorPortǁcalibrate__mutmut_14, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_15': xǁPredictionCalibratorPortǁcalibrate__mutmut_15, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_16': xǁPredictionCalibratorPortǁcalibrate__mutmut_16, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_17': xǁPredictionCalibratorPortǁcalibrate__mutmut_17, 
        'xǁPredictionCalibratorPortǁcalibrate__mutmut_18': xǁPredictionCalibratorPortǁcalibrate__mutmut_18
    }
    xǁPredictionCalibratorPortǁcalibrate__mutmut_orig.__name__ = 'xǁPredictionCalibratorPortǁcalibrate'

    @abstractmethod
    def _calibrate(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Concrete calibration implementation to be defined by adapters.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level.

        Returns:
            Set of calibrated category predictions.
        """
        pass
