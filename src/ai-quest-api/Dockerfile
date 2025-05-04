FROM public.ecr.aws/lambda/python:3.12

# Install Poetry
RUN pip install poetry

# Set Poetry to not create a virtual environment (important for Docker)
RUN poetry config virtualenvs.create false

# Copy only pyproject.toml and poetry.lock first
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-interaction --no-root

# Copy the rest of the application
COPY app/ ./app/

CMD [ "app.lambda_handler.handler" ]
