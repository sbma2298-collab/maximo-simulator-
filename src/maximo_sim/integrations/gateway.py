"""An API boundary that keeps external calls outside MBO business rules."""

# Any supports JSON-like values in request and response dictionaries.
from typing import Any, Protocol


# IntegrationGateway defines the minimum contract for an external-system adapter.
class IntegrationGateway(Protocol):
    # send accepts a route and payload and returns a parsed response.
    def send(self, route: str, payload: dict[str, Any]) -> dict[str, Any]: ...


# FakeIntegrationGateway records calls for lessons and tests without network access.
class FakeIntegrationGateway:
    # Constructor starts with no recorded outbound messages.
    def __init__(self):
        # Each call is saved as a route and detached payload tuple.
        self.calls: list[tuple[str, dict[str, Any]]] = []

    # send records the request and returns a predictable success response.
    def send(self, route: str, payload: dict[str, Any]) -> dict[str, Any]:
        # Append a defensive payload copy for later assertions.
        self.calls.append((route, dict(payload)))
        # Return a small result shaped like parsed JSON.
        return {"status": "accepted", "route": route}
