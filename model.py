from flask_sqlalchemy import SQLAlchemy
from flask_security import UserMixin, RoleMixin
from flask_security.utils import hash_password

db = SQLAlchemy()

  
roles_users = db.Table('roles_users',
            db.Column('user_id',db.Integer(), db.ForeignKey('user.id')),
            db.Column('role_id',db.Integer(), db.ForeignKey('role.id')))


class User(db.Model, UserMixin):
    __tablename__='user'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    username = db.Column(db.String(1000))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    active = db.Column(db.Boolean)
    fs_uniquifier = db.Column(db.String(100))
    roles = db.relationship ('Role',secondary=roles_users,backref='role')

    def __str__(self):
        return self.email


class Role(db.Model, RoleMixin):
    __tablename__='role'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    name = db.Column(db.String(1000))
    
    def __str__(self):
        return self.name

class Category(db.Model):
    __tablename__='category'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    name = db.Column(db.String(1000),unique=True)

class Item(db.Model):
    __tablename__='item'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    name = db.Column(db.String(1000),unique=True)
    unit = db.Column(db.String(100))
    price = db.Column(db.Integer)
    category_id = db.Column(db.Integer, db.ForeignKey("category.id"))
    category = db.relationship("Category", backref="item")


class Purchase(db.Model):
    __tablename__='purchase'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
    cost = db.Column(db.Integer)
    purchase_time = db.Column(db.String(100))
