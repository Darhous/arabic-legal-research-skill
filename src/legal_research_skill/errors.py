class LegalResearchSkillError(Exception):
    """Base exception for expected CLI and loading errors."""


class InputError(LegalResearchSkillError):
    """The input file cannot be read or parsed."""


class SchemaValidationError(LegalResearchSkillError):
    """The input is not compliant with the research-state schema."""


class UnknownValidatorError(LegalResearchSkillError):
    """A requested validator name is not registered."""
