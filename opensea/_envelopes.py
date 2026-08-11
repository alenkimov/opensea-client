from typing import NotRequired, TypedDict

from pydantic import TypeAdapter

from .models import (
    AssetEvent,
    Collection,
    CollectionIntervalStat,
    CollectionOfferAggregate,
    Nft,
    NftDetailed,
    SaleEvent,
    TotalCollectionStats,
)


class _AssetEventsEnvelope(TypedDict):
    asset_events: list[AssetEvent]
    next: NotRequired[str]


class _CollectionSalesEnvelope(TypedDict):
    asset_events: list[SaleEvent]
    next: NotRequired[str]


class _CollectionStatsEnvelope(TypedDict):
    total: TotalCollectionStats
    intervals: list[CollectionIntervalStat]


class _TopCollectionsEnvelope(TypedDict):
    collections: list[Collection]
    next: NotRequired[str]


class _CollectionOfferAggregatesEnvelope(TypedDict):
    offer_aggregates: list[CollectionOfferAggregate]
    next: NotRequired[str]


class _NftListEnvelope(TypedDict):
    nfts: list[Nft]
    next: NotRequired[str]


class _NftEnvelope(TypedDict):
    nft: NftDetailed


_ASSET_EVENTS_ADAPTER = TypeAdapter(_AssetEventsEnvelope)
_COLLECTION_SALES_ADAPTER = TypeAdapter(_CollectionSalesEnvelope)
_COLLECTION_STATS_ADAPTER = TypeAdapter(_CollectionStatsEnvelope)
_TOP_COLLECTIONS_ADAPTER = TypeAdapter(_TopCollectionsEnvelope)
_COLLECTION_OFFER_AGGREGATES_ADAPTER = TypeAdapter(_CollectionOfferAggregatesEnvelope)
_NFT_LIST_ADAPTER = TypeAdapter(_NftListEnvelope)
_NFT_ADAPTER = TypeAdapter(_NftEnvelope)
