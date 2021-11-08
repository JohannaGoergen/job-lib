FROM python:3.10-buster

ARG POETRY_VERSION
ARG SQLITE_MOUNT_BUCKET

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && apt-get install -y tini sqlite3 libsqlite3-dev curl gnupg2

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENV APP_HOME /app
ENV DEBIAN_FRONTEND noninteractive


WORKDIR $APP_HOME

# GCSFuse allows us to mount GCS as a volume
#RUN echo "deb http://packages.cloud.google.com/apt gcsfuse-buster main" | tee /etc/apt/sources.list.d/gcsfuse.list
#RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
#
#RUN apt-get update && apt-get install -y gcsfuse
RUN set -e; \
    apt-get update -y && apt-get install -y \
    lsb-release; \
    echo "deb http://packages.cloud.google.com/apt gcsfuse-buster main" | \
    tee /etc/apt/sources.list.d/gcsfuse.list; \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | \
    apt-key add -; \
    apt-get update; \
    apt-get install -y gcsfuse \
    && apt-get clean

RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt
#
## Will mount the gcsfuse filesystem here
#VOLUME ["db"]
#RUN mkdir db
#RUN chmod o+rwx db

COPY . .

RUN python manage.py collectstatic --noinput
#RUN chmod +x /app/gcsfuse_run.sh

# Use tini to manage zombie processes and signal forwarding
# https://github.com/krallin/tini
#ENTRYPOINT ["/usr/bin/tini", "--"]

# Pass the startup script as arguments to Tini
#CMD ["/app/gcsfuse_run.sh"]
CMD exec gunicorn -c gunicorn.conf.py --bind 0.0.0.0:$PORT app.wsgi:application
