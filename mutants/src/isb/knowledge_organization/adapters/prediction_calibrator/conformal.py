import math

from isb.knowledge_organization.ports.prediction_calibrator import PredictionCalibratorPort
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


class ConformalCalibratorAdapter(PredictionCalibratorPort):
    """Adapter implementing Split Conformal Prediction calibration."""

    def __init__(self, nonconformity_scores: list[float]) -> None:
        args = [nonconformity_scores]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁConformalCalibratorAdapterǁ__init____mutmut_orig'), object.__getattribute__(self, 'xǁConformalCalibratorAdapterǁ__init____mutmut_mutants'), args, kwargs, self)

    def xǁConformalCalibratorAdapterǁ__init____mutmut_orig(self, nonconformity_scores: list[float]) -> None:
        """Initializes the adapter with calibration set nonconformity scores.

        Args:
            nonconformity_scores: A list of float values representing nonconformity scores.

        Raises:
            RuntimeError: If the calibration sample size is less than 10.
        """
        if len(nonconformity_scores) < 10:
            raise RuntimeError("Insufficient calibration data. Need at least 10 samples.")

        # Store sorted scores to optimize quantile computation
        self._nonconformity_scores = sorted(nonconformity_scores)

    def xǁConformalCalibratorAdapterǁ__init____mutmut_1(self, nonconformity_scores: list[float]) -> None:
        """Initializes the adapter with calibration set nonconformity scores.

        Args:
            nonconformity_scores: A list of float values representing nonconformity scores.

        Raises:
            RuntimeError: If the calibration sample size is less than 10.
        """
        if len(nonconformity_scores) <= 10:
            raise RuntimeError("Insufficient calibration data. Need at least 10 samples.")

        # Store sorted scores to optimize quantile computation
        self._nonconformity_scores = sorted(nonconformity_scores)

    def xǁConformalCalibratorAdapterǁ__init____mutmut_2(self, nonconformity_scores: list[float]) -> None:
        """Initializes the adapter with calibration set nonconformity scores.

        Args:
            nonconformity_scores: A list of float values representing nonconformity scores.

        Raises:
            RuntimeError: If the calibration sample size is less than 10.
        """
        if len(nonconformity_scores) < 11:
            raise RuntimeError("Insufficient calibration data. Need at least 10 samples.")

        # Store sorted scores to optimize quantile computation
        self._nonconformity_scores = sorted(nonconformity_scores)

    def xǁConformalCalibratorAdapterǁ__init____mutmut_3(self, nonconformity_scores: list[float]) -> None:
        """Initializes the adapter with calibration set nonconformity scores.

        Args:
            nonconformity_scores: A list of float values representing nonconformity scores.

        Raises:
            RuntimeError: If the calibration sample size is less than 10.
        """
        if len(nonconformity_scores) < 10:
            raise RuntimeError(None)

        # Store sorted scores to optimize quantile computation
        self._nonconformity_scores = sorted(nonconformity_scores)

    def xǁConformalCalibratorAdapterǁ__init____mutmut_4(self, nonconformity_scores: list[float]) -> None:
        """Initializes the adapter with calibration set nonconformity scores.

        Args:
            nonconformity_scores: A list of float values representing nonconformity scores.

        Raises:
            RuntimeError: If the calibration sample size is less than 10.
        """
        if len(nonconformity_scores) < 10:
            raise RuntimeError("XXInsufficient calibration data. Need at least 10 samples.XX")

        # Store sorted scores to optimize quantile computation
        self._nonconformity_scores = sorted(nonconformity_scores)

    def xǁConformalCalibratorAdapterǁ__init____mutmut_5(self, nonconformity_scores: list[float]) -> None:
        """Initializes the adapter with calibration set nonconformity scores.

        Args:
            nonconformity_scores: A list of float values representing nonconformity scores.

        Raises:
            RuntimeError: If the calibration sample size is less than 10.
        """
        if len(nonconformity_scores) < 10:
            raise RuntimeError("insufficient calibration data. need at least 10 samples.")

        # Store sorted scores to optimize quantile computation
        self._nonconformity_scores = sorted(nonconformity_scores)

    def xǁConformalCalibratorAdapterǁ__init____mutmut_6(self, nonconformity_scores: list[float]) -> None:
        """Initializes the adapter with calibration set nonconformity scores.

        Args:
            nonconformity_scores: A list of float values representing nonconformity scores.

        Raises:
            RuntimeError: If the calibration sample size is less than 10.
        """
        if len(nonconformity_scores) < 10:
            raise RuntimeError("INSUFFICIENT CALIBRATION DATA. NEED AT LEAST 10 SAMPLES.")

        # Store sorted scores to optimize quantile computation
        self._nonconformity_scores = sorted(nonconformity_scores)

    def xǁConformalCalibratorAdapterǁ__init____mutmut_7(self, nonconformity_scores: list[float]) -> None:
        """Initializes the adapter with calibration set nonconformity scores.

        Args:
            nonconformity_scores: A list of float values representing nonconformity scores.

        Raises:
            RuntimeError: If the calibration sample size is less than 10.
        """
        if len(nonconformity_scores) < 10:
            raise RuntimeError("Insufficient calibration data. Need at least 10 samples.")

        # Store sorted scores to optimize quantile computation
        self._nonconformity_scores = None

    def xǁConformalCalibratorAdapterǁ__init____mutmut_8(self, nonconformity_scores: list[float]) -> None:
        """Initializes the adapter with calibration set nonconformity scores.

        Args:
            nonconformity_scores: A list of float values representing nonconformity scores.

        Raises:
            RuntimeError: If the calibration sample size is less than 10.
        """
        if len(nonconformity_scores) < 10:
            raise RuntimeError("Insufficient calibration data. Need at least 10 samples.")

        # Store sorted scores to optimize quantile computation
        self._nonconformity_scores = sorted(None)
    
    xǁConformalCalibratorAdapterǁ__init____mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁConformalCalibratorAdapterǁ__init____mutmut_1': xǁConformalCalibratorAdapterǁ__init____mutmut_1, 
        'xǁConformalCalibratorAdapterǁ__init____mutmut_2': xǁConformalCalibratorAdapterǁ__init____mutmut_2, 
        'xǁConformalCalibratorAdapterǁ__init____mutmut_3': xǁConformalCalibratorAdapterǁ__init____mutmut_3, 
        'xǁConformalCalibratorAdapterǁ__init____mutmut_4': xǁConformalCalibratorAdapterǁ__init____mutmut_4, 
        'xǁConformalCalibratorAdapterǁ__init____mutmut_5': xǁConformalCalibratorAdapterǁ__init____mutmut_5, 
        'xǁConformalCalibratorAdapterǁ__init____mutmut_6': xǁConformalCalibratorAdapterǁ__init____mutmut_6, 
        'xǁConformalCalibratorAdapterǁ__init____mutmut_7': xǁConformalCalibratorAdapterǁ__init____mutmut_7, 
        'xǁConformalCalibratorAdapterǁ__init____mutmut_8': xǁConformalCalibratorAdapterǁ__init____mutmut_8
    }
    xǁConformalCalibratorAdapterǁ__init____mutmut_orig.__name__ = 'xǁConformalCalibratorAdapterǁ__init__'

    def _calibrate(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        args = [raw_scores, confidence_level]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_orig'), object.__getattribute__(self, 'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_mutants'), args, kwargs, self)

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_orig(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_1(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = None
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_2(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = None
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_3(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil(None)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_4(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) / confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_5(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n - 1) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_6(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 2) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_7(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = None
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_8(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(None, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_9(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, None)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_10(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_11(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, )
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_12(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k + 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_13(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 2, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_14(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n + 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_15(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n - 2)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_16(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = None

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_17(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = None
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_18(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 + q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_19(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 2.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score >= threshold
        }
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_20(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = None
        return prediction_set

    def xǁConformalCalibratorAdapterǁ_calibrate__mutmut_21(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        """Calculates the adjusted conformal quantile threshold and returns matching categories.

        Args:
            raw_scores: Validated dictionary mapping category names to raw scores.
            confidence_level: Validated target confidence level (1 - alpha).

        Returns:
            A set of categories that are statistically valid.
        """
        n = len(self._nonconformity_scores)
        k = math.ceil((n + 1) * confidence_level)
        idx = min(k - 1, n - 1)
        q_hat = self._nonconformity_scores[idx]

        threshold = 1.0 - q_hat
        prediction_set = {
            category for category, score in raw_scores.items()
            if score > threshold
        }
        return prediction_set
    
    xǁConformalCalibratorAdapterǁ_calibrate__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_1': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_1, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_2': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_2, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_3': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_3, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_4': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_4, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_5': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_5, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_6': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_6, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_7': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_7, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_8': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_8, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_9': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_9, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_10': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_10, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_11': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_11, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_12': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_12, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_13': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_13, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_14': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_14, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_15': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_15, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_16': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_16, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_17': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_17, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_18': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_18, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_19': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_19, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_20': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_20, 
        'xǁConformalCalibratorAdapterǁ_calibrate__mutmut_21': xǁConformalCalibratorAdapterǁ_calibrate__mutmut_21
    }
    xǁConformalCalibratorAdapterǁ_calibrate__mutmut_orig.__name__ = 'xǁConformalCalibratorAdapterǁ_calibrate'
