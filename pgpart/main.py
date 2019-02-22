#!/usr/bin/env python3
import sys
import os
import subprocess
from os.path import join
from datetime import datetime, timedelta, time

import psycopg2

import sql


# How many tables the script with generate ahead
TABLES_AHEAD = int(os.getenv('PGEVSTORE_TABLES_AHEAD') or 8)

# How many tables the script with leaf behind before triming
TABLES_BEHIND = int(os.getenv('PGEVSTORE_TABLES_BEHIND') or 4*60)

# How long is the range of each table partition in hours
TABLES_INTERVAL = int(os.getenv('PGEVSTORE_TABLES_INTERVAL') or 6)

# Where to put dump files when they get cold
DUMP_PATH = os.getenv('PGEVSTORE_DUMP_PATH') or './bkp'

# Postgres string connection
DNS = os.getenv('PGEVSTORE_DNS')

# Date and time for the first partition when first setting up the system
DEFAULT_BEGIN = os.getenv('PGEVSTORE_DEFAULT_BEGIN')


def main():
    if len(sys.argv) < 2:
        print("command is missing")
        return

    if not DNS:
        print("the string connection is missing, please set the enviroment variable 'PGEVSTORE_DNS'")
        return

    command = sys.argv[1]
    if command == "up":

        if TABLES_INTERVAL not in [1, 2, 3, 4, 6, 8, 12, 24]:
            print("invalid value for 'PGEVSTORE_TABLES_INTERVAL', the allowed values are: 1, 2, 3, 4, 6, 8, 12 and 24")
            return

        pgpart_up()
    elif command == "trim":
        pgpart_trim()
    else:
        print("invalid command")


def pgpart_up():
    with psycopg2.connect(DNS) as conn:
        with conn.cursor() as cur:
            create_table(cur)
            create_partitions(cur)


def pgpart_trim():
    with psycopg2.connect(DNS) as conn:
        with conn.cursor() as cur:
            cur.execute(sql.SELECT_ALL_PARTITION)
            rows = cur.fetchall()

            params = cur.connection.get_dsn_parameters()

    for i, (partition, ) in enumerate(rows):
        print("{}/{}: {}".format(i+1, len(rows), partition))
        dt = datetime.strptime(partition, "events_%Y%m%d_%H")

        if dt + timedelta(hours=TABLES_INTERVAL) * TABLES_BEHIND > datetime.now():
            print('skip')
            continue

        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                try:
                    detach_table(cur, partition)
                except Exception:
                    pass

        generate_backup(params, partition, DUMP_PATH)

        with psycopg2.connect(DNS) as conn:
            with conn.cursor() as cur:
                drop_table(cur, partition)


def create_table(cur):
    cur.execute(sql.CREATE_TABLE)


def create_partitions(cur):
    cur.execute(sql.SELECT_LATEST_PARTITION)
    row = cur.fetchone()

    try:
        dt = datetime.strptime(row[0], "events_%Y%m%d_%H")
    except (ValueError, TypeError):
        dt = None

    now = datetime.now()
    now_hour = int(now.hour / TABLES_INTERVAL) * TABLES_INTERVAL
    now_dt = datetime.combine(now.date(), time.min).replace(hour=now_hour)

    if not dt:
        if DEFAULT_BEGIN:
            dt = datetime.strptime(DEFAULT_BEGIN, "%Y-%m-%d %H")
        else:
            dt = now_dt

    table_interval = timedelta(hours=TABLES_INTERVAL)

    end_dt = now_dt + table_interval * TABLES_AHEAD

    while dt <= end_dt:
        print('{}: creating partition for {}'.format(datetime.now(), dt))

        sqlCommand = sql.CREATE_PARTITION.format(
            table_name='events_' + dt.strftime("%Y%m%d_%H"),
            dt=dt.isoformat(),
            dt_p_one=(dt + table_interval).isoformat(),
        )

        cur.execute(sqlCommand)

        dt += table_interval


def generate_backup(params, table, bkp_path):
    path = join(bkp_path, table + '.sql.gz')
    cmd = 'pg_dump -U {user} -h {host} -p {port} -t {table} {dbname} | gzip > {path}'
    cmd = cmd.format(
        user=params.get('user'),
        host=params.get('host') or 'localhost',
        port=params.get('port'),
        table=table,
        dbname=params.get('dbname'),
        path=path,
    )

    subprocess.call(['bash', '-c', cmd])


def drop_table(cur, table):
    cur.execute(sql.DROP_TABLE.format(table_name=table))


def detach_table(cur, table):
    cur.execute(sql.DETACH_TABLE.format(table_name=table))


if __name__ == "__main__":
    main()
