FROM public.ecr.aws/lambda/python:3.13

# Set working directory to Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements file
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY main.py .

# Set the CMD to the handler
CMD [ "main.handler" ]
