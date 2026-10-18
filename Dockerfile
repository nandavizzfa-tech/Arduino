FROM python:3.11-slim
RUN apt-get update && apt-get install -y curl ca-certificates && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR=/usr/local/bin sh
RUN arduino-cli core update-index && arduino-cli core install arduino:avr
COPY app.py /app.py
CMD ["python", "/app.py"]
