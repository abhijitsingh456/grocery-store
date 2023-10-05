from model import db
from model import *
from flask import render_template, url_for,redirect, flash
from flask import request
from flask import current_app as app
from datetime import datetime
from datetime import date
from flask_security import login_required, roles_accepted



@app.route('/',methods=["GET","POST"])
def index():
	if request.method=="GET":
		#categories=db.session.query(Category)
		return render_template("homepage.html")
