import math

from isb.knowledge_organization.ports.prediction_calibrator import PredictionCalibratorPort


class ConformalCalibratorAdapter(PredictionCalibratorPort):
    """Adapter implementing Split Conformal Prediction calibration."""

    def __init__(self, nonconformity_scores: list[float]) -> None:
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

    def _calibrate(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
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
