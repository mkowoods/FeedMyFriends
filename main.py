from flask import Flask, request, render_template
from urlparse import urlparse
import scraper
import json
import time
import model
import os

app = Flask(__name__)


#Controller
def new_post_controller(new_url):

    post = {}

    try:
        post = scraper.ScrapeSite(new_url).get_site_dict()
        post['timestamp'] = time.time()
        post['status'] = "OK"
        #TODO: start worker to write results to database, should also add date parameter to record
    except:
        #TODO: need to predefine certain Exceptions or fail for "unknown"
        post['status'] = "Exception"

    return post



#View

@app.route("/scraper_api", methods=['GET', 'POST'])
def scraper_api():
    """method to handle the scraping of new posts entered from the browser or other sources"""
    url = request.args.get('url')
    return json.dumps(new_post_controller(url))

@app.route("/admin")
def admin():
    tmp ={'redis_conn': model.redis_cache.REDIS_CONN,
          'postgres_conn': model.redis_cache.pgdb.DB_CONN}
    return json.dumps(tmp)

@app.route("/get_feeds", methods=['GET'])
def get_feeds():
    return json.dumps(model.model.get_all_feeds())


@app.route("/get_posts_by_feed", methods=['GET'])
def get_posts_by_feed():
    feed_id = request.args.get('feed_id')
    return json.dumps(model.model.get_posts_by_feed(feed_id))

@app.route("/get_wall", methods=['GET'])
def get_wall():
    return json.dumps(model.model.get_wall())


@app.route("/set_feed", methods = ['GET', 'POST'])
def set_feed():
    feed_name = request.values.get('feed_name')
    option = request.values.get('option')
    out = "Error"
    if feed_name:
        res = model.model.set_feed(feed_name)
        if option == "dev":
            res = "Testing Received %s"%feed_name
        if res:
            out = json.dumps(res)
    return out

@app.route("/set_post", methods = ['GET', 'POST'])
def set_post():
    url = request.args.get('url')
    feed_id = request.args.get('feed_id')
    out = "Error"
    if url and feed_id:
        post_data = new_post_controller(url)
        res = model.model.set_post(feed_id, post_data)
        if res:
            out = res
    return json.dumps(out)

@app.route("/flush_cache", methods = ['GET', 'POST'])
def flush_cache():
    submission_key = request.args.get('key')
    admin_key = os.environ.get('ADMIN_KEY', 'LOCAL')
    if submission_key == admin_key:
        res = model.model.flushdb()
        return json.dumps(res)
    else:
        return 'Failed'

@app.route("/")
def index():
    feeds = model.model.get_all_feeds()
    wall = model.model.get_wall()
    current_time = time.time()
    return render_template("index.html", feeds = feeds, wall = wall, current_time = current_time)


if __name__ == "__main__":
    print 'Redis DB Connection: %s'%model.redis_cache.REDIS_CONN
    print 'Postgres DB Connection: %s'%model.redis_cache.pgdb.DB_CONN
    app.run(debug=True)