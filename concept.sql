BEGIN;

CREATE TABLE events (
    key             UUID,  -- event key
    parent_key      UUID,  -- parent key
    topic           TEXT,  -- event's topic
    source          TEXT,  -- identification of external source of the event
    description     TEXT,  -- event's description
    data            JSONB,  -- related data in json format
    ev_time         timestamp,  -- event's generation time
    created_at      timestamp  --  timestamp in which the event was recorded to the database
) PARTITION BY RANGE (created_at);

-- hourly partition
CREATE TABLE events_20190201_23
    (LIKE events INCLUDING DEFAULTS INCLUDING CONSTRAINTS)
    PARTITION BY HASH (topic, source);

-- hash partitions
CREATE TABLE events_20190201_23_0
    (LIKE events_20190201_23 INCLUDING DEFAULTS INCLUDING CONSTRAINTS);
ALTER TABLE events_20190201_23 ATTACH PARTITION events_20190201_23_0
    FOR VALUES WITH (MODULUS 2, REMAINDER 0);

CREATE TABLE events_20190201_23_1
    (LIKE events_20190201_23 INCLUDING DEFAULTS INCLUDING CONSTRAINTS);
ALTER TABLE events_20190201_23 ATTACH PARTITION events_20190201_23_1
    FOR VALUES WITH (MODULUS 2, REMAINDER 1);

-- attach 1th partition level to events table
ALTER TABLE events ATTACH PARTITION events_20190201_23
    FOR VALUES FROM ('2019-02-01 23:00:00') TO ('2019-02-02 00:00:00');

END;
