import logging
from unittest.mock import MagicMock

import pytest
from prometheus_client import REGISTRY

from isb.knowledge_organization.adapters.prediction_calibrator.conformal import ConformalCalibratorAdapter
from isb.knowledge_organization.application.use_cases.categorize_document import CategorizeDocumentUseCase
from isb.knowledge_organization.domain.document import Document
from isb.knowledge_organization.ports.document_repository import DocumentRepositoryPort, TriageRepositoryPort
from isb.knowledge_organization.ports.prediction_calibrator import DEFAULT_CONFIDENCE_LEVEL, PredictionCalibratorPort


class MockPredictionCalibrator(PredictionCalibratorPort):
    def __init__(self, returned_set: set[str]) -> None:
        self.returned_set = returned_set
        self.called_with_scores: dict[str, float] | None = None
        self.called_with_confidence: float | None = None

    def _calibrate(self, raw_scores: dict[str, float], confidence_level: float) -> set[str]:
        self.called_with_scores = raw_scores
        self.called_with_confidence = confidence_level
        return self.returned_set


def test_categorize_document_scenario_1_clear_classification() -> None:
    # Arrange
    doc = Document(
        document_id="doc-123",
        content="This is work related content.",
        metadata={}
    )

    calibrator = MockPredictionCalibrator(returned_set={"Work"})
    doc_repo = MagicMock(spec=DocumentRepositoryPort)
    triage_repo = MagicMock(spec=TriageRepositoryPort)

    use_case = CategorizeDocumentUseCase(
        calibrator=calibrator,
        document_repository=doc_repo,
        triage_repository=triage_repo
    )

    # Act
    use_case.execute(doc, raw_scores={"Work": 0.85, "Personal": 0.15}, confidence_level=0.85)

    # Assert
    assert doc.category == "Work"
    assert doc.status == "Completed"
    doc_repo.save.assert_called_once_with(doc)
    triage_repo.push.assert_not_called()
    assert calibrator.called_with_scores == {"Work": 0.85, "Personal": 0.15}
    assert calibrator.called_with_confidence == 0.85


def test_categorize_document_default_confidence() -> None:
    # Arrange
    doc = Document(
        document_id="doc-123",
        content="This is work related content.",
        metadata={}
    )

    calibrator = MockPredictionCalibrator(returned_set={"Work"})
    doc_repo = MagicMock(spec=DocumentRepositoryPort)
    triage_repo = MagicMock(spec=TriageRepositoryPort)

    use_case = CategorizeDocumentUseCase(
        calibrator=calibrator,
        document_repository=doc_repo,
        triage_repository=triage_repo
    )

    # Act (omit confidence_level)
    use_case.execute(doc, raw_scores={"Work": 0.85, "Personal": 0.15})

    # Assert
    assert calibrator.called_with_confidence == 0.90


def test_categorize_document_scenario_2_ambiguous_classification(caplog: pytest.LogCaptureFixture) -> None:
    # Arrange
    doc = Document(
        document_id="doc-456",
        content="This is ambiguous content.",
        metadata={}
    )

    calibrator = MockPredictionCalibrator(returned_set={"Research", "Work"})
    doc_repo = MagicMock(spec=DocumentRepositoryPort)
    triage_repo = MagicMock(spec=TriageRepositoryPort)

    use_case = CategorizeDocumentUseCase(
        calibrator=calibrator,
        document_repository=doc_repo,
        triage_repository=triage_repo
    )

    # Get baseline metric value
    metric_before = REGISTRY.get_sample_value(
        "isb_classification_triage_total",
        {"trigger": "ambiguous"}
    ) or 0.0

    # Act
    with caplog.at_level(logging.WARNING):
        use_case.execute(doc, raw_scores={"Research": 0.50, "Work": 0.45})

    # Assert
    assert doc.category is None
    assert doc.status == "NeedsReview"
    assert doc.metadata.get("triage_reason") == "ambiguous"

    doc_repo.save.assert_called_once_with(doc)
    triage_repo.push.assert_called_once_with(doc)

    # Verify warning log matches exactly and doesn't allow mutated string prefix or mutated set parameter
    assert any(
        record.message.startswith("Classification triage triggered: ambiguous. Document ID: doc-456. Prediction set: ")
        for record in caplog.records
    )
    assert any(
        str({"Research", "Work"}) in record.message or str({"Work", "Research"}) in record.message
        for record in caplog.records
    )

    # Verify metric incremented
    metric_after = REGISTRY.get_sample_value(
        "isb_classification_triage_total",
        {"trigger": "ambiguous"}
    ) or 0.0
    assert metric_after == metric_before + 1.0


def test_categorize_document_scenario_3_out_of_domain_classification(caplog: pytest.LogCaptureFixture) -> None:
    # Arrange
    doc = Document(
        document_id="doc-789",
        content="Gibberish content.",
        metadata={}
    )

    calibrator = MockPredictionCalibrator(returned_set=set())
    doc_repo = MagicMock(spec=DocumentRepositoryPort)
    triage_repo = MagicMock(spec=TriageRepositoryPort)

    use_case = CategorizeDocumentUseCase(
        calibrator=calibrator,
        document_repository=doc_repo,
        triage_repository=triage_repo
    )

    # Get baseline metric value
    metric_before = REGISTRY.get_sample_value(
        "isb_classification_triage_total",
        {"trigger": "out_of_domain"}
    ) or 0.0

    # Act
    with caplog.at_level(logging.WARNING):
        use_case.execute(doc, raw_scores={"Research": 0.10, "Work": 0.05})

    # Assert
    assert doc.category is None
    assert doc.status == "NeedsReview"
    assert doc.metadata.get("triage_reason") == "out_of_domain"
    assert doc.metadata.get("OutOfDomain") == "true"

    doc_repo.save.assert_called_once_with(doc)
    triage_repo.push.assert_called_once_with(doc)

    # Verify warning log matches exactly and doesn't allow mutated string prefix or mutated set parameter
    assert any(
        record.message.startswith(
            "Classification triage triggered: out_of_domain. Document ID: doc-789. Prediction set: "
        )
        for record in caplog.records
    )
    assert any("set()" in record.message for record in caplog.records)

    # Verify metric incremented
    metric_after = REGISTRY.get_sample_value(
        "isb_classification_triage_total",
        {"trigger": "out_of_domain"}
    ) or 0.0
    assert metric_after == metric_before + 1.0


def test_categorize_document_default_confidence_uses_valid_level_with_real_adapter() -> None:
    """Uses a real ConformalCalibratorAdapter to verify the default confidence_level=0.90
    is a valid value in (0.0, 1.0). A mutated default of 1.9 would raise ValueError
    from the port validator before any calibration occurs.
    """
    # 10 calibration scores -> sorted: [0.10, 0.20, 0.30, 0.40, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90]
    # confidence_level=0.90 -> k=ceil(11*0.90)=10 -> idx=min(9,9)=9 -> q_hat=0.90
    # threshold = 1.0 - 0.90 = 0.10
    # Work score 0.11 >= 0.10 -> included
    nonconformity_scores = [0.10, 0.20, 0.30, 0.40, 0.50, 0.55, 0.60, 0.70, 0.80, 0.90]
    real_adapter = ConformalCalibratorAdapter(nonconformity_scores=nonconformity_scores)
    doc = Document(document_id="doc-real", content="Real content.", metadata={})
    doc_repo = MagicMock(spec=DocumentRepositoryPort)
    triage_repo = MagicMock(spec=TriageRepositoryPort)

    use_case = CategorizeDocumentUseCase(
        calibrator=real_adapter,
        document_repository=doc_repo,
        triage_repository=triage_repo,
    )

    # Omit confidence_level to exercise the default — mutated 1.9 would raise ValueError
    use_case.execute(doc, raw_scores={"Work": 0.11})

    # With real default 0.90, threshold=0.10, Work 0.11 is included
    assert doc.category == "Work"
    assert doc.status == "Completed"


def test_execute_default_confidence_level_is_exactly_090() -> None:
    """Directly asserts DEFAULT_CONFIDENCE_LEVEL is exactly 0.90.

    Kills the 0.90 -> 1.9 mutation on the constant — no inspect trickery needed.
    The use case execute() default is bound to DEFAULT_CONFIDENCE_LEVEL at import time.
    """
    assert DEFAULT_CONFIDENCE_LEVEL == pytest.approx(0.90)
    assert 0.0 < DEFAULT_CONFIDENCE_LEVEL < 1.0

