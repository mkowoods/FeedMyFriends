A simple flask based app to allow friends to post interesting articles/blog posts to a common site to create a private feed.

It's like a chat room for a small group of friends.

You can find the app @ http://feedmyfriends.herokuapp.com/

TODO:
- Mostly Javascript based, i'll need to setup a quick parser to go through and asynchronously pull the relevant data
from links posted to the site. Initially, might just limit it to the favicon and title of the page, but eventually want to
expand to include more meaning ful text.

- Need to setup a backend to store links posted based on the associated site

Other notes:
Tip for building libxml on MAC OS X: STATIC_DEPS=true sudo pip install lxml