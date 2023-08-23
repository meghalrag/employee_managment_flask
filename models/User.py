# Import from system libraries
from datetime import datetime
from flask_bcrypt import generate_password_hash, check_password_hash

# Import from application modules
from models.db import db


# Object Document Model (ODM) for User Objects
class User(db.Document):
    username = db.EmailField(required=True, unique=True)
    phone_number = db.StringField(required=True, unique=True)
    password = db.StringField(required=True)
    roles = db.ListField(db.StringField(), default=['employee'])

    # function to hash a password for security encryption
    def hash_password(self):
        self.password = generate_password_hash(self.password).decode('utf8')

    # function to hash a password for security decryption
    def check_password_hash(self, password):
        return check_password_hash(self.password, password)
    
    
class UserProfile(db.Document):
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    name = db.StringField(required=True)
    email = db.EmailField(required=True, unique=True)
    phone_number = db.StringField(required=True, unique=True)
    designation = db.StringField(required=True)
    department = db.StringField(required=True)
    manager = db.StringField(required=True)
    hired_date = db.DateTimeField(default=datetime.utcnow)


class UserFileMapping(db.Document):
    user = db.ReferenceField('User', reverse_delete_rule=db.CASCADE)
    file_id = db.StringField(required=True)
    exported_date = db.DateTimeField(default=datetime.utcnow)


class TokenBlacklist(db.Document):
    jti = db.StringField(unique=True, required=True)
