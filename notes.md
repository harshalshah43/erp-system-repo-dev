# after starting docker container for postgres

docker exec -it db_container1 psql -U harshal

container name: db_container1
username: harshal

# select default schema for current session
SET search_path TO ecom;

# This lists all databases in that Postgres instance
docker exec -it db_container1 psql -U harshal -l