from decimal import Decimal

from pydantic import Field

from ..enums import OrderStatus
from .base import OpenSeaModel
from .events import Criteria


class OrderAsset(OpenSeaModel):
    contract: str
    identifier: str | None = None


class Price(OpenSeaModel):
    currency: str
    decimals: int
    value: Decimal


class ListingPrice(OpenSeaModel):
    current: Price


class OrderItem(OpenSeaModel):
    item_type: int = Field(alias="itemType")
    token: str
    identifier_or_criteria: str = Field(alias="identifierOrCriteria")
    start_amount: Decimal = Field(alias="startAmount")
    end_amount: Decimal = Field(alias="endAmount")


class ConsiderationItem(OrderItem):
    recipient: str


class ProtocolParameters(OpenSeaModel):
    offerer: str
    offer: list[OrderItem]
    consideration: list[ConsiderationItem]
    start_time: str = Field(alias="startTime")
    end_time: str = Field(alias="endTime")
    order_type: int = Field(alias="orderType")
    zone: str
    zone_hash: str = Field(alias="zoneHash")
    salt: str
    conduit_key: str = Field(alias="conduitKey")
    total_original_consideration_items: int = Field(alias="totalOriginalConsiderationItems")
    counter: int


class ProtocolData(OpenSeaModel):
    parameters: ProtocolParameters
    signature: str | None = None


class Offer(OpenSeaModel):
    order_hash: str
    chain: str
    price: Price
    remaining_quantity: int
    status: OrderStatus
    protocol_data: ProtocolData | None = None
    protocol_address: str | None = None
    asset: OrderAsset | None = None
    order_created_at: int | None = None
    criteria: Criteria | None = None


class Listing(OpenSeaModel):
    order_hash: str
    chain: str
    price: ListingPrice
    remaining_quantity: int
    status: OrderStatus
    type: str
    protocol_data: ProtocolData | None = None
    protocol_address: str | None = None
    asset: OrderAsset | None = None
    order_created_at: int | None = None
