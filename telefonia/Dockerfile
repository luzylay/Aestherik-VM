FROM ubuntu:22.04
RUN apt-get update && apt-get install -y \
    asterisk \
    asterisk-core-sounds-en-wav \
    asterisk-core-sounds-es-wav \
    curl \
    && rm -rf /var/lib/apt/lists/*
CMD ["asterisk", "-f"]
