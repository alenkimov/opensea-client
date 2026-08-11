from .base import OpenSeaModel
from .nfts import Nft


class CollectionInner(OpenSeaModel):
    slug: str


class ContractInner(OpenSeaModel):
    address: str


class NumericTraitData(OpenSeaModel):
    type: str
    min: float | None = None
    max: float | None = None


class TraitData(OpenSeaModel):
    type: str
    value: str


class Criteria(OpenSeaModel):
    collection: CollectionInner | None = None
    contract: ContractInner | None = None
    traits: list[TraitData] | None = None
    numeric_traits: list[NumericTraitData] | None = None
    encoded_token_ids: str | None = None


class Payment(OpenSeaModel):
    quantity: str
    token_address: str
    decimals: int
    symbol: str


class Event(OpenSeaModel):
    event_type: str
    event_timestamp: int
    chain: str
    quantity: int
    transaction: str | None = None
    order_hash: str | None = None
    protocol_address: str | None = None
    payment: Payment | None = None


class OrderEvent(Event):
    order_type: str
    maker: str
    is_private_listing: bool
    start_date: int | None = None
    expiration_date: int | None = None
    asset: Nft | None = None
    taker: str | None = None
    criteria: Criteria | None = None


class SaleEvent(Event):
    closing_date: int
    seller: str
    buyer: str
    nft: Nft | None = None


class TransferEvent(Event):
    transfer_type: str
    from_address: str
    to_address: str
    nft: Nft | None = None


AssetEvent = OrderEvent | SaleEvent | TransferEvent
