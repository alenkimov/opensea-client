import asyncio
from collections.abc import Callable

import httpx
import pytest
from better_proxy import Proxy

import opensea.client as client_module
from opensea import (
    ChainIdentifier,
    CollectionIntervalStat,
    EventType,
    OpenSeaAPIError,
    OpenSeaClient,
    OpenSeaConfigurationError,
    OpenSeaInvalidResponseError,
    OpenSeaNotFoundError,
    OpenSeaTransportError,
    SaleEvent,
    TotalCollectionStats,
)


def run(coro):  # type: ignore[no-untyped-def]
    return asyncio.run(coro)


def make_client(
    handler: Callable[[httpx.Request], httpx.Response],
) -> tuple[OpenSeaClient, httpx.AsyncClient]:
    http_client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    return OpenSeaClient("secret-key", http_client=http_client), http_client


def nft_payload(*, detailed: bool = False) -> dict[str, object]:
    payload: dict[str, object] = {
        "identifier": "42",
        "collection": "example",
        "contract": "0xabc",
        "token_standard": "erc721",
        "opensea_url": "https://opensea.io/assets/ethereum/0xabc/42",
        "updated_at": "2026-01-01T00:00:00Z",
        "is_disabled": False,
        "is_nsfw": False,
        "traits": [],
    }
    if detailed:
        payload.update(
            {
                "creator": "0xcreator",
                "owners": [{"address": "0xowner", "quantity": 1, "quantity_string": "1"}],
                "is_suspicious": False,
            }
        )
    return payload


def sale_payload() -> dict[str, object]:
    return {
        "event_type": "sale",
        "event_timestamp": 1_700_000_000,
        "chain": "ethereum",
        "quantity": 1,
        "closing_date": 1_700_000_001,
        "seller": "0xseller",
        "buyer": "0xbuyer",
        "nft": nft_payload(),
        "payment": {
            "quantity": "100",
            "token_address": "0xtoken",
            "decimals": 18,
            "symbol": "WETH",
        },
    }


def test_list_events_uses_repeated_event_type_params_and_parses_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.path == "/api/v2/events/collection/my-collection"
        assert request.url.params.multi_items() == [
            ("after", "10"),
            ("before", "20"),
            ("event_type", "sale"),
            ("event_type", "transfer"),
            ("traits", '[{"traitType":"Eyes","value":"Blue"}]'),
            ("limit", "50"),
            ("next", "cursor"),
        ]
        assert request.headers["x-api-key"] == "secret-key"
        assert request.headers["accept"] == "application/json"
        return httpx.Response(
            200,
            json={"asset_events": [sale_payload()], "next": "next-page"},
        )

    client, http_client = make_client(handler)
    try:
        events, next_cursor = run(
            client.list_events_by_collection(
                "my-collection",
                after=10,
                before=20,
                event_type=[EventType.SALE, EventType.TRANSFER],
                traits='[{"traitType":"Eyes","value":"Blue"}]',
                limit=50,
                next_cursor="cursor",
            )
        )
    finally:
        run(http_client.aclose())

    assert next_cursor == "next-page"
    assert isinstance(events[0], SaleEvent)


def test_get_collection_sales_forces_sale_filter() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params.multi_items() == [
            ("after", "10"),
            ("event_type", "sale"),
            ("limit", "25"),
        ]
        return httpx.Response(200, json={"asset_events": [sale_payload()]})

    client, http_client = make_client(handler)
    try:
        sales, next_cursor = run(client.get_collection_sales("collection", after=10, limit=25))
    finally:
        run(http_client.aclose())

    assert isinstance(sales[0], SaleEvent)
    assert next_cursor is None


def test_get_collection_stats() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/collections/example/stats"
        return httpx.Response(
            200,
            json={
                "total": {
                    "volume": 12.5,
                    "sales": 3,
                    "num_owners": 2,
                    "floor_price": 1.25,
                    "floor_price_symbol": "ETH",
                },
                "intervals": [{"interval": "one_day", "volume": 4.0, "sales": 1}],
            },
        )

    client, http_client = make_client(handler)
    try:
        intervals, total = run(client.get_collection_stats("example"))
    finally:
        run(http_client.aclose())

    assert total.floor_price == 1.25
    assert isinstance(total, TotalCollectionStats)
    assert isinstance(intervals[0], CollectionIntervalStat)
    assert intervals[0].interval == "one_day"


def test_get_nfts_by_collection_serializes_filters() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/collection/example/nfts"
        assert request.url.params.multi_items() == [
            ("traits", "[]"),
            ("has_agent_binding", "true"),
            ("limit", "200"),
            ("next", "abc"),
        ]
        return httpx.Response(200, json={"nfts": [nft_payload()], "next": "def"})

    client, http_client = make_client(handler)
    try:
        nfts, next_cursor = run(
            client.get_nfts_by_collection(
                "example",
                traits="[]",
                has_agent_binding=True,
                limit=200,
                next_cursor="abc",
            )
        )
    finally:
        run(http_client.aclose())

    assert nfts[0].identifier == "42"
    assert next_cursor == "def"


def test_get_nft_encodes_path_segments() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.raw_path == (
            b"/api/v2/chain/ethereum/contract/0xabc%2Fdef/nfts/token%2F42"
        )
        return httpx.Response(200, json={"nft": nft_payload(detailed=True)})

    client, http_client = make_client(handler)
    try:
        nft = run(client.get_nft(ChainIdentifier.ETHEREUM, "0xabc/def", "token/42"))
    finally:
        run(http_client.aclose())

    assert nft.creator == "0xcreator"


def test_documented_not_found_error_has_safe_details() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            404,
            json={"detail": "missing"},
            headers={"x-request-id": "request-1"},
        )

    client, http_client = make_client(handler)
    try:
        with pytest.raises(OpenSeaNotFoundError) as exc_info:
            run(client.get_nfts_by_collection("missing", next_cursor="sensitive-cursor"))
    finally:
        run(http_client.aclose())

    error = exc_info.value
    assert error.status_code == 404
    assert error.data == {"detail": "missing"}
    assert error.request_id == "request-1"
    assert "sensitive-cursor" not in error.url


def test_non_json_error_body_is_bounded() -> None:
    body = "failure" * 300

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text=body)

    client, http_client = make_client(handler)
    try:
        with pytest.raises(OpenSeaAPIError) as exc_info:
            run(client.get_collection_stats("broken"))
    finally:
        run(http_client.aclose())

    error = exc_info.value
    assert error.data is None
    assert error.body_excerpt == body[:1000]


def test_malformed_success_response_raises_typed_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not-json")

    client, http_client = make_client(handler)
    try:
        with pytest.raises(OpenSeaInvalidResponseError):
            run(client.get_collection_stats("broken"))
    finally:
        run(http_client.aclose())


def test_missing_envelope_payload_raises_typed_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    client, http_client = make_client(handler)
    try:
        with pytest.raises(OpenSeaInvalidResponseError):
            run(client.get_nft(ChainIdentifier.ETHEREUM, "0xabc", "42"))
    finally:
        run(http_client.aclose())


def test_invalid_envelope_cursor_raises_typed_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"asset_events": [], "next": 123})

    client, http_client = make_client(handler)
    try:
        with pytest.raises(OpenSeaInvalidResponseError):
            run(client.list_events_by_collection("example"))
    finally:
        run(http_client.aclose())


def test_invalid_nested_payload_raises_typed_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"nfts": [{}]})

    client, http_client = make_client(handler)
    try:
        with pytest.raises(OpenSeaInvalidResponseError):
            run(client.get_nfts_by_collection("example"))
    finally:
        run(http_client.aclose())


def test_httpx_failures_raise_typed_transport_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection failed", request=request)

    client, http_client = make_client(handler)
    try:
        with pytest.raises(OpenSeaTransportError) as exc_info:
            run(client.get_collection_stats("broken"))
    finally:
        run(http_client.aclose())

    assert isinstance(exc_info.value.__cause__, httpx.ConnectError)


def test_limit_is_validated_before_request() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        pytest.fail(f"unexpected request: {request.url}")

    client, http_client = make_client(handler)
    try:
        with pytest.raises(ValueError, match="between 1 and 200"):
            run(client.get_nfts_by_collection("example", limit=201))
    finally:
        run(http_client.aclose())


def test_external_client_is_not_closed_by_context_manager() -> None:
    async def exercise() -> httpx.AsyncClient:
        external = httpx.AsyncClient(transport=httpx.MockTransport(lambda _: httpx.Response(200)))
        async with OpenSeaClient("key", http_client=external):
            pass
        return external

    external = run(exercise())
    try:
        assert not external.is_closed
    finally:
        run(external.aclose())


def test_internal_client_is_closed_and_aclose_is_idempotent() -> None:
    async def exercise() -> bool:
        client = OpenSeaClient("key")
        internal = client._http_client
        async with client:
            pass
        await client.aclose()
        return internal.is_closed

    assert run(exercise())


def test_proxy_is_normalized_for_internal_http_client(monkeypatch: pytest.MonkeyPatch) -> None:
    real_async_client = httpx.AsyncClient
    captured: dict[str, object] = {}

    def create_async_client(**kwargs: object) -> httpx.AsyncClient:
        captured.update(kwargs)
        kwargs["transport"] = httpx.MockTransport(lambda _: httpx.Response(200))
        kwargs.pop("proxy")
        return real_async_client(**kwargs)

    monkeypatch.setattr(client_module.httpx, "AsyncClient", create_async_client)
    client = OpenSeaClient("key", proxy="http://user:pass@localhost:8080")
    try:
        assert captured["proxy"] == "http://user:pass@localhost:8080"
    finally:
        run(client.aclose())


def test_proxy_and_external_client_are_rejected() -> None:
    external = httpx.AsyncClient()
    try:
        with pytest.raises(OpenSeaConfigurationError, match="cannot be combined"):
            OpenSeaClient(
                "key",
                proxy=Proxy.from_str("http://localhost:8080"),
                http_client=external,
            )
    finally:
        run(external.aclose())
