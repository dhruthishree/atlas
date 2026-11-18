FROM rust:1.80-slim as builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
RUN apt-get update && apt-get install -y ca-certificates curl && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/core-engine /app/core-engine
EXPOSE 8080
ENV PORT=8080
ENV HOST=0.0.0.0
CMD ["/app/core-engine"]
