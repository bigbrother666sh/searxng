# Custom exceptions for simplified engines

class EngineException(Exception):
    """Base class for engine-related exceptions."""
    pass

class SearxEngineAPIException(EngineException):
    """Raised when an engine API returns an error or unexpected response."""
    pass

class SearxEngineCaptchaException(EngineException):
    """Raised when an engine returns a CAPTCHA challenge."""
    def __init__(self, message, suspended_time=None):
        super().__init__(message)
        self.suspended_time = suspended_time

class SearxXPathSyntaxException(EngineException):
    """Raised when there is a syntax error in XPath expression."""
    pass

class SearxEngineXPathException(EngineException):
    """Raised when there is an error evaluating XPath expression."""
    pass

# Placeholder for other exceptions if needed
pass
