import imaplib
import email
import yaml


# Load credentials from a YAML file
with open("credentials.yml") as f:
    my_credentials = yaml.load(f, Loader=yaml.FullLoader)

# Extract username and password
user, password = my_credentials["user"], my_credentials["password"]

# IMAP server URL
imap_url = 'imap.gmail.com'

# Connect to the IMAP server using SSL
my_mail = imaplib.IMAP4_SSL(imap_url)

# Log in to the email account
my_mail.login(user, password)

# Select the 'Inbox' folder
my_mail.select('Inbox')

# Search criteria: looking for emails from a specific sender
key = 'FROM'
value = 'seunbisi99@gmail.com'
_, data = my_mail.search(None, key, value)

# Get list of email IDs
mail_id_list = data[0].split()

# Fetch only the last email ID
last_email_id = mail_id_list[-1] if mail_id_list else None

if last_email_id:
    # Fetch the last email
    _, data = my_mail.fetch(last_email_id, '(RFC822)')
    my_msg = email.message_from_bytes(data[0][1])

    # Extract email body
    body = ""
    for part in my_msg.walk():
        if part.get_content_type() == 'text/plain':
            body = part.get_payload()
            break

    # Generate a timestamped filename
    filename = "NEW_CEO.txt"

    # Write the body to a text file
    with open(filename, "w") as file:
        file.write(body)
    print(f"Email body written to {filename}")
else:
    print("No emails found from the specified sender.")
