import pytest

from isb.knowledge_organization.adapters.prediction_calibrator.conformal import ConformalCalibratorAdapter
from isb.knowledge_organization.ports.prediction_calibrator import DEFAULT_CONFIDENCE_LEVEL, PredictionCalibratorPort


def test_default_confidence_level_constant_is_exactly_090() -> None:
    """Directly asserts the DEFAULT_CONFIDENCE_LEVEL constant value.

    Kills the 0.90 -> 1.9 mutation on the module constant — no inspect trickery needed.
    """
    assert DEFAULT_CONFIDENCE_LEVEL == pytest.approx(0.90)
    assert 0.0 < DEFAULT_CONFIDENCE_LEVEL < 1.0


def test_calibrate_uses_default_confidence_level_constant() -> None:
    """Verifies the calibrate() default parameter refers to DEFAULT_CONFIDENCE_LEVEL."""
    import inspect
    sig = inspect.signature(PredictionCalibratorPort.calibrate)
    default = sig.parameters["confidence_level"].default
    # The default must be the constant, not a hard-coded literal
    assert default == DEFAULT_CONFIDENCE_LEVEL
def test_conformal_calibrator_quantile_calculation() -> None:
    # Arrange
    # 10 sorted scores: [0.05, 0.08, 0.12, 0.15, 0.18, 0.22, 0.25, 0.30, 0.35, 0.40]
    nonconformity_scores = [0.40, 0.05, 0.22, 0.15, 0.08, 0.30, 0.12, 0.25, 0.35, 0.18]
    adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)

    # Act & Assert
    # Confidence level 0.90 -> k = ceil(11 * 0.90) = 10 -> idx = min(9, 9) = 9
    # sorted_scores[9] = 0.40
    # Threshold: 1.0 - 0.40 = 0.60
    # Work score 0.70 >= 0.60 -> included
    # Finance score 0.50 < 0.60 -> excluded
    prediction_set = adapter.calibrate(
        raw_scores={"Work": 0.70, "Finance": 0.50},
        confidence_level=0.90
    )
    assert prediction_set == {"Work"}


def test_conformal_calibrator_default_confidence_level() -> None:
    # Arrange
    nonconformity_scores = [0.40, 0.05, 0.22, 0.15, 0.08, 0.30, 0.12, 0.25, 0.35, 0.18]
    adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)

    # Act & Assert
    # Default confidence level is 0.90 (strictly in (0.0, 1.0)).
    # A mutated default of 1.9 would raise ValueError in the port validator.
    # Threshold with 0.90: 1.0 - 0.40 = 0.60.
    # Work score 0.70 >= 0.60 -> included; Finance 0.50 < 0.60 -> excluded.
    prediction_set = adapter.calibrate(raw_scores={"Work": 0.70, "Finance": 0.50})
    assert prediction_set == {"Work"}

    # Verify the default produces a DIFFERENT result than confidence_level=0.50
    # to ensure the default is not an arbitrary value
    prediction_set_low = adapter.calibrate(
        raw_scores={"Work": 0.70, "Finance": 0.50},
        confidence_level=0.50
    )
    # At 0.50: threshold = 1.0 - 0.22 = 0.78, so Work (0.70) is excluded
    assert prediction_set_low == set()
    # The two results differ, confirming default != 0.50
    assert prediction_set != prediction_set_low


def test_conformal_calibrator_quantile_calculation_smaller_confidence() -> None:
    # Arrange
    nonconformity_scores = [0.40, 0.05, 0.22, 0.15, 0.08, 0.30, 0.12, 0.25, 0.35, 0.18]
    adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)

    # Act & Assert
    # Confidence level 0.50 -> k = ceil(11 * 0.50) = 6 -> idx = min(5, 9) = 5
    # sorted_scores = [0.05, 0.08, 0.12, 0.15, 0.18, 0.22, 0.25, 0.30, 0.35, 0.40]
    # sorted_scores[5] = 0.22
    # Threshold: 1.0 - 0.22 = 0.78
    # Work score 0.80 >= 0.78 -> included
    # Finance score 0.75 < 0.78 -> excluded
    prediction_set = adapter.calibrate(
        raw_scores={"Work": 0.80, "Finance": 0.75},
        confidence_level=0.50
    )
    assert prediction_set == {"Work"}


def test_conformal_calibrator_exact_threshold_match() -> None:
    # Arrange
    nonconformity_scores = [0.40, 0.05, 0.22, 0.15, 0.08, 0.30, 0.12, 0.25, 0.35, 0.18]
    adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)

    # Act & Assert
    # Confidence level 0.90 -> Threshold: 1.0 - 0.40 = 0.60
    # Score 0.60 should be exactly included because of `>=`
    prediction_set = adapter.calibrate(
        raw_scores={"Work": 0.60},
        confidence_level=0.90
    )
    assert prediction_set == {"Work"}


def test_conformal_calibrator_n_plus_one_differential_math() -> None:
    # Arrange
    nonconformity_scores = [0.40, 0.05, 0.22, 0.15, 0.08, 0.30, 0.12, 0.25, 0.35, 0.18]
    adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)

    # Act & Assert
    # Confidence level 0.68, n = 10.
    # Under correct n + 1: k = ceil(11 * 0.68) = 8 -> idx = min(7, 9) = 7.
    # sorted_scores[7] = 0.30 -> threshold = 1.0 - 0.30 = 0.70.
    # Work score 0.66 < 0.70 -> excluded -> empty set.
    # Under mutated n + 2: k = ceil(12 * 0.68) = 9 -> idx = min(8, 9) = 8.
    # sorted_scores[8] = 0.35 -> threshold = 1.0 - 0.35 = 0.65.
    # Work score 0.66 >= 0.65 -> would be included.
    prediction_set = adapter.calibrate(
        raw_scores={"Work": 0.66},
        confidence_level=0.68
    )
    assert prediction_set == set()


def test_conformal_calibrator_idx_bound_high_confidence() -> None:
    # Arrange
    nonconformity_scores = [0.40, 0.05, 0.22, 0.15, 0.08, 0.30, 0.12, 0.25, 0.35, 0.18]
    adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)

    # Act & Assert
    # Confidence level 0.99, n = 10.
    # k = ceil(11 * 0.99) = 11 -> k - 1 = 10.
    # Correct clamp: idx = min(10, 9) = 9 -> sorted_scores[9] = 0.40.
    # Mutated clamp min(k - 1, n + 1): idx = min(10, 11) = 10 -> raises IndexError.
    prediction_set = adapter.calibrate(
        raw_scores={"Work": 0.70},
        confidence_level=0.99
    )
    assert prediction_set == {"Work"}


def test_conformal_calibrator_boundary_indexing_differential_math() -> None:
    # Arrange
    nonconformity_scores = [0.40, 0.05, 0.22, 0.15, 0.08, 0.30, 0.12, 0.25, 0.35, 0.18]
    adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)

    # Act & Assert
    # Confidence level 0.90, n = 10.
    # Correct clamp: idx = min(9, 9) = 9 -> sorted_scores[9] = 0.40 -> threshold = 0.60.
    # Score 0.62 >= 0.60 -> included.
    # Mutated clamp min(k-1, n-2): idx = min(9, 8) = 8 -> sorted_scores[8] = 0.35 -> threshold = 0.65.
    # Score 0.62 < 0.65 -> would be excluded.
    prediction_set = adapter.calibrate(
        raw_scores={"Work": 0.62},
        confidence_level=0.90
    )
    assert prediction_set == {"Work"}


def test_conformal_calibrator_validation_confidence_out_of_bounds() -> None:
    nonconformity_scores = [0.1] * 10
    adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)

    with pytest.raises(ValueError, match=r"^Confidence level must be strictly between 0\.0 and 1\.0$"):
        adapter.calibrate(raw_scores={"Work": 0.9}, confidence_level=1.5)

    with pytest.raises(ValueError, match=r"^Confidence level must be strictly between 0\.0 and 1\.0$"):
        adapter.calibrate(raw_scores={"Work": 0.9}, confidence_level=0.0)

    with pytest.raises(ValueError, match=r"^Confidence level must be strictly between 0\.0 and 1\.0$"):
        adapter.calibrate(raw_scores={"Work": 0.9}, confidence_level=1.0)


def test_conformal_calibrator_validation_empty_raw_scores() -> None:
    nonconformity_scores = [0.1] * 10
    adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)

    with pytest.raises(ValueError, match=r"^Raw scores dictionary cannot be empty$"):
        adapter.calibrate(raw_scores={}, confidence_level=0.90)


def test_conformal_calibrator_insufficient_calibration_data() -> None:
    nonconformity_scores = [0.1] * 9  # 9 is less than 10

    with pytest.raises(RuntimeError, match=r"^Insufficient calibration data\. Need at least 10 samples\.$"):
        ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)
