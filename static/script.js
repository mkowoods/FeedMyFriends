//assumes post is a json like object containing all of the requisite fields
var add_article = function(post){
    var new_article = $("#proto-article").clone()
    new_article.removeAttr("id")
    new_article.find(".source")
    $(".posts").append(new_article)
    new_article.show()
    
    new_article.click(function() {
       $(this) 
        
    });
}


var main = function() {
  $('.article').click(function() {
    $('.article').removeClass('current');
    $('.description').hide();

    $(this).addClass('current');
    $(this).children('.description').show();
  });

  $(document).keypress(function(event) {
    if(event.which === 111) {
      $('.description').hide();

      $('.current').children('.description').show();
    }

    else if(event.which === 110) {
      var currentArticle = $('.current');
      var nextArticle = currentArticle.next();
      
      currentArticle.removeClass('current');
      nextArticle.addClass('current');
    }
  });
}

$(document).ready(main);