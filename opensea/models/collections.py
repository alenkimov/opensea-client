from .base import OpenSeaModel


class CollectionIntervalStat(OpenSeaModel):
    interval: str
    volume: float
    sales: int


class TotalCollectionStats(OpenSeaModel):
    volume: float
    sales: int
    num_owners: int
    floor_price: float
    floor_price_symbol: str
