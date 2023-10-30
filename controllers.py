from model import db
from model import *
from flask import render_template, url_for,redirect, flash
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
import os

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
		db.session.add(new_store)
		db.session.commit()
		return render_template("store_waiting_approval.html")


@app.route('/manager_homepage',methods=["GET","POST"])
@roles_accepted('manager')
def manager_homepage():
	if request.method=="GET":
		#checking if a store exists for the currently logged in manager
		store_mgr=db.session.query(store_managers).filter_by(user_id=current_user.id).first()
		#if Yes, checking if his store has been approved by the admin 
		if store_mgr:
			store = db.session.query(Store).filter_by(id=store_mgr.store_id).first()
			if (store.approval_status==1):
				return render_template("manager_homepage.html")
			else:
				return render_template("store_waiting_approval.html")
		else:	#if store doesn't exists, enter a store
			return redirect(url_for("enter_store_details"))


@app.route('/add_new_category',methods=["POST"])
@roles_accepted('manager')
def add_new_category():
	if request.method=="POST":
		category_name = request.form["category_name"]	
		new_category = Category(name=category_name, approval_status=0)
		db.session.add(new_category)
		db.session.commit()
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
		if 'item_image' not in request.files:
			flash('No file part','error')
			return redirect(request.url)
		item_image = request.files['item_image']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
		if item_image.filename == '':
			flash('No selected file','error')
			return redirect(request.url)
		if item_image and allowed_file(item_image.filename):
			item_image.save(os.path.join(app.config['UPLOAD_FOLDER']+'/item_images', item_name + '.jpg'))
		category=db.session.query(Category).filter_by(name=category_name).first()
		new_item = Item(name=item_name, unit=item_unit, price=unit_price, best_before=best_before, category=category,approval_status=0)
		db.session.add(new_item)
		db.session.commit()
		return redirect(url_for("manager_homepage"))


@app.route('/admin_homepage',methods=["GET","POST"])
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
		store_item = Store_Item(store_id=store_mgr.store_id, item_id=item.id)
		db.session.add(store_item)
		db.session.commit()
		return redirect(url_for("manager_homepage"))
