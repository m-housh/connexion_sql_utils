FROM mhoush/psycopg2

ADD . /app

RUN pip install --upgrade \
    /app \
    -r /app/requirements_dev.txt

WORKDIR /app

VOLUME /app

