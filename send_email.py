import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from email.mime.base import MIMEBase
from email import encoders

SMTP_SERVER_HOST = "localhost"
SMTP_SERVER_PORT = 1025
SENDER_ADDRESS = "example@eg.in"
SENDER_PASSWORD = ""

def send_mail(to_address, message, subject, content="text", attachment_file=None):
    msg = MIMEMultipart()
    msg["From"]=SENDER_ADDRESS
    msg["To"]=to_address
    msg["Subject"]=subject

    if (content=="html"):
        msg.attach(MIMEText(message,"html"))
    else:
        msg.attach(MIMEText(message,"plain"))
    

    if attachment_file:
        with open(attachment_file, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition", f"attachment; filename={attachment_file}",
        )
        msg.attach(part)

    s = smtplib.SMTP(host=SMTP_SERVER_HOST, port = SMTP_SERVER_PORT)
    s.login(SENDER_ADDRESS, SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    
    return True

def format_message(template_file, username=None, data={}):
    with open(template_file) as file_:
        template = Template(file_.read())
        message = template.render(username=username, data=data)
        return message   

def send_daily_mail(data):
    message = format_message("./templates/email_msg.html",data=data)
    send_mail(data["email"],subject="Hello",message=message, content="html") 

def send_monthly_report(username,email,purchases):
    monthly_message = format_message("./templates/monthly_report.html",username=username,data=purchases)
    send_mail(email,subject="Monthly Report",message=monthly_message, content='html')


def main():
    new_users = [
        {"name":"Abhijit", "email":"abhi@gmail.com"},
        {"name":"Abhishek","email":"abhishek@gmail.com"}
    ]
    for user in new_users:
        #Task in Celery
        send_daily_mail(user)


if __name__ == "__main__":
    main()
