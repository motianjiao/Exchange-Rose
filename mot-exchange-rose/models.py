from google.appengine.ext import ndb
    
class User(ndb.Model):
    email = ndb.StringProperty()
    full_name = ndb.StringProperty()
    contactInfo = ndb.StringProperty()
    address = ndb.StringProperty()
    description = ndb.StringProperty()
    profile_photo_url = ndb.StringProperty()
    last_login_date_time = ndb.DateTimeProperty(auto_now=False)
    
class Item(ndb.Model):
    name = ndb.StringProperty()
    category = ndb.StringProperty()
    description = ndb.StringProperty()
    purpose = ndb.StringProperty()
    status = ndb.StringProperty()
    owner = ndb.KeyProperty(kind=User)
    
class Comment(ndb.Model):
    writer = ndb.KeyProperty(kind=User)
    item = ndb.KeyProperty(kind=Item)
    content = ndb.StringProperty()
    data_time = ndb.DateTimeProperty()

class Message(ndb.Model):
    sender = ndb.KeyProperty(kind=User)
    receiver = ndb.KeyProperty(kind=User)
    content = ndb.StringProperty()
    date_time = ndb.DateTimeProperty()