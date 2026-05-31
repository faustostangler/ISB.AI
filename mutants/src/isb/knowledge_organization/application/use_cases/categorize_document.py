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


class CategorizeDocumentUseCase:
    """Use case to categorize a document using conformal calibration and handle triage routing."""

    def __init__(
        self,
        calibrator: PredictionCalibratorPort,
        document_repository: DocumentRepositoryPort,
        triage_repository: TriageRepositoryPort,
    ) -> None:
        args = [calibrator, document_repository, triage_repository]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁCategorizeDocumentUseCaseǁ__init____mutmut_orig'), object.__getattribute__(self, 'xǁCategorizeDocumentUseCaseǁ__init____mutmut_mutants'), args, kwargs, self)

    def xǁCategorizeDocumentUseCaseǁ__init____mutmut_orig(
        self,
        calibrator: PredictionCalibratorPort,
        document_repository: DocumentRepositoryPort,
        triage_repository: TriageRepositoryPort,
    ) -> None:
        self._calibrator = calibrator
        self._document_repository = document_repository
        self._triage_repository = triage_repository

    def xǁCategorizeDocumentUseCaseǁ__init____mutmut_1(
        self,
        calibrator: PredictionCalibratorPort,
        document_repository: DocumentRepositoryPort,
        triage_repository: TriageRepositoryPort,
    ) -> None:
        self._calibrator = None
        self._document_repository = document_repository
        self._triage_repository = triage_repository

    def xǁCategorizeDocumentUseCaseǁ__init____mutmut_2(
        self,
        calibrator: PredictionCalibratorPort,
        document_repository: DocumentRepositoryPort,
        triage_repository: TriageRepositoryPort,
    ) -> None:
        self._calibrator = calibrator
        self._document_repository = None
        self._triage_repository = triage_repository

    def xǁCategorizeDocumentUseCaseǁ__init____mutmut_3(
        self,
        calibrator: PredictionCalibratorPort,
        document_repository: DocumentRepositoryPort,
        triage_repository: TriageRepositoryPort,
    ) -> None:
        self._calibrator = calibrator
        self._document_repository = document_repository
        self._triage_repository = None
    
    xǁCategorizeDocumentUseCaseǁ__init____mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁCategorizeDocumentUseCaseǁ__init____mutmut_1': xǁCategorizeDocumentUseCaseǁ__init____mutmut_1, 
        'xǁCategorizeDocumentUseCaseǁ__init____mutmut_2': xǁCategorizeDocumentUseCaseǁ__init____mutmut_2, 
        'xǁCategorizeDocumentUseCaseǁ__init____mutmut_3': xǁCategorizeDocumentUseCaseǁ__init____mutmut_3
    }
    xǁCategorizeDocumentUseCaseǁ__init____mutmut_orig.__name__ = 'xǁCategorizeDocumentUseCaseǁ__init__'

    def execute(
        self,
        document: Document,
        raw_scores: dict[str, float],
        confidence_level: float = DEFAULT_CONFIDENCE_LEVEL,
    ) -> None:
        args = [document, raw_scores, confidence_level]# type: ignore
        kwargs = {}# type: ignore
        return _mutmut_trampoline(object.__getattribute__(self, 'xǁCategorizeDocumentUseCaseǁexecute__mutmut_orig'), object.__getattribute__(self, 'xǁCategorizeDocumentUseCaseǁexecute__mutmut_mutants'), args, kwargs, self)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_orig(
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_1(
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
        prediction_set = None
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_2(
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
        prediction_set = self._calibrator.calibrate(None, confidence_level)
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_3(
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
        prediction_set = self._calibrator.calibrate(raw_scores, None)
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_4(
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
        prediction_set = self._calibrator.calibrate(confidence_level)
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_5(
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
        prediction_set = self._calibrator.calibrate(raw_scores, )
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_6(
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
        PREDICTION_SET_SIZE_HISTOGRAM.observe(None)

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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_7(
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

        if len(prediction_set) != 1:
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_8(
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

        if len(prediction_set) == 2:
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_9(
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
            category = None
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_10(
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
            category = next(None)
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_11(
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
            category = next(iter(None))
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_12(
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
            document.category = None
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_13(
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
            document.status = None
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_14(
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
            document.status = "XXCompletedXX"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_15(
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
            document.status = "completed"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_16(
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
            document.status = "COMPLETED"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_17(
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
            self._document_repository.save(None)
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_18(
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
        elif prediction_set:
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_19(
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
            document.category = ""
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_20(
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
            document.status = None
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_21(
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
            document.status = "XXNeedsReviewXX"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_22(
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
            document.status = "needsreview"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_23(
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
            document.status = "NEEDSREVIEW"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_24(
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
            document.metadata["triage_reason"] = None
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_25(
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
            document.metadata["XXtriage_reasonXX"] = "out_of_domain"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_26(
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
            document.metadata["TRIAGE_REASON"] = "out_of_domain"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_27(
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
            document.metadata["triage_reason"] = "XXout_of_domainXX"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_28(
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
            document.metadata["triage_reason"] = "OUT_OF_DOMAIN"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_29(
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
            document.metadata["OutOfDomain"] = None
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_30(
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
            document.metadata["XXOutOfDomainXX"] = "true"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_31(
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
            document.metadata["outofdomain"] = "true"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_32(
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
            document.metadata["OUTOFDOMAIN"] = "true"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_33(
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
            document.metadata["OutOfDomain"] = "XXtrueXX"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_34(
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
            document.metadata["OutOfDomain"] = "TRUE"
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_35(
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
                None,
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_36(
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
                None,
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_37(
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
                None,
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_38(
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_39(
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_40(
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_41(
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
                "XXClassification triage triggered: out_of_domain. Document ID: %s. Prediction set: %sXX",
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_42(
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
                "classification triage triggered: out_of_domain. document id: %s. prediction set: %s",
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_43(
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
                "CLASSIFICATION TRIAGE TRIGGERED: OUT_OF_DOMAIN. DOCUMENT ID: %S. PREDICTION SET: %S",
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_44(
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
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger=None).inc()
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_45(
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
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="XXout_of_domainXX").inc()
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_46(
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
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="OUT_OF_DOMAIN").inc()
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_47(
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
            self._document_repository.save(None)
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_48(
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
            self._triage_repository.push(None)
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_49(
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
            document.category = ""
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

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_50(
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
            document.status = None
            document.metadata["triage_reason"] = "ambiguous"
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_51(
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
            document.status = "XXNeedsReviewXX"
            document.metadata["triage_reason"] = "ambiguous"
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_52(
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
            document.status = "needsreview"
            document.metadata["triage_reason"] = "ambiguous"
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_53(
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
            document.status = "NEEDSREVIEW"
            document.metadata["triage_reason"] = "ambiguous"
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_54(
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
            document.metadata["triage_reason"] = None
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_55(
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
            document.metadata["XXtriage_reasonXX"] = "ambiguous"
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_56(
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
            document.metadata["TRIAGE_REASON"] = "ambiguous"
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_57(
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
            document.metadata["triage_reason"] = "XXambiguousXX"
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_58(
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
            document.metadata["triage_reason"] = "AMBIGUOUS"
            logger.warning(
                "Classification triage triggered: ambiguous. Document ID: %s. Prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_59(
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
                None,
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_60(
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
                None,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_61(
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
                None,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_62(
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
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_63(
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
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_64(
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
                )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_65(
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
                "XXClassification triage triggered: ambiguous. Document ID: %s. Prediction set: %sXX",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_66(
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
                "classification triage triggered: ambiguous. document id: %s. prediction set: %s",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_67(
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
                "CLASSIFICATION TRIAGE TRIGGERED: AMBIGUOUS. DOCUMENT ID: %S. PREDICTION SET: %S",
                document.document_id,
                prediction_set,
            )
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="ambiguous").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_68(
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
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger=None).inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_69(
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
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="XXambiguousXX").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_70(
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
            CLASSIFICATION_TRIAGE_COUNTER.labels(trigger="AMBIGUOUS").inc()
            self._document_repository.save(document)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_71(
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
            self._document_repository.save(None)
            self._triage_repository.push(document)

    def xǁCategorizeDocumentUseCaseǁexecute__mutmut_72(
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
            self._triage_repository.push(None)
    
    xǁCategorizeDocumentUseCaseǁexecute__mutmut_mutants : ClassVar[MutantDict] = { # type: ignore
    'xǁCategorizeDocumentUseCaseǁexecute__mutmut_1': xǁCategorizeDocumentUseCaseǁexecute__mutmut_1, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_2': xǁCategorizeDocumentUseCaseǁexecute__mutmut_2, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_3': xǁCategorizeDocumentUseCaseǁexecute__mutmut_3, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_4': xǁCategorizeDocumentUseCaseǁexecute__mutmut_4, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_5': xǁCategorizeDocumentUseCaseǁexecute__mutmut_5, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_6': xǁCategorizeDocumentUseCaseǁexecute__mutmut_6, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_7': xǁCategorizeDocumentUseCaseǁexecute__mutmut_7, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_8': xǁCategorizeDocumentUseCaseǁexecute__mutmut_8, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_9': xǁCategorizeDocumentUseCaseǁexecute__mutmut_9, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_10': xǁCategorizeDocumentUseCaseǁexecute__mutmut_10, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_11': xǁCategorizeDocumentUseCaseǁexecute__mutmut_11, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_12': xǁCategorizeDocumentUseCaseǁexecute__mutmut_12, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_13': xǁCategorizeDocumentUseCaseǁexecute__mutmut_13, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_14': xǁCategorizeDocumentUseCaseǁexecute__mutmut_14, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_15': xǁCategorizeDocumentUseCaseǁexecute__mutmut_15, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_16': xǁCategorizeDocumentUseCaseǁexecute__mutmut_16, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_17': xǁCategorizeDocumentUseCaseǁexecute__mutmut_17, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_18': xǁCategorizeDocumentUseCaseǁexecute__mutmut_18, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_19': xǁCategorizeDocumentUseCaseǁexecute__mutmut_19, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_20': xǁCategorizeDocumentUseCaseǁexecute__mutmut_20, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_21': xǁCategorizeDocumentUseCaseǁexecute__mutmut_21, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_22': xǁCategorizeDocumentUseCaseǁexecute__mutmut_22, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_23': xǁCategorizeDocumentUseCaseǁexecute__mutmut_23, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_24': xǁCategorizeDocumentUseCaseǁexecute__mutmut_24, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_25': xǁCategorizeDocumentUseCaseǁexecute__mutmut_25, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_26': xǁCategorizeDocumentUseCaseǁexecute__mutmut_26, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_27': xǁCategorizeDocumentUseCaseǁexecute__mutmut_27, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_28': xǁCategorizeDocumentUseCaseǁexecute__mutmut_28, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_29': xǁCategorizeDocumentUseCaseǁexecute__mutmut_29, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_30': xǁCategorizeDocumentUseCaseǁexecute__mutmut_30, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_31': xǁCategorizeDocumentUseCaseǁexecute__mutmut_31, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_32': xǁCategorizeDocumentUseCaseǁexecute__mutmut_32, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_33': xǁCategorizeDocumentUseCaseǁexecute__mutmut_33, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_34': xǁCategorizeDocumentUseCaseǁexecute__mutmut_34, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_35': xǁCategorizeDocumentUseCaseǁexecute__mutmut_35, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_36': xǁCategorizeDocumentUseCaseǁexecute__mutmut_36, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_37': xǁCategorizeDocumentUseCaseǁexecute__mutmut_37, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_38': xǁCategorizeDocumentUseCaseǁexecute__mutmut_38, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_39': xǁCategorizeDocumentUseCaseǁexecute__mutmut_39, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_40': xǁCategorizeDocumentUseCaseǁexecute__mutmut_40, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_41': xǁCategorizeDocumentUseCaseǁexecute__mutmut_41, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_42': xǁCategorizeDocumentUseCaseǁexecute__mutmut_42, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_43': xǁCategorizeDocumentUseCaseǁexecute__mutmut_43, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_44': xǁCategorizeDocumentUseCaseǁexecute__mutmut_44, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_45': xǁCategorizeDocumentUseCaseǁexecute__mutmut_45, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_46': xǁCategorizeDocumentUseCaseǁexecute__mutmut_46, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_47': xǁCategorizeDocumentUseCaseǁexecute__mutmut_47, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_48': xǁCategorizeDocumentUseCaseǁexecute__mutmut_48, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_49': xǁCategorizeDocumentUseCaseǁexecute__mutmut_49, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_50': xǁCategorizeDocumentUseCaseǁexecute__mutmut_50, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_51': xǁCategorizeDocumentUseCaseǁexecute__mutmut_51, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_52': xǁCategorizeDocumentUseCaseǁexecute__mutmut_52, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_53': xǁCategorizeDocumentUseCaseǁexecute__mutmut_53, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_54': xǁCategorizeDocumentUseCaseǁexecute__mutmut_54, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_55': xǁCategorizeDocumentUseCaseǁexecute__mutmut_55, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_56': xǁCategorizeDocumentUseCaseǁexecute__mutmut_56, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_57': xǁCategorizeDocumentUseCaseǁexecute__mutmut_57, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_58': xǁCategorizeDocumentUseCaseǁexecute__mutmut_58, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_59': xǁCategorizeDocumentUseCaseǁexecute__mutmut_59, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_60': xǁCategorizeDocumentUseCaseǁexecute__mutmut_60, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_61': xǁCategorizeDocumentUseCaseǁexecute__mutmut_61, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_62': xǁCategorizeDocumentUseCaseǁexecute__mutmut_62, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_63': xǁCategorizeDocumentUseCaseǁexecute__mutmut_63, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_64': xǁCategorizeDocumentUseCaseǁexecute__mutmut_64, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_65': xǁCategorizeDocumentUseCaseǁexecute__mutmut_65, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_66': xǁCategorizeDocumentUseCaseǁexecute__mutmut_66, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_67': xǁCategorizeDocumentUseCaseǁexecute__mutmut_67, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_68': xǁCategorizeDocumentUseCaseǁexecute__mutmut_68, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_69': xǁCategorizeDocumentUseCaseǁexecute__mutmut_69, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_70': xǁCategorizeDocumentUseCaseǁexecute__mutmut_70, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_71': xǁCategorizeDocumentUseCaseǁexecute__mutmut_71, 
        'xǁCategorizeDocumentUseCaseǁexecute__mutmut_72': xǁCategorizeDocumentUseCaseǁexecute__mutmut_72
    }
    xǁCategorizeDocumentUseCaseǁexecute__mutmut_orig.__name__ = 'xǁCategorizeDocumentUseCaseǁexecute'
