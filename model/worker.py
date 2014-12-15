

import postgres_db


"""implemented to allow for communication between the Cache Layer and the DB layer"""


def get_n_recent_posts(feed_id, start_time, n):
    return postgres_db.get_n_most_recent_posts(postgres_db.PG_ENGINE, feed_id, start_time=start_time, n=n)