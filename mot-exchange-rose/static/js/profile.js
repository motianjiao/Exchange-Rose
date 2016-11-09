var profile = profile || {};

$(document).ready(function(){
	if (window.location.pathname === "/profile/editPage" && profile.userEmail) {
		profile.enableButtons()
		profile.enableViewItemsButton(profile.userEmail)
		profile.fetchUserInfo(profile.userEmail)
	} else if (window.location.pathname.startsWith("/profile/viewPage")){
		profile.disableButtons()
		var params = getUrlVars();
		if (params.email && params.email === profile.userEmail) {
			window.location = "/profile/editPage"
		} else if (params.email) {
			profile.fetchUserInfo(params.email);
			profile.enableViewItemsButton(params.email)
			profile.hideUpdateButton()
		} else {
			alert("error parsing user email")
		}
	}
})

profile.disableButtons = function() {
	$("#contact").prop('disabled', true);
	$("#address").prop('disabled', true);
	$("#full-name").prop('disabled', true);
	$("#user-description").prop('disabled', true);
}

profile.enableViewItemsButton = function(email) {
	$("#view-items-btn").click(function() {
		window.location = "/?email=" + email;
	})
}

profile.hideUpdateButton = function() {
	$(".action-btn").hide()
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
		console.log("profile update url is " + profile.uploadUrl )
		$.ajax({
			url: profile.uploadUrl,
			data : profile.readData(),
			contentType: false,
			processData:false,        
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
	
	$(".image-name-container img").click(function() {
		$("#profile-image").click()
	})
	
	$("#profile-image").change(function() {
		console.log("image changed")
		if (this.files && this.files[0]) {
			var reader = new FileReader();
	        reader.onload = function (e) {
	            $('.image-name-container img').attr('src', e.target.result);
	        }
	        reader.readAsDataURL(this.files[0]);
		}
	})
}

profile.readData = function() {
	var data = {};
	var formData = new FormData();
	formData.append('contact', $("#contact").val());
	formData.append('address', $("#address").val());
	formData.append('name', $('#full-name').val());
	formData.append( 'description', $("#user-description").val());
	
	input = document.getElementById('profile-image');
	if (input && input.files && input.files[0]) {
		formData.append('image', input.files[0]);
	}
	
	data.contact = $("#contact").val();
	data.address = $("#address").val();
	data.name = $("#full-name").val();
	data.description = $("#user-description").val();
	return formData;
}

profile.renderData = function(data) {
	$("#contact").val(data.contact);
	$("#address").val(data.address);
	$("#full-name").val(data.full_name);
	$("#user-description").val(data.description);
	$("#last-logged-in").val(data.last_login_date_time);
	$("#username").val(data.username)
	if (data.profile_photo_url && data.profile_photo_url !== "None") {
		$('.image-name-container img').attr('src', "/img/" + data.profile_photo_url);
	}
}
