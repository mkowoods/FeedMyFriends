
A simple flask based app to allow friends to post interesting articles/blog posts to a common site to create a private feed.

You can find the app @ http://feedmyfriends.herokuapp.com/

The Stack is:
- PostgreSQL DB
- Redis for a Cache
- Flask for the application
- gunicorn to handle the server.
- The app uses a custom scraper module to grab data from remote sites
