Connexion Sqlalchemy Utils Example
----------------------------------

By cloning the repo:
    
.. code-block:: bash

    git clone https://github.com/m-housh/connexion_sql_utils.git

    cd ./connexion_sql_utils

    docker-compose up

Without cloning the repo:

.. code-block:: bash

    docker pull mhoush/connexion_sql_utils
    docker pull postgres/alpine

    docker run -d --name some_postgres \
        -e POSTGRES_PASSWORD=postgres \
        postgres:alpine

    docker run --rm -it --link some_postgres:postgres \
        -e DB_HOST=postgres \
        -e DB_PASSWORD=postgres \
        -p "8080:8080" \
        mhoush/connexion_sql_utils

Check out the example api at ``http://localhost:8080/ui``


