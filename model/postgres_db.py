from sqlalchemy import create_engine, exc, sql
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Float
import os


DB_CONN = os.environ.get('HEROKU_POSTGRESQL_BLACK_URL', "postgresql://mwoods@localhost/fmfapp")

PG_ENGINE = create_engine(DB_CONN)

metadata = MetaData()

feeds = Table('feeds', metadata,
              Column('feed_id', String, primary_key=True),
              Column('create_time', Float),
              Column('feed_name', String),
              Column('attribute1', String),
              Column('attribute2', String)
)

posts = Table('posts', metadata,
              Column('post_id', String, primary_key=True),
              Column('create_time', Float),
              Column('feed_id', None, ForeignKey('feeds.feed_id')),
              Column('title', String),
              Column('url', String),
              Column('description', String),
              Column('favicon_url', String),
              Column('attribute1', String),
              Column('attribute2', String)
)

keywords = Table('keywords', metadata,
                 Column('id', Integer, primary_key=True),
                 Column('keyword', String, nullable=False),
                 Column('post_id', None, ForeignKey('posts.post_id')),
                 Column('feed_id', None, ForeignKey('feeds.feed_id')),
                 Column('attribute1', String),
                 Column('attribute2', String)
)


def row_to_dict(row):
    return dict(zip(row.keys(), row.values()))

def set_feed(eng, feed_id, feed_name, create_time):
    ins = feeds.insert().values(feed_id=feed_id, feed_name=feed_name, create_time=create_time)
    result = eng.execute(ins)
    return result

def set_post(eng, *args):
    ins = posts.insert()
    result = eng.execute(ins, args)
    return result


def get_feeds(eng):
    s = sql.select([feeds]).\
        order_by(feeds.c.feed_name)
    result = eng.execute(s)
    output = []
    for row in result:
        feed_mapping = row_to_dict(row)
        output.append(feed_mapping)
    result.close()
    return output


def get_n_most_recent_posts_by_feed(eng, feed_id, start_time = 0.0, n = 25):
    """returns a tuple of (post_id, create_time) that are associated with th given feed_id"""
    s = sql.select([posts.c.post_id, posts.c.create_time]).\
                            where(posts.c.create_time > start_time).\
                            where(posts.c.feed_id == feed_id).\
                            order_by(-posts.c.create_time).\
                            limit(n)

    result = eng.execute(s)
    return [row_to_dict(row) for row in result.fetchall()]

def get_wall(eng, n=25):
    s = sql.select([posts]).order_by(-posts.c.create_time).\
                            limit(n)

    result = eng.execute(s)
    output =[]
    for row in result:
        post_mapping = row_to_dict(row)
        output.append(post_mapping)
    result.close()
    return output

def get_post(eng, post_id):
    s = sql.select([posts]).where(posts.c.post_id == post_id)
    result = eng.execute(s)
    return row_to_dict(result.fetchone())

def get_feed_by_id(eng, feed_id):
    s = sql.select([feeds]).where(feeds.c.feed_id == feed_id)
    result = eng.execute(s)
    return row_to_dict(result.fetchone())

def delete_post(eng, post_id):
    result = eng.execute(posts.delete().where(posts.c.post_id == post_id))
    return bool(result.rowcount)


if __name__ == "__main__":
    metadata.create_all(PG_ENGINE)
    import time

    SAMPLE_POST = {"create_time": 0.0,
                    "post_id": None,
                    "feed_id": None,
                    "url" : "http://www.nytimes.com",
                    "description" : "Fake Post for nytimes Fake Post for nytimes Fake Post for nytimes",
                    "title": "nytimes site",
                    "host_name": "www.nytimes.com",
                    "favicon_url": "http://static01.nyt.com/favicon.ico"
                    }
    def drop_and_replace_database():
        metadata.drop_all(PG_ENGINE)
        metadata.create_all(PG_ENGINE)

    def sample():
        try:
            GLOBAL_TITLE_PREFIX = SAMPLE_POST['title']
            for i in range(10):
                feed_id = 'test_id%s'%(i)
                create_time = time.time()
                tmp = set_feed(PG_ENGINE, feed_id, 'Feed %s'%i, create_time)
                for j in range(5):
                    SAMPLE_POST['create_time'] = time.time()
                    SAMPLE_POST['post_id'] = 'test_post-%s-%s'%(i,j)
                    SAMPLE_POST['feed_id'] = feed_id
                    SAMPLE_POST['title'] = GLOBAL_TITLE_PREFIX+"-"+feed_id
                    tmp = set_post(PG_ENGINE, SAMPLE_POST)
        except exc.IntegrityError:
            print "Key Already Exists"
        print get_n_most_recent_feeds(PG_ENGINE)