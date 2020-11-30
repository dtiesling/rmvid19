FROM python:3.8

RUN pip install pipenv

COPY app /app
COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock

WORKDIR /app

RUN pipenv sync

ENTRYPOINT [ "pipenv", "run", "gunicorn", "-b", ":8000", "app.wsgi" ]
