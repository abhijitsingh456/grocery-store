from flask import Flask
from model import *
from flask_restful import Resource, Api
import os
from flask_cors import CORS
from flask_security import Security, SQLAlchemySessionUserDatastore, SQLAlchemyUserDatastore
from  workers import *
import workers
import flask_babel
from flask_security import user_registered
from flask_caching import Cache

api = None
app = Flask(__name__)
CORS(app)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(current_dir, "database.sqlite3")
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_PASSWORD_SALT'] = 'dfs5dfs7fsd87f7s9d7fs7ff7s8'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False
app.config['SECURITY_USERNAME_ENABLE']=True
app.config['UPLOAD_FOLDER'] = './static/uploads'
app.config["CELERY_BROKER_URL"] = "redis://localhost:6379/1"
app.config["CELERY_RESULT_BACKEND"] = "redis://localhost:6379/2"
app.config["REDIS_URL"] = "redis://localhost:6379"
app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_HOST"] = "localhost"
app.config["CACHE_REDIS_PORT"] = 6379
SECRET_KEY = "d4g5d4g54t54njuj7msdnj8m"
SECURITY_PASSWORD_HASH = "bcrypt"


db.init_app(app)
api = Api(app)

celery=workers.celery
celery.conf.update(
    broker_url = app.config["CELERY_BROKER_URL"],
    result_backend = app.config["CELERY_RESULT_BACKEND"]
)
celery.Task = workers.ContextTask 

cache=Cache(app)

with app.app_context():
    db.create_all()
    
app.app_context().push()
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)

user=db.session.query(User).filter_by(username='admin').first()
if user:
   pass
else:
   user_datastore.create_role(name='admin')
   user_datastore.create_role(name='manager')
   user_datastore.create_role(name='user')
   user_datastore.create_user(username='admin', email='admin@example.com',password='admin', roles=['admin'])
   db.session.commit()


security = Security(app, user_datastore)


flask_babel.Babel(app)


@user_registered.connect_via(app)
def user_registered_sighandler(app, user, confirm_token, confirmation_token, form_data):
    default_role = user_datastore.find_role("user")
    user_datastore.add_role_to_user(user, default_role)
    db.session.commit()

from controllers import *
from api import *

api.add_resource(StoresWaitingAPI, "/api/stores_waiting")
api.add_resource(CategoriesWaitingAPI, "/api/categories_waiting")
api.add_resource(ItemsWaitingAPI, "/api/items_waiting")

api.add_resource(CategoriesAPI, "/api/categories")
api.add_resource(ItemsAPI, "/api/items")

#used to return list of stores which are selling a particular item
api.add_resource(StoresAPI, "/api/stores/<item_id>")

api.add_resource(DelCategoriesWaitingAPI, "/api/del_categories_waiting")
api.add_resource(DelItemsWaitingAPI, "/api/del_items_waiting")

if __name__ == '__main__':
    app.run(port=8080)
    