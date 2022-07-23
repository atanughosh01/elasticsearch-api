FROM python:alpine3.9
COPY . /app
WORKDIR /app
RUN chmod -R 777 .
RUN python -m venv venv
RUN . venv/bin/activate
RUN apk update && apk add gcc && apk add musl-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["/bin/sh", "-c", "exec flask run --host=0.0.0.0 --port=5000"]