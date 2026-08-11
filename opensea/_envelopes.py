from typing import NotRequired, TypedDict

from pydantic import TypeAdapter

from .models import (
    AssetEvent,
    CollectionIntervalStat,
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


class _NftListEnvelope(TypedDict):
    nfts: list[Nft]
    next: NotRequired[str]


class _NftEnvelope(TypedDict):
    nft: NftDetailed


_ASSET_EVENTS_ADAPTER = TypeAdapter(_AssetEventsEnvelope)
_COLLECTION_SALES_ADAPTER = TypeAdapter(_CollectionSalesEnvelope)
_COLLECTION_STATS_ADAPTER = TypeAdapter(_CollectionStatsEnvelope)
_NFT_LIST_ADAPTER = TypeAdapter(_NftListEnvelope)
_NFT_ADAPTER = TypeAdapter(_NftEnvelope)
