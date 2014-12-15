__author__ = 'mwoods'



"""
DB Architecture uses Redis to serve requests and PostgreSQL for persistence.

Notes on SCHEMA Design

since keys like user id are sensitive to uniqueness we use timestamps in combination with increment to ensure
uniqueness between sessions

the "tables":

counters:
    NOTE: In order to ensure uniqueness in the event of a crash the first portion
    feed_id_suffix: int
    post_id_suffix: int


table: feed (hash)
    key: feed:feed_id
    attributes:
        id
        create_time
        feed_name


table: post (hash)
    key: post:post_id
    attributes:
        id
        feed_id
        create_time
        title
        url
        description
        favicon_url


table: recent-posts (sorted set)
    key: recent-posts:feed_id
    score: post_create_time
    value: post_id

"""


import redis_cache
import urlparse
import os

redis_url = redis_cache.redis_url
model = redis_cache.FMFRedisHandler(host=redis_url.hostname, port=redis_url.port, db=0, password=redis_url.password)
