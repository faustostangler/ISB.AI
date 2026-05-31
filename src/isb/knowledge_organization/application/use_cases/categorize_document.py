import logging

from prometheus_client import Counter, Histogram

from isb.knowledge_organization.domain.document import Document
from isb.knowledge_organization.ports.document_repository import DocumentRepositoryPort, TriageRepositoryPort
from isb.knowledge_organization.ports.prediction_calibrator import DEFAULT_CONFIDENCE_LEVEL, PredictionCalibratorPort

logger = logging.getLogger("isb.knowledge_organization.use_cases.categorize_document")

CLASSIFICATION_TRIAGE_COUNTER = Counter(
    "isb_classification_triage_total",
    "Total number of classification triage events",
    ["trigger"],
)

PREDICTION_SET_SIZE_HISTOGRAM = Histogram(
    "isb_prediction_set_size",
    "Cardinality distribution of prediction sets",
)


class CategorizeDocumentUseCase:
    """Use case to categorize a document using conformal calibration and handle triage routing."""

    def __init__(
        self,
        calibrator: PredictionCalibratorPort,
        document_repository: DocumentRepositoryPort,
        triage_repository: TriageRepositoryPort,
    ) -> None:
        self._calibrator = calibrator
        self._document_repository = document_repository
        self._triage_repository = triage_repository

    def execute(
        self,
        document: Document,
        raw_scores: dict[str, float],
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    ) -> None:
        """Executes the categorization logic for a document.

        Args:
            document: The Document domain model to categorize.
            raw_scores: Uncalibrated classification probability scores.
            confidence_level: The target confidence interval level.
        """
        prediction_set = self._calibrator.calibrate(raw_scores, confidence_level)
        PREDICTION_SET_SIZE_HISTOGRAM.observe(len(prediction_set))

        if len(prediction_set) == 1:
            category = next(iter(prediction_set))
            document.category = category
            document.status = "Completed"
            self._document_repository.save(document)
        elif not prediction_set:
            document.category = None
            document.status = "NeedsReview"
            document.metadata["triage_reason"] = "out_of_domain"
            document.metadata["OutOfDomain"] = "true"
            logger.warning(
                "Classification triage triggered: out_of_domain. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="out_of_domain").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)
        else:
            document.category = None
            document.status = "NeedsReview"
            document.metadata["triage_reason"] = "ambiguous"
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)
