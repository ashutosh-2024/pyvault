"""Databases: one module per topic, in the order they appear on the site.
Topics reuse the Deep Dive block schema (content/deepdive/_blocks.py) and add
`summary` (one line, shown on the topic's card)."""
from . import (btree_indexes, transactions, locking, query_execution, internals,
               redis, distributed, sharding, durability,
               recovery, normalization, sql_fundamentals,
               columnar, caching)

TOPICS = [
    btree_indexes.TOPIC,
    transactions.TOPIC,
    locking.TOPIC,
    query_execution.TOPIC,
    internals.TOPIC,
    redis.TOPIC,
    distributed.TOPIC,
    sharding.TOPIC,
    durability.TOPIC,
    recovery.TOPIC,
    normalization.TOPIC,
    sql_fundamentals.TOPIC,
    columnar.TOPIC,
    caching.TOPIC,
]
