FROM python:3.8

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY . /app
RUN pip install -r /app/requirements.txt

WORKDIR /app
RUN chmod 755 /app/start.sh
EXPOSE 8000

ENTRYPOINT ["/app/start.sh"]