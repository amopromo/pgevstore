CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS events (
        key             UUID,
        source          TEXT,
        ev_type         TEXT,
        description     TEXT,
        data            JSONB,
        ev_time         timestamp,
        tags            integer[]
    ) PARTITION BY RANGE (ev_time);
"""

SELECT_LATEST_PARTITION = """
    SELECT tablename
    FROM pg_catalog.pg_tables
    WHERE tablename ~ 'events_\d+_\d+'
    ORDER BY tablename DESC
"""

SELECT_ALL_PARTITION = """
    SELECT tablename
    FROM pg_catalog.pg_tables
    WHERE tablename ~ 'events_\d+_\d+'
    ORDER BY tablename
"""

CREATE_PARTITION = """
    CREATE TABLE IF NOT EXISTS {table_name} PARTITION OF events FOR VALUES FROM ('{dt}') TO ('{dt_p_one}');
"""

DROP_TABLE = """
    DROP TABLE {table_name}
"""

DETACH_TABLE = """
    ALTER TABLE IF EXISTS events DETACH PARTITION {table_name}
"""
