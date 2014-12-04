import os
from flask import Flask, render_template
import urlparse
import redis
import scraper

app = Flask(__name__)


#url = urlparse.urlparse(os.environ.get('REDISTOGO_URL', 'redis://localhost'))
url = urlparse.urlparse("redis://redistogo:f5805ed46d02698376e37d9a84c1cd4c@dab.redistogo.com:9506/")
redis = redis.Redis(host=url.hostname, port=url.port, db=0, password=url.password)





@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)