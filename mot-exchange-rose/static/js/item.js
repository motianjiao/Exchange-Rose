var item = item || {};

item.commentTemplate = _.template(
		`
		<div class="item-comment">
		<div class="comment-author-container">
		<img class="item-author-img" src="/img/<%= authorImg %>" />
		<span class="author"><%=author %></span>
		</div>
		<div class="comment-info-container">
		<span class="comment">
			<%= content %>
		</span>
		<span class="comment-datetime">
			<%= datetime %>
		</span>
		</div>
		</div>
		`
)






$(document).ready(function() {
	if (window.location.pathname === "/item/insertPage") {
		item.updateButtonText("submit");
		item.renderInsertOnwer()
		item.enableCreateButtons()
	} else if (window.location.pathname.startsWith("/item/viewPage")) {
		var params = getUrlVars();
		if (params.itemLink) {
			item.fetchItemInfo(params.itemLink);
		} else {
			alert("item not presented")
			window.location = "/"
		}
		
	}
})


item.fetchItemInfo = function(itemLink) {
	$.ajax({
		url: "/item/getInfo",
		type: "GET",
		dataType : "json",
		data : {
			itemLink : itemLink
		}
	})
	.always(function(data, status, err) {
		if (data.success) {
			if (profile && data.owner === profile.userEmail) {
				item.itemKey = itemLink
				item.updateButtonText("update")
				item.enableCreateButtons()
				item.enableDeleteButtons()
			} else {
				item.enableViewPage(itemLink);
			}
			item.renderData(data);
		} else {
			alert("failed to read item info")
		}
	}) 	
}


item.renderData = function(data) {
	console.log(data);
	$("#item-title").val(data.title);
	$("#item-purpose").val(data.purpose);
	$("#item-category").val(data.category);
	$("#item-description").val(data.description);
	$("#item-owner").val(data.owner);
	if (data.item_image_url && data.item_image_url !== "None") {
		$('.item-image-container img').attr('src', "/img/" + data.item_image_url);
	}
	item.renderComments(data.comments);
}

item.renderComments = function(comments) {
	comments.map(function(comment) {
		var temp = item.commentTemplate(
				{
					author: comment.author,
					authorImg: comment.authorImg,
					datetime: comment.datetime,
					content: comment.content
				}
			)
		$(".item-comment-container").append(temp);
	})
}

item.updateButtonText = function(text) {
	$("#item-action-btn").html(text);
}

item.enableCreateButtons = function() {
	$("#item-action-btn").click(function() {
		var data = item.readData();
		if (item.itemKey) {
			data.append('itemKey', item.itemKey)
		}
		if (data) {
			$.ajax({
				url: item.uploadUrl,
				type: "POST",
				dataType : "json",
				contentType: false,
				processData:false,       
				data: data
			})
			.always(function(data, status, err) {
				if (data.success && data.itemKey) {
					window.location = "/item/viewPage?itemLink=" + data.itemKey
				} else {
					alert("failed to read user info")
				}
			}) 	
		}
	})
	
	
	
	
	$(".item-image-container img").click(function() {
		$("#item-image").click()
	})
	
	$("#item-image").change(function() {
		console.log("image changed")
		if (this.files && this.files[0]) {
			var reader = new FileReader();
	        reader.onload = function (e) {
	            $('.item-image-container img').attr('src', e.target.result);
	        }
	        reader.readAsDataURL(this.files[0]);
		}
	})
}

item.enableDeleteButtons = function() {
	$("#item-delete-btn").prop("disabled", false);
	$("#item-delete-btn").click(function() {
		$.ajax({
			url: "/item/delete",
			type: "POST",
			dataType : "json",
			data: {
				itemKey: item.itemKey
			}
		})
		.always(function(data, status, err) {
			if (data.success) {
				window.location = "/"
			} else {
				alert("failed to read user info")
			}
		}) 	
	})
}

item.enableViewPage = function(itemLink) {
	$("#item-title").prop('disabled', true);
	$("#item-purpose").prop('disabled', true);
	$("#item-category").prop('disabled', true);
	$("#item-description").prop('disabled', true);
	$("#item-action-btn").html("Add Comment");
	$("#item-action-btn").click(function() {
		if (profile.userEmail) {
			$("#comment-dialog").fadeToggle();
		} else {
			$("#login-btn").click();
		}
		
	})
	$("#comment-cancel-btn").click(function() {
		$("#comment-dialog").fadeOut();
	})
	
	$("#comment-submit-btn").click(function() {
		var comment = $("#comment").val();
		if (!comment) {
			alert("comment cannot be empty");
		} else {
			$.ajax({
				url: "/comment/add",
				type: "POST",
				dataType : "json",      
				data: {
					itemKey: itemLink,
					content: comment
				}
			})
			.always(function(data, status, err) {
				if (data.success) {
					location.reload();
				} else {
					alert("failed to add comment")
				}
			}) 	
		}
	})
}

item.renderInsertOnwer = function() {
	$("#item-owner").val(profile.userEmail)
}

item.readData = function() {
	var formData = new FormData();
	var title = $("#item-title").val();
	var purpose = $("#item-purpose").val();
	var category = $("#item-category").val();
	var description = $("#item-description").val();
	if (!title) {
		alert("missing title");
		return false;
	}
	if (!purpose) {
		alert("missing purpose")
		return false;
	}
	if (!category) {
		alert("missing category")
		return false;
	}
	if (!description) {
		alert("missing description")
		return false;
	}
	
	input = document.getElementById('item-image');
	if (input && input.files && input.files[0]) {
		formData.append('image', input.files[0]);
	}
	formData.append('title', title);
	formData.append('purpose', purpose);
	formData.append('category', category);
	formData.append('description', description);
	return formData;
}