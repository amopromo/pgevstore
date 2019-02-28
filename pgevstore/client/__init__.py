import psycopg2
import uuid


class Client:
    def __init__(self, dns):
        self.conn = psycopg2.connect(dns)

    def __del__(self):
        self.conn.close()

    def add_event(self, source, ev_type, description, data, tags, ev_time):
        if not source:
            raise Exception('The "source" value should not be empty')

        if not ev_type:
            raise Exception('The "ev_type" value should not be empty')

        key = uuid.uuid4()

        with self.conn() as cur:
            cur.execute("""
            INSERT INTO events(key, source, ev_type, description, data, tags, ev_time)
            SELECT {key}
                 , {source}
                 , {ev_type}
                 , {description}
                 , {data}
                 , {tags}
                 , CASE WHEN {ev_time} IS NOT NULL THEN {ev_time} ELSE now() END
            """, {
                "key": key,
                "source": source,
                "ev_type": ev_type,
                "description": description,
                "data": data,
                "tags": tags,
                "ev_time": ev_time,
            })
