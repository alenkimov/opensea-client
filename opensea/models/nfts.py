from typing import Any

from .base import OpenSeaModel


class AgentNftResponse(OpenSeaModel):
    chain: str
    token_id: str
    contract_address: str


class AgentBindingResponse(OpenSeaModel):
    agent_id: str
    binding_contract: str
    agent: AgentNftResponse
    registered_by: str | None = None


class Trait(OpenSeaModel):
    trait_type: str
    value: Any
    display_type: str | None = None
    max_value: str | None = None


class Nft(OpenSeaModel):
    identifier: str
    collection: str
    contract: str
    token_standard: str
    opensea_url: str
    updated_at: str
    is_disabled: bool
    is_nsfw: bool
    traits: list[Trait]
    name: str | None = None
    description: str | None = None
    image_url: str | None = None
    display_image_url: str | None = None
    display_animation_url: str | None = None
    metadata_url: str | None = None
    original_image_url: str | None = None
    original_animation_url: str | None = None
    estimated_value_usd: float | None = None
    decimals: int | None = None


class Owner(OpenSeaModel):
    address: str
    quantity: int
    quantity_string: str


class Rarity(OpenSeaModel):
    strategy_id: str
    strategy_version: str
    rank: int | None = None


class SubscriptionInfoResponse(OpenSeaModel):
    is_renewable: bool
    is_expired: bool
    expires_at: float | None = None


class NftDetailed(Nft):
    creator: str
    owners: list[Owner]
    is_suspicious: bool
    animation_url: str | None = None
    rarity: Rarity | None = None
    subscription: SubscriptionInfoResponse | None = None
    agent_binding: AgentBindingResponse | None = None
