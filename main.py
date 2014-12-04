from flask import Flask, request, render_template
import scraper
import json
import time

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


@app.route("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)