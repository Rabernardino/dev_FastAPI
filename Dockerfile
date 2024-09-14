FROM python:3.12-slim
ENV POETRY_VIRTUALENVS_CREATE=false

RUN apt-get update && apt-get install -y gcc python3-dev libffi-dev libpq-dev

WORKDIR app/
COPY . .

RUN chmod +x ./entrypoint.sh
RUN pip install poetry
RUN poetry config installer.max-workers 10
RUN poetry install 

EXPOSE 8000
CMD poetry run uvicorn --host 0.0.0.0 fast_zero.app:app