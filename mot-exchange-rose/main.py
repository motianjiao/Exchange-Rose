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
import logging
import os

from google.appengine.api import users, blobstore
from google.appengine.ext import ndb
import jinja2
import webapp2
from handlers import blob_handler
from handlers.base_handlers import LoggedInPages, RosefireHandler, BaseAction
from rosefire import RosefireTokenVerifier
from utils.item_utils import create_item, update_item, delete_item, get_item_with_key, get_item_with_key, get_items
from utils.user_utils import get_user_from_email, update_user_info, create_user_from_email_if_not_exist, update_login_time, get_all_users
from utils.comment_utils import get_comments_of_item, add_comment

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

class AddComment(BaseAction):
    def handle_post(self, email):
        user = get_user_from_email(email)
        itemKey = self.request.get("itemKey");
        content = self.request.get("content");
        obj = {};
        self.response.headers['Content-Type'] = 'application/json'
        if add_comment(user, itemKey, content):
            obj = {
                'success': True
            }
        else:
            obj = {
                'success': False
            }
        self.response.out.write(json.dumps(obj))


class UpdateUserInfo(BaseAction):
    def handle_post(self, email):
        user = get_user_from_email(email)
        data = {}
        data["contactInfo"] = self.request.get("contact")
        data["full_name"] = self.request.get("name")
        data["address"] = self.request.get("address")
        data["description"] = self.request.get("description")
        
        if self.get_uploads() and len(self.get_uploads()) == 1:
            logging.info("Received an image blob")
            media_blob = self.get_uploads()[0]
            media_blob_key = media_blob.key()
            data["media_blob_key"] = media_blob_key;
        else:
            logging.info("no image found")
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
            data["profile_photo_url"] = str(user.media_blob_key);
            print str(user.media_blob_key);
            data["success"] = True
        else:
            data["success"] = False
        self.response.out.write(json.dumps(data))

class GetItemInfo(webapp2.RequestHandler):
    def get(self):
        itemLink = self.request.get("itemLink")
        item = get_item_with_key(itemLink)
        data = {}
        if item:
            ownerEmail = item.owner.get().email;
            data["title"] = item.title;
            data["category"] = item.category;
            data["purpose"] = item.purpose;
            data["owner"] = ownerEmail;
            data["description"] = item.description;
            data["item_image_url"] = str(item.media_blob_key);
            data["success"] = True
            comments = get_comments_of_item(item);
            commentArr = [];
            for comment in comments.fetch():
                tmp = comment.to_dict();
                commentArr.append({
                 "author" : tmp["writer"].get().full_name,
                 "authorImg": str(tmp["writer"].get().media_blob_key),
                 "content": tmp["content"],
                 "datetime": str(tmp["date_time"])
                })
            data["comments"] = commentArr;
        else:
            data["success"] = False
        self.response.out.write(json.dumps(data))






class EditProfilePage(LoggedInPages):
    def get_template(self):
        return "templates/profile.html"

    def update_values(self, email, values):
        values["route"] = "/profile/edit"
        values["profile_update_url"] = blobstore.create_upload_url('/profile/update')

class ViewProfilePage(LoggedInPages):
    def get_template(self):
        return "templates/profile.html"

    def update_values(self, email, values):
        values["route"] = "/profile/view"

class InsertItemAction(BaseAction):
    def handle_post(self, email):
        obj = {};
        media_blob_key = False;
        if self.get_uploads() and len(self.get_uploads()) == 1:
            logging.info("Received an image blob")
            media_blob = self.get_uploads()[0]
            media_blob_key = media_blob.key()
        
        itemKey = self.request.get("itemKey");
        purpose = self.request.get("purpose")
        category = self.request.get("category")
        description = self.request.get("description")
        title = self.request.get("title");
        if itemKey:
            item = get_item_with_key(itemKey)
            values = {
                "title": title,
                "description": description,
                "category": category,
                "purpose": purpose,
            }
            if (media_blob_key):
                values["media_blob_key"] = media_blob_key;
            obj["success"] = update_item(email, item, values)
            obj["itemKey"] = itemKey
        else:
            itemKey = create_item(email, title, purpose, category, description, media_blob_key)
            if itemKey:
                obj["itemKey"] = itemKey
                obj["success"] = True
            else:
                obj["success"] = False
        self.response.out.write(json.dumps(obj))

class InsertItemPage(LoggedInPages):
    def get_page_title(self):
        return "Create Item"

    def update_values(self, email, values):
        values["route"] = "/item/insert"
        values["item_update_url"] = blobstore.create_upload_url('/item/insert') 

    def get_template(self):
        return "templates/item.html"

class ViewItemPage(LoggedInPages):
    def get_page_title(self):
        return "View Item"

    def update_values(self, email, values):
        values["route"] = "/item/view"
        values["item_update_url"] = blobstore.create_upload_url('/item/insert');

    def get_template(self):
        return "templates/item.html"


config = {}
config['webapp2_extras.sessions'] = {
    # This key is used to encrypt your sessions
    'secret_key': "whatEverYouLike",
}


class LogoutHandler(RosefireHandler):
    def get(self):
        del self.session["user_info"]
        self.redirect(uri="/")

class GetItems(webapp2.RequestHandler):
    def get(self):
        limit = self.request.get("limit");
        offset = self.request.get("offset");
        print limit;
        print offset;
        item_query = get_items(offset, limit)
        obj = {};
        if item_query:
            obj["success"] = True
            obj["item_query"] = item_query
        else:
            obj["success"] = False
        self.response.out.write(json.dumps(obj))

class deleteItem(BaseAction):
    def handle_post(self, email):
        itemKey = self.request.get("itemKey");
        obj = {};
        if delete_item(email, itemKey):
            obj["success"] = True
        else:
            obj["success"] = False
        self.response.out.write(json.dumps(obj))


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ("/profile/editPage", EditProfilePage),
    ("/profile/viewPage", ViewProfilePage),
    ("/item/insert", InsertItemAction),
    ("/item/insertPage", InsertItemPage),
    ("/item/viewPage", ViewItemPage),
    ("/item/delete", deleteItem),
    ("/item/getInfo", GetItemInfo),
    ("/item/getItems", GetItems),
    ("/profile/update", UpdateUserInfo),
    ("/profile/getInfo", getUserInfo),
    ("/profile/listPage", UserListPage),
    ("/rosefire-logout", LogoutHandler),
    ('/rosefire-login', RosefireLoginHandler),
    ('/img/([^/]+)?', blob_handler.BlobServer),
    ('/comment/add', AddComment)
], debug=True, config=config)
