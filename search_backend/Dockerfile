# Use Rust image to build binary
FROM rust:1.76 AS builder
WORKDIR /app/lecturesearch-web
COPY . .
RUN cargo install --path . && cargo build --release

# Start Ubuntu image and run Rust binary here
# TODO: Figure out how to install Typesense here
FROM ubuntu:22.04
WORKDIR /app
RUN apt update && apt install -y curl sqlite net-tools
COPY --from=builder /app/lecturesearch-web/target/release/lecturesearch-web /app/lecturesearch-web
EXPOSE 8080
CMD ["/app/lecturesearch-web"]