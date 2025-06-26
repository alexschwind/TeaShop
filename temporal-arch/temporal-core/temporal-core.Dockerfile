# Dockerfile.base
FROM ubuntu

# Set workdir just as a placeholder
WORKDIR /app

COPY ./temporal /app/temporal

RUN chmod +x ./temporal

# Entrypoint will be overridden by each service container
CMD ["./temporal", "server", "start-dev", "--db-filename", "your_temporal.db", "--ui-ip", "0.0.0.0"]