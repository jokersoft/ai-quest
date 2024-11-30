FROM python:3.13

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt
COPY app/ /app
WORKDIR /app

RUN pip install uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EXPOSE 8000
