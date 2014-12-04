from urlparse import urlparse
import redis
import os

#url = urlparse.urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost'))
redis_url = urlparse("redis://redistogo:f5805ed46d02698376e37d9a84c1cd4c@dab.redistogo.com:9506/")
redis = redis.Redis(host=redis_url.hostname, port=redis_url.port, db=0, password=redis_url.password)


def get_top10_posts(feed):
    pass
