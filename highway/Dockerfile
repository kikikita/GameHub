# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy the dependency files
COPY highway/poetry.lock highway/pyproject.toml ./

# Install project dependencies
RUN poetry install --no-root

COPY highway/alembic ./alembic
COPY highway/alembic.ini .
COPY highway/src ./src

# Copy .env file from the root
COPY .env .env

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["bash", "-c", "poetry run alembic upgrade head && poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000"]
