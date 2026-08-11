from decimal import Decimal

from pydantic import TypeAdapter

from opensea.models import (
    AssetEvent,
    CollectionFee,
    Nft,
    OfferAggregatePrice,
    OrderEvent,
    TotalCollectionStats,
    TransferEvent,
)


def test_event_union_uses_required_shape_fields() -> None:
    events = TypeAdapter(list[AssetEvent]).validate_python(
        [
            {
                "event_type": "listing",
                "event_timestamp": 1,
                "chain": "ethereum",
                "quantity": 1,
                "order_type": "basic",
                "maker": "0xmaker",
                "is_private_listing": False,
            },
            {
                "event_type": "transfer",
                "event_timestamp": 2,
                "chain": "ethereum",
                "quantity": 1,
                "transfer_type": "single",
                "from_address": "0xfrom",
                "to_address": "0xto",
            },
        ]
    )

    assert isinstance(events[0], OrderEvent)
    assert isinstance(events[1], TransferEvent)


def test_monetary_json_numbers_preserve_decimal_precision() -> None:
    stats = TotalCollectionStats.model_validate(
        {
            "volume": Decimal("123.123456789012345678"),
            "sales": 1,
            "num_owners": 1,
            "floor_price": Decimal("0.020498799999"),
            "floor_price_symbol": "ETH",
        }
    )
    offer_price = OfferAggregatePrice.model_validate(
        {
            "usd_price": "35.50",
            "token_unit": Decimal("0.0142"),
            "chain": "ethereum",
        }
    )
    fee = CollectionFee.model_validate(
        {
            "fee": Decimal("2.500000000000000001"),
            "recipient": "0xrecipient",
            "required": True,
        }
    )
    nft = Nft.model_validate(
        {
            "identifier": "1",
            "collection": "example",
            "contract": "0xabc",
            "token_standard": "erc721",
            "opensea_url": "https://example.com",
            "updated_at": "2026-01-01T00:00:00Z",
            "is_disabled": False,
            "is_nsfw": False,
            "traits": [],
            "estimated_value_usd": Decimal("1234.567890123456789"),
        }
    )

    assert stats.volume == Decimal("123.123456789012345678")
    assert stats.floor_price == Decimal("0.020498799999")
    assert offer_price.token_unit == Decimal("0.0142")
    assert fee.fee == Decimal("2.500000000000000001")
    assert nft.estimated_value_usd == Decimal("1234.567890123456789")
