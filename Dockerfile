FROM python:3.10-slim as reqs
COPY ./pyproject.toml ./
COPY ./poetry.lock ./
RUN pip install poetry && \
    poetry export -f requirements.txt -o requirements.txt

FROM python:3.10-slim as base
RUN mkdir /opt/project
WORKDIR /opt/project
COPY --from=reqs ./requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app/
ENV PYTHONPATH "${PYTHONPATH}:/opt/project"

FROM base as uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]

FROM base as gunicorn
CMD ["gunicorn", "--workers", "8", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:80", "app.main:app"]
