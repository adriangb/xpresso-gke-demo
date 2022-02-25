FROM python:3.10-slim as base
RUN mkdir /opt/project
WORKDIR /opt/project
ENV PYTHONPATH "${PYTHONPATH}:/opt/project"
COPY ./requirements.txt .
RUN pip install --no-cache-dir -U pip wheel && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf requirements.txt
COPY ./app ./app/
CMD ["python", "app/main.py"]
