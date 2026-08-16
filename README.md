# OpenSea Client

Небольшой строго асинхронный Python 3.13+ клиент для операций из
[`opensea-filtered.yaml`](opensea-filtered.yaml). Клиент использует один переиспользуемый
`httpx.AsyncClient`, Pydantic v2 и `better-proxy.Proxy`.

## Установка

После клонирования репозитория установите библиотеку и зависимости через uv:

```shell
uv sync
```

Из другого uv-проекта библиотеку можно установить по локальному пути:

```shell
uv add ../opensea-client
```

## Использование

```python
import asyncio

from opensea import OpenSeaClient


async def main() -> None:
    async with OpenSeaClient("your-api-key") as client:
        sales, next_cursor = await client.get_collection_sales("doodles-official", limit=20)
        for sale in sales:
            print(sale.nft, sale.payment)

        intervals, total = await client.get_collection_stats("doodles-official")
        print(intervals, total.floor_price)


asyncio.run(main())
```

Доступные методы:

- `list_events_by_account()` → `(list[AssetEvent], next_cursor)`;
- `list_events_by_collection()` → `(list[AssetEvent], next_cursor)`;
- `list_events_by_nft()` → `(list[AssetEvent], next_cursor)`;
- `get_collection_sales()` → `(list[SaleEvent], next_cursor)`;
- `get_top_collections()` → `(list[Collection], next_cursor)`;
- `get_collection()` → `CollectionDetailed`;
- `get_collection_offer_aggregates()` → `(list[CollectionOfferAggregate], next_cursor)`;
- `get_collection_stats()` → `(list[CollectionIntervalStat], TotalCollectionStats)`;
- `get_nfts_by_collection()` → `(list[Nft], next_cursor)`;
- `get_nfts_by_account()` → `(list[Nft], next_cursor)`;
- `get_nft()` → `NftDetailed`;
- `get_token_balances_by_account()` → `(list[TokenBalance], next_cursor)`;
- `get_profile_listings()` → `(list[Listing], next_cursor)`;
- `get_profile_offers()` → `(list[Offer], next_cursor)`;
- `get_profile_offers_received()` → `(list[Offer], next_cursor)`;
- `get_best_offer_nft()` → `Offer`;
- `get_best_listing_nft()` → `Listing`;
- `get_best_listings_collection()` → `(list[Listing], next_cursor)`.

Можно передать `proxy=Proxy(...)` либо готовый `httpx.AsyncClient`. Эти параметры нельзя
совмещать: транспорт и прокси переданного клиента настраивает вызывающая сторона. Внешний клиент
не закрывается вызовом `OpenSeaClient.aclose()`.

## Разработка

```shell
uv run ruff check .
uv run pytest -q
npm ci
npm exec -- redocly lint opensea-filtered.yaml
```

Чтобы заново получить сокращённую спецификацию из `opensea-api.json`:

```shell
npm exec -- redocly bundle opensea --output opensea-filtered.yaml
```
