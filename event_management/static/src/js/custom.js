$(window).scroll(function() {
    var scroll = $(window).scrollTop();
    if (scroll <= 200) {
        $(".header-area").removeClass("background-header");
    }
});



(function ($) {

	"use strict";

	// Header Type = Fixed
  $(window).scroll(function() {
    var scroll = $(window).scrollTop();
    var box = $('.header-text').height();
    var header = $('header').height();

    if (scroll >= box - header) {
      $("header").addClass("background-header");
    } else {
      $("header").removeClass("background-header");
    }
  });


  // Acc
    $(document).on("click", ".naccs .menu div", function() {
      var numberIndex = $(this).index();

      if (!$(this).is("active")) {
          $(".naccs .menu div").removeClass("active");
          $(".naccs ul li").removeClass("active");

          $(this).addClass("active");
          $(".naccs ul").find("li:eq(" + numberIndex + ")").addClass("active");

          var listItemHeight = $(".naccs ul")
            .find("li:eq(" + numberIndex + ")")
            .innerHeight();
          $(".naccs ul").height(listItemHeight + "px");
        }
    });



	// Menu Dropdown Toggle
  if($('.menu-trigger').length){
    $(".menu-trigger").on('click', function() {
      $(this).toggleClass('active');
      $('.header-area .nav').slideToggle(200);
    });
  }


	// Page loading animation
	 $(window).on('load', function() {

        $('#js-preloader').addClass('loaded');

    });

})(window.jQuery);

$(document).ready(function(){

//	$('.owl-listing').owlCarousel({
//		items:1,
//		loop:true,
//		dots: true,
//		nav: false,
//		autoplay: true,
//		margin:30,
//		  responsive:{
//			  0:{
//				  items:1
//			  },
//			  600:{
//				  items:1
//			  },
//			  1000:{
//				  items:1
//			  },
//			  1600:{
//				  items:1
//			  }
//		  }
//	})

	//Displaying or hiding search form depending on user
    var userCheckMenuAuditorium =  $('p#user_check_menu_auditorium').text().trim();
    var userCheck = $('.main-banner > .container > .row > .col-lg-10.m-auto > form#search-form').parent('.col-lg-10.m-auto').siblings('p#user_check').text().trim();
    if (userCheck === 'Administrator') {
        $('.main-banner > .container > .row > .col-lg-10.m-auto > form#search-form').show();
        $('.main-banner > .container > .row > .col-lg-10.offset-lg-1').show();
        $('.contact-hide-details').show();
//        $('.page-heading > .container > .row > .col-lg-6 > .top-text.header-text').show();
    } else {
        $('.main-banner > .container > .row > .col-lg-10.m-auto > form#search-form').hide();
//        $('.main-banner > .container > .row > hide-icons-user').hide();

    }
    if (userCheck === "Public user") {
       $('.main-banner > .container > .row > .col-lg-10.offset-lg-1').show();
       $('.contact-hide-details').show();
//       $('.page-heading > .container > .row > .col-lg-6 > .top-text.header-text').show();
    }

//    if($('a.account-page').html().indexOf('Administrator') > 0){
//        $('.only_admin').show();
//        $('.place_only_admin').show();
//    }

//    if(userCheck === "Administrator" && userCheck === "Public user") {
//        $('.main-banner > .container > .row > #show.show-only-am-only').hide();
//    }
    if(userCheck != "Administrator" && userCheck != "Public user") {
        $('.main-banner .top-text h2').text(userCheck);
        $('.main-banner > .container > .row > #show.show-only-am-only').show();
    }
    if(userCheckMenuAuditorium.length > 0) {
        $('.menu_venues').hide();
        $('.venue_show').hide();
    }
    else {
         $('.menu_venues').show();
         $('.only_admin').show();
         $('.place_only_admin').show();
         $('.venue_show').show();
        }

})

$(window).scroll(function() {
    var scroll = $(window).scrollTop();
    if (scroll <= 0) {
        $(".header-area").removeClass("background-header");
    }
});

$('nav.dropdown > a#menu_service_div_id').on('click', function(e){
    e.preventDefault();
    $('html, body').animate({
        scrollTop: $(".popular-categories").offset().top - 160
    }, 300)
})

 function getParameterByName(name, url) {
     if (!url) url = window.location.href;
     name = name.replace(/[\[\]]/g, "\\$&");
     var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
         results = regex.exec(url);
     if (!results) return null;
     if (!results[2]) return '';
     return decodeURIComponent(results[2].replace(/\+/g, " "));
 }

 $(window).on('load', function(){
    if(window.location.hash == '#loginModal?error=true'){
        $('#LoginModal').modal('toggle')
        if(getParameterByName('error') == 'true'){
            $('div#LoginModal .form-group.form-button').after('<div class="d-block"><p class="alert alert-danger" role="alert">Wrong login/password</p></div>')

        }
    }
    if(window.location.search == '?error'){
    alert('Event already exists for this date, Please choose another date.');
    window.history.pushState(null, '', '/booking');
    }
 })

 $(window).on('load', function(){
    if(window.location.hash == '#loginModal'){
        $('#LoginModal').modal('toggle')
        }
//       else:
//            window.location.href = "/";
 })

//$('td').click(function () {
//    var string_no = $(this).text().trim();
//    var string_no2 = $(this).find("p#record_value").text().trim();
//    console.log(string_no);
//    console.log(string_no2);
//    window.location.href = "/record/"+string_no2+"/";
//});
//
// $(window).on('load', function(){
//    if(window.location.pathname == '/booking'){
//      var venue = $('input#current_user_auditorium').val();
//      if(venue != '' || venue != null){
//      var venue_val = $('select#venue_id').val();
//      console.log(venue_val)
//      console.log('venue_val')
//      console.log(venue)
//      console.log('venue')
//       if(venue_val != '' || venue_val != null){
//            $('select#venue_id').val(venue).trigger('change')
//              renderCalendar()
//      }else{
//      var calendar = new Calendar(calendarEl, {
//      events: [
//        {
//
//        }
//      ],
//
//    });
//    }
//    }
//    }
// })

// $('.modal-button').on('click', function(e){
//    if(window.location.hash == '#loginModal?error=true'){
//      window.location.href = "/";
//   $('#LoginModal').modal('toggle')
//               }
//})


$('select#district_id').on('change', function(){
    var val = $(this).val();
$('select#place_id > option').each(function(){
    if($(this).data('distid') == val){
        $(this).show()
    }else{
        $(this).hide()
    }
})
})

$('select#venue_id').on('change', function(){
    var price = $(this).find('option:selected').data('price');
if(price != '' || price != null){
    $('input#auditorium_price').val(price).trigger('change')
}

})


$('.dropdown > a#menu_service_div_id').on('click', function(e){
    e.preventDefault();
            window.location.href = "/#service_div";
    $('html, body').animate({
        scrollTop: $(".popular-categories").offset().top - 160
    }, 300)
})