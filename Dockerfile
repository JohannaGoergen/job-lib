FROM python:3.10-buster

ARG POETRY_VERSION

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV APP_HOME /app

WORKDIR $APP_HOME

RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD exec gunicorn -c gunicorn.conf.py --bind 0.0.0.0:$PORT app.wsgi:application
