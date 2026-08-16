import asyncio
from collections.abc import Callable
from datetime import date
from decimal import Decimal

import httpx
import pytest
from better_proxy import Proxy

import opensea.client as client_module
from opensea import (
    ChainIdentifier,
    Collection,
    CollectionDetailed,
    CollectionIntervalStat,
    CollectionOfferAggregate,
    EventType,
    OpenSeaAPIError,
    OpenSeaClient,
    OpenSeaConfigurationError,
    OpenSeaInvalidResponseError,
    OpenSeaNotFoundError,
    OpenSeaTransportError,
    ProfileOffersReceivedSortBy,
    ProfileOrderSortBy,
    SaleEvent,
    SortDirection,
    TopCollectionsSortBy,
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
        "estimated_value_usd": 1234.56789,
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


def payment_token_payload() -> dict[str, object]:
    return {
        "symbol": "WETH",
        "address": "0xtoken",
        "chain": "ethereum",
        "image": "https://example.com/weth.png",
        "name": "Wrapped Ether",
        "decimals": 18,
        "eth_price": "1.0",
        "usd_price": "2500.0",
    }


def collection_payload(*, detailed: bool = False) -> dict[str, object]:
    payload: dict[str, object] = {
        "collection": "example",
        "name": "Example Collection",
        "safelist_status": "verified",
        "is_disabled": False,
        "is_nsfw": False,
        "trait_offers_enabled": True,
        "collection_offers_enabled": True,
        "opensea_url": "https://opensea.io/collection/example",
        "contracts": [{"address": "0xabc", "chain": "ethereum"}],
    }
    if detailed:
        payload.update(
            {
                "editors": ["0xeditor"],
                "fees": [{"fee": 2.5, "recipient": "0xrecipient", "required": True}],
                "total_supply": 10_000,
                "unique_item_count": 9_500,
                "created_date": "2024-01-02",
                "pricing_currencies": {
                    "listing_currency": payment_token_payload(),
                    "offer_currency": payment_token_payload(),
                },
            }
        )
    return payload


def offer_aggregate_payload() -> dict[str, object]:
    price = {
        "usd_price": "2500.0",
        "token_unit": 1.0,
        "symbol": "WETH",
        "chain": "ethereum",
    }
    return {
        "offer_price": price,
        "total_value": {**price, "token_unit": 3.0, "usd_price": "7500.0"},
        "total_offers": 3,
        "bidders": [{"address": "0xbidder", "quantity": 3}],
    }


def offer_payload() -> dict[str, object]:
    return {
        "order_hash": "0xoffer",
        "chain": "ethereum",
        "remaining_quantity": 1,
        "status": "ACTIVE",
        "asset": {"contract": "0xabc", "identifier": "42"},
        "price": {"currency": "WETH", "decimals": 18, "value": "900000000000000000"},
        "protocol_data": protocol_data_payload(),
    }


def listing_payload() -> dict[str, object]:
    return {
        "order_hash": "0xlisting",
        "chain": "ethereum",
        "remaining_quantity": 1,
        "status": "ACTIVE",
        "type": "basic",
        "asset": {"contract": "0xabc", "identifier": "42"},
        "protocol_data": protocol_data_payload(),
        "price": {
            "current": {
                "currency": "ETH",
                "decimals": 18,
                "value": "1000000000000000000",
            }
        },
    }


def protocol_data_payload() -> dict[str, object]:
    item = {
        "itemType": 2,
        "token": "0xabc",
        "identifierOrCriteria": "42",
        "startAmount": "1",
        "endAmount": "1",
    }
    return {
        "parameters": {
            "offerer": "0xofferer",
            "offer": [item],
            "consideration": [{**item, "recipient": "0xrecipient"}],
            "startTime": "1700000000",
            "endTime": "1700003600",
            "orderType": 0,
            "zone": "0xzone",
            "zoneHash": "0xhash",
            "salt": "123",
            "conduitKey": "0xconduit",
            "totalOriginalConsiderationItems": 1,
            "counter": 0,
        },
        "signature": "0xsignature",
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


def test_list_events_by_account_serializes_filters_and_encodes_address() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.raw_path.split(b"?", 1)[0] == (b"/api/v2/events/accounts/0xabc%2Fdef")
        assert request.url.params.multi_items() == [
            ("after", "10"),
            ("before", "20"),
            ("event_type", "sale"),
            ("event_type", "transfer"),
            ("chain", "ethereum"),
            ("limit", "50"),
            ("next", "cursor"),
        ]
        return httpx.Response(
            200,
            json={"asset_events": [sale_payload()], "next": "next-page"},
        )

    client, http_client = make_client(handler)
    try:
        events, next_cursor = run(
            client.list_events_by_account(
                "0xabc/def",
                after=10,
                before=20,
                event_type=[EventType.SALE, EventType.TRANSFER],
                chain=ChainIdentifier.ETHEREUM,
                limit=50,
                next_cursor="cursor",
            )
        )
    finally:
        run(http_client.aclose())

    assert isinstance(events[0], SaleEvent)
    assert next_cursor == "next-page"


def test_list_events_by_nft_serializes_filters_and_encodes_path() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.raw_path.split(b"?", 1)[0] == (
            b"/api/v2/events/chain/ethereum/contract/0xabc%2Fdef/nfts/token%2F42"
        )
        assert request.url.params.multi_items() == [
            ("after", "10"),
            ("before", "20"),
            ("event_type", "sale"),
            ("limit", "200"),
            ("next", "cursor"),
        ]
        return httpx.Response(
            200,
            json={"asset_events": [sale_payload()], "next": None},
        )

    client, http_client = make_client(handler)
    try:
        events, next_cursor = run(
            client.list_events_by_nft(
                ChainIdentifier.ETHEREUM,
                "0xabc/def",
                "token/42",
                after=10,
                before=20,
                event_type=EventType.SALE,
                limit=200,
                next_cursor="cursor",
            )
        )
    finally:
        run(http_client.aclose())

    assert isinstance(events[0], SaleEvent)
    assert next_cursor is None


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


def test_get_top_collections_serializes_filters_and_parses_page() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/collections/top"
        assert request.url.params.multi_items() == [
            ("sort_by", "total_volume"),
            ("chains", "ethereum,base"),
            ("category", "pfps"),
            ("limit", "25"),
            ("cursor", "current-page"),
        ]
        return httpx.Response(
            200,
            json={"collections": [collection_payload()], "next": "next-page"},
        )

    client, http_client = make_client(handler)
    try:
        collections, next_cursor = run(
            client.get_top_collections(
                sort_by=TopCollectionsSortBy.TOTAL_VOLUME,
                chains=[ChainIdentifier.ETHEREUM, ChainIdentifier.BASE],
                category="pfps",
                limit=25,
                cursor="current-page",
            )
        )
    finally:
        run(http_client.aclose())

    assert isinstance(collections[0], Collection)
    assert collections[0].contracts[0].chain == "ethereum"
    assert next_cursor == "next-page"


def test_get_collection_encodes_slug_and_parses_details() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.raw_path == b"/api/v2/collections/example%2Fcollection"
        return httpx.Response(200, json=collection_payload(detailed=True))

    client, http_client = make_client(handler)
    try:
        collection = run(client.get_collection("example/collection"))
    finally:
        run(http_client.aclose())

    assert isinstance(collection, CollectionDetailed)
    assert collection.created_date == date(2024, 1, 2)
    assert collection.fees[0].fee == Decimal("2.5")
    assert collection.pricing_currencies.offer_currency.symbol == "WETH"


def test_get_collection_offer_aggregates_serializes_page_options() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/collections/example/offer_aggregates"
        assert request.url.params.multi_items() == [
            ("limit", "10"),
            ("cursor", "current-page"),
            ("sort_direction", "asc"),
        ]
        return httpx.Response(
            200,
            json={"offer_aggregates": [offer_aggregate_payload()], "next": "next-page"},
        )

    client, http_client = make_client(handler)
    try:
        aggregates, next_cursor = run(
            client.get_collection_offer_aggregates(
                "example",
                limit=10,
                cursor="current-page",
                sort_direction=SortDirection.ASC,
            )
        )
    finally:
        run(http_client.aclose())

    assert isinstance(aggregates[0], CollectionOfferAggregate)
    assert aggregates[0].offer_price.token_unit == Decimal("1.0")
    assert aggregates[0].bidders[0].quantity == 3
    assert next_cursor == "next-page"


def test_get_collection_stats() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/collections/example/stats"
        return httpx.Response(
            200,
            content=(
                b'{"total":{"volume":12.500000000001234567,"sales":3,'
                b'"num_owners":2,"floor_price":0.020498799999,'
                b'"floor_price_symbol":"ETH"},"intervals":[{"interval":"one_day",'
                b'"volume":4.000000000001234567,"sales":1}]}'
            ),
        )

    client, http_client = make_client(handler)
    try:
        intervals, total = run(client.get_collection_stats("example"))
    finally:
        run(http_client.aclose())

    assert total.floor_price == Decimal("0.020498799999")
    assert total.volume == Decimal("12.500000000001234567")
    assert isinstance(total, TotalCollectionStats)
    assert isinstance(intervals[0], CollectionIntervalStat)
    assert intervals[0].volume == Decimal("4.000000000001234567")
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
    assert nfts[0].estimated_value_usd == Decimal("1234.56789")
    assert next_cursor == "def"


def test_get_nfts_by_account_serializes_filters() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v2/chain/ethereum/account/0xowner/nfts"
        assert request.url.params.multi_items() == [
            ("collection", "example"),
            ("limit", "100"),
            ("next", "abc"),
        ]
        return httpx.Response(200, json={"nfts": [nft_payload()], "next": None})

    client, http_client = make_client(handler)
    try:
        nfts, next_cursor = run(
            client.get_nfts_by_account(
                ChainIdentifier.ETHEREUM,
                "0xowner",
                collection="example",
                limit=100,
                next_cursor="abc",
            )
        )
    finally:
        run(http_client.aclose())

    assert nfts[0].identifier == "42"
    assert next_cursor is None


def test_account_orders_and_balances_use_documented_pagination() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/offers_received"):
            assert request.url.params.multi_items() == [
                ("after", "cursor"),
                ("limit", "25"),
                ("collection_slugs", "one"),
                ("collection_slugs", "two"),
                ("chains", "ethereum"),
                ("sort_by", "TOP_ASSET_OFFER"),
                ("sort_direction", "desc"),
            ]
            return httpx.Response(200, json={"offers": [offer_payload()]})
        if request.url.path.endswith("/offers"):
            assert request.url.params.multi_items() == [
                ("limit", "101"),
                ("sort_by", "END_TIME"),
                ("sort_direction", "desc"),
            ]
            return httpx.Response(200, json={"offers": [offer_payload()]})
        if request.url.path.endswith("/listings"):
            assert request.url.params.multi_items() == [
                ("limit", "101"),
                ("sort_by", "END_TIME"),
                ("sort_direction", "desc"),
            ]
            return httpx.Response(200, json={"listings": [listing_payload()]})
        assert request.url.path.endswith("/tokens")
        assert request.url.params.multi_items() == [
            ("limit", "20"),
            ("chains", "ethereum"),
            ("sort_direction", "desc"),
            ("disable_spam_filtering", "false"),
        ]
        return httpx.Response(
            200,
            json={
                "token_balances": [
                    {
                        "address": "0xweth",
                        "chain": "ethereum",
                        "name": "Wrapped Ether",
                        "symbol": "WETH",
                        "usd_price": "2500.25",
                        "decimals": 18,
                        "opensea_url": "https://opensea.io/token/ethereum/0xweth",
                        "quantity": "1.25",
                        "usd_value": "3125.3125",
                    }
                ]
            },
        )

    async def exercise(client: OpenSeaClient):
        received_offers = await client.get_profile_offers_received(
            "0xowner",
            after="cursor",
            limit=25,
            collection_slugs=["one", "two"],
            chains=[ChainIdentifier.ETHEREUM],
            sort_by=ProfileOffersReceivedSortBy.TOP_ASSET_OFFER,
        )
        made_offers = await client.get_profile_offers(
            "0xowner", limit=101, sort_by=ProfileOrderSortBy.END_TIME
        )
        listings = await client.get_profile_listings(
            "0xowner", limit=101, sort_by=ProfileOrderSortBy.END_TIME
        )
        balances = await client.get_token_balances_by_account(
            "0xowner", chains=[ChainIdentifier.ETHEREUM]
        )
        return received_offers, made_offers, listings, balances

    client, http_client = make_client(handler)
    try:
        (received, _), (made, _), (listings, _), (balances, _) = run(exercise(client))
    finally:
        run(http_client.aclose())

    assert received[0].price.value == Decimal(900000000000000000)
    assert made[0].protocol_data is not None
    assert made[0].protocol_data.parameters.offer[0].start_amount == Decimal(1)
    assert listings[0].price.current.value == Decimal(1000000000000000000)
    assert balances[0].quantity == Decimal("1.25")


def test_best_nft_offer_and_listing_parse_direct_models() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if "/offers/" in request.url.path:
            return httpx.Response(200, json=offer_payload())
        if request.url.path == "/api/v2/listings/collection/example/best":
            assert request.url.params.multi_items() == [
                ("include_private_listings", "false"),
                ("traits", "[]"),
                ("limit", "20"),
                ("next", "cursor"),
            ]
            return httpx.Response(
                200,
                json={"listings": [listing_payload()], "next": None},
            )
        assert request.url.params["include_private_listings"] == "false"
        return httpx.Response(200, json=listing_payload())

    async def exercise(client: OpenSeaClient):
        return (
            await client.get_best_offer_nft("example", "42"),
            await client.get_best_listing_nft("example", "42", include_private_listings=False),
            await client.get_best_listings_collection(
                "example",
                include_private_listings=False,
                traits="[]",
                limit=20,
                next_cursor="cursor",
            ),
        )

    client, http_client = make_client(handler)
    try:
        offer, listing, (listings, next_cursor) = run(exercise(client))
    finally:
        run(http_client.aclose())

    assert offer.order_hash == "0xoffer"
    assert listing.order_hash == "0xlisting"
    assert listings[0].order_hash == "0xlisting"
    assert next_cursor is None


def test_order_protocol_data_is_fully_validated() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        payload = offer_payload()
        protocol_data = payload["protocol_data"]
        assert isinstance(protocol_data, dict)
        parameters = protocol_data["parameters"]
        assert isinstance(parameters, dict)
        del parameters["counter"]
        return httpx.Response(200, json=payload)

    client, http_client = make_client(handler)
    try:
        with pytest.raises(OpenSeaInvalidResponseError):
            run(client.get_best_offer_nft("example", "42"))
    finally:
        run(http_client.aclose())


def test_paginated_endpoints_accept_explicit_null_next() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v2/collections/top":
            payload: dict[str, object] = {"collections": [], "next": None}
        elif request.url.path.endswith("/offer_aggregates"):
            payload = {"offer_aggregates": [], "next": None}
        elif request.url.path.endswith("/tokens"):
            payload = {"token_balances": [], "next": None}
        elif request.url.path.endswith("/offers") or request.url.path.endswith("/offers_received"):
            payload = {"offers": [], "next": None}
        elif "/listings" in request.url.path:
            payload = {"listings": [], "next": None}
        elif request.url.path.endswith("/nfts"):
            payload = {"nfts": [], "next": None}
        else:
            payload = {"asset_events": [], "next": None}
        return httpx.Response(200, json=payload)

    async def fetch_pages(client: OpenSeaClient) -> list[str | None]:
        pages = [
            await client.list_events_by_account("0xaccount"),
            await client.list_events_by_collection("example"),
            await client.list_events_by_nft(ChainIdentifier.ETHEREUM, "0xcontract", "42"),
            await client.get_collection_sales("example"),
            await client.get_top_collections(),
            await client.get_collection_offer_aggregates("example"),
            await client.get_nfts_by_collection("example"),
            await client.get_nfts_by_account(ChainIdentifier.ETHEREUM, "0xaccount"),
            await client.get_token_balances_by_account("0xaccount"),
            await client.get_profile_offers("0xaccount"),
            await client.get_profile_offers_received("0xaccount"),
            await client.get_profile_listings("0xaccount"),
            await client.get_best_listings_collection("example"),
        ]
        return [next_cursor for _, next_cursor in pages]

    client, http_client = make_client(handler)
    try:
        cursors = run(fetch_pages(client))
    finally:
        run(http_client.aclose())

    assert cursors == [None] * 13


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


def test_get_collection_validates_direct_response_model() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={})

    client, http_client = make_client(handler)
    try:
        with pytest.raises(OpenSeaInvalidResponseError):
            run(client.get_collection("broken"))
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
        with pytest.raises(ValueError, match="between 1 and 100"):
            run(client.get_top_collections(limit=101))
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
