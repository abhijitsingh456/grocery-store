from model import db
from model import *
from flask import render_template, url_for,redirect, flash, jsonify
from flask import request
from flask import current_app as app
from datetime import datetime
from datetime import date
from flask_security import login_required, roles_accepted, login_user
from app import user_datastore
from flask_security import hash_password
from flask_wtf import FlaskForm
from wtforms import (StringField, PasswordField, SubmitField,              
                     BooleanField)
from wtforms.validators import DataRequired, Length, Email, EqualTo
from flask_login import current_user
from sqlalchemy import and_, exc
from flask import send_file
import os
import tasks
from app import cache

ALLOWED_EXTENSIONS = {'jpg','jpeg'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class RegistrationForm(FlaskForm):
	username = StringField('Username',validators=[DataRequired(),Length(min=4, max=20)])
	email = StringField('Email',validators=[DataRequired(),Email()])
	password = PasswordField('Password',validators=[DataRequired()])
	confirm_password = PasswordField('Confirm Password',validators=[DataRequired(),EqualTo('password')])
	submit = SubmitField('Sign Up')

'''
#for testing celery
@app.route("/hello",methods=["GET","POST"])
def hello():
	now = datetime.now()
	print ("now in flask=", now)
	dt_string = now.strftime("%d/%m/%Y %H:%M:%S")	
	print ("date and time", dt_string)
	job = tasks.print_current_time_job.apply_async(eta=now + timedelta(seconds=10))
	result = job.wait()
	return str(result),200
'''

@app.route("/store_reports/<store_id>",methods=["GET","POST"])
def store_reports(store_id):
	job = tasks.generate_store_reports.apply_async(args=(store_id,))
	result = job.wait()
	return send_file("inventory_report.csv")

@app.route('/',methods=["GET","POST"])
def index():
	if request.method=="GET":
		#categories=db.session.query(Category)
		if (current_user.roles==["manager"]):
			return redirect(url_for("manager_homepage"))
		if (current_user.roles==["admin"]):
			return redirect(url_for("admin_homepage"))
		return render_template("homepage.html")

@app.route('/register_manager',methods=["GET","POST"])
def register_manager():
	if request.method=="GET":
		return render_template("./security/register_manager.html", register_form = RegistrationForm())
	if request.method=="POST":
		username=request.form["username"]
		email=request.form["email"]
		password=request.form["password"]
		manager = user_datastore.create_user(username=username, email=email,password=hash_password(password), roles=['manager'])
		db.session.commit()
		login_user(manager)
		return redirect(url_for("enter_store_details"))


@app.route('/enter_store_details',methods=["GET","POST"])
@roles_accepted('manager')
def enter_store_details():
	if request.method=="GET":
		#checking if a store exists for the currently logged in manager
		store_mgr=db.session.query(store_managers).filter_by(user_id=current_user.id).first()
		#if Yes, checking if his store has been approved by the admin 
		if store_mgr:
			store = db.session.query(Store).filter_by(id=store_mgr.store_id).first()
			if (store.approval_status==1):
				return redirect(url_for("manager_homepage"))
			else:
				return render_template("store_waiting_approval.html")
		else:
			return render_template("enter_store_details.html")
	if request.method=="POST":
		username = request.form["username"]
		store_name = request.form["store_name"]
		store_address= request.form["store_address"]
		user=db.session.query(User).filter_by(username=username).first()
		new_store = Store(name=store_name, address=store_address, manager=user,approval_status=0)
		try:
			db.session.add(new_store)
			db.session.commit()
		except exc.IntegrityError:
			db.session.rollback()
			error='Store Name already exists! Please try a different name.'
			return render_template("enter_store_details.html",error=error)
		return render_template("store_waiting_approval.html")


@app.route('/manager_homepage',methods=["GET","POST"])
@cache.cached(timeout=50)
@roles_accepted('manager')
def manager_homepage():
	if request.method=="GET":
		#checking if a store exists for the currently logged in manager
		store_mgr=db.session.query(store_managers).filter_by(user_id=current_user.id).first()
		#if Yes, checking if his store has been approved by the admin 
		if store_mgr:
			store = db.session.query(Store).filter_by(id=store_mgr.store_id).first()
			if (store.approval_status==1):
				return render_template("manager_homepage.html", store_id=store_mgr.store_id)
			else:
				return render_template("store_waiting_approval.html")
		else:	#if store doesn't exists, enter a store
			return redirect(url_for("enter_store_details"))


@app.route('/add_new_category',methods=["POST"])
@roles_accepted('manager')
def add_new_category():
	if request.method=="POST":
		category_name = request.form["category_name"]
		try:	
			new_category = Category(name=category_name, approval_status=0)
			db.session.add(new_category)
			db.session.commit()
		except exc.IntegrityError:
			db.session.rollback()
			error='Category Name already exists! Please try a different name.'
			return render_template("manager_homepage.html",error=error)
		return redirect(url_for("manager_homepage"))	

@app.route('/add_new_item',methods=["POST"])
@roles_accepted('manager')
def add_new_item():
	if request.method=="POST":
		category_name = request.form["category_name"]
		item_name = request.form["item_name"]
		item_unit = request.form["item_unit"]
		unit_price = request.form["unit_price"]
		best_before = request.form["best_before"]
		item_image = request.files['item_image']
		'''
		if 'item_image' not in request.files:
			flash('No file part','error')
			return redirect(url_for("manager_homepage"))
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
		if item_image.filename == '':
			flash('No selected file','error')
			return redirect(url_for("manager_homepage"))
		'''
		category=db.session.query(Category).filter_by(name=category_name).first()
		try:
			new_item = Item(name=item_name, unit=item_unit, price=unit_price, best_before=best_before, category=category,approval_status=0)
			db.session.add(new_item)
			db.session.commit()			
			if item_image and allowed_file(item_image.filename):
				item_image.save(os.path.join(app.config['UPLOAD_FOLDER']+'/item_images', item_name + '.jpg'))
		except exc.IntegrityError:
			db.session.rollback()
			error='Item Name already exists! Please try a different name.'
			return render_template("manager_homepage.html",error=error)
		return redirect(url_for("manager_homepage"))


@app.route('/admin_homepage',methods=["GET","POST"])
@cache.cached(timeout=50)
@roles_accepted('admin')
def admin_homepage():
	if request.method=="GET":
		return(render_template("admin_homepage.html"))

@app.route("/stores_waiting/change_status/<store_id>",methods=["GET"])
@roles_accepted('admin')
def change_store_status(store_id):
	if request.method=="GET":
		try:
			db.session.query(Store).filter(Store.id==int(store_id)).update({'approval_status':1})
			db.session.commit()
			return redirect(url_for("admin_homepage"))
		except:
			return redirect(url_for("admin_homepage"))

@app.route("/categories_waiting/change_status/<category_id>",methods=["GET"])
@roles_accepted('admin')
def change_category_status(category_id):
	if request.method=="GET":
		try:
			db.session.query(Category).filter(Category.id==int(category_id)).update({'approval_status':1})
			db.session.commit()
			return redirect(url_for("admin_homepage"))
		except:
			return redirect(url_for("admin_homepage"))

@app.route("/items_waiting/change_status/<item_id>",methods=["GET"])
@roles_accepted('admin')
def change_item_status(item_id):
	if request.method=="GET":
		try:
			db.session.query(Item).filter(Item.id==int(item_id)).update({'approval_status':1})
			db.session.commit()
			return redirect(url_for("admin_homepage"))
		except:
			return redirect(url_for("admin_homepage"))

@app.route("/add_to_store",methods=["POST"])
@roles_accepted('manager')
def add_to_store():
	if request.method=="POST":
		item_name = request.form["item_name"]
		#to find the store to add the item to, first finding the manager who's logged in so that we then find which store he's linked to
		store_mgr=db.session.query(store_managers).filter_by(user_id=current_user.id).first()	
		item = db.session.query(Item).filter_by(name=item_name).first()
		quantity_remaining = request.form["quantity_remaining"]
		temp = db.session.query(Store_Item).filter(Store_Item.store_id==store_mgr.store_id,Store_Item.item_id==item.id).first()
		if temp:
			old_quantity_rem = temp.quantity_remaining
			db.session.query(Store_Item).filter(Store_Item.store_id==store_mgr.store_id,Store_Item.item_id==item.id).update({'quantity_remaining':int(old_quantity_rem)+int(quantity_remaining)})
		else:
			store_item = Store_Item(store_id=store_mgr.store_id, item_id=item.id, quantity_remaining=quantity_remaining)
			db.session.add(store_item)
		db.session.commit()
		return redirect(url_for("manager_homepage"))
	
@app.route("/checkout",methods=["POST"])
@roles_accepted('user')
def checkout():
	if request.method=="POST":
		purchases = request.get_json()
		'''purchases=[{'user_id': 9, 'item_name': 'Potoato', 'store_name': 'Fresh Stores', 'quantity': '4', 'total_amount': 68}, 
   			{'user_id': 9, 'item_name': 'Apple', 'store_name': 'Fresh Stores', 'quantity': '5', 'total_amount': 750}]'''
		current_datetime = str(datetime.now())
		for purchase in purchases:
			item=db.session.query(Item).filter_by(name=purchase['item_name']).first()
			store=db.session.query(Store).filter_by(name=purchase['store_name']).first()

			old_quantity_rem = int(db.session.query(Store_Item).filter(Store_Item.store_id==store.id,Store_Item.item_id==item.id).first().quantity_remaining)
			if (old_quantity_rem-int((purchase['quantity']))<0):
				continue
			else:
				db.session.query(Store_Item).filter(Store_Item.store_id==store.id,Store_Item.item_id==item.id).update({'quantity_remaining':int(old_quantity_rem)-int(purchase['quantity'])})

				new_purchase = Purchase(user_id=purchase['user_id'],item_name=purchase['item_name'], store_name=purchase['store_name'],\
							quantity=purchase['quantity'], total_amount=purchase['total_amount'], purchase_time=current_datetime)
				db.session.add(new_purchase)
				db.session.commit()
		return redirect(url_for("index"))

@app.route('/edit_category',methods=["POST"])
@roles_accepted('manager')
def edit_category():
	if request.method=="POST":
		old_category_name = request.form["old_category_name"]
		new_category_name = request.form["new_category_name"]
		try:
			db.session.query(Category).filter(Category.name==old_category_name).update({'name':new_category_name})
			db.session.commit()
		except exc.IntegrityError:
			db.session.rollback()
			error='Category Name already exists! Please try a different name.'
			return render_template("manager_homepage.html",error=error)
		return redirect(url_for("manager_homepage"))

@app.route('/edit_item',methods=["POST"])
@roles_accepted('manager')
def edit_item():
		category_name = request.form["category_name"]
		old_item_name = request.form["old_item_name"]
		new_item_name = request.form["new_item_name"]
		item_unit = request.form["item_unit"]
		unit_price = request.form["unit_price"]
		best_before = request.form["best_before"]
		try:
			db.session.query(Item).filter(Item.name==old_item_name).update({'name':new_item_name,'unit':item_unit, 'price':unit_price, 'best_before':best_before})
			db.session.commit()
			try:
				os.rename(app.config['UPLOAD_FOLDER']+'/item_images/' + old_item_name + '.jpg',app.config['UPLOAD_FOLDER']+'/item_images/' + new_item_name + '.jpg')
			except:
				pass #for the condition when there's no image for the item
		except exc.IntegrityError:
			db.session.rollback()
			error='Item Name already exists! Please try a different name.'
			return render_template("manager_homepage.html",error=error)
		return redirect(url_for("manager_homepage")) 

@app.route('/delete_cat_request/<cat_name>')
@roles_accepted('manager')
def del_req_cat(cat_name):
	category = db.session.query(Category).filter(Category.name==cat_name).first()
	#checking if there's already a request made to delete this category
	del_request = db.session.query(DeleteRequests).filter(DeleteRequests.class_=="category",DeleteRequests.class_id==category.id).first()
	if (del_request):
		return (redirect(url_for("manager_homepage")))
	else:
		new_cat_del_request = DeleteRequests(class_="category",class_id=category.id)
		db.session.add(new_cat_del_request)
		db.session.commit()
		return (redirect(url_for("manager_homepage")))

@app.route('/delete_item_request/<item_name>')
@roles_accepted('manager')
def del_req_item(item_name):
	item = db.session.query(Item).filter(Item.name==item_name).first()
	#checking if there's already a request made to delete this item
	del_request = db.session.query(DeleteRequests).filter(DeleteRequests.class_=="item",DeleteRequests.class_id==item.id).first()
	if (del_request):
		return (redirect(url_for("manager_homepage")))
	else:
		new_item_del_request = DeleteRequests(class_="item",class_id=item.id)
		db.session.add(new_item_del_request)
		db.session.commit()
		return (redirect(url_for("manager_homepage")))

@app.route("/del_categories_waiting/<category_id>",methods=["GET"])
@roles_accepted('admin')
def del_category(category_id):
	if request.method=="GET":
		items_to_del = db.session.query(Item).filter(Item.category.has(id=int(category_id))).all()
		#patients = Patient.query.filter(Patient.mother.has(phenoscore=10))
		item_ids_to_del = []
		for item in items_to_del:
			item_ids_to_del.append(item.id)
		db.session.query(Store_Item).filter(Store_Item.item_id.in_(item_ids_to_del)).delete()
		db.session.query(Item).filter(Item.id.in_(item_ids_to_del)).delete()
		db.session.query(Category).filter(Category.id==int(category_id)).delete()
		db.session.query(DeleteRequests).filter(DeleteRequests.class_=="category",DeleteRequests.class_id==int(category_id)).delete()
		db.session.commit()
		return redirect(url_for("admin_homepage"))

@app.route("/del_items_waiting/<item_id>",methods=["GET"])
@roles_accepted('admin')
def del_items(item_id):
	if request.method=="GET":
		item = db.session.query(Item).filter(Item.id==int(item_id)).first()
		db.session.query(Store_Item).filter(Store_Item.item_id==int(item_id)).delete()
		db.session.query(Item).filter(Item.id==int(item_id)).delete()
		db.session.query(DeleteRequests).filter(DeleteRequests.class_=="item",DeleteRequests.class_id==int(item_id)).delete()
		db.session.commit()
		os.remove(app.config['UPLOAD_FOLDER']+'/item_images/' + item.name + '.jpg')
		return redirect(url_for("admin_homepage"))

@app.route("/my_purchases",methods=["GET"])
@roles_accepted('user')
def my_purchases():
	purchases = db.session.query(Purchase).filter(Purchase.user_id==current_user.id).all()
	return render_template("my_purchases.html",purchases=purchases)