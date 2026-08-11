export default function openseaFixes() {
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
      },
    },
  };
}
