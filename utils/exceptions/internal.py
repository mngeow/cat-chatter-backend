from dataclasses import dataclass
from typing import Optional

# Internal exceptions: raise by the infrastructure or service layers.
# The router will decide what HTTP status code to return
# The goal of this separation is to have full visibility on which codes can be returned
# just by looking at the code of the router


@dataclass
class DuplicateEntityDatabase(Exception):
    entity: str
    name: str
    readable_message: Optional[str] = None


@dataclass
class ConnectionToHostFailed(Exception):
    host_name: str


@dataclass
class UnhandledException(Exception):
    """A generic exception, for any case where we explicitly choose to send a 500 without explanation"""

    message: str


@dataclass
class EntityNotFound(Exception):
    entity: str
    id: Optional[str] = None
    readable_message: Optional[str] = None


@dataclass
class DuplicateEntity(Exception):
    entity: str
    id: Optional[str] = None
    readable_message: Optional[str] = None


@dataclass
class Unauthorized(Exception):
    message: str
    readable_message: Optional[str] = None

@dataclass
class Forbidden(Exception):
    message: str
    readable_message: Optional[str] = None

@dataclass
class BadRequest(Exception):
    message: str
    readable_message: Optional[str] = None

@dataclass
class RateLimitExceeded(Exception):
    message: str
    readable_message: Optional[str] = None

@dataclass
class AWSServiceException(Exception):
    service_name: str
    message: str
    readable_message: Optional[str] = None