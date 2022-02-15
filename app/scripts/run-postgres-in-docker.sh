#!/bin/bash
export DB_USERNAME=postgres
export DB_PASSWORD=postgres
export DB_HOST=localhost
export DB_PORT=5432
export DB_DATABASE_NAME=postgres

run_migrations () {
    for i in 1 2 3 4 5; do
        echo "Migration attempt $i"
        if poetry run python app/migrations/run.py ; then
            echo "Done with migrations"
            return
        else
            echo "Migrations failed"
            sleep 5
        fi
    done
    # one last time to print error
    poetry run app/migrations/run.py
}

# run_migrations &
docker run --rm --name postgres -it -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres ; killall
