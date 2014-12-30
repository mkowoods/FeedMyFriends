var COLOR_MAP = {}                         
                        
//Done to override jquery and make contain case insensitive, which is used in the feedSearch function
jQuery.expr[":"].containsIgnoreCase = jQuery.expr.createPseudo(function(arg) {
    return function( elem ) {
        return jQuery(elem).text().toUpperCase().indexOf(arg.toUpperCase()) >= 0;
    };
});

//assumes post is a json like object containing all of the requisite fields
var articleJSONtoHTML = function (post) {
    var new_article = $(".article:first").clone()
    //TODO: Review process for getting favicon
    new_article.attr({post_id: post.post_id, create_time: post.create_time})
    new_article.find(".icon").html($('<img />', {src: post.favicon_url}))
    new_article.find(".title").html(($("<a>", {"text":post.title, 
                                               "href": post.url, 
                                               "target": "_blank"})))
    new_article.find(".description").html(post.description)
    new_article.find(".time-since-post").html("0.0 min")
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
    //console.log(url)
    request = $.ajax({
                type: "POST",
                url: "set_post",
                data: {url: url, feed_id: feed_id}//, option: "dev"}       
                });
    request.done(function(data){
        //console.log(data)
        if (data === "Error"){
            $(".post-input-form").addClass("has-error")
        } else {
            articleJSONtoHTML(data).prependTo($(".posts"))
            $(".post-input-form").addClass("has-success")
        }
    });
 };

var addPostToFeed = function(post_id, feed_id, callback_function) {
    request = $.ajax({
        type: "POST",
        url: "assign_feed_to_post",
        data: {post_id: post_id, feed_id: feed_id}
    });
    request.done(function(data){
        if(data.status == "OK"){
            //console.log(post_id+" has been added to feed:"+feed_id)
            callback_function(false)
        }else {
            //console.log("Error")
            callback_function(true);
        }
        
    });
};

var filterByFeed = function(feed_id){
        //set default value for min_time = 0.0
    
    var params = {feed_id: feed_id}
    //params['max_time'] = $(".posts div[feed_id='"+feed_id+"']:last").attr("create_time")
    params['min_time'] = 0.0
    //console.log(params)
    request = $.ajax({
            type: "GET",
            url: "get_posts_by_feed",
            data: params//, option: "dev"}       
            });
    request.done(function(data){
        //console.log(data)
        $(".posts .article").hide("fast");
        if (data === "Error"){
            $(".post-input-form").addClass("has-error")
        } else {
            $.each(data, function(i, obj){
                if(params['max_time'] && i === 0){
                    return true;
                } else if ($(".posts div[post_id='"+obj.post_id+"']").length){
                    $(".posts div[post_id='"+obj.post_id+"']").show("slow")       
                }
                else {
                    articleJSONtoHTML(obj).appendTo($(".posts"));
                }
            });
            
            //$(".posts div[feed_id='"+feed_id+"']").show("slow");
        }
    });
};


//TODO: NEED TO complete
var updateColor = function (){
    var colors = fmf_colors
    var feeds = $("#feeds .nav li")
    feeds.each(function(idx){
        console.log($(this).find("div").attr("feed_id"))
        $(this).css('background-color', fmf_colors[idx % fmf_colors.length])
        })
    }

var feedSearch = function(el) {
    //accepts a jquery element and then binds to it  the keydown handler to create the
    //search funtion
    var search_bar = $(el)
    //console.log("Search bar from init of feedSearch")
    //console.log(search_bar)
    var post_id = $(el).parents(".article").attr("post_id")
    
    search_bar.keyup(function(e){
        $("#feeds li").css('background-color', "")
        $("#feeds li div").hide()
        search_bar.parent().removeClass("has-error has-success has-warning")
        var search_str = search_bar.val()
        
        if(search_str !== ""){
            var search_results = $("#feeds li div:containsIgnoreCase("+search_str+")")
            search_results.show()
        } else {
            $("#feeds li div").show()
        }
        
        if(search_results == undefined){
            search_bar.parent().addClass("has-error")
        } else if (search_results.length === 1){
            search_bar.parent().addClass("has-success")
            //console.log("Search Bar from successful results")
            //console.log(search_bar)
            if(e.keyCode == 13){
                var _tearDownSearchBar = function(hasError) {
                    search_bar.val("")
                    search_bar.parent().removeClass("has-success")
                    if (hasError){
                        var resp_html = "<div id='added-alert'>Sorry We had an Error</div>"
                    } else {
                        var resp_html = "<div id='added-alert'>Added to "+search_str+"</div>"
                    }
                    search_bar.parent().append(resp_html)
                    $("#added-alert").fadeIn(1500, function() {
                        $(this).fadeOut(1500, function(){
                            $(this).remove()
                        });   
                    });
                };
                addPostToFeed(post_id, search_results.attr('feed_id'), _tearDownSearchBar)

                $("#feeds li div").show("slow")
                
            };
        } else {
            search_bar.parent().addClass("has-error")
        }
    });
}

var main = function(){
    /*Functions that are bound to html objects. To be loaded after the document*/
    
    $("#feed-input-btn").click(function(){
        addFeed();
    });
    
    $("#post-input-btn").click(function(){
        addPost();
    });
    
    $("#logo").click(function() {
        return null
    }
        
        
    $("#post-input").click(function(){
        $(".post-input-form").removeClass("has-error has-success")
    });
    
    
    $("#feeds li").click(function(){
        //console.log("hit div")
        if($(this).hasClass('active')){
            $(this).removeClass('active');
            $(".posts .article").show("slow");
        }else{   
            $("#feeds li.active").removeClass('active')
            $(this).addClass('active')
            var feed_id = $(this).find('div').attr('feed_id');
            filterByFeed(feed_id);
        }
    });
    
    $("body").on("click", ".add-feed-btn", function() {
        console.log($(this))
        var feed_search_form = $(this).siblings(".feed-search")
        feed_search_form.toggle()
        feedSearch(feed_search_form.find(".feed-search-bar"))
        return false;
    });
        
};
$(document).ready(main);