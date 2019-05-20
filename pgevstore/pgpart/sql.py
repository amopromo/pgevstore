CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS events (
        key             UUID,
        source          TEXT,
        description     TEXT,
        data            JSONB,
        tags            integer[],
        ev_time         timestamp
    ) PARTITION BY RANGE (ev_time);
"""

CREATE_INDEX_SOURCE = """
    CREATE INDEX IF NOT EXISTS events_source_idx ON events (source)
"""

SELECT_LATEST_PARTITION = """
    SELECT tablename
    FROM pg_catalog.pg_tables
    WHERE tablename ~ '^events_\d+$'
    ORDER BY tablename DESC
"""

SELECT_FIRST_LVL_PARTITION = """
    SELECT tablename
    FROM pg_catalog.pg_tables
    WHERE tablename ~ '^events_\d+$'
    ORDER BY tablename
"""

CREATE_RANGE_PARTITION = """
    CREATE TABLE IF NOT EXISTS {range_partition_name}
        (LIKE events INCLUDING DEFAULTS INCLUDING CONSTRAINTS)
        PARTITION BY HASH (source);
"""

CREATE_HASH_PARTITION = """
    CREATE TABLE IF NOT EXISTS {range_partition_name}_{hash_mod_remainder}
        (LIKE {range_partition_name} INCLUDING DEFAULTS INCLUDING CONSTRAINTS);
    ALTER TABLE {range_partition_name} ATTACH PARTITION {range_partition_name}_{hash_mod_remainder}
        FOR VALUES WITH (MODULUS {hash_mod}, REMAINDER {hash_mod_remainder});
"""

ATTACH_RANGE_TABLE = """
    ALTER TABLE events ATTACH PARTITION {range_partition_name}
    FOR VALUES FROM ('{dt}') TO ('{dt_p_one}');
"""

DETACH_TABLE = """
    ALTER TABLE IF EXISTS events DETACH PARTITION {table_name}
"""

DROP_TABLE = """
    DROP TABLE {table_name}
"""
