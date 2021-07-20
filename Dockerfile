FROM python:3.8

RUN pip install pipenv
COPY Pipfile /app/Pipfile
COPY Pipfile.lock /app/Pipfile.lock
WORKDIR /app
RUN pipenv sync
COPY app /app
EXPOSE 8080
ENTRYPOINT [ "pipenv", "run", "gunicorn", "-b", ":8080", "app.wsgi" ]
