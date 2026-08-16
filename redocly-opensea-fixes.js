export default function openseaFixes() {
  const paginatedResponseSchemas = [
    "AssetEventsResponse",
    "CollectionOfferAggregatesPaginatedResponse",
    "CollectionPaginatedResponse",
    "NftListResponse",
    "OffersResponse",
    "ListingsResponse",
    "TokenBalancePaginatedResponse",
  ];

  return {
    id: "opensea-fixes",

    decorators: {
      oas3: {
        "fix-empty-event-schema": () => ({
          Root: {
            leave(root) {
              const event = root.components?.schemas?.Event;

              if (event && Object.keys(event).length === 0) {
                event.type = "object";
              }
            },
          },
        }),
        "normalize-examples": () => ({
          Parameter: {
            leave(parameter) {
              const example = parameter.example;

              if (
                parameter.schema?.type === "string" &&
                example !== undefined &&
                typeof example !== "string"
              ) {
                parameter.example =
                  typeof example === "object" ? JSON.stringify(example) : String(example);
              }
              if (
                parameter.schema?.type === "array" &&
                typeof example === "string"
              ) {
                parameter.example = example.split(",").map((item) => item.trim());
              }
              if (
                Array.isArray(parameter.schema?.enum) &&
                typeof parameter.example === "string" &&
                !parameter.schema.enum.includes(parameter.example)
              ) {
                const matchingValue = parameter.schema.enum.find(
                  (value) =>
                    typeof value === "string" &&
                    value.toLowerCase() === parameter.example.toLowerCase(),
                );
                if (matchingValue !== undefined) {
                  parameter.example = matchingValue;
                }
              }
            },
          },
          Schema: {
            leave(schema) {
              if (
                schema.type === "string" &&
                schema.example !== undefined &&
                typeof schema.example !== "string"
              ) {
                schema.example = String(schema.example);
              }
            },
          },
        }),
        "make-pagination-next-nullable": () => ({
          Root: {
            leave(root) {
              for (const schemaName of paginatedResponseSchemas) {
                const next = root.components?.schemas?.[schemaName]?.properties?.next;

                if (next?.type === "string") {
                  next.type = ["string", "null"];
                }
              }
            },
          },
        }),
      },
    },
  };
}
