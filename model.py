from urlparse import urlparse
import redis
import time
import os




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


class FMFRedisHandler(redis.StrictRedis):

    def __init__(self, host, port, password, db=0):
        redis.StrictRedis.__init__(self, host=host, port=port, password=password, db=db)

    def _run_checks(self):
        """method to confirming essential keys are available"""
        pass

    def set_feed(self, feed_name):
        feed_mapping = {}
        create_time = time.time()
        feed_id_suffix = str(self.incr("feed_id_suffix", 1))
        feed_id = str(int(create_time//100))+"-"+feed_id_suffix
        feed_mapping['create_time'] = create_time
        feed_mapping['feed_name'] = feed_name
        feed_mapping['id'] = feed_id

        resp = self.hmset('feed:'+feed_id, feed_mapping)
        if resp:
            return feed_id
        else:
            return False

    def set_post(self, feed_id, post_dict):

        create_time = time.time()
        post_id_suffix = str(self.incr("post_id_suffix", 1))
        post_id = str(int(create_time//100))+"-"+post_id_suffix
        post_dict['id'] = post_id
        post_dict['create_time'] = create_time
        post_dict['feed_id'] = feed_id

        resp = self.hmset('post:'+post_id, post_dict)
        self.zadd('recent_posts:'+feed_id, create_time, post_id)

        return resp

    def get_recent_posts(self, feed_id, start_idx = 0, end_idx = -1):
        resp = self.zrevrange('recent_posts:'+str(feed_id), start_idx, end_idx)
        return [self.hgetall('post:'+str(post)) for post in resp]



if __name__ == "__main__":
    redis_url = urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost:6379'))
    rs = FMFRedisHandler(host=redis_url.hostname, port=redis_url.port, db=0, password=redis_url.password)

    rs.flushdb()
    def test_add_posts():
        feed = 'test-feed'
        post_ids = ['test-post%s' % n for n in range(5)]
        #random.shuffle(self.post_ids)

        for post in post_ids:
            #create_time = time.time()
            post_dict = {post : 'this is a sample post'}
            rs.set_post(feed, post_dict)

    test_add_posts()

    print rs.get_recent_posts('test-feed')






