FROM eclipse-temurin:8-jre-focal

RUN apt-get update && \
    apt-get install -y python3.12 python3-pip python3.12-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app