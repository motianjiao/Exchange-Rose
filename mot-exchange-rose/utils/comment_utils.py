'''
Created on Oct 17, 2016

@author: mot
'''
from datetime import datetime


from models import Comment
from utils import item_utils


def add_comment(user, itemKey, content):
    if not user:
        print "missing user"
        return False
    now = datetime.now()
    item = item_utils.get_item_with_key(itemKey)
    if not item:
        print "wrong item key"
        return False
    if not content:
        print "missing content"
        return False;
    comment = Comment(writer = user.key, item = item.key, content = content, date_time = now)
    comment.put();
    return True;
    
def get_comments_of_item(item):
    return Comment.query(Comment.item == item.key).order(-Comment.date_time)