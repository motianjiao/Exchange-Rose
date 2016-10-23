var profile = profile || {};

$(document).ready(function(){
	if (window.location.pathname === "/profile/edit" && profile.userEmail) {
		profile.enableButtons()
		profile.fetchUserInfo(profile.userEmail)
	} else if (window.location.pathname.startsWith("/profile/view")){
		profile.disableButtons()
		var params = getUrlVars();
		if (params.email && params.email === profile.userEmail) {
			window.location = "/profile/edit"
		} else if (params.email) {
			profile.fetchUserInfo(params.email);
		} else {
			alert("error parsing user email")
		}
	}
})

profile.disableButtons = function() {
	$(".action-btn").html("View Items")
	$("#contact").prop('disabled', true);
	$("#address").prop('disabled', true);
	$("#full-name").prop('disabled', true);
	$("#user-description").prop('disabled', true);
	
}

profile.fetchUserInfo = function(email) {
	$.ajax({
		url: "/profile/getInfo?email=" + email,
		type: "GET",
		dataType : "json"
	})
	
	.always(function(data, status, err) {
		if (data.success) {
			profile.renderData(data)
		} else {
			alert("failed to read user info")
		}
	}) 
}

profile.enableButtons = function() {
	$(".action-btn").click(function() {
		$.ajax({
			url: "/profile/update",
			data : profile.readData(),
			type : "POST",
			dataType: "json"
		})
		
		.always(function(data, status, err) {
			console.log(data)
			if (data.success) {
				alert("user info updated");
			} else {
				alert("failed to update user info");
			}
			window.location.reload();
		})
	})
}

profile.readData = function() {
	var data = {};
	data.contact = $("#contact").val();
	data.address = $("#address").val();
	data.name = $("#full-name").val();
	data.description = $("#user-description").val();
	return data;
}

profile.renderData = function(data) {
	$("#contact").val(data.contact);
	$("#address").val(data.address);
	$("#full-name").val(data.full_name);
	$("#user-description").val(data.description);
	$("#last-logged-in").val(data.last_login_date_time);
	$("#username").val(data.username)
}
