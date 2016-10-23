#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import json
import os

from google.appengine.api import users
from google.appengine.ext import ndb
import jinja2
import webapp2

from handlers.base_handlers import LoggedInPages, RosefireHandler, BaseAction
from rosefire import RosefireTokenVerifier
from utils import user_utils
from utils.user_utils import get_user_from_email, update_user_info, create_user_from_email_if_not_exist, update_login_time, get_all_users


def __init_jinja_env():
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
        extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols", "jinja2.ext.with_"],
        autoescape=True)
    # Example of a Jinja filter (useful for formatting data sometimes)
    #   jenv.filters["time_and_date_format"] = date_utils.time_and_date_format
    return jenv

jinja_env = __init_jinja_env()


ROSEFIRE_SECRET = 'XHVaootQIVTrvYe1xJtn'


class MainPage(LoggedInPages):
    def update_values(self, email, values):
        values["route"] = "/"
    
    def get_template(self):
        return "templates/main_page.html"

class UserListPage(LoggedInPages):
    def update_values(self, email, values):
        values["route"] = "/profile/list"
        users = get_all_users();
        values["user_query"] = users;
    
    def get_template(self):
        return "templates/userList.html"



class RosefireLoginHandler(RosefireHandler):
    def get(self):
        if "user_info" not in self.session:
            token = self.request.get('token')
            auth_data = RosefireTokenVerifier(ROSEFIRE_SECRET).verify(token)
            user_info = {"name": auth_data.name,
                         "username": auth_data.username,
                         "email": auth_data.email,
                         "role": auth_data.group}
            user = create_user_from_email_if_not_exist(auth_data.email)
            update_login_time(user)
            self.session["user_info"] = json.dumps(user_info)
        self.redirect(uri="/")

class UpdateUserInfo(BaseAction):
    def handle_post(self, email):
        print "update user info"
        user = get_user_from_email(email)
        data = {}
        data["contactInfo"] = self.request.get("contact")
        data["full_name"] = self.request.get("name")
        data["address"] = self.request.get("address")
        data["description"] = self.request.get("description")
        self.response.headers['Content-Type'] = 'application/json'  
        if update_user_info(user, data):      
            obj = {
               'success': True
            }       
        else:
            obj = {
                'success': False
            }
        self.response.out.write(json.dumps(obj))

class getUserInfo(webapp2.RequestHandler):
    def get(self):
        email = self.request.get('email');
        user = get_user_from_email(email);
        data = {} 
        if user:
            data["contact"] = user.contactInfo;
            data["address"] = user.address;
            data["last_login_date_time"] = str(user.last_login_date_time);
            data["username"] = user.email;
            data["description"] = user.description;
            data["full_name"] = user.full_name;
            data["profile_photo_url"] = user.profile_photo_url;
            data["success"] = True
        else:
            data["success"] = False
        self.response.out.write(json.dumps(data))

class EditProfilePage(LoggedInPages):    
    def get_template(self):
        return "templates/profile.html"
    
    def update_values(self, email, values):
        values["route"] = "/profile/edit"

class ViewProfilePage(LoggedInPages):
    def get_template(self):
        return "templates/profile.html"
    
    def update_values(self, email, values):
        values["route"] = "/profile/view"
        
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('Hello world!')

config = {}
config['webapp2_extras.sessions'] = {
    # This key is used to encrypt your sessions
    'secret_key': "whatEverYouLike",
}


class LogoutHandler(RosefireHandler):
    def get(self):
        del self.session["user_info"]
        self.redirect(uri="/")





app = webapp2.WSGIApplication([
    ('/', MainPage),
    ("/profile/edit", EditProfilePage),
    ("/profile/view", ViewProfilePage),
    ("/profile/update", UpdateUserInfo),
    ("/profile/getInfo", getUserInfo),
    ("/profile/list", UserListPage),
    ("/rosefire-logout", LogoutHandler),
    ('/rosefire-login', RosefireLoginHandler)
], debug=True, config = config)
