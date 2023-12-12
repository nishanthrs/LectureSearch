# Web Server: Search Backend

* Implemented via Rust Axum web server framework

## Typesense Rust Client

* No official Rust client supported, so had to use the [Typesense OpenAPI spec]()
* Generated it via `openapi-generator-cli generate -i typesense_openapi.yml -g rust -o ./typesense_openapi_codegen`
* However, even that codegen cmd didn't work, so I cloned the [Typesense Rust client repo](https://github.com/typesense/typesense-rust/) and moved the `typesense_codegen` pkg to this folder
* Figured out how to write the code by reading [the docs](https://github.com/typesense/typesense-rust/tree/main/typesense_codegen) and the method headers
* Testing it out by starting a local Typesense server: `./typesense-server --data-dir=$(pwd)/typesense-data --api-key=$TYPESENSE_API_KEY --enable-cors`

TODO: Experiment with other search index offerings ([Meilisearch](https://www.meilisearch.com/docs/reference/api/overview)) or vector DBs ([Qdrant](https://qdrant.tech/documentation/))
