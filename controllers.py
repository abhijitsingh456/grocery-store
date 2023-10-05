from model import db
from model import *
from flask import render_template, url_for,redirect, flash
from flask import request
from flask import current_app as app
from sqlalchemy import exc, func
from sqlalchemy.sql import text
from datetime import datetime
from datetime import date
from flask_security import login_required, roles_accepted
import uuid


@app.route('/',methods=["GET","POST"])
def index():
	if request.method=="GET":
		#categories=db.session.query(Category)
		return render_template("homepage.html")
	if request.method=="POST":
		search_query=request.form["search_query"]
		user=db.session.query(User).filter_by(username=username).first()
		shows=[]
		shows_=db.session.query(Show).order_by(Show.updated_on.desc())
		for show in shows_:
			if (search_query.upper() in show.name.upper()) or (search_query.upper() in show.venue.upper()) or (search_query.upper() in show.tag.upper()) or (search_query.upper() in show.date.upper()):
				shows.append(show)
		if len(shows)==0:
			error="No search results found"
			return render_template("search_results.html",user=user, error=error)		
		else:
			return render_template('search_results.html',user=user, shows=shows)
