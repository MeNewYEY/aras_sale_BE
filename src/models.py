from flask_sqlalchemy import SQLAlchemy
from datetime import date, time, datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)
    first_name = db.Column(db.String(250), unique=False, nullable=False)
    last_name = db.Column(db.String(250), unique=False, nullable=False)
    phone_number = db.Column(db.String(50), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    user_type= db.Column(db.String(50), unique=False, nullable=False)
    order = db.relationship('Order', backref='user', lazy=True)
    
    def __init__(self,user_name,password,first_name,last_name,phone_number):
        self.user_name=user_name
        self.password=password
        self.first_name=first_name
        self.last_name=last_name
        self.phone_number=phone_number
        self.user_type=user_type
        self.created_at = datetime.now()
        self.is_active=True 

    def __repr__(self):
        return '<User %r>' % self.user_name

    def serialize(self):
        return {
            "id": self.id,
            "user_name": self.user_name,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone_number": self.phone_number,
            "user_type": self.user_type
            # do not serialize the password, its a security breach
        }

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    number = db.Column(db.String(250), unique=False, nullable=False)
    serial = db.Column(db.String(250), unique=False, nullable=False)
    description = db.Column(db.String(250), unique=False, nullable=False)
    condition = db.Column(db.String(100), unique=False, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), unique=False, nullable=False)
    
    def __init__(self,data,user_id):
        self.user_id=user_id
        self.number = data["number"]
        self.serial = data["serial"]
        self.description = data["description"]
        self.condition = data["condition"]
        self.created_at = datetime.now()

    def __repr__(self):
        return '<Order %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "number": self.number,
            "serial": self.serial,
            "description": self.description,
            "condition": self.condition,
            "created_at": self.created_at
        }

