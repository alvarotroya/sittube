# Dockerfile
FROM python:3.11-slim-buster

WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Install Poetry
RUN pip install poetry

# Copy only requirements to cache them in docker layer
COPY pyproject.toml poetry.lock ./

# Project initialization:
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi

# Copying the rest of the project
COPY . .

# Running the application
EXPOSE 8000
WORKDIR /app/sittube
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--workers", "1"]