from flask_restful import Resource
from model import db
from model import *
from flask_restful import fields, marshal_with
from validation import *
from flask_restful import reqparse
from sqlalchemy import exc, func
from sqlalchemy import or_,and_
from datetime import *

stores_waiting_approval={
    "id":fields.Integer,
    "name":fields.String,
    "address":fields.String,
    "manager":fields.String,
    "approval_status":fields.String,
}

categories={
    "id":fields.Integer,
    "name":fields.String,
    "approval_status":fields.String    
}

items={
    "id":fields.Integer,
    "name":fields.String,
    "unit":fields.String,
    "price":fields.Integer,
    "best_before":fields.String,
    "unit":fields.String,
    "approval_status":fields.String, 
    "category_name":fields.String    
}

#template for stores selling a particular item
stores={
    "id":fields.Integer,
    "store_id":fields.Integer,
    "item_id":fields.Integer,
    "quantity_remaining":fields.Integer,
    "store_name":fields.String  
}


class StoresWaitingAPI (Resource):
    @marshal_with(stores_waiting_approval)
    def get(self):
          stores = db.session.query(Store).filter_by(approval_status=0).all()
          if stores:
            return stores
          else:
            raise NotFoundError(status_code=404)

class CategoriesWaitingAPI (Resource):
    @marshal_with(categories)
    def get(self):
          categories = db.session.query(Category).filter_by(approval_status=0).all()
          if categories:
            return categories
          else:
            raise NotFoundError(status_code=404)

class ItemsWaitingAPI (Resource):
    @marshal_with(items)
    def get(self):
          items = db.session.query(Item).filter_by(approval_status=0).all()
          if items:
            for i in range (len(items)):
                items[i].category_name=items[i].category.name
            return items
          else:
            raise NotFoundError(status_code=404)
                        
class CategoriesAPI (Resource):
    @marshal_with(categories)
    def get(self):
          categories = db.session.query(Category).filter_by(approval_status=1).all()
          if categories:
            return categories
          else:
            raise NotFoundError(status_code=404)

class CategoriesAPI (Resource):
    @marshal_with(categories)
    def get(self):
          categories = db.session.query(Category).filter_by(approval_status=1).all()
          if categories:
            return categories
          else:
            raise NotFoundError(status_code=404)

class ItemsAPI (Resource):
    @marshal_with(items)
    def get(self):
          items = db.session.query(Item).filter_by(approval_status=1).all()
          if items:
            for i in range (len(items)):
                items[i].category_name=items[i].category.name
                print (type(items[i]))
            return items
          else:
            raise NotFoundError(status_code=404)
          
#used to return list of stores which are selling a particular item
class StoresAPI (Resource):
    @marshal_with(stores)
    def get(self, item_id):
        #All Stores, will be used to find store name from store_id in the next step
        all_stores = db.session.query(Store).all()

        #stores selling a particular item
        stores = db.session.query(Store_Item).filter_by(item_id=item_id).all()
        for i in range(len(stores)):
          for j in range(len(all_stores)):
            if (all_stores[j].id==stores[i].store_id):
              stores[i].store_name=all_stores[j].name
              break
        return stores
    
class DelCategoriesWaitingAPI (Resource):
  @marshal_with(categories)
  def get(self):
    result = []
    del_categories = db.session.query(DeleteRequests).filter(DeleteRequests.class_=="category").all()
    for category in del_categories:
      category_to_del = db.session.query(Category).filter_by(id=category.class_id).first()
      result.append(category_to_del)
    return result  

class DelItemsWaitingAPI (Resource):
  @marshal_with(items)
  def get(self):
    result = []
    del_items = db.session.query(DeleteRequests).filter(DeleteRequests.class_=="item").all()
    for item in del_items:
      item_to_del = db.session.query(Item).filter_by(id=item.class_id).first()
      item_to_del.category_name=item_to_del.category.name
      result.append(item_to_del)
    return result          