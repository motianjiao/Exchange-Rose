'''
Created on Oct 17, 2016

@author: mot
'''
from datetime import datetime

from google.appengine.ext import ndb

from models import Item
from utils import user_utils
from utils.user_utils import get_user_key_from_email


def create_item(email, title, purpose, category, description, media_blob_key):
    if not email:
        print "missing email for logged in user"
        return False;
    if not title:
        print "missing title"
        return False;
    if not purpose:
        print "missing purpose"
        return False;
    if not category:
        print "missing category"
        return False;
    if not description:
        print "missing description"
        return False;
    item = Item(title = title, 
                category = category, 
                purpose = purpose, 
                description = description, 
                owner = user_utils.get_user_key_from_email(email), 
                status = "active",
                upload_date_time = datetime.now())
    if (media_blob_key):
        item.media_blob_key = media_blob_key
    item.put()
    print "item inserted"
    print str(item)
    return item.key.urlsafe()

def get_item_with_key(itemKey):
    key = ndb.Key(urlsafe = itemKey)
    item = key.get();
    return item;
    
def delete_item(email, key):
    item = get_item_with_key(key)
    if not item:
        print "Item does not exist"
        return False;
    if item.owner != get_user_key_from_email(email):
        print "Item does not belong to the logged in user"
        return False;
    item.key.delete()
    return True
    
def update_item(email, item, values):
    owner = get_user_key_from_email(email)
    if not item:
        print "Item does not exist"
        return
    if item.owner != owner:
        print "Item does not belong to the logged in user"
        return
    for key in values:
        setattr(item, key, values[key])
    item.put()
    print "update item successfully"
    return True;

def get_items_for_email(email):
    pass

def item_to_dict(item):
    dic = item.to_dict();
    dic["owner"] = dic["owner"].get().email;
    print dic;
    dic["upload_date_time"] = dic["upload_date_time"].strftime('%m/%d/%Y');
    dic["itemLink"] = item.key.urlsafe()
    dic["media_blob_key"] = str(dic["media_blob_key"]);
    return dic;

def get_items(offset, limit, email):
    if (email):
        key = get_user_key_from_email(email)
        item_query = Item.query(Item.owner == key).order()
    else:
        item_query = Item.query().order()
    result = [];
    for item in item_query:
        result.append(item_to_dict(item));
    return result
