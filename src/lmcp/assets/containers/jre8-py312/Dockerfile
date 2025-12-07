FROM docker.io/eclipse-temurin:8-jre-noble

COPY entrypoint.sh /usr/local/bin/entrypoint.sh

RUN apt-get update && \
    apt-get install -y python3.12 python3-pip python3.12-venv curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    curl -LsSf https://github.com/astral-sh/uv/releases/download/0.5.11/uv-x86_64-unknown-linux-gnu.tar.gz | tar -xzf - -C /usr/local/bin --strip-components=1 uv-x86_64-unknown-linux-gnu/uv && \
    chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/uv

WORKDIR /app

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]