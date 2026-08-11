from pydantic import TypeAdapter

from opensea.models import AssetEvent, OrderEvent, TransferEvent


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
