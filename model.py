from flask_sqlalchemy import SQLAlchemy
#from flask_security import UserMixin, RoleMixin
from flask_security.models import fsqla_v3 as fsqla

from flask_security.utils import hash_password

db = SQLAlchemy()

  
roles_users = db.Table('roles_users',
            db.Column('user_id',db.Integer(), db.ForeignKey('user.id')),
            db.Column('role_id',db.Integer(), db.ForeignKey('role.id')))


class User(db.Model, fsqla.FsUserMixin):
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


class Role(db.Model, fsqla.FsRoleMixin):
    __tablename__='role'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    name = db.Column(db.String(1000))
    
    def __str__(self):
        return self.name

store_managers = db.Table('store_managers',
            db.Column('user_id',db.Integer(), db.ForeignKey('user.id')),
            db.Column('store_id',db.Integer(), db.ForeignKey('store.id')))

class Store(db.Model):
    __tablename__='store'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    name = db.Column(db.String(1000),unique=True)
    address = db.Column(db.String(1000))
    manager = db.relationship ('User',secondary=store_managers,backref='user', uselist=False)
    approval_status =  db.Column(db.Integer, nullable=False)


item_category = db.Table('item_category',
            db.Column('item_id',db.Integer(), db.ForeignKey('item.id')),
            db.Column('category_id',db.Integer(), db.ForeignKey('category.id')))

class Category(db.Model):
    __tablename__='category'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    name = db.Column(db.String(1000),unique=True)
    approval_status =  db.Column(db.Integer, nullable=False)


class Item(db.Model):
    __tablename__='item'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    name = db.Column(db.String(1000),unique=True)
    unit = db.Column(db.String(100))
    price = db.Column(db.Integer)
    best_before = db.Column(db.String(100))
    category = db.relationship ('Category',secondary=item_category,backref='category', uselist=False)
    approval_status =  db.Column(db.Integer, nullable=False)

class Store_Item(db.Model):
    __tablename__='store_item'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey("store.id"))
    item_id = db.Column(db.Integer, db.ForeignKey("item.id"))
    quantity_remaining = db.Column(db.Integer)

class Purchase(db.Model):
    __tablename__='purchase'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    item_name = db.Column(db.String(100))
    store_name = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    total_amount = db.Column(db.Integer)
    purchase_time = db.Column(db.String(100))

class DeleteRequests(db.Model):
    __tablename__='deleteRequests'
    id = db.Column(db.Integer, nullable=False, unique=True, autoincrement=True, primary_key=True)
    class_ = db.Column(db.String(100)) #will be either category or item depending on the entry
    class_id = db.Column(db.Integer) #id of cateogry or item to be deleted
    
