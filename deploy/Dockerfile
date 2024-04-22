FROM python:3.11
ENV PYTHONBUFFERED 1
ENV PORT 80

WORKDIR /app

COPY poetry.lock .
COPY pyproject.toml .

RUN pip install poetry && poetry config virtualenvs.create false
RUN poetry install

COPY . .
EXPOSE $PORT

CMD ["python", "manage.py", "runserver", "0.0.0.0:$PORT"]