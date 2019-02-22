# pgevstore

## This is a work in progress

- The goal of this project is to serve others system storing and querying events and aggregations of this events
- The main idea is to leverage postgres partitioning abilities

## Comands
### `up`
Create events table and partitions keeping only the amount of range partitions specified by `PGEVSTORE_TABLES_AHEAD`

### `trim`
Creates a dump for and delete range partitions keeping only the amount of range partitions specified by `PGEVSTORE_TABLES_BEHIND`.


## Enviroment Variables
- PGEVSTORE_TABLES_AHEAD
    - How many tables the script with generate ahead
- PGEVSTORE_TABLES_BEHIND
    - How many tables the script with leaf behind before triming
- PGEVSTORE_TABLES_INTERVAL
    - How long is the range of each table partition in hours
- PGEVSTORE_HASH_MODULUS
    - How long is the range of each table partition in hours
- PGEVSTORE_DUMP_PATH
    - Where to put dump files when they get cold
- PGEVSTORE_DNS
    - Postgres string connection
- PGEVSTORE_DEFAULT_BEGIN
    - Date and time for the first partition when first setting up the system
