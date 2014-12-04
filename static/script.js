var TEST_POST_FROM_SERVER = {"url" : "http://www.nytimes.com", 
                             "description" : "Fake Post for nytimes",
                             "title": "nytimes site",
                             "host_name": "www.nytimes.com",
                             "favicon": "http://static01.nyt.com/favicon.ico",
                            };
                             
                        


//assumes post is a json like object containing all of the requisite fields
var add_article_to_client = function (post) {
    var new_article = $("#proto-article .article").clone()
    //TODO: Review process for getting favicon
    new_article.find(".icon").html($('<img />', {src: post.favicon}))
    new_article.find(".title").html(($("<a>", {"text":post.title, 
                                               "href": post.url, 
                                               "target": "_blank"})))
    new_article.find(".description p").html(post.description)
    $(".posts :first").removeClass("current")
    new_article.addClass("current")
    new_article.prependTo($(".posts"))
    
}




var main = function() {
 for(i=0; i<5; i++){
     console.log(i)
     add_article(TEST_POST_FROM_SERVER)
 }
}
$(document).ready(main);