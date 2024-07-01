FROM python:3.12

WORKDIR /app

RUN apt update && apt install -y python-poetry

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

CMD ["poetry", "run", "python", "-m", "equalizator"]