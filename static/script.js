var TEST_POST_FROM_SERVER = {"url" : "http://www.nytimes.com", 
                             "description" : "Fake Post for nytimes",
                             "title": "nytimes site",
                             "host_name": "www.nytimes.com",
                             "favicon_url": "http://static01.nyt.com/favicon.ico",
                            };
                             
                        


//assumes post is a json like object containing all of the requisite fields
var addArticleToClient = function (post) {
    var new_article = $("#proto-article .article").clone()
    //TODO: Review process for getting favicon
    new_article.find(".icon").html($('<img />', {src: post.favicon_url}))
    new_article.find(".title").html(($("<a>", {"text":post.title, 
                                               "href": post.url, 
                                               "target": "_blank"})))
    new_article.find(".description p").html(post.description)
    $(".posts :first").removeClass("current")
    new_article.addClass("current")
    new_article.prependTo($(".posts"))   
}



var addFeed = function () {
    var feed_name = $("#feed-input").val()
    console.log(feed_name)
    request = $.ajax({
                type: "POST",
                url: "set_feed",
                data: {feed_name: feed_name, option: "dev"}       
                });
    //prepend feed name an ID to the list
 };


var addPost = function () {
    var feed_name = $("#feed-input").val()
    console.log(feed_name)
    request = $.ajax({
                type: "POST",
                url: "set_feed",
                data: {feed_name: feed_name, option: "dev"}       
                });
    //prepend feed name an ID to the list
 };

var updateColor = function (){
    var feeds = $("#feeds > .nav > li")
    feeds.each(function(feed){
        console.log(feed.attr("feed_id"))
        })
    }

var main = function(){
    /*Functions that are bound to html objects. To be loaded after the document*/
    $("#feed-input-btn").click(function(){
        addFeed()
    });
        
        
};
$(document).ready(main);