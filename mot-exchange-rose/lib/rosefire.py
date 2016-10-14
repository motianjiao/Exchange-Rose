
import jwt


class RosefireError(Exception):
    pass

class AuthData():

    def __init__(self, username, name, provider, group, issued_at):
        self.username = username
        self.provider = provider
        self.group = group
        self.name = name
        self.issued_at = issued_at
        self.email = username + "@rose-hulman.edu"

class RosefireTokenVerifier():

    def __init__(self, secret):
        self.secret = secret

    def verify(self, token):
        decodedToken = jwt.decode(token, self.secret)
        iat = decodedToken.get("iat")
        uid = decodedToken["d"].get("uid")
        group = decodedToken["d"].get("group")
        name = decodedToken["d"].get("name")
        provider = decodedToken["d"].get("provider")
        return AuthData(uid, name, provider, group, iat)
