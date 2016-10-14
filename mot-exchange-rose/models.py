from google.appengine.ext import ndb
    
class User(ndb.Model):
    email = ndb.StringProperty()
    first_name = ndb.StringProperty()
    last_name = ndb.StringProperty()
    contactInfo = ndb.StringProperty()
    profile_photo_url = ndb.StringProperty()
    last_login_date_time = ndb.StringProperty()
    
class Item(ndb.Model):
    name = ndb.StringProperty()