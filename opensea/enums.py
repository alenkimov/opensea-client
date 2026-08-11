from enum import StrEnum


class ChainIdentifier(StrEnum):
    BLAST = "blast"
    BASE = "base"
    ETHEREUM = "ethereum"
    ZORA = "zora"
    ARBITRUM = "arbitrum"
    SEI = "sei"
    AVALANCHE = "avalanche"
    POLYGON = "polygon"
    OPTIMISM = "optimism"
    APE_CHAIN = "ape_chain"
    FLOW = "flow"
    B3 = "b3"
    SONEIUM = "soneium"
    RONIN = "ronin"
    BERA_CHAIN = "bera_chain"
    SOLANA = "solana"
    SHAPE = "shape"
    UNICHAIN = "unichain"
    GUNZILLA = "gunzilla"
    ABSTRACT = "abstract"
    ANIMECHAIN = "animechain"
    HYPEREVM = "hyperevm"
    SOMNIA = "somnia"
    MONAD = "monad"
    HYPERLIQUID = "hyperliquid"
    MEGAETH = "megaeth"
    INK = "ink"
    ROBINHOOD = "robinhood"
    STABLECHAIN = "stablechain"


class EventType(StrEnum):
    SALE = "sale"
    TRANSFER = "transfer"
    MINT = "mint"
    LISTING = "listing"
    OFFER = "offer"
    TRAIT_OFFER = "trait_offer"
    COLLECTION_OFFER = "collection_offer"


class TopCollectionsSortBy(StrEnum):
    ONE_DAY_VOLUME = "one_day_volume"
    SEVEN_DAYS_VOLUME = "seven_days_volume"
    THIRTY_DAYS_VOLUME = "thirty_days_volume"
    FLOOR_PRICE = "floor_price"
    ONE_DAY_SALES = "one_day_sales"
    SEVEN_DAYS_SALES = "seven_days_sales"
    THIRTY_DAYS_SALES = "thirty_days_sales"
    TOTAL_VOLUME = "total_volume"
    TOTAL_SALES = "total_sales"


class SortDirection(StrEnum):
    ASC = "asc"
    DESC = "desc"
