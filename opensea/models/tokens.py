from decimal import Decimal

from ..enums import TokenBalanceStatus
from .base import OpenSeaModel


class TokenBalance(OpenSeaModel):
    address: str
    chain: str
    name: str
    symbol: str
    usd_price: Decimal
    decimals: int
    opensea_url: str
    quantity: Decimal
    usd_value: Decimal
    image_url: str | None = None
    status: TokenBalanceStatus = TokenBalanceStatus.OK
    base_token_liquidity_usd: Decimal | None = None
    quote_token_liquidity_usd: Decimal | None = None
