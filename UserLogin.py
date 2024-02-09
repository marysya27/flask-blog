from flask_login import UserMixin
from flask import url_for

class UserLogin(UserMixin):
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self 
    
    def create(self, user):
        self.__user = user
        return self
    
    def get_id(self):
        return str(self.__user['user_id'])
    
    def getName(self):
        return self.__user['username'] if self.__user else 'none'
    
    def getEmail(self):
        return self.__user['email'] if self.__user else 'none'
    
    def getAvatar(self, app):
        img = None
        if not self.__user['avatar']:
            try:
                with app.open_resource(app.root_path + url_for('static', filename='imgs/avatar-default-svgrepo-com.png'), "rb") as f:
                    img = f.read()
            except FileNotFoundError as e:
                print(e)
        else:
            img = self.__user['avatar']

        return img
    

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext == 'png' or ext == 'PNG' or ext == 'jpeg':
            return True
        return False
    