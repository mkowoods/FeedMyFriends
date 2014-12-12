from sqlalchemy import create_engine, exc, sql
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Float


DB_CONN = "postgresql://mwoods@localhost/fmfapp"

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


def set_feed(eng, feed_id, feed_name, create_time):
    ins = feeds.insert().values(feed_id=feed_id, feed_name=feed_name, create_time=create_time)
    result = eng.execute(ins)
    return result

def set_post(eng, *args):
    ins = posts.insert()
    result = eng.execute(ins, args)
    return result

def get_n_most_recent_feeds(eng, start_time = 0.0, n=10):
    s = sql.select([feeds]).where(feeds.c.create_time > start_time).order_by(-feeds.c.create_time).limit(n)
    result = eng.execute(s)
    output =[]
    for row in result:
        feed_mapping = {'create_time': row['create_time'],
                        'feed_name': row['feed_name'],
                        'feed_id': row['feed_id']}
        output.append(feed_mapping)
    result.close()
    return output


def get_n_most_recent_posts(eng, feed_id, start_time = 0.0, n = 25):
    s = sql.select([posts]).where(posts.c.create_time > start_time).\
                            where(posts.c.feed_id == feed_id).\
                            order_by(-posts.c.create_time).\
                            limit(n)

    result = eng.execute(s)
    output =[]
    for row in result:
        post_mapping = {'create_time': row['create_time'],
                        'post_id': row['post_id'],
                        'feed_id': row['feed_id'],
                        'title': row['title'],
                        'url': row['url'],
                        'description': row['description'],
                        'favicon_url': row['favicon_url']
                        }
        output.append(post_mapping)
    result.close()
    return output





if __name__ == "__main__":
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