FROM python:3.13

# Install Poetry correctly
RUN pip install poetry

# Set Poetry to not create a virtual environment (important for Docker)
RUN poetry config virtualenvs.create false

# Copy only pyproject.toml and poetry.lock first
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-root

# Copy the rest of the application
COPY . .

# Set PYTHONPATH to include the app directory
ENV PYTHONPATH=/usr/src/app

# Install and run web server
RUN pip install uvicorn
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
