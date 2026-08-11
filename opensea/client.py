import json
from collections.abc import Sequence
from decimal import Decimal
from types import TracebackType
from typing import Self, TypeVar
from urllib.parse import quote

import httpx
from better_proxy import Proxy
from pydantic import BaseModel, TypeAdapter, ValidationError

from ._envelopes import (
    _ASSET_EVENTS_ADAPTER,
    _COLLECTION_OFFER_AGGREGATES_ADAPTER,
    _COLLECTION_SALES_ADAPTER,
    _COLLECTION_STATS_ADAPTER,
    _NFT_ADAPTER,
    _NFT_LIST_ADAPTER,
    _TOP_COLLECTIONS_ADAPTER,
)
from .enums import ChainIdentifier, EventType, SortDirection, TopCollectionsSortBy
from .errors import (
    OpenSeaAPIError,
    OpenSeaBadRequestError,
    OpenSeaConfigurationError,
    OpenSeaInvalidResponseError,
    OpenSeaNotFoundError,
    OpenSeaTransportError,
)
from .models import (
    AssetEvent,
    Collection,
    CollectionDetailed,
    CollectionIntervalStat,
    CollectionOfferAggregate,
    Nft,
    NftDetailed,
    SaleEvent,
    TotalCollectionStats,
)

_DEFAULT_BASE_URL = "https://api.opensea.io"
_ERROR_BODY_LIMIT = 1_000
_EnvelopeT = TypeVar("_EnvelopeT")
_ModelT = TypeVar("_ModelT", bound=BaseModel)


class OpenSeaClient:
    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: httpx.Timeout | float = 30.0,
        proxy: Proxy | str | None = None,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key:
            raise OpenSeaConfigurationError("api_key must not be empty")
        if proxy is not None and http_client is not None:
            raise OpenSeaConfigurationError(
                "proxy cannot be combined with a caller-supplied http_client"
            )

        self._api_key = api_key
        self._base_url = str(httpx.URL(base_url)).rstrip("/")
        self._owns_http_client = http_client is None

        if http_client is None:
            normalized_proxy = Proxy.from_str(proxy) if isinstance(proxy, str) else proxy
            self._http_client = httpx.AsyncClient(
                timeout=timeout,
                proxy=normalized_proxy.as_url if normalized_proxy is not None else None,
            )
        else:
            self._http_client = http_client

    async def list_events_by_collection(
        self,
        slug: str,
        *,
        after: int | None = None,
        before: int | None = None,
        event_type: EventType | Sequence[EventType] | None = None,
        traits: str | None = None,
        limit: int | None = None,
        next_cursor: str | None = None,
    ) -> tuple[list[AssetEvent], str | None]:
        """Return collection events and the next-page cursor."""
        self._validate_limit(limit)
        params: list[tuple[str, str | int]] = []
        self._append_optional(params, "after", after)
        self._append_optional(params, "before", before)
        if isinstance(event_type, EventType):
            params.append(("event_type", event_type.value))
        elif event_type is not None:
            params.extend(("event_type", item.value) for item in event_type)
        self._append_optional(params, "traits", traits)
        self._append_optional(params, "limit", limit)
        self._append_optional(params, "next", next_cursor)

        slug_path = quote(slug, safe="")
        envelope = await self._get_envelope(
            f"/api/v2/events/collection/{slug_path}", params, _ASSET_EVENTS_ADAPTER
        )
        return envelope["asset_events"], envelope.get("next")

    async def get_top_collections(
        self,
        *,
        sort_by: TopCollectionsSortBy = TopCollectionsSortBy.ONE_DAY_VOLUME,
        chains: Sequence[ChainIdentifier] | None = None,
        category: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> tuple[list[Collection], str | None]:
        """Return ranked collections and the next-page cursor."""
        self._validate_limit(limit, maximum=100)
        params: list[tuple[str, str | int]] = [("sort_by", sort_by.value)]
        if chains is not None:
            params.append(("chains", ",".join(chain.value for chain in chains)))
        self._append_optional(params, "category", category)
        params.append(("limit", limit))
        self._append_optional(params, "cursor", cursor)

        envelope = await self._get_envelope(
            "/api/v2/collections/top", params, _TOP_COLLECTIONS_ADAPTER
        )
        return envelope["collections"], envelope.get("next")

    async def get_collection(self, slug: str) -> CollectionDetailed:
        """Return one collection with its detailed metadata."""
        slug_path = quote(slug, safe="")
        return await self._get_model(f"/api/v2/collections/{slug_path}", [], CollectionDetailed)

    async def get_collection_sales(
        self,
        slug: str,
        *,
        after: int | None = None,
        before: int | None = None,
        traits: str | None = None,
        limit: int | None = None,
        next_cursor: str | None = None,
    ) -> tuple[list[SaleEvent], str | None]:
        """Return collection sales and the next-page cursor."""
        self._validate_limit(limit)
        params: list[tuple[str, str | int]] = []
        self._append_optional(params, "after", after)
        self._append_optional(params, "before", before)
        params.append(("event_type", EventType.SALE.value))
        self._append_optional(params, "traits", traits)
        self._append_optional(params, "limit", limit)
        self._append_optional(params, "next", next_cursor)

        slug_path = quote(slug, safe="")
        envelope = await self._get_envelope(
            f"/api/v2/events/collection/{slug_path}", params, _COLLECTION_SALES_ADAPTER
        )
        return envelope["asset_events"], envelope.get("next")

    async def get_collection_stats(
        self, slug: str
    ) -> tuple[list[CollectionIntervalStat], TotalCollectionStats]:
        """Return interval statistics followed by aggregate collection totals."""
        slug_path = quote(slug, safe="")
        envelope = await self._get_envelope(
            f"/api/v2/collections/{slug_path}/stats", [], _COLLECTION_STATS_ADAPTER
        )
        return envelope["intervals"], envelope["total"]

    async def get_collection_offer_aggregates(
        self,
        slug: str,
        *,
        limit: int = 20,
        cursor: str | None = None,
        sort_direction: SortDirection = SortDirection.DESC,
    ) -> tuple[list[CollectionOfferAggregate], str | None]:
        """Return collection offer aggregates and the next-page cursor."""
        self._validate_limit(limit, maximum=100)
        params: list[tuple[str, str | int]] = [("limit", limit)]
        self._append_optional(params, "cursor", cursor)
        params.append(("sort_direction", sort_direction.value))

        slug_path = quote(slug, safe="")
        envelope = await self._get_envelope(
            f"/api/v2/collections/{slug_path}/offer_aggregates",
            params,
            _COLLECTION_OFFER_AGGREGATES_ADAPTER,
        )
        return envelope["offer_aggregates"], envelope.get("next")

    async def get_nfts_by_collection(
        self,
        slug: str,
        *,
        traits: str | None = None,
        has_agent_binding: bool | None = None,
        limit: int | None = None,
        next_cursor: str | None = None,
    ) -> tuple[list[Nft], str | None]:
        """Return collection NFTs and the next-page cursor."""
        self._validate_limit(limit)
        params: list[tuple[str, str | int]] = []
        self._append_optional(params, "traits", traits)
        if has_agent_binding is not None:
            params.append(("has_agent_binding", str(has_agent_binding).lower()))
        self._append_optional(params, "limit", limit)
        self._append_optional(params, "next", next_cursor)

        slug_path = quote(slug, safe="")
        envelope = await self._get_envelope(
            f"/api/v2/collection/{slug_path}/nfts", params, _NFT_LIST_ADAPTER
        )
        return envelope["nfts"], envelope.get("next")

    async def get_nft(
        self,
        chain: ChainIdentifier,
        address: str,
        identifier: str,
    ) -> NftDetailed:
        """Return one detailed NFT."""
        chain_path = quote(str(chain), safe="")
        address_path = quote(address, safe="")
        identifier_path = quote(identifier, safe="")
        envelope = await self._get_envelope(
            f"/api/v2/chain/{chain_path}/contract/{address_path}/nfts/{identifier_path}",
            [],
            _NFT_ADAPTER,
        )
        return envelope["nft"]

    async def aclose(self) -> None:
        if self._owns_http_client and not self._http_client.is_closed:
            await self._http_client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def _get_envelope(
        self,
        path: str,
        params: list[tuple[str, str | int]],
        adapter: TypeAdapter[_EnvelopeT],
    ) -> _EnvelopeT:
        response = await self._request("GET", path, params=params)
        try:
            payload = json.loads(response.content, parse_float=Decimal)
            return adapter.validate_python(payload)
        except (ValueError, ValidationError) as exc:
            safe_url = str(response.request.url.copy_with(query=None))
            raise OpenSeaInvalidResponseError(
                status_code=response.status_code,
                method=response.request.method,
                url=safe_url,
            ) from exc

    async def _get_model(
        self,
        path: str,
        params: list[tuple[str, str | int]],
        model_type: type[_ModelT],
    ) -> _ModelT:
        response = await self._request("GET", path, params=params)
        try:
            payload = json.loads(response.content, parse_float=Decimal)
            return model_type.model_validate(payload)
        except (ValueError, ValidationError) as exc:
            safe_url = str(response.request.url.copy_with(query=None))
            raise OpenSeaInvalidResponseError(
                status_code=response.status_code,
                method=response.request.method,
                url=safe_url,
            ) from exc

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: list[tuple[str, str | int]],
    ) -> httpx.Response:
        url = f"{self._base_url}{path}"
        try:
            response = await self._http_client.request(
                method,
                url,
                params=params,
                headers={"Accept": "application/json", "x-api-key": self._api_key},
            )
        except httpx.HTTPError as exc:
            raise OpenSeaTransportError(method=method, url=url, message=str(exc)) from exc

        if not response.is_success:
            self._raise_api_error(response)
        return response

    @staticmethod
    def _raise_api_error(response: httpx.Response) -> None:
        try:
            data = response.json()
        except ValueError:
            data = None

        body_excerpt = response.text[:_ERROR_BODY_LIMIT] or None
        safe_url = str(response.request.url.copy_with(query=None))
        error_type: type[OpenSeaAPIError]
        if response.status_code == 400:
            error_type = OpenSeaBadRequestError
        elif response.status_code == 404:
            error_type = OpenSeaNotFoundError
        else:
            error_type = OpenSeaAPIError
        raise error_type(
            status_code=response.status_code,
            method=response.request.method,
            url=safe_url,
            data=data,
            body_excerpt=body_excerpt,
            request_id=response.headers.get("x-request-id"),
        )

    @staticmethod
    def _append_optional(
        params: list[tuple[str, str | int]], name: str, value: str | int | None
    ) -> None:
        if value is not None:
            params.append((name, value))

    @staticmethod
    def _validate_limit(limit: int | None, *, maximum: int = 200) -> None:
        if limit is not None and not 1 <= limit <= maximum:
            raise ValueError(f"limit must be between 1 and {maximum}")
