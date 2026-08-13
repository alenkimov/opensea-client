export default function openseaFixes() {
  const paginatedResponseSchemas = [
    "AssetEventsResponse",
    "CollectionOfferAggregatesPaginatedResponse",
    "CollectionPaginatedResponse",
    "NftListResponse",
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
        "stringify-string-parameter-examples": () => ({
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
