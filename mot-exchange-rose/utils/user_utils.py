from datetime import datetime
from google.appengine.ext import ndb

from models import User


def create_user_from_email_if_not_exist(email):
    email = email.lower()
    player = User.get_by_id(email, parent=get_parent_key_from_email(email))
    if not player:
        player = User(id=email, parent = get_parent_key_from_email(email), email=email)
        player.put()
    return player

def update_login_time(user):
    user.last_login_date_time = datetime.now()
    user.put()

def get_user_from_email(email):
    email = email.lower()
    user = User.get_by_id(email, parent=get_parent_key_from_email(email))
    return user

def get_all_users():
    return User.query()

def get_parent_key(user):
    return get_parent_key_from_email(user.email())

def get_parent_key_from_email(email):
    return ndb.Key("Entity", email.lower())

def get_user_key_from_email(email):
    user = get_user_from_email(email);
    return user.key;

def update_user_info(user, values):
    for key in values:
        setattr(user, key, values[key])
    user.put()
    return True;