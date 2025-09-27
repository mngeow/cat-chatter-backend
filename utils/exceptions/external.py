from dataclasses import dataclass
from typing import Optional, Type

from fastapi import Request
from fastapi.applications import FastAPI
from fastapi.responses import ORJSONResponse
from loguru import logger
from pydantic import BaseModel
from starlette_context import context
from starlette_context.header_keys import HeaderKeys

from core_utils.exceptions.exceptions_internal import (
    BadRequest,
    DuplicateEntity,
    DuplicateEntityDatabase,
    EntityNotFound,
    Unauthorized,
    Forbidden,
    RateLimitExceeded,
    AWSServiceException
)

# HTTP Exceptions - All these exceptions should return a response with an appropriate HTTP response code (4xx ot 5xx)
# Those exceptions should only be called in the Routes !!

# See https://www.restapitutorial.com/httpstatuscodes.html for docs on HTTP status codes

# Creating a new exception
# 1. Create a class
# 2. Create a handler
# 3. Register the exception and the handler in `register_exception_handlers`


class HTTPProblemResponseSchema(BaseModel):
    """Model of the RFC7807 Problem response schema."""

    title: str
    status: int
    detail: str
    readable_message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "title": "Unauthorized",
                    "status": 401,
                    "detail": "Auth token not present in authorization header",
                    "readable_message": "It looks like something went wrong. Please refresh the page or try again later. If the problem persists, contact support for assistance.",
                }
            ]
        }


@dataclass
class HTTPERROR(Exception):
    @property
    def request_id(self):
        return context.data.get(HeaderKeys.request_id)

    @property
    def correlation_id(self):
        return context.data.get(HeaderKeys.correlation_id)

    def dict(self):
        obj_dict = self.__dict__
        obj_dict.update({"name": self.__class__.__name__})
        return obj_dict


async def http_error_handler(request: Request, http_exception: Type[HTTPERROR]):
    status_code = getattr(http_exception, "status_code", None)
    _ = getattr(http_exception, "errors", None)
    ex_message = getattr(http_exception, "message")
    user_friendly_error_message = getattr(http_exception, "ex").readable_message
    title = getattr(http_exception, "ex").__class__.__name__

    logger.error(
        f"HTTP exception occured, status code is {status_code} and error message is {ex_message}"
    )

    if status_code is None:
        status_code = 500
        logger.exception(f"Unhandled exception occured, status code is {status_code}")

    http_response_schema = HTTPProblemResponseSchema(
        status=status_code,
        title=title,
        detail=ex_message,
        readable_message=user_friendly_error_message,
    )

    response = ORJSONResponse(
        status_code=status_code, content=http_response_schema.model_dump()
    )

    response.headers.update(
        {
            "request_id": http_exception.request_id,
            "correlation_id": http_exception.correlation_id,
        }
    )
    return response


@dataclass
class UserInputDuplicate_409(Exception):
    ex: DuplicateEntityDatabase

    @property
    def message(self):
        return f"Warning: {self.ex.entity} already exists {self.ex.name}"


async def user_input_error_exc_handler(request: Request, exc: UserInputDuplicate_409):
    return ORJSONResponse(
        status_code=409,
        content={"message": exc.message},
    )


# ====================================================
# 428 [Precondition Required] Error CLasses
# ====================================================


@dataclass
class HTTP428(HTTPERROR):
    status_code = 428

# ====================================================
# 429 [Too Many Requests] Error CLasses
# ====================================================


@dataclass
class HTTP429(HTTPERROR):
    status_code = 429

@dataclass
class GenericRateLimitExceeded(HTTP429):
    ex: RateLimitExceeded

    @property
    def message(self):
        return self.ex.message


# ====================================================
# 500 [Internal Server Error] Error CLasses
# ====================================================

@dataclass
class HTTP500(HTTPERROR):
    status_code = 500

@dataclass
class AWSServiceException_500(HTTP500):
    ex: AWSServiceException

    @property
    def message(self):
        return f"Error encountered while using aws {self.ex.service_name}: {self.ex.message}"

# ====================================================
# 400 [Bad Request] Error CLasses
# ====================================================
@dataclass
class HTTP400(HTTPERROR):
    status_code = 400


@dataclass
class InvalidRequestPayload(HTTP400):
    ex: ValueError | KeyError

    @property
    def message(self):
        return f"Invalid request payload, error from server is {str(self.ex)}"


@dataclass
class GenericBadRequest_400(HTTP400):
    ex: BadRequest

    @property
    def message(self):
        return self.ex.message


# ====================================================
# 401 [Unauthorized] Error CLasses
# ====================================================
@dataclass
class HTTP401(HTTPERROR):
    status_code = 401


@dataclass
class SessionIDTokenInvalid(HTTP401):
    @property
    def message(self):
        return "Session ID token is invalid"


@dataclass
class SessionIDTokenExpired(HTTP401):
    @property
    def message(self):
        return "Session ID token expired"


@dataclass
class ForbiddenEmailDomain(HTTP401):
    email_domain: str

    @property
    def message(self):
        return f"Attempted access from user with {self.email_domain=}, but this email domain is not allowed access."


@dataclass
class Unauthorized_401(HTTP401):
    ex: Unauthorized

    @property
    def message(self):
        return self.ex.message
    

# ====================================================
# 403 [Forbidden] Error Classes
# ====================================================
@dataclass
class HTTP403(HTTPERROR):
    status_code = 403

@dataclass
class OwnershipForbidden(HTTP403):
    ex: Forbidden

    @property
    def message(self):
        return "Attempted to access object owned by another user"

@dataclass
class Forbidden_403(HTTP403):
    ex: Forbidden

    @property
    def message(self):
        return self.ex.message

# ====================================================
# 409 [Duplicate Entity] Error Classes
# ====================================================
@dataclass
class HTTP409(HTTPERROR):
    status_code = 409


@dataclass
class DuplicateEntityError(HTTP409):
    ex: DuplicateEntity

    @property
    def message(self):
        return f"Entitie(s): {self.ex.entity}  with id {self.ex.id} already exists"


# ====================================================
# 404 [Not Found] Error CLasses
# ====================================================
@dataclass
class HTTP404(HTTPERROR):
    status_code = 404


@dataclass
class NotFoundError(HTTP404):
    message: Optional[str] = None


@dataclass
class GenericNotFoundError(HTTP404):
    ex: EntityNotFound

    @property
    def message(self):
        return f"Entitie(s): {self.ex.entity} with id {self.ex.id} not found"


def register_exception_handlers(app: FastAPI) -> FastAPI:
    """Registers all the default exception handlers"""
    app.add_exception_handler(HTTPERROR, http_error_handler)
    app.add_exception_handler(UserInputDuplicate_409, user_input_error_exc_handler)
    return app
