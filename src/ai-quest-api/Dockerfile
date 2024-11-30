FROM public.ecr.aws/lambda/python:3.13

COPY requirements.txt  .
RUN  pip3 install -r requirements.txt
COPY app/ ./app/

CMD [ "app.lambda_handler.handler" ]
