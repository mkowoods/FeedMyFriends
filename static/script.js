var TEST_POST_FROM_SERVER = {"url" : "http://www.nytimes.com", 
                             "description" : "Fake Post for nytimes",
                             "title": "nytimes site",
                             "host_name": "www.nytimes.com",
                             "favicon_url": "http://static01.nyt.com/favicon.ico",
                            };
                             
                        


//assumes post is a json like object containing all of the requisite fields
var articleJSONtoHTML = function (post) {
    var new_article = $(".article:first").clone()
    //TODO: Review process for getting favicon
    new_article.attr({feed_id: post.feed_id, post_id: post.post_id, create_time: post.create_time})
    new_article.find(".icon").html($('<img />', {src: post.favicon_url}))
    new_article.find(".title").html(($("<a>", {"text":post.title, 
                                               "href": post.url, 
                                               "target": "_blank"})))
    new_article.find(".description").html(post.description)
    $(".posts :first").removeClass("current")
    new_article.addClass("current")
    return new_article
}

var addFeed = function () {
    var feed_name = $("#feed-input").val()
    //console.log(feed_name)
    request = $.ajax({
                type: "POST",
                url: "set_feed",
                data: {feed_name: feed_name}//, option: "dev"}
                });
    //    prepend feed name an ID to the list
    request.done(function(data){
        $("#feeds ul").prepend($("<li>").html($("<div>", {feed_id: data, text: feed_name})))
    });
 };

var addPost = function () {
    var feed_id = "-1";
    var url = $("#post-input").val()
    //var feed_id = should select current active feed
    console.log(url)
    request = $.ajax({
                type: "POST",
                url: "set_post",
                data: {url: url, feed_id: feed_id}//, option: "dev"}       
                });
    request.done(function(data){
        console.log(data)
        if (data === "Error"){
            $(".post-input-form").addClass("has-error")
        } else {
            articleJSONtoHTML(data).appendToTo($(".posts"))
            $(".post-input-form").addClass("has-success")
        }
    });
 };

//TODO: NEED TO complete
var updateColor = function (){
    var feeds = $("#feeds > .nav > li")
    feeds.each(function(feed){
        console.log(feed.attr("feed_id"))
        })
    }


var filterByFeed = function(feed_id){
        //set default value for min_time = 0.0
    
    var params = {feed_id: feed_id}
    params['max_time'] = $(".posts div[feed_id='"+feed_id+"']:last").attr("create_time")
    params['min_time'] = 0.0

    request = $.ajax({
            type: "POST",
            url: "get_posts_by_feed",
            data: params//, option: "dev"}       
            });
    request.done(function(data){
        //console.log(data)
        if (data === "Error"){
            $(".post-input-form").addClass("has-error")
        } else {
            $.each(data, function(i, obj){
                if(params['max_time'] && i === 0){
                    return true;
                }else {
                    articleJSONtoHTML(obj).appendTo($(".posts"));
                }
            });
            $(".posts .article").hide();
            $(".posts div[feed_id='"+feed_id+"']").show();
        }
    });
};


var main = function(){
    /*Functions that are bound to html objects. To be loaded after the document*/
    $("#feed-input-btn").click(function(){
        addFeed();
    });
    
    $("#post-input-btn").click(function(){
        addPost();
    });
        
    $("#post-input").click(function(){
        $(".post-input-form").removeClass("has-error has-success")
    });
    
    $("#feeds li div").click(function(){
        var feed_id = $(this).attr('feed_id');
        filterByFeed(feed_id);
    });
                                 
        
};
$(document).ready(main);