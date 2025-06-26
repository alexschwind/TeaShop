# Dockerfile.base
FROM python:3.11-slim

# Install Flask globally
RUN pip install flask requests

# Set workdir just as a placeholder
WORKDIR /app

# Entrypoint will be overridden by each service container
CMD ["flask", "--app", "app.py", "run", "--host=0.0.0.0", "--debug"]