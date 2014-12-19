from flask import Flask, request, render_template, Response
from urlparse import urlparse
import scraper
import json
import time
import model
import os

app = Flask(__name__)
ADMIN_KEY = os.environ.get('ADMIN_KEY', 'LOCAL')

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

class JSONResponse(Response):

    def __init__(self, response):
        Response.__init__(self)
        self.response = response
        self.mimetype = "application/json"


@app.route("/scraper_api", methods=['GET', 'POST'])
def scraper_api():
    """method to handle the scraping of new posts entered from the browser or other sources"""
    url = request.values.get('url')

    return json.dumps(new_post_controller(url)), 200, {'Content-Type': 'application/json'}

@app.route("/admin")
def admin():
    submission_key = request.args.get('key')
    if submission_key == ADMIN_KEY:    
        tmp ={'redis_conn': model.redis_cache.REDIS_CONN,
              'postgres_conn': model.redis_cache.pgdb.DB_CONN}
        return json.dumps(tmp)
    else:
        return "Fuck Off!"

@app.route("/get_feeds", methods=['GET'])
def get_feeds():
    return json.dumps(model.model.get_all_feeds())


@app.route("/get_posts_by_feed", methods=['GET'])
def get_posts_by_feed():
    feed_id = request.args.get('feed_id')
    return json.dumps(model.model.get_posts_by_feed(feed_id))

@app.route("/get_wall", methods=['GET'])
def get_wall():
    data = json.dumps(model.model.get_wall(),indent=4, separators=(',', ': '))
    return JSONResponse(response = data)


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

@app.route("/set_post", methods=['GET', 'POST'])
def set_post():
    url = request.values.get('url')
    feed_id = request.values.get('feed_id')
    if not feed_id:
        feed_id = "-1"
    if url and feed_id:
        post_data = new_post_controller(url)
        res = model.model.set_post(feed_id, post_data)
        if res:
            out = res
    return json.dumps(out) if out else "Error"

@app.route("/flush_cache", methods=['GET', 'POST'])
def flush_cache():
    submission_key = request.args.get('key')
    if submission_key == ADMIN_KEY:
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