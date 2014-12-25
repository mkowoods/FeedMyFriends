from sqlalchemy import create_engine, exc, sql
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, Float
import os
import time

DB_CONN = os.environ.get('HEROKU_POSTGRESQL_PURPLE_URL', "postgresql://mwoods@localhost/fmfapp")

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

posts_feeds = Table('posts_feeds', metadata,
                    Column('id', String, primary_key=True),
                    Column('post_id', String),
                    Column('feed_id', String),
                    Column('create_time', Float))

def insert(eng, table, **kwargs):
    ins = table.insert().values(kwargs)
    result = eng.execute(ins)
    return result

def get_all_rows(eng, table):
    s = sql.select([table])
    result = eng.execute(s)
    return result

def row_to_dict(row):
    return dict(zip(row.keys(), row.values()))

def set_feed(eng, feed_id, feed_name, create_time):
    ins = feeds.insert().values(feed_id=feed_id, feed_name=feed_name, create_time=create_time)
    result = eng.execute(ins)
    return result

def set_post(eng, post_id, create_time, feed_id, title, url, description, favicon_url):
    ins = posts.insert().values(post_id = post_id, create_time = create_time,
                                feed_id = feed_id, title=title,
                                url = url, description = description,
                                favicon_url = favicon_url
                                )
    result = eng.execute(ins)
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


def get_n_most_recent_posts_by_feed(eng, feed_id, ub_time = float('inf'), n = 25):
    """returns the first 25 records less than the upper bound time
        can iterate through the list by taking the lowest time of the result and passing back
        into the function"""
    s = sql.select([posts_feeds]).\
                    where(posts_feeds.c.create_time < ub_time).\
                    where(posts_feeds.c.feed_id == feed_id).\
                    order_by(-posts_feeds.c.create_time).\
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

def add_post_to_feed(eng, post_id, feed_id):
    """Takes in a post_id and feed_id and upon completion returns the primary key created
    If there's a conflict in the database it will return an IntegrityError
    (IntegrityError) duplicate key value violates unique constraint "posts_feeds_pkey"
    """
    uid = feed_id+"|"+post_id
    res = insert(eng, posts_feeds, id = uid,
                                    post_id = post_id,
                                    feed_id = feed_id,
                                    create_time = time.time())
    return res.inserted_primary_key



if __name__ == "__main__":
    metadata.create_all(PG_ENGINE)
