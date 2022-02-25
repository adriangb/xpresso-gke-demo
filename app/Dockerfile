FROM python:3.10-slim as base
RUN mkdir /opt/project
WORKDIR /opt/project
ENV PYTHONPATH "${PYTHONPATH}:/opt/project"

FROM base as migrations
COPY ./requirements-migrations.txt .
RUN pip install --no-cache-dir -U pip wheel && \
    pip install --no-cache-dir -r requirements-migrations.txt && \
    rm -rf requirements-migrations.txt
COPY ./app/ ./app/
CMD ["python", "app/db/migrations/run.py"]

FROM base as api
COPY ./requirements.txt .
RUN pip install --no-cache-dir -U pip wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf requirements.txt
COPY ./app ./app/
CMD ["python", "app/main.py"]
