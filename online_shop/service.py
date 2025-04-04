import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import threading

from_email = 'shobushomurotov@gmail.com'

def send_email(to_email, sunject, body):
    email_message = MIMEMultipart()
    email_message['From'] = from_email
    email_message['To'] = to_email
    email_message['Subject'] = 'Important thing'
    email_message.attach(MIMEText('bu yerda sizning reklamangiz bolishi mumkin edi', 'plain'))

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

    server.login(from_email, 'nrjs hwdb kljn oacf')
    try:
        server.sendmail(from_email, to_email, email_message.as_string())
        server.quit()
        print('Email sent!')
    except Exception as e:
        print(f'An error occurred while sending: {str(e)}')

def send_email_async(to_email, subject, body):
    t = threading.Thread(target=send_email, args=(to_email, subject, body))
    t.start()

users = [
    'shomurotov.sh.123@gmail.com'
]


def send_email_to_users():
    for user in users:
        send_email_async(user, "Mahsulotlar buyurtmasi", "Sizning buyurtmangiz qabul qilindi! endi 1 hafta kutsez boldi 😂")


t1 = threading.Thread(target=send_email_to_users)
t1.start()