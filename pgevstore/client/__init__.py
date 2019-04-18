import json
import uuid

import psycopg2


class Client:
    def __init__(self, dns):
        self.conn = psycopg2.connect(dns)

    def __del__(self):
        self.conn.close()

    def add_event(self, source, ev_type, description, data, tags, ev_time=None):
        if not source:
            raise Exception('The "source" value should not be empty')

        if not ev_type:
            raise Exception('The "ev_type" value should not be empty')

        key = uuid.uuid4()

        with self.conn.cursor() as cur:
            cur.execute("""
            INSERT INTO events(key, source, ev_type, description, data, tags, ev_time)
            SELECT %(key)s
                 , %(source)s
                 , %(ev_type)s
                 , %(description)s
                 , %(data)s
                 , %(tags)s
                 , CASE WHEN %(ev_time)s IS NOT NULL THEN %(ev_time)s ELSE now() END
            """, {
                "key": key,
                "source": source,
                "ev_type": ev_type,
                "description": description,
                "data": json.dumps(data),
                "tags": tags,
                "ev_time": ev_time,
            })

        self.conn.commit()
