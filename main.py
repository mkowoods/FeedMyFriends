from flask import Flask, request, render_template, Response
from urlparse import urlparse
import scraper
import json
import time
import model
import os
import logging

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
    except ValueError, e:
        #TODO: need to predefine certain Exceptions or fail for "unknown"
        post['status'] = "Exception: scraper.ValueError %s"%(e)
    except Exception as e:
        post['status'] = "Exception: %s, %s"%(type(e), e)
    app.logger.info("SCRAPER_STATUS: %s"%post['status'])
    return post

#Misc Support Functions
class JSONResponse(Response):

    def __init__(self, obj):
        Response.__init__(self, json.dumps(obj, indent=4, separators=(',', ': ')),
                          mimetype = "application/json")


def is_admin(submitted_key):
    return submitted_key == ADMIN_KEY

#View

@app.route("/delete_post", methods=['DELETE'])
def delete_key():
    submission_key = request.args.get('key')
    post_id = request.args.get('post_id')
    if is_admin(submission_key):
         return JSONResponse(model.model.delete_post(post_id))
    else:
        return "You're not Admin"

@app.route("/scraper_api", methods=['GET'])
def scraper_api():
    """method to handle the scraping of new posts entered from the browser or other sources"""
    url = request.values.get('url')
    return JSONResponse(new_post_controller(url))

@app.route("/admin", methods=['GET'])
def admin():
    submission_key = request.args.get('key')
    if is_admin(submission_key):
        tmp = {'redis_conn': model.redis_cache.REDIS_CONN,
               'postgres_conn': model.redis_cache.pgdb.DB_CONN}
        return JSONResponse(tmp), 200
    else:
        return JSONResponse("{status: 404}"), 404

@app.route("/flush_cache", methods=['DELETE'])
def flush_cache():
    submission_key = request.args.get('key')
    if submission_key == ADMIN_KEY:
        res = model.model.flushdb()
        return JSONResponse(res)
    else:
        return 'Failed'

@app.route("/get_feeds", methods=['GET'])
def get_feeds():
    return JSONResponse(model.model.get_all_feeds())


@app.route("/get_posts_by_feed", methods=['GET'])
def get_posts_by_feed():
    feed_id = request.values.get('feed_id')
    max_time = request.values.get('max_time')
    min_time = request.values.get('min_time')
    try:
        max_time = float(max_time) if max_time else float('inf')
        min_time = float(min_time) if min_time else 0.0
        return JSONResponse(model.model.get_posts_by_feed(feed_id, min_time=min_time, max_time=max_time))
    except ValueError:
        return "Parameter failed Conversion To Float"
    else:
        return "Error"


@app.route("/get_wall", methods=['GET'])
def get_wall():
    return JSONResponse(obj=model.model.get_wall())


@app.route("/set_feed", methods = ['POST'])
def set_feed():
    feed_name = request.values.get('feed_name')
    option = request.values.get('option')
    out = "Error"
    if feed_name:
        res = model.model.set_feed(feed_name)
        if option == "dev":
            res = "Testing Received %s"%feed_name
        if res:
            out = JSONResponse(res)
    return out

@app.route("/set_post", methods=['POST'])
def set_post():
    url = request.values.get('url')
    feed_id = request.values.get("feed_id")
    option = request.values.get('option')
    #logging.info("SET_POST: url:%s, feed_id:%s, option:%s"%(url, feed_id, option))
    app.logger.info("SET_POST: url:%s, feed_id:%s, option:%s"%(url, feed_id, option))
    out = None
    if url:
        post_data = new_post_controller(url)
        if post_data['status'] == "OK":
            if option == "dev":
                post_data['status'] = 'DEV'
                post_data['feed_id'] = feed_id
                post_data['post_id'] = str(int(time.time()*1000))+'-DevID'
                post_data['create_time'] = time.time()
                out = post_data
            else:
                out = model.model.set_post(feed_id, post_data)
    return JSONResponse(out) if out else "Error"

@app.route("/assign_feed_to_post", methods=['POST'])
def assign_feed_to_post():
    feed_id = request.form['feed_id']
    post_id = request.form['post_id']
    key = model.model.add_post_to_feed(post_id=post_id, feed_id=feed_id)
    out = {'status':'OK', 'key':key} if key else {'status': 'Error'}
    return JSONResponse(out)

@app.route("/")
def index():
    feeds = model.model.get_all_feeds()
    wall = model.model.get_wall()
    current_time = time.time()

    try:
        return render_template("index.html", feeds = feeds, wall = wall, current_time = current_time)
    except Exception, e:
        logging.error(e)
        return "Error"


if __name__ == "__main__":
    print 'Redis DB Connection: %s'%model.redis_cache.REDIS_CONN
    print 'Postgres DB Connection: %s'%model.redis_cache.pgdb.DB_CONN
    app.run(debug=True)