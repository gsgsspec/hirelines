import os
import base64
from hirelines.metadata import getConfig
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import encoders
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def sendRegistrainMail(mail_data):
    
    try:

        root_path  = getConfig()['DIR']['root_path']
        email_config = getConfig()['SEND_EMAIL_CONFIG']
        creds = f"{root_path}{email_config['creds']}"
        token =  f"{root_path}{email_config['token']}"
        template_file_path =  root_path + "/app_api/functions/email_templates/registration.html"
        

        with open(template_file_path, 'r') as template_file:
            email_template = template_file.read()

        email_body =  (email_template.replace('[user_name]',mail_data['name'])
                      .replace('[user_email]',mail_data['email'])
                      .replace('[user_password]',mail_data['password'])
                      .replace('[login_url]',mail_data['url'])
                    )

        creds = None

        if os.path.exists(token):
            creds = Credentials.from_authorized_user_file(token, SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    cred, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(token, 'w') as token:
                token.write(creds.to_json())
                
        service = build('gmail', 'v1', credentials=creds)

        message = MIMEMultipart("mixed")
        message['To'] = mail_data['email']
        message['From'] = f"Hirelines <{email_config['sender']}>"
        message['Subject'] = "Welcome to Hirelines! Your Account Details"
        emailbody = MIMEText(email_body, "html")
        message.attach(emailbody)

        eml_atch = MIMEText('', 'plain')
        encoders.encode_base64(eml_atch)
        eml_atch.add_header('Content-Transfer-Encoding', "")

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_draft_request_body = {
            'raw': encoded_message
        }
        
        service.users().messages().send(userId="me",body=create_draft_request_body).execute()

    except Exception as e:
        raise