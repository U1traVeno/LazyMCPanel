FROM eclipse-temurin:21-jre-focal

COPY ../entrypoint.sh /app/entrypoint.sh

RUN apt-get update && \
    apt-get install -y python3.12 python3-pip python3.12-venv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENTRYPOINT ["/app/entrypoint.sh"]