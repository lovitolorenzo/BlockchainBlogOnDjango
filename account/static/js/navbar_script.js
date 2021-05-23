$( document ).ready(function() {
	
	$(".dropdown-menu").css("background","white");
	
	$(".fa, .link, a").css("color","black");
	$(".icon-bar").css("background","black");
	
	$(".form-control").css("border-radius","0");
	$(".dropdown-menu").css({
		"border-bottom-right-radius":"0",
		"border-bottom-left-radius":"0"
	});
	
	// Open close dropdown on click
	$("li.dropdown").click(function(){
		if($(this).hasClass("open")) {
			$(this).find(".dropdown-menu").slideUp("fast");
			$(this).removeClass("open");
		}
		else { 
			$(this).find(".dropdown-menu").slideDown("fast");
			$(this).toggleClass("open");
		}
	});

	// Close dropdown on mouseleave
	$("li.dropdown").mouseleave(function(){
		$(this).find(".dropdown-menu").slideUp("fast");
		$(this).removeClass("open");
	});
	
	$("#collapse-1").click(function(){
		$(this).find(".dropdown-menu").slideUp("fast");
		$(this).removeClass("open");
	});

	// Navbar toggle
	$(".navbar-toggle").click(function(){
		$(".navbar-collapse").toggleClass("collapse").slideToggle("fast");
	});
});