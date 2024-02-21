# Use Rust image to build binary
FROM rust:1.76 AS builder
WORKDIR /app/lecturesearch-web
COPY . .
RUN cargo install --path . && cargo build --release
EXPOSE 8080

# Install Typesense server and run Rust binary here
FROM typesense/typesense:0.25.2
WORKDIR /app
ENV TYPESENSE_API_KEY="xyz"
RUN mkdir -p /app/typesense-data
ENV TYPESENSE_DATA_DIR=/app/typesense-data
EXPOSE 8108
COPY --from=builder /app/lecturesearch-web/target/release/lecturesearch-web /app/lecturesearch-web
RUN typesense-server --data-dir=${TYPESENSE_DATA_DIR} --api-key=${TYPESENSE_API_KEY}
CMD ["/app/lecturesearch-web"]