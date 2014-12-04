#Last Migrated to Production 12/3/2014 22:16 PST

A simple flask based app to allow friends to post interesting articles/blog posts to a common site to create a private feed.

It's like a chat room for a small group of friends.

You can find the app @ http://feedmyfriends.herokuapp.com/

TODO:
- Mostly Javascript based, i'll need to setup a quick parser to go through and asynchronously pull the relevant data
from links posted to the site. Initially, might just limit it to the favicon and title of the page, but eventually want to
expand to include more meaning ful text.
 - Update: Parser has been defined in in scraper.py. The parser extracts core attributes like the title, description and associated keywords, by searching thru the meta tags.
 - Update: building Javascript function to handle automatic posting 

- Need to setup a backend to store links posted based on the associated site:
 - Update: The app is currently using a redis database, which for the time being is shown in the code. 

Other notes:
  - Tip for building libxml on MAC OS X: STATIC_DEPS=true sudo pip install lxml
  - Setup Threading in the meantime:     
   - http://stackoverflow.com/questions/18430692/perform-task-directly-after-returning-json/18430861#18430861
  - Setting up Background Tasks on Heroku: https://devcenter.heroku.com/articles/python-rq; http://python-rq.org/
  - 
