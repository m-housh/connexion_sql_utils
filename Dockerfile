FROM mhoush/psycopg2

ADD . /app

RUN pip install --upgrade /app 

WORKDIR /app

CMD ["/usr/bin/make", "run-example"]
