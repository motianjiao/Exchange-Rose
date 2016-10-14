'''
Created on Oct 13, 2016

@author: mot
'''
from google.appengine.api import users
import webapp2
from webapp2_extras import sessions

import main
import json


class RosefireHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)

        try:
            # Dispatch the request.
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def session(self):
        # Returns a session using the default cookie key.
        return self.session_store.get_session()

class LoggedInPages(RosefireHandler):
    def get(self):
        self.handleRoseLoggedIn()
    
    def handleRoseLoggedIn(self):
        template = main.jinja_env.get_template(self.get_template())
        values = {}
        if "user_info" in self.session:
            user_info = json.loads(self.session["user_info"])
            email = user_info["email"]
            values = {"user_email": email,
                      "logout_url": "/rosefire-logout",
                      "user_type" : "rose",
                      "profile_url": "/profile?email=" + email
                     }
            print values
            self.update_values(email, values)
        self.response.out.write(template.render(values))
    
    def get_page_title(self):
        return "Password Keeper"

    def update_values(self, email, values):
    # Subclasses should override this method to add additional data for the Jinja template.
        pass
    
    def get_template(self):
        return "templates/main_page.html"
    