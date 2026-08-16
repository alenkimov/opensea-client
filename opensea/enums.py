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


class ProfileOrderSortBy(StrEnum):
    START_TIME = "START_TIME"
    END_TIME = "END_TIME"


class ProfileOffersReceivedSortBy(StrEnum):
    START_TIME = "START_TIME"
    TOP_ASSET_OFFER = "TOP_ASSET_OFFER"


class TokenBalanceSortBy(StrEnum):
    USD_VALUE = "USD_VALUE"
    MARKET_CAP = "MARKET_CAP"
    ONE_DAY_VOLUME = "ONE_DAY_VOLUME"
    PRICE = "PRICE"
    ONE_DAY_PRICE_CHANGE = "ONE_DAY_PRICE_CHANGE"
    SEVEN_DAY_PRICE_CHANGE = "SEVEN_DAY_PRICE_CHANGE"


class OrderStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    FULFILLED = "FULFILLED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class TokenBalanceStatus(StrEnum):
    OK = "OK"
    WARNING = "WARNING"
    SPAM = "SPAM"
    LOW_LIQUIDITY = "LOW_LIQUIDITY"
    LOW_VALUE = "LOW_VALUE"
