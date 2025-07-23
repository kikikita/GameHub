# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy the dependency files
COPY poetry.lock pyproject.toml ./

# Install project dependencies
RUN poetry install --no-root
COPY ./alembic ./alembic
COPY alembic.ini .

# Copy .env file
COPY ./.env ./.env

# Copy the rest of the application code
COPY ./src ./src

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["bash", "-c", "alembic upgrade head && poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000"]
