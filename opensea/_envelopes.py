from typing import NotRequired, TypedDict

from pydantic import TypeAdapter

from .models import (
    AssetEvent,
    Collection,
    CollectionIntervalStat,
    CollectionOfferAggregate,
    Listing,
    Nft,
    NftDetailed,
    Offer,
    SaleEvent,
    TokenBalance,
    TotalCollectionStats,
)


class _AssetEventsEnvelope(TypedDict):
    asset_events: list[AssetEvent]
    next: NotRequired[str | None]


class _CollectionSalesEnvelope(TypedDict):
    asset_events: list[SaleEvent]
    next: NotRequired[str | None]


class _CollectionStatsEnvelope(TypedDict):
    total: TotalCollectionStats
    intervals: list[CollectionIntervalStat]


class _TopCollectionsEnvelope(TypedDict):
    collections: list[Collection]
    next: NotRequired[str | None]


class _CollectionOfferAggregatesEnvelope(TypedDict):
    offer_aggregates: list[CollectionOfferAggregate]
    next: NotRequired[str | None]


class _NftListEnvelope(TypedDict):
    nfts: list[Nft]
    next: NotRequired[str | None]


class _NftEnvelope(TypedDict):
    nft: NftDetailed


class _OffersEnvelope(TypedDict):
    offers: list[Offer]
    next: NotRequired[str | None]


class _ListingsEnvelope(TypedDict):
    listings: list[Listing]
    next: NotRequired[str | None]


class _TokenBalancesEnvelope(TypedDict):
    token_balances: list[TokenBalance]
    next: NotRequired[str | None]


_ASSET_EVENTS_ADAPTER = TypeAdapter(_AssetEventsEnvelope)
_COLLECTION_SALES_ADAPTER = TypeAdapter(_CollectionSalesEnvelope)
_COLLECTION_STATS_ADAPTER = TypeAdapter(_CollectionStatsEnvelope)
_TOP_COLLECTIONS_ADAPTER = TypeAdapter(_TopCollectionsEnvelope)
_COLLECTION_OFFER_AGGREGATES_ADAPTER = TypeAdapter(_CollectionOfferAggregatesEnvelope)
_NFT_LIST_ADAPTER = TypeAdapter(_NftListEnvelope)
_NFT_ADAPTER = TypeAdapter(_NftEnvelope)
_OFFERS_ADAPTER = TypeAdapter(_OffersEnvelope)
_LISTINGS_ADAPTER = TypeAdapter(_ListingsEnvelope)
_TOKEN_BALANCES_ADAPTER = TypeAdapter(_TokenBalancesEnvelope)
