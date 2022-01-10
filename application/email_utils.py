import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_email(from_email, from_password, to_email, subject, body):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    html = MIMEText(body, 'html')
    msg.attach(html)
    server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server_ssl.ehlo()
    server_ssl.login(from_email, from_password)
    server_ssl.sendmail(from_email, to_email, msg.as_string())
    server_ssl.close()
