from flask import Flask, request, render_template
from urlparse import urlparse
import scraper
import json
import time
import model
import os

app = Flask(__name__)
redis_url = urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost:6379'))
rs = model.FMFRedisHandler(host=redis_url.hostname, port=redis_url.port, db=0, password=redis_url.password)


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

@app.route("/get_feeds", methods=['GET'])
def get_feeds():
    return json.dumps(rs.get_feeds())

@app.route("/get_recent_posts", methods=['GET'])
def get_recent_posts():
    feed_id = request.args.get('feed_id')
    return json.dumps(rs.get_recent_posts(feed_id))

@app.route("/get_wall", methods=['GET'])
def get_wall():
    return json.dumps(rs.get_wall())

@app.route("/")
def index():
    feeds = rs.get_feeds()
    wall = rs.get_wall()
    current_time = time.time()
    return render_template("index.html", feeds = feeds, wall = wall, current_time = current_time)


if __name__ == "__main__":
    app.run(debug=True)