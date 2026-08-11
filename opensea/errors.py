from typing import Any


class OpenSeaError(Exception):
    """Base exception raised by the client."""


class OpenSeaConfigurationError(OpenSeaError, ValueError):
    """The client was configured with incompatible or missing options."""


class OpenSeaTransportError(OpenSeaError):
    def __init__(self, *, method: str, url: str, message: str) -> None:
        self.method = method
        self.url = url
        self.message = message
        super().__init__(f"OpenSea request failed: {method} {url}: {message}")


class OpenSeaAPIError(OpenSeaError):
    def __init__(
        self,
        *,
        status_code: int,
        method: str,
        url: str,
        data: Any = None,
        body_excerpt: str | None = None,
        request_id: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.method = method
        self.url = url
        self.data = data
        self.body_excerpt = body_excerpt
        self.request_id = request_id
        message = f"OpenSea returned HTTP {status_code} for {method} {url}"
        if request_id:
            message += f" (request ID: {request_id})"
        super().__init__(message)


class OpenSeaBadRequestError(OpenSeaAPIError):
    """The API rejected the request as invalid."""


class OpenSeaNotFoundError(OpenSeaAPIError):
    """The requested OpenSea resource was not found."""


class OpenSeaInvalidResponseError(OpenSeaError):
    def __init__(self, *, status_code: int, method: str, url: str) -> None:
        self.status_code = status_code
        self.method = method
        self.url = url
        super().__init__(f"OpenSea returned an invalid response for {method} {url}")
