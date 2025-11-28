FROM python:3.13-slim
LABEL authors="Marcos Alvarado"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    APP_HOME=/develop

# Set the working directory
WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && \
    apt-get install -y gcc libmagic1 libmagic-dev && \
    rm -rf /var/lib/apt/lists/*

RUN touch .env

# Update pip
RUN python -m pip install --upgrade pip
RUN pip install uv

COPY pyproject.toml .

RUN uv sync

COPY . .

EXPOSE 8000

RUN chmod +x docker-entrypoint.sh
RUN mv docker-entrypoint.sh /bin

ENTRYPOINT ["docker-entrypoint.sh"]
