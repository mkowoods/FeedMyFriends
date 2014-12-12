from urlparse import urlparse
import redis
import time
import os
import pgdb



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
        feed_mapping['feed_id'] = feed_id

        resp = self.hmset('feed:'+feed_id, feed_mapping)
        if resp:
            return feed_id

    def set_post(self, feed_id, post_dict):

        create_time = time.time()
        post_id_suffix = str(self.incr("post_id_suffix", 1))
        post_id = str(int(create_time//100))+"-"+post_id_suffix
        post_dict['post_id'] = post_id
        post_dict['create_time'] = create_time
        post_dict['feed_id'] = feed_id

        resp = self.hmset('post:'+post_id, post_dict)
        self.zadd('recent_posts:'+feed_id, create_time, post_id)

        return resp

    def get_wall(self):
        feeds = self.get_feeds()
        all_posts = []
        for feed in feeds:
            feed_id = feed['feed_id']
            all_posts.extend(self.get_recent_posts(feed_id))
        return all_posts



    def get_recent_posts(self, feed_id, start_idx=0, end_idx=-1):
        resp = self.zrevrange('recent_posts:'+str(feed_id), start_idx, end_idx)
        if resp:
            return [self.hgetall('post:'+str(post)) for post in resp]
        else:
            posts = pgdb.get_n_most_recent_posts(pgdb.PG_ENGINE, feed_id)
            for post in posts:
                self.hmset('post:'+post['post_id'], post)
                self.zadd('recent_posts:'+post['feed_id'], post['create_time'], post['post_id'])
            return posts

    def get_feeds(self):
        resp = self.keys("feed:*")
        if resp:
            return [self.hgetall(feed_id) for feed_id in resp]
        else:
            #currently defaulted to get all feeds, can switch feeds to get subsets of feeds based on the create
            #date as a cutoff "Top 5 feeds where create_date > last_known create_date"
            feeds = pgdb.get_n_most_recent_feeds(pgdb.PG_ENGINE)
            for feed in feeds:
                self.hmset('feed:'+feed['feed_id'], feed)
            return feeds


if __name__ == "__main__":
    redis_url = urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost:6379'))
    rs = FMFRedisHandler(host=redis_url.hostname, port=redis_url.port, db=0, password=redis_url.password)









