FROM python:3.9

WORKDIR /app

RUN pip install poetry

COPY poetry.lock pyproject.toml ./

RUN poetry install

ADD . .

ENTRYPOINT ["poetry", "run", "uvicorn", "--host", "0.0.0.0", "webhook_receiver:app"]