var itemList = itemList || {};
itemList.data = itemList.data || {};
itemList.displayData = itemList.displayData || {}
itemList.template = _.template(
`<div class="item" id="<%= itemLink %>">
	<div class="item-image-description-container">
	<div class="item-image-container">
		<img src="/img/<%= item_image_url %>"/>
	</div>
	<div class="item-info-container">
		<div class="item-title-container">
		<h2 class="title">
			<%= title %>
		</h2>
		</div>
		<div class="item-category">
			<label>Category: </label>
			<span><%= category %></span>
		</div>
		<div class="item-purpose">
			<label>For: </label>
			<span><%= purpose %></span>
		</div>
		<div class="item-description">
			<p><%= description %></p>
		</div>
	</div>
	</div>
	<div class="owner-info">
		<span class="owner-email">
			<%= ownerEmail %>
		</span>
	</div>
</div>`
)
itemList.limit = 20;
itemList.offset = 0;

$(document).ready(function() {
	$.ajax({
		url: "/item/getItems?limit=" + itemList.limit + "&offset=" + itemList.offset,
		type: "GET",
		dataType : "json"
	})
	
	.always(function(data, status, err) {
		console.log(data);
		if (data.success) {
			itemList.data = data.item_query;
			itemList.displayData = itemList.data;
			itemList.renderData()
		} else {

		}
	}) 
	itemList.enableButtons();
})

itemList.renderData = function() {
	$(".item-list").html("");
	itemList.displayData.map(function(item) {
		var listItem = itemList.template(
					{title: item.title,
					 category: item.category,
					 description: item.description,
					 ownerEmail: item.owner,
					 purpose: item.purpose,
					 itemLink: item.itemLink,
					 item_image_url: item.media_blob_key
					})
		
		$(".item-list").append(listItem)
		$("#" + item.itemLink).click(function() {
			window.location = "item/viewPage?itemLink=" + item.itemLink;
		})
	})
}

itemList.enableButtons = function() {
	$("input:radio[name=purpose]").click(function() {
		var self = this;
		if ($(self).val() === "all") {
			itemList.displayData = itemList.data;
		} else {
			itemList.displayData = itemList.data.filter(function(item) {
				return item.purpose === $(self).val();
			})
		}
		itemList.renderData();
	})
	
	$("#input-search-text").keyup(function() {
		var value = $(this).val().toLowerCase();
		itemList.displayData = itemList.data.filter(function(item) {
			return item.title.toLowerCase().includes(value) 
					|| item.category.toLowerCase().includes(value) 
					|| item.description.toLowerCase().includes(value);
		})
		itemList.renderData();
	})
}
