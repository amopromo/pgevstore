import json
import uuid

import psycopg2


class Client:
    def __init__(self, dns):
        self.conn = psycopg2.connect(dns)

    def __del__(self):
        self.conn.close()

    def add_event(self, source, description, data, tags, ev_time=None):
        if not source:
            raise Exception('The "source" value should not be empty')

        key = uuid.uuid4()

        with self.conn.cursor() as cur:
            cur.execute("""
            INSERT INTO events(key, source, description, data, tags, ev_time)
            SELECT %(key)s
                 , %(source)s
                 , %(description)s
                 , %(data)s
                 , %(tags)s
                 , CASE WHEN %(ev_time)s IS NOT NULL THEN %(ev_time)s ELSE now() END
            """, {
                "key": key,
                "source": source,
                "description": description,
                "data": json.dumps(data),
                "tags": tags,
                "ev_time": ev_time,
            })

        self.conn.commit()

    def add_batch(self, batch):
        batch_size = len(batch)

        if batch_size == 0:
            return

        args = []

        for row in batch:
            (source, description, data, tags, ev_time, ) = row

            if not source:
                raise Exception('The "source" value should not be empty')

            key = uuid.uuid4()

            args += [key, source, description, json.dumps(data), tags, ev_time]

        args_sql = ','.join(['({})'.format(','.join(['%s'] * 6))] * batch_size)
        sql = """
            INSERT INTO events(key, source, description, data, tags, ev_time)
            VALUES {}
        """.format(args_sql)

        rowcount = 0
        with self.conn.cursor() as cur:
            cur.execute(sql, tuple(args))

            rowcount = cur.rowcount

        self.conn.commit()

        return rowcount
