var nav = nav || {};

$(document).ready(function() {
  nav.enableButtons();
})

nav.enableButtons = function() {
  $("#login-btn").click(function() {
    const registryToken = "d4a9675d-4864-4d39-bdb7-4e497cba6b41"
    Rosefire.signIn(registryToken, function(error, rfUser){
    	if (error) {
			console.log(err)
				return
			}
		window.location.replace('/rosefire-login?token=' + rfUser.token)
	})
  })
}
