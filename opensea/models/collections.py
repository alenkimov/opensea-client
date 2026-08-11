from datetime import date
from decimal import Decimal

from .base import OpenSeaModel


class CollectionContract(OpenSeaModel):
    address: str
    chain: str


class Collection(OpenSeaModel):
    collection: str
    name: str
    safelist_status: str
    is_disabled: bool
    is_nsfw: bool
    trait_offers_enabled: bool
    collection_offers_enabled: bool
    opensea_url: str
    contracts: list[CollectionContract]
    description: str | None = None
    image_url: str | None = None
    banner_image_url: str | None = None
    owner: str | None = None
    category: str | None = None
    project_url: str | None = None
    wiki_url: str | None = None
    discord_url: str | None = None
    telegram_url: str | None = None
    twitter_username: str | None = None
    instagram_username: str | None = None


class CollectionFee(OpenSeaModel):
    fee: Decimal
    recipient: str
    required: bool


class CollectionRarity(OpenSeaModel):
    calculated_at: str
    max_rank: int
    total_supply: int
    strategy_id: str
    strategy_version: str


class PaymentToken(OpenSeaModel):
    symbol: str
    address: str
    chain: str
    image: str
    name: str
    decimals: int
    eth_price: str
    usd_price: str


class PricingCurrencies(OpenSeaModel):
    listing_currency: PaymentToken
    offer_currency: PaymentToken


class CollectionDetailed(Collection):
    editors: list[str]
    fees: list[CollectionFee]
    total_supply: int
    unique_item_count: int
    created_date: date
    pricing_currencies: PricingCurrencies
    required_zone: str | None = None
    rarity: CollectionRarity | None = None


class CollectionIntervalStat(OpenSeaModel):
    interval: str
    volume: Decimal
    sales: int


class TotalCollectionStats(OpenSeaModel):
    volume: Decimal
    sales: int
    num_owners: int
    floor_price: Decimal
    floor_price_symbol: str


class OfferAggregatePrice(OpenSeaModel):
    usd_price: str
    token_unit: Decimal
    chain: str
    symbol: str | None = None


class CollectionOfferBidder(OpenSeaModel):
    address: str
    quantity: int


class CollectionOfferAggregate(OpenSeaModel):
    offer_price: OfferAggregatePrice
    total_value: OfferAggregatePrice
    total_offers: int
    bidders: list[CollectionOfferBidder]
