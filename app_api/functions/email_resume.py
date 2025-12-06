from __future__ import print_function
import os, base64
from datetime import datetime
from django.conf import settings
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from email.utils import parseaddr, parsedate_to_datetime

from hirelines.metadata import getConfig
from app_api.models import Resume, ResumeFile, Source
from .services import getEmailFetchUsers
from apscheduler.schedulers.background import BackgroundScheduler

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def gmail_service():

    creds = None

    root_path  = getConfig()['DIR']['root_path']
    token_path = root_path + "/app_api/functions/creds/hirelines/token.json"
    cred_path = root_path + "/app_api/functions/creds/hirelines/creds.json"

    # Load token if exists
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # Authentication if no valid token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                cred_path, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def fetch_gmail_attachments():
    try:
        service = gmail_service()

        from_emails = getEmailFetchUsers()

        check_user_query = " OR ".join([f"from:{u['email']}" for u in from_emails])

        # print("\n[+] Checking Gmail inbox for emails that have attachments...\n")

        query = f"has:attachment newer_than:1d ({check_user_query})"

        results = service.users().messages().list(
            userId="me",
            q=query
        ).execute()

        messages = results.get("messages", [])

        if not messages:
            # print("[!] No emails with attachments found in inbox.")
            return

        # print(f"[+] Found {len(messages)} email(s) with attachments.\n")

        for msg in messages:

            msg_data = service.users().messages().get(
                userId="me",
                id=msg["id"]
            ).execute()

            headers = msg_data["payload"]["headers"]

            raw_from = next((h["value"] for h in headers if h["name"] == "From"), None)
            name, from_email = parseaddr(raw_from)

            # print("---------------------------------------------")
            # print("📨 Email From :", from_email)
            # print("📅 Email Date :", date_raw)
            # print("📎 Attachments:")

            if Resume.objects.filter(mailid=msg["id"]).exists():
                # print(f"⛔ Skipping duplicate attachment: {msg['id']}")
                continue

            # Check attachment parts
            for part in msg_data["payload"].get("parts", []):

                if part.get("filename"):
                    filename = part["filename"]

                    allowed_ext = (".pdf", ".doc", ".docx")

                    if not filename.lower().endswith(allowed_ext):
                        continue

                    attachment_id = part["body"]["attachmentId"]

                    att = service.users().messages().attachments().get(
                        userId="me",
                        messageId=msg["id"],
                        id=attachment_id
                    ).execute()

                    file_data = base64.urlsafe_b64decode(att["data"])  # BLOB-ready bytes

                    user = next((u for u in from_emails if u["email"].lower() == from_email.lower()), None)
                    
                    sourceid = None

                    if user:
                        source = Source.objects.filter(userid=user['id']).last()
                        sourceid = source.id

                    new_resume = Resume(
                        sourceid = sourceid,
                        filename=filename,
                        mailid=msg["id"],
                        companyid=user["companyid"],
                        status="P"
                    )
                    new_resume.save()

                    resume_file = ResumeFile(
                        resumeid=new_resume.id,
                        filename = new_resume.filename,
                        filecontent=file_data
                    )
                    resume_file.save()

        #         print("    -", part["filename"])

        # print("\n[+] Finished checking emails with attachments.\n")
    except Exception as e:
        print("Saving resume failed:", e)

def sampleProg():
    print("Started",datetime.now())

def processEmailsFetch():
    scheduler = BackgroundScheduler()
    scheduler.add_job(sampleProg, trigger='interval', seconds=5, id="email_process_hirelines",replace_existing=True)
    scheduler.start()
