from abc import ABC, abstractmethod

#: Default confidence level (1 - alpha) used when no explicit value is provided.
#: Guarantees the true category appears in the prediction set >= 90% of the time.
DEFAULT_CONFIDENCE_LEVEL: float = 0.90


class PredictionCalibratorPort(ABC):
    """Port interface for prediction calibration using statistical conformal intervals."""

    def calibrate(self, raw_scores: dict[str, float], confidence_level: float = DEFAULT_CONFIDENCE_LEVEL) -> set[str]:
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
