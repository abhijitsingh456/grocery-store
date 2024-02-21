from workers import celery
from datetime import date
from celery.schedules import crontab
from model import db
from model import *
from sqlalchemy import and_
from flask import jsonify
from send_email import send_daily_mail
from send_email import send_monthly_report
from datetime import datetime
import csv
from flask import send_file
'''
@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(10.0,print_current_time_job.s(), name='at every 10') #include crontab here, look at the examples

@celery.task()
def print_current_time_job():
    print ("START")
    now = datetime.now()
    print ("now in task=", now)
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    print ("date and time", dt_string)
    print ("COMPLETE")
    return dt_string
'''

@celery.on_after_finalize.connect
def setup_periodic_tasks(sender, **kwargs): 
        sender.add_periodic_task(60.0,daily_mail.s(), name='at every 10') #for testing
        #sender.add_periodic_task(crontab(hour=15, minute=30),daily_mail.s())
        #sender.add_periodic_task(crontab(0, 0, day_of_month='1'),monthly_mail.s())

@celery.task()
def daily_mail():
    purchases = db.session.query(Purchase).all()
    user_ids = [] #list of user ids who have made a purhcase today, no need to send email
    for purchase in purchases:
        if (purchase.purchase_time.partition(" ")[0]==str(date.today())):
            user_ids.append(purchase.user_id)
    users = db.session.query(User).filter(and_(User.id.not_in(user_ids), User.roles.any(name="user"))) #list of user ids who have not made a purhcase today,send email
    print (users)
    for user in users:   
        send_daily_mail(user.__dict__)

@celery.task()
def monthly_mail():
    user_email = {}
    #user_email = {"user_id_1":{username:"",email:""},
    #               "user_id_2":{username:"", email:""}}
    users = db.session.query(User).all()
    for user in users:
        user_email[user.id] = {"username":user.username, "email":user.email}
    
    purchase_dict = {}    
    #purchase_dict= {"user_id_1":[{purchase_1},{purchase_2}],
    #                "user_id_2":[{purchase_1}, {purchase_2}]}
    purchases = db.session.query(Purchase).all()
    for purchase in purchases:
        if ((datetime.strptime(purchase.purchase_time, "%Y-%m-%d %H:%M:%S.%f").date() < datetime.today().date())):               
            purchase.username = user_email[purchase.user_id]["username"]
            purchase.email = user_email[purchase.user_id]["email"]
            try:
                purchase_dict[purchase.user_id].append(purchase.__dict__)
            except:
                purchase_dict[purchase.user_id] = [purchase.__dict__]
        else:
            pass

    #{10: [{'_sa_instance_state': <sqlalchemy.orm.state.InstanceState object at 0x7f453448de40>, 'store_name': 'Fresh Stores', 'id': 5, 'total_amount': 170, 'item_name': 'Potoato', 'quantity': 10, 'user_id': 10, 'purchase_time': '2023-12-01 03:02:06.275811', 'username': 'nitesh', 'email': 'nitesh@yahoo.in'}]}
    
    for user_id,purchases in purchase_dict.items():
       email = purchase_dict[user_id][0]["email"]
       username = purchase_dict[user_id][0]["username"]
       send_monthly_report(username,email,purchases)

@celery.task()
def generate_store_reports(store_id):
    query_inventory = db.session.query(Store_Item).filter(Store_Item.store_id==store_id)
    inventory = [] 
    for item_in_inventory in query_inventory:
        item = db.session.query(Item).filter(Item.id==item_in_inventory.item_id).first()
        item_in_inventory.name = item.name
        item_in_inventory.unit = item.unit
        item_in_inventory.price = item.price
        item_in_inventory.best_before = item.best_before
        inventory.append(item_in_inventory.__dict__)


    with open('inventory_report.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["Name", "Unit", "Price", "Best Before", "Quantity Remaining"]
        writer.writerow(field)
        for item_in_inventory in inventory:
            writer.writerow([item_in_inventory["name"], item_in_inventory["unit"], item_in_inventory["price"],\
                             item_in_inventory["best_before"], item_in_inventory["quantity_remaining"]])        
        
        '''with open('inventory_report.csv', mode ='r')as file:
            csvFile = csv.reader(file)
            for lines in csvFile:
                print(lines)'''
