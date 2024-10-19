import os
import base64
import re
import pytz
import mimetypes
from django.utils import timezone
from hirelines.metadata import getConfig
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from app_api.models import Branding, Company, Email_template


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



def sendEmail(company,paper_type,participant_paper_id,event,replacements,to_email,calender_details=None):
    # try:
        CRLF = "\r\n"
        root_path  = getConfig()['DIR']['root_path']
        email_config = getConfig()['SEND_EMAIL_CONFIG']
        creds_path = f"{root_path}{email_config['creds']}"
        token = f"{root_path}{email_config['token']}"

        creds = None

        if os.path.exists(token):
            creds = Credentials.from_authorized_user_file(token, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
                creds = flow.run_local_server(port=0)
            with open(token, 'w') as token1:
                token1.write(creds.to_json())

        service = build('gmail', 'v1', credentials=creds)

        brand = Branding.objects.filter(companyid=company).last()
        company_obj = Company.objects.get(id=company)

        if brand:
            brand = brand
        
        else:
            brand = Branding.objects.get(companyid=0)

        email_template = ''
        
        check = Email_template.objects.filter(event=event, company_id=company,paper_type=paper_type)
    
        if check:
          
            # paperwise_temp = PaperWiseEmailTemp.objects.filter(event=event, company_id=company,paperid=participant_paper_id).last()
            # if paperwise_temp:
            #     email_template = paperwise_temp
            
            # else:
            email_template = Email_template.objects.get(event=event, company_id=company,paper_type=paper_type)


        sender_label  = email_template.sender_label if email_template.sender_label else company_obj.company_name

        if event == "Call_Schedule":
            email_list = [email.strip() for email in to_email.split(",")]
            to_email = email_list[0]
            cc_recipients = ', '.join(email_list[1:])
        else:
            to_email = to_email

        # sender_email = email_config['sender']
        # media_config = getConfig()['MEDIA']
        # media_path = media_config['media_path']
        receiver_email = to_email
        message = MIMEMultipart("mixed")
        message["Subject"] = email_template.email_subject if email_template else ''
        message["From"] = f"{sender_label} "
        message["To"] = receiver_email

        if event == "Call_Schedule":
            message["Cc"] = cc_recipients

        email_body = email_template.email_body if email_template else ''
        template_heading = email_template.template_heading if email_template else ''

        company = Company.objects.filter(id=company).last()

        if replacements:
            for placeholder, value in replacements.items():
                email_body = email_body.replace(placeholder, value)

        css = brand.content if brand else ""
        match = re.search(r'--brand-primary-color:\s*(.*?);', css)
        brand_primary_color = match.group(1) if match else None
        social_link = brand.sociallinks if brand.sociallinks else ""
        social_links = {}
        social_links_pattern = re.compile(r'(Linkedin|Facebook|Youtube|Twitter)\s*:\s*(.*?)(?:,|$)')
        
        for match in social_links_pattern.finditer(social_link):
            platform, url = match.groups()
            social_links[platform] = url.strip() 
        
        company_website = company_obj.website if company_obj.website else ''    

        email_body= (email_body
                     .replace("[clr_primary]",brand_primary_color)
                     .replace("[logo]",str(brand.logourl) if brand.logourl else "")
                     .replace("[heading]",template_heading)
                     .replace("[company_website]",company_website)
                     .replace("[Linkedin]",social_links.get('Linkedin') if social_links.get('Linkedin') else "#")
                     .replace("[Facebook]",social_links.get('Facebook') if social_links.get('Facebook') else "#")
                     .replace("[Youtube]",social_links.get('Youtube') if social_links.get('Youtube') else "#")
                     .replace("[Twitter]",social_links.get('Twitter') if social_links.get('Twitter') else "#")
                     )

        html_content = f"""
            {email_body}
        """

        emailbody = MIMEText(html_content, "html")
        message.attach(emailbody)

        if calender_details is not None:
            
            cal_time = calender_details
            cal_time = cal_time.astimezone(pytz.timezone('Asia/Kolkata'))
            examdtstart = cal_time.replace(tzinfo=pytz.timezone('Asia/Kolkata'))
            
            dur = timezone.timedelta(minutes=30)
            examdtend = (cal_time + dur).replace(tzinfo=pytz.timezone('Asia/Kolkata'))
            dtstamp = timezone.now().strftime("%Y%m%dT%H%M%S")
            dtstart = examdtstart.strftime("%Y%m%dT%H%M%S")
            dtend = examdtend.strftime("%Y%m%dT%H%M%S")
            description = "DESCRIPTION: exam invitation" + CRLF

            organizer = "ORGANIZER;CN=Swarabharathi:mailto:first" + CRLF + " @gmail.com"
            attendee = "ATTENDEE;CUTYPE=INDIVIDUAL;ROLE=REQ-PARTICIPANT;PARTSTAT=ACCEPTED;RSVP=TRUE" + CRLF + " ;CN=" + receiver_email + " mailto:" + receiver_email + CRLF
            ical = "BEGIN:VCALENDAR" + CRLF + "PRODID:pyICSParser" + CRLF + "VERSION:2.0" + CRLF + "CALSCALE:GREGORIAN" + CRLF

             # Add the VTIMEZONE
            ical += "BEGIN:VTIMEZONE" + CRLF + "TZID:Asia/Kolkata" + CRLF
            ical += "BEGIN:STANDARD" + CRLF + "DTSTART:19700101T000000" + CRLF + "TZOFFSETFROM:+0530" + CRLF + "TZOFFSETTO:+0530" + CRLF + "TZNAME:IST" + CRLF + "END:STANDARD" + CRLF + "END:VTIMEZONE" + CRLF

            ical += "METHOD:REQUEST" + CRLF + "BEGIN:VEVENT" + CRLF + "DTSTART:" + dtstart + CRLF + "DTEND:" + dtend + CRLF + "DTSTAMP:" + dtstamp + CRLF + organizer + CRLF
            ical += "UID:FIXMEUID" + dtstamp + CRLF
            ical += attendee + "CREATED:" + dtstamp + CRLF + description + "LAST-MODIFIED:" + dtstamp + CRLF + "LOCATION:" + CRLF + "SEQUENCE:0" + CRLF + "STATUS:CONFIRMED" + CRLF
            ical += "SUMMARY:Exam invitation " + CRLF + "TRANSP:OPAQUE" + CRLF + "END:VEVENT" + CRLF + "END:VCALENDAR" + CRLF

            eml_body = "\n.ics file will be visible in the invite of outlook and outlook.com but not google calendar"
            part_cal = MIMEText(ical, 'calendar;method=REQUEST')
            msgAlternative = MIMEMultipart('alternative')
            message.attach(msgAlternative)

            msgAlternative.attach(part_cal)

        # if email_template.email_attachment_path:
        #     filename = os.path.join(media_path, 'media', str(email_template.email_attachment_path))
        #     type_subtype, _ = mimetypes.guess_type(filename)
        #     maintype, subtype = type_subtype.split('/')
        #     with open(filename, 'rb') as fp:
        #         msg = MIMEBase(maintype, subtype)
        #         msg.set_payload(fp.read())
            
        #     if email_template.email_attachment_name:
        #         attachment_name = f"{email_template.email_attachment_name}.pdf"
        #     else:
        #         attachment_name = "SB-Attachment"
        #     msg.add_header("Content-Disposition", "attachment", filename=attachment_name)
        #     encoders.encode_base64(msg)
        #     message.attach(msg)

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_draft_request_body = {
            'raw': encoded_message
        }
        
        service.users().messages().send(userId="me", body=create_draft_request_body).execute()
        
    # except Exception as e:
    #     print(str(e))
    #     raise