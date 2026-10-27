"""Domain errors raised by SupplierAssessment rules."""


class DuplicateAssessmentQuestion(ValueError):
    """Raised when an assessment contains the same question code twice."""


class UnknownAssessmentQuestion(LookupError):
    """Raised when an answer references a question outside the assessment."""


class InvalidAssessmentAnswer(ValueError):
    """Raised when an answer score is outside the question scoring range."""


class MandatoryAssessmentAnswersMissing(ValueError):
    """Raised when assessment completion is attempted with mandatory answers missing."""

    def __init__(self, missing_question_codes: tuple[str, ...]) -> None:
        self.missing_question_codes = missing_question_codes
        joined = ", ".join(missing_question_codes)
        super().__init__(f"Mandatory assessment answers are missing: {joined}")


class AssessmentAlreadyCompleted(ValueError):
    """Raised when a completed assessment is modified or completed again."""
