import os
import json
import requests
import string
import secrets
import ast
import time
import base64

# import ffmpeg
import re
import pandas as pd
from django.db.models import Q, Count, Avg
from datetime import datetime, date
from datetime import datetime, timedelta, time, date
from django.db.models import Q
from collections import defaultdict


from django.utils import timezone
from django.shortcuts import redirect
from urllib.parse import urljoin, urlparse
from rest_framework.authtoken.models import Token
from xhtml2pdf import pisa
from openpyxl import load_workbook
from openpyxl.styles import Border, Side
from .constants import public_email_domains
from hirelines.metadata import getConfig
from hirelines.settings import BASE_DIR
from .mailing import sendRegistrainMail
from app_api.models import (
    Account,
    CompanyCredits,
    CompanyData,
    Credits,
    JobDesc,
    Candidate,
    Payments,
    Registration,
    ReferenceId,
    Company,
    User,
    User_data,
    RolesPermissions,
    Workflow,
    CallSchedule,
    Vacation,
    WorkCal,
    ExtendedHours,
    HolidayCal,
    QResponse,
    CdnData,
    IvFeedback,
    Email_template,
    InterviewMedia,
    Brules,
    Branding,
    Role,
    JdAnalysis,
    Source,
    Uploads,
    Resume,
    Profile,
    ProfileActivity,
    ProfileEducation,
    ProfileExperience,
    ProfileProjects,
    ProfileSkills,
    ProfileAwards,
    ProfileCertificates,
    ProfileAddress,
    ResumeFile,
    Lookupmaster,
    ProfileAnalysis,
    Workspace,
    Client,
    JobBoard,
    JobBoardCredential,
    JDJobBoards
)
from app_api.functions.database import (
    saveJdNewTest,
    saveAddJD,
    saveUpdateJd,
    deleteTestInJdDB,
    saveInterviewersJD,
    addProfileActivityDB
)
from app_api.functions.mailing import sendEmail
from django.forms.models import model_to_dict
from .constants import const_candidate_status, const_paper_types
from .excel_mapping import validate_excel_with_json
from hirelines import settings
from .database import addCandidateDB
from .jd_profile_matching import calculateJDProfileMatching


def addCompanyDataService(dataObjs):
    try:

        bussiness_email = str(dataObjs["reg-bemail"])

        email_domain = bussiness_email.split("@")[1]

        if email_domain in public_email_domains:
            return 1

        email_check = CompanyData.objects.filter(companyemail=bussiness_email)

        if email_check:
            return 2

        company_data = CompanyData(
            companyname=dataObjs["reg-company"],
            companyemail=bussiness_email,
            location=dataObjs["reg-location"],
            contactperson=dataObjs["reg-name"],
            companytype=dataObjs["reg-companytype"],
            registerationtime=datetime.now(),
        )
        company_data.save()

        return 0

    except Exception as e:
        raise


def registerUserService(dataObjs):
    try:

        bussiness_email = str(dataObjs["reg-bemail"])

        user_email_domain = bussiness_email.split("@")[1]

        if user_email_domain in public_email_domains:
            return 1

        user_check = User.objects.filter(email=bussiness_email).last()

        if user_check:
            return 2

        company_check = Company.objects.filter(emaildomain=user_email_domain).last()

        random_password = generate_random_password()

        if company_check:

            return 3

        else:

            company = Company(
                name=dataObjs["reg-company"],
                emaildomain=user_email_domain,
                email=bussiness_email,
                companytype=dataObjs["reg-companytype"],
                registrationdate=datetime.now(),
                status="A",
                freetrail="I",
            )
            company.save()

            user = User(
                name=dataObjs["reg-name"],
                datentime=datetime.now(),
                location=dataObjs["reg-location"],
                companyid=company.id,
                role="HR-Admin",
                password=random_password,
                email=bussiness_email,
                status="A",
            )

            user.save()

            free_trail_data = getConfig()["FREETRAIL"]

            payments = Payments(
                companyid=company.id,
                dateofpay=datetime.now(),
                modeofpay="T",
                amount=30000,
                credits=free_trail_data["registration_grace_credits"],
            )
            payments.save()

            company_account, company_account_flag = Account.objects.get_or_create(
                companyid=company.id,
            )

            company_account.credit = payments.credits
            company_account.balance = (
                int(payments.credits) + int(company_account.balance)
                if company_account.balance
                else payments.credits
            )
            company_account.save()

            credits = Credits(
                companyid=company.id,
                transdatetime=payments.dateofpay,
                transtype="C",
                user=user.id,
                transid=payments.id,
                points=payments.credits,
                balance=company_account.balance,
            )
            credits.save()

            CompanyCredits(
                companyid=company.id,
                transtype="S",
                credits=free_trail_data["screening_credits_charges"],
            ).save()

            CompanyCredits(
                companyid=company.id,
                transtype="E",
                credits=free_trail_data["coding_credits_charges"],
            ).save()

            CompanyCredits(
                companyid=company.id,
                transtype="I",
                credits=free_trail_data["interview_credits_charges"],
            ).save()

            default_branding = Branding.objects.filter(companyid=0).last()

            company_branding = Branding(
                companyid=company.id,
                content=default_branding.content,
                logourl=default_branding.logourl if default_branding.logourl else "",
                sociallinks=(
                    default_branding.sociallinks if default_branding.sociallinks else ""
                ),
                status="A",
            )

            company_branding.save()

            code = f"RC{user.id:03}"
            source = Source(
                code=code,
                label=user.name,
                companyid=user.companyid,
                userid=user.id,
            )            

            source.save()

            acert_domain = getConfig()["DOMAIN"]["acert"]
            endpoint = "/api/add-company"

            url = urljoin(acert_domain, endpoint)

            company_data = {
                "id": company.id,
                "company_name": company.name,
                "brand_content": company_branding.content,
                "company_email": bussiness_email,
                "company_logo": str(company_branding.logourl),
                "sociallinks": company_branding.sociallinks,
            }

            send_company_data = requests.post(url, json=company_data)

            hirelines_domain = getConfig()["DOMAIN"]["hirelines"]
            mail_data = {
                "name": user.name,
                "email": user.email,
                "password": user.password,
                "url": f"{hirelines_domain}/login",
            }
            sendRegistrainMail(mail_data)

        return 0

    except Exception as e:
        print(str(e))
        raise


def getJobDescData(jid, company_id):
    try:

        job_desc = JobDesc.objects.filter(id=jid).last()

        deleted_candidate_ids = Candidate.objects.filter(
            jobid=jid, deleteflag="Y"
        ).values_list("id", flat=True)

        if job_desc:

            screening_tests = 0
            screening_fail = 0
            screening_pass = 0
            coding_tests = 0
            coding_fail = 0
            coding_pass = 0
            interviews = 0
            offer_letters = 0
            rejected = 0

            registrations = Registration.objects.filter(
                companyid=company_id, jobid=jid
            ).exclude(candidateid__in=deleted_candidate_ids)

            for registation in registrations:

                if registation.papertype == "S":
                    screening_tests += 1
                    if registation.status == "F":
                        screening_fail += 1
                    elif registation.status == "P":
                        screening_pass += 1

                elif registation.papertype == "E":
                    coding_tests += 1
                    if registation.status == "F":
                        coding_fail += 1
                    elif registation.status == "P":
                        coding_pass += 1

                elif registation.papertype == "I":
                    interviews += 1
                    if registation.status == "O":
                        offer_letters += 1
                    elif registation.status == "R":
                        rejected += 1

            jd_data = {
                "jobid": job_desc.id,
                "title": job_desc.title,
                "screening_tests": screening_tests,
                "screening_pending": screening_tests
                - (screening_fail + screening_pass),
                "screening_fail": screening_fail,
                "screening_pass": screening_pass,
                "coding_tests": coding_tests,
                "coding_pending": coding_tests - (coding_fail + coding_pass),
                "coding_fail": coding_fail,
                "coding_pass": coding_pass,
                "interviews": interviews,
                "interview_pending": interviews - (offer_letters + rejected),
                "offer_letters": offer_letters,
                "rejected": rejected,
                "display_flag": (
                    job_desc.dashboardflag if job_desc.dashboardflag else "N"
                ),
            }
            return jd_data

    except Exception as e:
        raise


def jdTestAdd(jdData, compyId):
    try:
        if jdData:
            test_data = saveJdNewTest(jdData, compyId)
            return test_data
    except Exception as e:
        raise


def addJdServices(addjdData, companyID, hrEmail):
    try:
        jdData = saveAddJD(addjdData, companyID, hrEmail)
        return jdData
    except Exception as e:
        raise


def companyUserLst(companyID):
    try:
        usersDataLst = []
        userLst = User.objects.filter(companyid=companyID).order_by("-id")
        for user in userLst:
            userData = model_to_dict(user)
            usersDataLst.append(userData)

        lstRoles = Role.objects.all()
        roleslst = []

        for rolee in lstRoles:
            userRole = model_to_dict(rolee)
            if userRole["Name"] != "HR-Admin":
                roleslst.append(userRole)

        return {"usrs": usersDataLst, "roles": roleslst}
    except Exception as e:
        raise


def updateJdDataService(addjdData):
    try:
        jdData = JobDesc.objects.filter(id=addjdData["JdID"]).last()
        if jdData:

            # modifiedSkillList = []
            # # Check if skillLst is a list-like string or a plain CSV string
            # parsed_skillLst = ast.literal_eval(jdData.skillset)  # Try parsing as a list of dictionaries

            # print('parsed_skillLst :: ',parsed_skillLst)

            # for skill in parsed_skillLst:
            #     key = list(skill.keys())[0]  # Extract the first key
            #     subSkills = skill[key].split(',') if ',' in skill[key] else [skill[key]]

            #     for subSkill in subSkills:
            #         modifiedSkillList.append(subSkill.strip())

            jdDataDict = {
                "id": jdData.id,
                "title": "" if jdData.title is None else jdData.title,
                "role": "" if jdData.role is None else jdData.role,
                "description": "" if jdData.description is None else jdData.description,
                "expmin": "" if jdData.expmin is None else jdData.expmin,
                "expmax": "" if jdData.expmax is None else jdData.expmax,
                "department": "" if jdData.department is None else jdData.department,
                "location": "" if jdData.location is None else jdData.location,
                "budget": "" if jdData.budget is None else jdData.budget,
                "skillset": "" if jdData.skillset is None else jdData.skillset.strip(),
                "secondaryskills": "" if jdData.secondaryskills is None else jdData.secondaryskills.strip(),
                "skillnotes": "" if jdData.skillnotes is None else jdData.skillnotes,
                "expjoindate": "" if jdData.expjoindate is None else jdData.expjoindate,
                "positions": "" if jdData.positions is None else jdData.positions,
                "status": "" if jdData.status is None else jdData.status,
                "hiringmanager": "" if jdData.hiringmanagerid is None else jdData.hiringmanagerid
            }
            return jdDataDict

    except Exception as e:
        raise


def updateJdServices(addjdData, companyID, hrEmail):
    try:
        saveUpdateJd(addjdData, companyID, hrEmail)
    except Exception as e:
        raise


def candidateRegistrationService(dataObjs):
    try:

        fname = dataObjs["fname"]
        lname = dataObjs["lname"]
        email = dataObjs["email"]
        mobile = dataObjs["mobile"]
        paper_id = dataObjs["paper_id"]
        company_id = dataObjs["company_id"]
        job_id = dataObjs["job_id"]

        candidate = Candidate(
            firstname=fname,
            lastname=lname,
            companyid=company_id,
            paperid=paper_id,
            email=email,
            mobile=mobile,
            jobid=job_id,
            registrationdate=datetime.now(),
            status="P",
        )

        year = datetime.now().strftime("%y")

        refid_obj, refid_flag = ReferenceId.objects.get_or_create(
            type="R", prefix1="{:03}".format(company_id), prefix2=year
        )

        if refid_flag == True:
            lastid = 1
            refid_obj.lastid = lastid
            refid_obj.save()

        if refid_flag == False:
            lastid = refid_obj.lastid + 1
            refid_obj.lastid = lastid
            refid_obj.save()

        candidate_id_seq = str("{:05}".format(int(refid_obj.lastid)))
        candidate_code = f"{refid_obj.prefix1}{refid_obj.prefix2}{candidate_id_seq}"

        candidate.candidateid = candidate_code

        candidate.save()

        # Acert API

        acert_domain = getConfig()["DOMAIN"]["acert"]
        endpoint = "/api/hirelines-add-candidate"

        url = urljoin(acert_domain, endpoint)

        candidate_data = {
            "fname": fname,
            "lname": lname,
            "email": email,
            "mobile": mobile,
            "paper_id": paper_id,
            "company_id": company_id,
            "reference_id": candidate.candidateid,
        }

        send_candidate_data = requests.post(url, json=candidate_data)

        response_content = send_candidate_data.content

        if response_content:
            json_data = json.loads(response_content.decode("utf-8"))

            c_registration = Registration(
                candidateid=candidate.id,
                paperid=candidate.paperid,
                registrationdate=candidate.registrationdate,
                status="P",
                companyid=candidate.companyid,
                jobid=candidate.jobid,
                papertype=json_data["data"],
            )

            c_registration.save()
    except Exception as e:
        raise


def getJdCandidatesData(jid, userid):
    try:

        user = User.objects.get(id=userid)

        candidates = (
            Candidate.objects.filter(jobid=jid, companyid=user.companyid)
            .exclude(deleteflag="Y")
            .order_by("-id")
        )

        candidates_data = []

        for candidate in candidates:

            registrations = Registration.objects.filter(
                candidateid=candidate.id, companyid=candidate.companyid
            )

            candidate_info = {
                "id": candidate.id,
                "cid": candidate.candidateid,
                "name": f"{candidate.firstname} {candidate.lastname}",
                "email": candidate.email,
                "registrations": {"S": [], "E": [], "I": []},
            }

            for registration in registrations:

                registration_info = {
                    "date": registration.registrationdate.strftime("%Y-%m-%d"),
                    "status": registration.status,
                }

                if registration.papertype == "S":
                    candidate_info["registrations"]["S"].append(registration_info)
                elif registration.papertype == "E":
                    candidate_info["registrations"]["E"].append(registration_info)
                elif registration.papertype == "I":
                    candidate_info["registrations"]["I"].append(registration_info)

            candidates_data.append(candidate_info)

        return candidates_data

    except Exception as e:
        raise


def getCandidatesData(userid):
    try:

        user = User.objects.get(id=userid)

        candidates_list = []

        candidates = (
            Candidate.objects.filter(companyid=user.companyid)
            .exclude(deleteflag="Y")
            .order_by("-id")
        )

        for candidate in candidates:

            c_status = const_candidate_status.get(candidate.status, "")

            job_desc = JobDesc.objects.filter(id=candidate.jobid).last()

            candidates_list.append(
                {
                    "id": candidate.id,
                    "candidate_id": candidate.candidateid,
                    "firstname": candidate.firstname,
                    "lastname": candidate.lastname,
                    "email": candidate.email,
                    "status": c_status,
                    "jd_title": job_desc.title if job_desc else "",
                }
            )

        return candidates_list

    except Exception as e:
        raise


def authentication_service(dataObjs):

    try:
        user = User.objects.get(
            email=dataObjs["email"], password=dataObjs["password"], status="A"
        )

    except:
        return (None,)

    try:

        if user:
            check1 = User_data.objects.filter(
                usr_email=user.email, usr_password=user.password, user="C"
            )

            if not check1:
                User_data(
                    username=user.email,
                    usr_email=user.email,
                    usr_password=user.password,
                    is_staff=True,
                    user="C",
                ).save()
            token_obj = (
                Token.objects.filter(user__usr_email=user.email)
                .order_by("-created")
                .first()
            )
            user_data = User_data.objects.get(
                usr_email=user.email, usr_password=user.password, user="C"
            )
            user_data.is_staff = True
            user_data.save()
            if token_obj:
                return token_obj.key
            else:
                check = User_data.objects.filter(usr_email=user.email).first()
                token_obj, token_flag = Token.objects.get_or_create(user=check)
                return token_obj.key
    except Exception as e:
        print(str(e))
        raise


def get_functions_service(user_role):
    try:
        functions = RolesPermissions.objects.filter(
            enable__contains=user_role
        ).order_by("orderby")
        temp = []

        for function in functions:

            functionObjList = [
                func for func in temp if func["menuItemParent"] == function.function
            ]
            if not functionObjList:
                uifuncObj = {
                    "menuItemParent": function.function,
                    "UIIcon": function.function_icon,
                    "menuItemKey": function.function_category,
                    "child": [],
                }
                uifuncObj["child"].append(
                    {
                        "menuItemName": function.sub_function,
                        "menuItemLink": function.function_link,
                    }
                )
                temp.append(uifuncObj)
            elif functionObjList:
                temp = [
                    menuItem
                    for menuItem in temp
                    if menuItem["menuItemParent"] != function.function
                ]
                functionObjList[0]["child"].append(
                    {
                        "menuItemName": function.sub_function,
                        "menuItemLink": function.function_link,
                    }
                )
                temp.append(functionObjList[0])
        menuItemList = temp
        return menuItemList
    except Exception as e:
        print(str(e))
        raise


def checkCompanyTrailPeriod(user_mail):
    try:

        user = User.objects.filter(email=user_mail).last()

        if user:

            company = Company.objects.get(id=user.companyid)

            trial_days = getConfig()["FREETRAIL"]["days"]

            if company.freetrail == "I" and company.status == "T":

                trial_end_date = company.registrationdate + timedelta(
                    days=int(trial_days)
                )

                if timezone.now() > trial_end_date:

                    company.freetrail = "C"
                    company.save()
                    return True

            if company.freetrail == "C" and company.status == "T":

                return True

    except Exception as e:
        raise


def generate_random_password(length=15):
    try:
        characters = string.ascii_letters + string.digits

        password = "".join(secrets.choice(characters) for _ in range(length))

        return password

    except Exception as e:
        raise


def getCompanyJdData(cid):
    try:
        company_jds = JobDesc.objects.filter(companyid=cid).exclude(
            status__in=["D", "I"]
        )

        jds_list = []

        if company_jds:

            for jd in company_jds:

                jds_list.append({"id": jd.id, "title": jd.title})

        return jds_list

    except Exception as e:
        raise


def getCompanyJDsList(companyId, user_role):
    try:
        company_jds = list(JobDesc.objects.filter(companyid=companyId).values())
        if len(company_jds) > 0:
            for jd in company_jds:
                userData = User.objects.filter(id=jd["createdby"]).last()
                userName = ""
                if userData:
                    userName = userData.name
                jd["createdbyUserName"] = userName
            company_jds.reverse()  # Reverse the list to show latest jobs first

            InactiveJds = []
            activeJds = []
            # Separate the jobs based on status
            for jd in company_jds:
                # if jd["status"] == "I":
                #     InactiveJds.append(jd)  # Add to inactive jobs list
                # else:
                #     # activeJds.append(jd)  # Add to active jobs list
                #     if user_role == "Hiring-Manager":
                #         if jd["approval_status"] in ["F", "O", "R", "H","A"]:
                #             activeJds.append(jd)
                #     else:
                #         activeJds.append(jd)
                # -------- INACTIVE TAB --------
                if jd["status"] == "I":
                    InactiveJds.append(jd)
                    continue

                # -------- HIRING MANAGER VIEW --------
                if user_role == "Hiring-Manager":

                    # Draft without approval → hide
                    if jd["status"] == "D" and not jd["approval_status"]:
                        continue

                    # Stopped jobs → hide
                    if jd["status"] == "P":
                        continue

                    activeJds.append(jd)

                # -------- OTHER ROLES (HR / ADMIN) --------
                else:
                    activeJds.append(jd)

            return {"activeJd": activeJds, "inactiveJd": InactiveJds}
        else:
            # If no jobs are found, return empty lists for both
            return {"activeJd": [], "inactiveJd": []}

    except Exception as e:
        raise


# def jdDetails(jdId, companyId):
#     try:
#         # Get the last JobDesc object for the provided jdId
#         jdData = JobDesc.objects.filter(id=jdId).last()
#         selectedInterviewerLst = []
#         total_interviewers_lst = []
#         if jdData:
#             # Manually create the dictionary with conditions for None values

#             interviewes_lst = User.objects.filter(status="A", companyid=companyId).values("id", "name")

#             for interviewer in interviewes_lst:
#                 if interviewer:
#                     total_interviewers_lst.append({"id": interviewer["id"], "name": interviewer["name"]})

#                 selectedInterviewerLst = []
#                 if jdData.interviewers:
#                     jd_interviewers = ast.literal_eval(jdData.interviewers)
#                     for selectedInterviewer in jd_interviewers:
#                         if selectedInterviewer:
#                             userData = list(User.objects.filter(id=selectedInterviewer).values("id", "name"))
#                             if userData:
#                                 if selectedInterviewer:
#                                     selectedInterviewerLst.append(
#                                         {
#                                             "id": userData[0]["id"],
#                                             "name": userData[0]["name"],
#                                         }
#                                     )

#             jdDataDict = {
#                 "id": jdData.id,
#                 "jdlibraryid": 0 if jdData.jdlibraryid is None else jdData.jdlibraryid,
#                 "title": "" if jdData.title is None else jdData.title,
#                 "role": "" if jdData.role is None else jdData.role,
#                 "description": "" if jdData.description is None else jdData.description,
#                 "expmin": "" if jdData.expmin is None else jdData.expmin,
#                 "expmax": "" if jdData.expmax is None else jdData.expmax,
#                 "department": "" if jdData.department is None else jdData.department,
#                 "location": "" if jdData.location is None else jdData.location,
#                 "budget": "" if jdData.budget is None else jdData.budget,
#                 "skillset": "" if jdData.skillset is None else jdData.skillset,
#                 "skillnotes": "" if jdData.skillnotes is None else jdData.skillnotes,
#                 "interviewers": (
#                     "" if jdData.interviewers is None else jdData.interviewers
#                 ),
#                 "expjoindate": "" if jdData.expjoindate is None else jdData.expjoindate,
#                 "positions": "" if jdData.positions is None else jdData.positions,
#                 "createdby": "" if jdData.createdby is None else jdData.createdby,
#                 "status": "" if jdData.status is None else jdData.status,
#                 "companyid": "" if jdData.companyid is None else jdData.companyid,
#                 "interviewes_lst": total_interviewers_lst,
#                 "selectedInterviewerLst": selectedInterviewerLst,
#             }
#             return jdDataDict
#         return None  # Return None if no data is found
#     except Exception as e:
#         raise


def jdDetails(jdId, companyId):
    try:
        # Get the last JobDesc object for the provided jdId
        jdData = JobDesc.objects.filter(id=jdId).last()
        workFlowDetails = []

        # skillLst = jdData.skillset.split(',')
        skillLst = jdData.skillset

        if skillLst:
            modifiedSkillList = []

            # Check if skillLst is a list-like string or a plain CSV string
            print("skillLst :: ", skillLst)
            parsed_skillLst = ast.literal_eval(
                skillLst
            )  # Try parsing as a list of dictionaries

            for skill in parsed_skillLst:
                key = list(skill.keys())[0]  # Extract the first key
                subSkills = skill[key].split(",") if "," in skill[key] else [skill[key]]

                for subSkill in subSkills:
                    modifiedSkillList.append(
                        subSkill.strip()
                    )  # Clean and append each sub-skill

        selectedInterviewerLst = []
        total_interviewers_lst = []
        if jdData:
            # Manually create the dictionary with conditions for None values

            interviewes_lst = User.objects.filter(
                status="A", companyid=companyId, role__in=["Interviewer", "HR-Admin", "HR-Executive"]
            ).values("id", "name")
            workFlowDetails = Workflow.objects.filter(
                jobid=jdId, teststatus="A"
            ).values()
            workFlowList = {}

            for workFlowData in workFlowDetails:
                # Replace None values with empty strings
                cleanData = {
                    key: (value if value is not None else "")
                    for key, value in workFlowData.items()
                }
                workFlowList[workFlowData["id"]] = cleanData

            for interviewer in interviewes_lst:
                if interviewer:
                    total_interviewers_lst.append(
                        {"id": interviewer["id"], "name": interviewer["name"]}
                    )

                selectedInterviewerLst = []
                if jdData.interviewers:
                    jd_interviewers = ast.literal_eval(jdData.interviewers)
                    for selectedInterviewer in jd_interviewers:
                        if selectedInterviewer:
                            userData = list(User.objects.filter(id=selectedInterviewer).values("id", "name"))
                            if userData:
                                if selectedInterviewer:
                                    selectedInterviewerLst.append(
                                        {
                                            "id": userData[0]["id"],
                                            "name": userData[0]["name"],
                                        }
                                    )

            jdDataDict = {
                "id": jdData.id,
                "jdlibraryid": 0 if jdData.jdlibraryid is None else jdData.jdlibraryid,
                "title": "" if jdData.title is None else jdData.title,
                "role": "" if jdData.role is None else jdData.role,
                "description": "" if jdData.description is None else jdData.description,
                "expmin": "" if jdData.expmin is None else jdData.expmin,
                "expmax": "" if jdData.expmax is None else jdData.expmax,
                "department": "" if jdData.department is None else jdData.department,
                "location": "" if jdData.location is None else jdData.location,
                "budget": "" if jdData.budget is None else jdData.budget,
                "skillset": "" if jdData.skillset is None else jdData.skillset,
                "skillnotes": "" if jdData.skillnotes is None else jdData.skillnotes,
                "interviewers": (
                    "" if jdData.interviewers is None else jdData.interviewers
                ),
                "expjoindate": "" if jdData.expjoindate is None else jdData.expjoindate,
                "positions": "" if jdData.positions is None else jdData.positions,
                "createdby": "" if jdData.createdby is None else jdData.createdby,
                "status": "" if jdData.status is None else jdData.status,
                "comments": "" if jdData.comments is None else jdData.comments,
                "approval_status": "" if jdData.approval_status is None else jdData.approval_status,
                "companyid": "" if jdData.companyid is None else jdData.companyid,
                "interviewes_lst": total_interviewers_lst,
                "selectedInterviewerLst": selectedInterviewerLst,
                "skillsList": modifiedSkillList,
                "workFlowDetails": workFlowList,
                "hiringmanager": "" if jdData.hiringmanagerid is None else jdData.hiringmanagerid,
            }
            return jdDataDict
        return None  # Return None if no data is found
    except Exception as e:
        raise


def checkTestHasPaperService(user, dataObjs):
    try:
        if dataObjs["workFlowId"]:
            workFlowDetails = Workflow.objects.filter(id=dataObjs["workFlowId"]).last()
            if workFlowDetails:
                if workFlowDetails.paperid:
                    return {
                        "paperId": workFlowDetails.paperid,
                        "testid": workFlowDetails.id,
                        "libraryId": workFlowDetails.paperlibraryid,
                        "paperType": workFlowDetails.papertype,
                    }
                else:
                    return {"paperId": "N"}
            else:
                return {"paperId": "N"}
        else:
            return {"paperId": "N"}
    except Exception as e:
        raise


def deleteTestInJdService(user, dataObjs):
    try:
        testDetails = deleteTestInJdDB(dataObjs)
        return testDetails
    except Exception as e:
        raise


def saveInterviewersService(user, dataObjs):
    try:
        testDetails = saveInterviewersJD(dataObjs)
        return testDetails
    except Exception as e:
        raise


# def workFlowDataService(data, cmpyId):
#     try:
#         intervierDeatils = User.objects.filter(
#             status="A", role="Interviewer", companyid=cmpyId
#         )
#         interviewersLst = []

#         for interviewer in intervierDeatils:
#             interviewerData = {}
#             interviewerData["userId"] = interviewer.id
#             interviewerData["name"] = interviewer.name
#             interviewersLst.append(interviewerData)

#         papersDetails = []
#         papersDetails = Workflow.objects.filter(jobid=data).values()

#         for test in papersDetails:
#             brulesDetails = Brules.objects.filter(
#                 workflowid=test["id"],
#                 jobdescid=test["jobid"],
#                 companyid=test["companyid"],
#             ).last()

#             if brulesDetails:
#                 test["promot"] = brulesDetails.passscore
#                 test["hold"] = brulesDetails.hold
#                 test["holdpercentage"] = brulesDetails.holdpercentage

#         jdData = list(JobDesc.objects.filter(id=data).values())

#         JdStatus = None
#         selectedJdInterviewers = ''
#         if len(jdData) > 0:
#             JdStatus = jdData[0]['status']
#             print('==========================')
#             print('jdData :: ',jdData[0]['skillset'])

#             if jdData[0]['interviewers']:
#                 selectedJdInterviewers = ast.literal_eval(jdData[0]['interviewers'])

#         return {"workFlowData": list(papersDetails), "jdInterviewers": interviewersLst,'jdStatus':JdStatus, 'selectedJDInterviewers':selectedJdInterviewers}
#     except Exception as e:
#         raise


def workFlowDataService(data, cmpyId):
    try:
        intervierDeatils = User.objects.filter(
            status="A", role="Interviewer", companyid=cmpyId
        )
        interviewersLst = []

        for interviewer in intervierDeatils:
            interviewerData = {}
            interviewerData["userId"] = interviewer.id
            interviewerData["name"] = interviewer.name
            interviewersLst.append(interviewerData)

        papersDetails = []
        papersDetails = Workflow.objects.filter(jobid=data).values()

        for test in papersDetails:
            brulesDetails = Brules.objects.filter(
                workflowid=test["id"],
                jobdescid=test["jobid"],
                companyid=test["companyid"],
            ).last()

            if brulesDetails:
                test["promot"] = brulesDetails.passscore
                test["hold"] = brulesDetails.hold
                test["holdpercentage"] = brulesDetails.holdpercentage

        jdData = list(JobDesc.objects.filter(id=data).values())

        JdStatus = None
        selectedJdInterviewers = ""
        if len(jdData) > 0:
            JdStatus = jdData[0]["status"]

            jdSkillsList = []
            skillList = jdData[0]["skillset"].split(",")
            for skill in skillList:
                jdSkillsList.append(skill.strip())

            if jdData[0]["interviewers"]:
                selectedJdInterviewers = ast.literal_eval(jdData[0]["interviewers"])

        return {
            "workFlowData": list(papersDetails),
            "jdInterviewers": interviewersLst,
            "jdStatus": JdStatus,
            "selectedJDInterviewers": selectedJdInterviewers,
            "skillsLst": jdSkillsList,
        }
    except Exception as e:
        raise


def skillsWithTopicsWithSubtopicsWithQuestionsService(dataObjs):
    try:
        # Extract skills list from input
        skillList = dataObjs.get("skillsSetLst", [])
        if not skillList:
            print("Error: 'skillsSetLst' is empty or missing.")
            return

        # Construct API endpoint
        acert_domain = getConfig()["DOMAIN"]["acert"]
        endpoint = "/api/getTopicAndSubtopicAndQuestions"
        url = urljoin(acert_domain, endpoint)

        # Prepare request payload
        startQuestionData = {"data": skillList}

        # Make the POST request
        response = requests.post(url, json=startQuestionData)

        # Check for HTTP errors
        response.raise_for_status()

        # Decode the response content
        response_content = response.content
        if response_content:
            # Parse JSON data
            json_data = json.loads(response_content.decode("utf-8"))
            return json_data
        else:
            print("Response content is empty.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
    except json.JSONDecodeError as e:
        print(f"Failed to decode JSON: {e}")
    except KeyError as e:
        print(f"Configuration error: Missing key {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    except Exception as e:
        raise


def getJdWorkflowService(jid, cid):
    try:

        jd_workflows = Workflow.objects.filter(
            jobid=jid, companyid=cid, paperid__isnull=False
        ).order_by("order")

        workflow_data = []

        if jd_workflows:
            for workflow in jd_workflows:
                workflow_data.append(
                    {
                        "id": workflow.id,
                        "papertype": workflow.papertype,
                        "title": workflow.papertitle,
                        "paperid": workflow.paperid,
                    }
                )

        return workflow_data

    except Exception as e:
        raise


def getCallScheduleDetails(cid):
    try:
        candidate = Candidate.objects.get(id=cid)

        jd = JobDesc.objects.get(id=candidate.jobid)

        if jd.interviewers:
            jd_interviewers = ast.literal_eval(jd.interviewers)
        else:
            jd_interviewers = ""

        job_interviewers = []

        for job_interviewer in jd_interviewers:

            interviewer = User.objects.get(id=job_interviewer)
            job_interviewers.append({"id": interviewer.id, "name": interviewer.name})

        candidate_data = {
            "cid": candidate.id,
            "c_name": f"{candidate.firstname} {candidate.lastname}",
            "c_email": candidate.email,
            "c_mobile": candidate.mobile,
        }

        return job_interviewers, candidate_data

    except Exception as e:
        raise


# def interviewSchedulingService(aplid, int_id):
#     try:

#         call_scheduling_constraints = getConfig()["CALL_SCHEDULING_CONSTRAINTS"]

#         WORK_HOURS = int(call_scheduling_constraints["work_hours"])
#         STARTING_HOUR = int(call_scheduling_constraints["starting_hour"])
#         BLOCK_HOURS = int(call_scheduling_constraints["block_hours"])
#         FREQUENCY = int(call_scheduling_constraints["frequency_mins"])

#         basedt = datetime.today().replace(
#             hour=STARTING_HOUR, minute=00, second=00, microsecond=00
#         )

#         scheduling_data = []
#         scheduled_calls = list(
#             CallSchedule.objects.filter(Q(status="S") | Q(status="R")).values_list(
#                 "datentime", "interviewerid"
#             )
#         )

#         scheduled_calls_list = []
#         for scheduled_call in scheduled_calls:
#             if scheduled_call[0]:
#                 # FIX: Convert DB time (UTC) to Local Time before formatting
#                 local_db_time = timezone.localtime(scheduled_call[0])

#                 scheduled_calls_list.append(
#                     [local_db_time.strftime("%Y-%m-%d %I:%M %p"), scheduled_call[1]]
#                 )

#         vacation_data = Vacation.objects.filter(empid=int_id).values(
#             "empid", "fromdate", "todate"
#         )
#         workcal_data = WorkCal.objects.filter(userid=int_id).values()

#         alter_timings_data = ExtendedHours.objects.filter(
#             empid=int_id, status="A"
#         ).values()
#         alter_timings_dates_list = []
#         alter_timings_list = {}

#         for alter_timings in alter_timings_data:

#             alter_dates_ = [
#                 [
#                     alter_timings["fromdate"] + timedelta(days=x),
#                     alter_timings["starttime"],
#                     alter_timings["workhours"],
#                     alter_timings["userid"],
#                 ]
#                 for x in range(
#                     (alter_timings["todate"] - alter_timings["fromdate"]).days + 1
#                 )
#             ]
#             for alter_date in alter_dates_:
#                 formated_alter_date = alter_date[0].strftime("%a-%d-%b-%Y")
#                 alter_timings_dates_list.append(formated_alter_date)
#                 alter_timings_list[str(alter_date[0].strftime("%Y-%m-%d"))] = [
#                     alter_date[0],
#                     alter_date[1],
#                     alter_date[2],
#                     alter_date[3],
#                 ]

#         for x in range(0, 15):  # days
#             hours_list = []
#             slots_list = []
#             status_list = []

#             telecallers = list(
#                 User.objects.filter(status="A", id=int_id).values_list("id", flat=True)
#             )

#             _date = (basedt + timedelta(days=x)).strftime("%Y-%m-%d")
#             _datetime = datetime.strptime(
#                 (
#                     basedt.replace(hour=00, minute=00, second=00, microsecond=00)
#                     + timedelta(days=x)
#                 ).strftime("%Y-%m-%d %H:%M:%S"),
#                 "%Y-%m-%d %H:%M:%S",
#             )
#             date_formated = (basedt + timedelta(days=x)).strftime("%a-%d-%b-%Y")
#             for vacation in vacation_data:
#                 from_date = datetime.strptime(str(vacation["fromdate"]), "%Y-%m-%d")
#                 to_date = datetime.strptime(str(vacation["todate"]), "%Y-%m-%d")
#                 if from_date <= _datetime <= to_date:
#                     if vacation["empid"] in telecallers:
#                         telecallers.remove(vacation["empid"])
#             # for alter_hours in
#             for work_data in workcal_data:
#                 # print("work_data['weekoff1']",work_data['weekoff1'],date_formated,alter_timings_dates_list)
#                 if (work_data["weekoff1"] == date_formated.split("-")[0]) and (
#                     date_formated not in alter_timings_dates_list
#                 ):
#                     if work_data["userid"] in telecallers:
#                         telecallers.remove(work_data["userid"])
#                 if work_data["weekoff2"] == date_formated.split("-")[0] and (
#                     date_formated not in alter_timings_dates_list
#                 ):
#                     if work_data["userid"] in telecallers:
#                         telecallers.remove(work_data["userid"])
#             for i in range(0, WORK_HOURS * 2):  # (0,24) 24 means 12 Hours
#                 slot_time = basedt + timedelta(minutes=30 * i)
#                 curr_time = datetime.now().replace(
#                     second=00
#                 )  # + datetime.timedelta(hours=4)
#                 hours_list.append(slot_time.strftime("%I:%M %p"))
#                 # print('_date',_date)
#                 # print('d_time',datetime.today().strftime("%Y-%m-%d"))
#                 # print('slot_time',slot_time)
#                 # print('slot_time ------- 2',(curr_time + timedelta(hours=BLOCK_HOURS, minutes=30)))
#                 if (_date == datetime.today().strftime("%Y-%m-%d")) and (
#                     slot_time <= (curr_time + timedelta(hours=BLOCK_HOURS, minutes=30))
#                 ):
#                     status_list.append("Blocked")
#                     slots_list.append([])
#                 else:

#                     occupied_tc = []

#                     tc = telecallers
#                     telecallers_set = set(tc)
#                     for slot in scheduled_calls_list:

#                         if slot[0] == _date + " " + slot_time.strftime("%I:%M %p"):

#                             if slot[1] in tc:
#                                 occupied_tc.append(slot[1])

#                     available_tc_list = list(
#                         telecallers_set.difference(set(occupied_tc))
#                     )
#                     for work_data in workcal_data:

#                         slot_date = datetime.strptime(_date, "%Y-%m-%d").date()
#                         slot_date_str = str(slot_date.strftime("%Y-%m-%d"))

#                         if slot_date_str in alter_timings_list:
#                             alter_data = alter_timings_list[slot_date_str]
#                             start_datetime = datetime.combine(
#                                 datetime.today(), alter_data[1]
#                             )
#                             if len(str(alter_data[2]).split(".")) == 2:
#                                 work_hours = int(alter_data[2].split(".")[0])
#                                 if work_hours - 1 > ((WORK_HOURS * 2) / 2):
#                                     work_hours = ((WORK_HOURS * 2) / 2) - 1
#                                 work_mins = 30
#                             else:
#                                 work_hours = int(alter_data[2])
#                                 if work_hours > ((WORK_HOURS * 2) / 2):
#                                     work_hours = (WORK_HOURS * 2) / 2
#                                 work_mins = 0

#                             end_datetime = start_datetime + timedelta(
#                                 hours=work_hours, minutes=work_mins
#                             )
#                             end_time = end_datetime.time()

#                             if alter_data[1] > slot_time.time():

#                                 if alter_data[3] in available_tc_list:
#                                     available_tc_list.remove(alter_data[3])

#                             if slot_time.time() >= end_time:
#                                 if alter_data[3] in available_tc_list:
#                                     available_tc_list.remove(alter_data[3])

#                         else:
#                             start_datetime = datetime.combine(
#                                 datetime.today(), work_data["starttime"]
#                             )
#                             if len(work_data["hours"].split(".")) == 2:
#                                 work_hours = int(work_data["hours"].split(".")[0])
#                                 if work_hours - 1 > ((WORK_HOURS * 2) / 2):
#                                     work_hours = ((WORK_HOURS * 2) / 2) - 1
#                                 work_mins = 30
#                             else:
#                                 work_hours = int(work_data["hours"])
#                                 if work_hours > ((WORK_HOURS * 2) / 2):
#                                     work_hours = (WORK_HOURS * 2) / 2
#                                 work_mins = 0

#                             end_datetime = start_datetime + timedelta(
#                                 hours=work_hours, minutes=work_mins
#                             )
#                             end_time = end_datetime.time()

#                             if work_data["starttime"] > slot_time.time():

#                                 if work_data["userid"] in available_tc_list:
#                                     available_tc_list.remove(work_data["userid"])

#                             if slot_time.time() >= end_time:
#                                 if work_data["userid"] in available_tc_list:
#                                     available_tc_list.remove(work_data["userid"])

#                     if not available_tc_list:
#                         status_list.append("No_Vacancy")
#                     else:
#                         status_list.append("Available")
#                     slots_list.append(available_tc_list)
#                 if HolidayCal.objects.filter(holidaydt=_date).exists():
#                     status_list = []
#                     while len(status_list) <= WORK_HOURS * 2:
#                         status_list.append("Holiday")

#             ids = []
#             for slo in slots_list:
#                 ids.append(list(slo))

#             dataObj = {
#                 "day": date_formated,
#                 "hours_list": hours_list,
#                 "slots_list": slots_list,
#                 "status": status_list,
#                 "ids": ids,
#             }
#             scheduling_data.append(dataObj)

#         return scheduling_data


#     except Exception as e:
#         raise
def interviewSchedulingService(aplid, int_id):
    try:
        call_scheduling_constraints = getConfig()["CALL_SCHEDULING_CONSTRAINTS"]

        WORK_HOURS = int(call_scheduling_constraints["work_hours"])
        STARTING_HOUR = int(call_scheduling_constraints["starting_hour"])
        BLOCK_HOURS = int(call_scheduling_constraints["block_hours"])
        # FREQUENCY = int(call_scheduling_constraints["frequency_mins"]) # Unused in snippet

        basedt = datetime.today().replace(
            hour=STARTING_HOUR, minute=00, second=00, microsecond=00
        )

        scheduling_data = []

        # 1. Fetch Scheduled Calls (Blockers)
        scheduled_calls = list(
            CallSchedule.objects.filter(Q(status="S") | Q(status="R")).values_list(
                "datentime", "interviewerid"
            )
        )

        scheduled_calls_list = []
        for scheduled_call in scheduled_calls:
            if scheduled_call[0]:
                # FIX: Convert DB time (UTC) to Local Time before formatting
                local_db_time = timezone.localtime(scheduled_call[0])
                scheduled_calls_list.append(
                    [local_db_time.strftime("%Y-%m-%d %I:%M %p"), scheduled_call[1]]
                )

        # 2. Fetch Helper Data
        vacation_data = list(
            Vacation.objects.filter(empid=int_id).values("empid", "fromdate", "todate")
        )
        workcal_data = list(
            WorkCal.objects.filter(userid=int_id).values()
        )  # Your Roster

        # 3. Fetch Alter Timings (Overrides)
        alter_timings_data = ExtendedHours.objects.filter(
            empid=int_id, status="A"
        ).values()
        alter_timings_list = {}

        # Process Alter Timings into a Dictionary keyed by Date string
        for alter in alter_timings_data:
            days_diff = (alter["todate"] - alter["fromdate"]).days + 1
            for x in range(days_diff):
                curr_alter_date = alter["fromdate"] + timedelta(days=x)
                date_str = curr_alter_date.strftime("%Y-%m-%d")

                alter_timings_list[date_str] = {
                    "starttime": alter["starttime"],
                    "workhours": alter["workhours"],
                    "userid": alter["userid"],
                }

        # 4. Main Scheduling Loop (Next 15 Days)
        for x in range(0, 15):
            hours_list = []
            slots_list = []
            status_list = []

            # Initialize Telecallers (Active Users)
            telecallers = list(
                User.objects.filter(status="A", id=int_id).values_list("id", flat=True)
            )

            # Current Date Calculation
            current_date_obj = basedt + timedelta(days=x)
            _date_str = current_date_obj.strftime("%Y-%m-%d")  # YYYY-MM-DD
            _day_name = current_date_obj.strftime("%A")  # Monday, Tuesday...
            date_formatted = current_date_obj.strftime("%a-%d-%b-%Y")  # Mon-15-Dec-2025

            # A. Remove users on Vacation
            # Check if this specific day is inside any vacation range
            current_date_start = datetime.strptime(
                _date_str + " 00:00:00", "%Y-%m-%d %H:%M:%S"
            )

            for vacation in vacation_data:
                v_from = datetime.combine(vacation["fromdate"], time.min)
                v_to = datetime.combine(vacation["todate"], time.max)

                if v_from <= current_date_start <= v_to:
                    if vacation["empid"] in telecallers:
                        telecallers.remove(vacation["empid"])

            # B. Check for Holidays
            if HolidayCal.objects.filter(holidaydt=_date_str).exists():
                # Fill entire day as Holiday
                for i in range(WORK_HOURS * 2):
                    slot_time = basedt + timedelta(minutes=30 * i)
                    hours_list.append(slot_time.strftime("%I:%M %p"))
                    status_list.append("Holiday")
                    slots_list.append([])
            else:
                # C. Generate Slots for the Day
                for i in range(0, WORK_HOURS * 2):
                    slot_dt = current_date_obj + timedelta(minutes=30 * i)
                    slot_time_str = slot_dt.strftime("%I:%M %p")
                    hours_list.append(slot_time_str)

                    # Logic to block past times
                    curr_time_limit = datetime.now() + timedelta(
                        hours=BLOCK_HOURS, minutes=30
                    )
                    is_past_or_blocked = (
                        _date_str == datetime.today().strftime("%Y-%m-%d")
                        and slot_dt <= curr_time_limit
                    )

                    if is_past_or_blocked:
                        status_list.append("Blocked")
                        slots_list.append([])
                        continue

                    # D. Determine Availability for THIS SPECIFIC SLOT

                    # Start with assumption: No one is working this slot unless proven otherwise
                    working_users_this_slot = set()

                    # We check every potential telecaller
                    for user_id in telecallers:
                        is_working = False

                        # 1. Check Alter Timings (Priority)
                        if _date_str in alter_timings_list:
                            alter_data = alter_timings_list[_date_str]
                            if alter_data["userid"] == user_id:
                                # Calculate Alter Start/End
                                start_t = alter_data["starttime"]
                                w_hours = float(
                                    alter_data["workhours"]
                                )  # Ensure float for half hours

                                start_dt_alter = datetime.combine(
                                    current_date_obj.date(), start_t
                                )
                                end_dt_alter = start_dt_alter + timedelta(hours=w_hours)

                                # Check if slot is within Alter window
                                if start_dt_alter <= slot_dt < end_dt_alter:
                                    is_working = True

                        # 2. Check Standard WorkCal (Only if no Alter override or to strictly follow requirement)
                        # Assuming Alter replaces standard roster. If not in Alter, check WorkCal.
                        else:
                            # Get all shifts for this user on this specific day name (e.g., "Monday")
                            user_shifts = [
                                w
                                for w in workcal_data
                                if w["userid"] == user_id and w["startday"] == _day_name
                            ]

                            for shift in user_shifts:
                                # Parse Shift Start
                                start_t = shift[
                                    "starttime"
                                ]  # Time object or string? Assuming Time object from DB
                                if isinstance(start_t, str):
                                    start_t = datetime.strptime(
                                        start_t, "%H:%M:%S"
                                    ).time()

                                w_hours = float(shift["hours"])

                                start_dt_shift = datetime.combine(
                                    current_date_obj.date(), start_t
                                )
                                end_dt_shift = start_dt_shift + timedelta(hours=w_hours)

                                # Check if slot is within this specific shift window
                                if start_dt_shift <= slot_dt < end_dt_shift:
                                    is_working = True
                                    break  # Found a valid shift for this slot, no need to check other shifts for same user

                        if is_working:
                            working_users_this_slot.add(user_id)

                    # E. Filter out users who are working but have a Scheduled Call (Booking)
                    available_for_slot = []
                    for user_id in working_users_this_slot:
                        # Construct key to check against scheduled calls
                        call_key = f"{_date_str} {slot_time_str}"

                        is_booked = False
                        for call in scheduled_calls_list:
                            if call[0] == call_key and call[1] == user_id:
                                is_booked = True
                                break

                        if not is_booked:
                            available_for_slot.append(user_id)

                    # F. Final Status for Slot
                    if not available_for_slot:
                        status_list.append("No_Vacancy")
                    else:
                        status_list.append("Available")

                    slots_list.append(available_for_slot)

            # Prepare Response Object
            # Convert sets/lists to required ID format
            ids = [list(s) for s in slots_list]

            dataObj = {
                "day": date_formatted,
                "hours_list": hours_list,
                "slots_list": slots_list,
                "status": status_list,
                "ids": ids,
            }
            scheduling_data.append(dataObj)

        return scheduling_data

    except Exception as e:
        import traceback

        print(traceback.format_exc())  # Helpful for debugging
        raise e


def getInterviewerCandidates(userid):
    try:

        call_details = CallSchedule.objects.filter(
            interviewerid=userid, status="S"
        ).order_by("-id")
        candidates = []

        for call_data in call_details:

            candidate = Candidate.objects.get(id=call_data.candidateid)
            jd = JobDesc.objects.get(id=candidate.jobid)

            candidates.append(
                {
                    "id": candidate.id,
                    "name": f"{candidate.firstname} {candidate.lastname}",
                    "scheduled_time": call_data.datentime.strftime("%d-%b-%Y %I:%M %p"),
                    "email": candidate.email,
                    "c_code": candidate.candidateid,
                    "jd": jd.title,
                    "scd_id": call_data.id,
                }
            )

        return candidates
    except Exception as e:
        raise


def getCandidateInterviewData(scd_id):
    try:

        resp = {
            "job_desc_data": None,
            "candidate_data": None,
            "interview_data": None,
            "screening_data": None,
            "coding_data": None,
            "profile_data": None,
            # "profiling_video_url":None
        }

        acert_domain = getConfig()["DOMAIN"]["acert"]
        endpoint = "/api/candidate-interviewdata"

        url = urljoin(acert_domain, endpoint)

        call_details = CallSchedule.objects.get(id=scd_id)

        candidate = Candidate.objects.get(id=call_details.candidateid)
        candidate_int_data = {
            "c_code": candidate.candidateid,
            "int_paperid": call_details.paper_id,
        }

        send_candidate_data = requests.post(url, json=candidate_int_data)
        response_content = send_candidate_data.content

        if response_content:
            json_data = json.loads(response_content.decode("utf-8"))
            interview_data = json_data["data"]["interviewdata"]
            screening_data = json_data["data"]["screeningdata"]
            coding_data = json_data["data"]["codingdata"]
            # profiling_video_url = json_data["data"]["profiling_video_url"]

            # if profiling_video_url:
            #     convertProfilingVideo(profiling_video_url, call_details.id)

            resp["interview_data"] = interview_data
            resp["screening_data"] = screening_data
            resp["coding_data"] = coding_data
            # resp['profiling_video_url'] = profiling_video_url

        job_desc = JobDesc.objects.get(id=candidate.jobid)

        skillsString = ""

        if job_desc:
            if job_desc.skillset:
                skillesSet = ast.literal_eval(job_desc.skillset)

                skillCount = 0
                for skill in skillesSet:
                    value = next(
                        iter(skill.values())
                    )  # Get the first value dynamically
                    skillCount += 1

                    if len(skillesSet) == skillCount:
                        skillsString += value
                    else:
                        skillsString += value + ", "

        job_desc_data = {
            "jd_title": job_desc.title,
            "role": job_desc.role,
            "location": job_desc.location,
            "skills": skillsString,
            "notes": job_desc.skillnotes,
            "instructions": call_details.instructions,
        }

        int_paper_title = (
            Workflow.objects.filter(paperid=call_details.paper_id).last().papertitle
        )
        meeting_link = call_details.meetinglink.split("api")[1]

        candidate_data = {
            "id": candidate.id,
            "name": f"{candidate.firstname} {candidate.lastname}",
            "mobile": candidate.mobile,
            "email": candidate.email,
            "code": candidate.candidateid,
            "int_paper": int_paper_title if int_paper_title else "N/A",
            "meetinglink": meeting_link,
            "schd_id": call_details.id,
        }

        if candidate.profileid:
            profile_details = getProfileDetailsService(candidate.profileid)
            resp["profile_data"] = profile_details
        
        resp["job_desc_data"] = job_desc_data
        resp["candidate_data"] = candidate_data

        return resp

    except Exception as e:
        raise


def questionsResponseService(dataObjs):
    try:
        candidate_id = dataObjs["candid__id"]
        call_schedule_id = dataObjs["candid_call_sched_id"]

        call_schd_data = CallSchedule.objects.filter(id=call_schedule_id).last()

        remark_note_data = ""

        if call_schd_data:
            remark_note_data = call_schd_data.intnotes

        ques_lst = QResponse.objects.filter(
            callscheduleid=call_schedule_id, candidateid=candidate_id
        )

        questions_lst = []

        if ques_lst:
            for ques in ques_lst:
                questions_lst.append({"q_id": ques.qid, "q_res": ques.qrate})

        return {"q_lst": questions_lst, "remark_note": remark_note_data}

    except Exception as e:
        raise


def getInterviewStatusService(dataObjs):
    try:

        call_schedule = CallSchedule.objects.get(
            id=dataObjs["schedule_id"], candidateid=dataObjs["candidate_id"]
        )

        if call_schedule.callendflag == "Y":
            return "call_ended"
        else:
            return "call_active"

    except Exception as e:
        raise


def getCdnData():
    try:

        cdn = CdnData.objects.filter().last()

        cdn_data = {"auth_key": cdn.authkey, "libraryid": cdn.libraryid}

        return cdn_data

    except Exception as e:
        raise


def interviewCompletionService(dataObjs, user_id):
    try:
        call_sch_details = CallSchedule.objects.filter(id=dataObjs["sch_id"]).last()
        call_sch_details.callendeddtt = datetime.now()
        call_sch_details.status = "C"
        call_sch_details.save()

        try:
            feedback = IvFeedback.objects.filter(
                candidateid=call_sch_details.candidateid, interviewerid=user_id
            ).last()
            feedback.gonogo = dataObjs["gonogo"]
            feedback.notes = dataObjs["notes"]
            feedback.companyid = (call_sch_details.companyid,)
            feedback.save()

        except:
            feedback = IvFeedback(
                candidateid=call_sch_details.candidateid,
                interviewerid=user_id,
                gonogo=dataObjs["gonogo"],
                notes=dataObjs["notes"],
                companyid=call_sch_details.companyid,
            )

            feedback.save()

        candidate = Candidate.objects.get(id=call_sch_details.candidateid)
        candidate.status = "I"
        candidate.save()
        jd = JobDesc.objects.get(id=candidate.jobid)
        interviewers_data = ast.literal_eval(jd.interviewers)
        interviewers = [int(item) for item in interviewers_data]
        hr_email = User.objects.get(id=call_sch_details.hrid).email

        interviewers_email_list = []

        users = User.objects.filter(status="A", companyid=candidate.companyid)

        interviewed_by = ""

        for user in users:
            if user.id in interviewers:
                interviewers_email_list.append(user.email)

                if user.id == call_sch_details.interviewerid:
                    interviewed_by = user.name

        interviewers_emails = ", ".join(interviewers_email_list)

        to_mail = f"{hr_email},{interviewers_emails}"

        interview_data = {
            "candidate_code": candidate.candidateid,
            "jd_title": jd.title,
            "interviewed_by": interviewed_by,
            "to_mail": to_mail,
            "paper_id": call_sch_details.paper_id,
            "int_notes": call_sch_details.intnotes,
        }

        acert_domain = getConfig()["DOMAIN"]["acert"]
        endpoint = "/api/interview-completion"

        url = urljoin(acert_domain, endpoint)

        send_interview_data = requests.post(url, json=interview_data)

        if candidate.profileid:
            addProfileActivityDB(candidate.profileid,"IC","Interview Completed",user_id)

    except Exception as e:
        raise


def getInterviewCandidates(userid):
    try:

        user = User.objects.get(id=userid)

        job_desc_ids = list(
            JobDesc.objects.filter(
                companyid=user.companyid, interviewers__contains=user.id
            ).values_list("id", flat=True)
        )
        candidate_ids = list(
            Candidate.objects.filter(
                companyid=user.companyid, jobid__in=job_desc_ids
            ).values_list("id", flat=True)
        )
        completed_interviews = CallSchedule.objects.filter(
            status="C", companyid=user.companyid, candidateid__in=candidate_ids
        )

        user_interviews = []

        for interview in completed_interviews:

            candidate = Candidate.objects.get(id=interview.candidateid)

            hr = User.objects.get(id=interview.hrid)
            interview = User.objects.get(id=interview.interviewerid)

            feedback = ""

            iv_feedback = IvFeedback.objects.filter(
                candidateid=candidate.id, interviewerid=user.id
            ).last()
            if iv_feedback:
                feedback = iv_feedback.gonogo

            user_interviews.append(
                {
                    "cid": candidate.id,
                    "c_code": candidate.candidateid,
                    "c_name": f"{candidate.firstname} {candidate.lastname}",
                    "c_email": candidate.email,
                    "hr": hr.name,
                    "interviewby": interview.name,
                    "feedback": feedback,
                }
            )

        return user_interviews

        # print('job_desc',job_desc)

    except Exception as e:
        raise


def getInterviewFeedback(cid, user_id):
    try:

        candidate = Candidate.objects.filter(id=cid).last()

        cdn_data = getCdnData()

        library_id = cdn_data["libraryid"]
        if candidate:

            feedback_data = ""

            interview_feedback = IvFeedback.objects.filter(
                candidateid=cid, interviewerid=user_id
            ).last()

            try:
                interview_file = (
                    InterviewMedia.objects.filter(candidateid=candidate.id)
                    .last()
                    .recorded
                )

                video_path = f"https://iframe.mediadelivery.net/embed/{library_id}/{interview_file}"

            except:
                video_path = ""

            if interview_feedback:

                feedback_data = {
                    "candidateid": interview_feedback.candidateid,
                    "name": f"{candidate.firstname} {candidate.lastname}",
                    "gonogo": interview_feedback.gonogo,
                    "notes": interview_feedback.notes,
                    "media_path": video_path,
                }

            else:
                feedback_data = {
                    "candidateid": cid,
                    "name": f"{candidate.firstname} {candidate.lastname}",
                    "gonogo": "N",
                    "notes": "",
                    "media_path": video_path,
                }

            return feedback_data

    except Exception as e:
        raise


def getCandidateWorkflowData(cid):
    try:

        candidate = Candidate.objects.filter(id=cid).last()

        candidate_data = {
            "candidate_info": None,
            "registrations_data": None,
            "feedbacks_data": None,
        }

        if candidate:

            jd = JobDesc.objects.get(id=candidate.jobid)

            source_label = ""

            if candidate.source:

                source = Source.objects.filter(
                    companyid=candidate.companyid, code=candidate.source
                ).last()

                if source:
                    source_label = f"{source.code} - {source.label}"

            else:
                source_label = "NA"

            candidate_info = {
                "cid": candidate.id,
                "c_code": candidate.candidateid,
                "firstname": candidate.firstname,
                "lastname": candidate.lastname,
                "email": candidate.email,
                "mobile": candidate.mobile,
                "jd": jd.title,
                "source_label": source_label,
            }

            candidate_data["candidate_info"] = candidate_info

            registrations = Registration.objects.filter(
                candidateid=candidate.id, companyid=candidate.companyid
            )
            notify_check = "N"
            call_completion_date = ""

            registrations_data = []

            registration_data = {
                "candidate_code": candidate.candidateid,
            }

            acert_domain = getConfig()["DOMAIN"]["acert"]
            endpoint = "/api/candiate-workflow-percentage"

            url = urljoin(acert_domain, endpoint)
            response = requests.post(url, json=registration_data)

            workflow_response_data = json.loads(response.content.decode("utf-8"))

            if registrations:

                for registration in registrations:

                    workflow = Workflow.objects.get(
                        jobid=registration.jobid, paperid=registration.paperid
                    )

                    paper_type = ""
                    call_status = ""
                    scheduled_time = ""
                    interviewer_name = ""
                    hold_percentage = ""
                    pass_percentage = ""
                    hold_check = ""

                    if workflow.papertype == "S":

                        paper_type = "Screening"
                        paper_brules = Brules.objects.get(
                            paperid=registration.paperid, jobdescid=registration.jobid
                        )
                        hold_percentage = (
                            paper_brules.holdpercentage
                            if paper_brules.holdpercentage is not None
                            else ""
                        )
                        pass_percentage = (
                            paper_brules.passscore if paper_brules.passscore else ""
                        )
                        hold_check = paper_brules.hold

                    elif workflow.papertype == "E":

                        paper_type = "Coding"
                        paper_brules = Brules.objects.get(
                            paperid=registration.paperid, jobdescid=registration.jobid
                        )
                        hold_percentage = (
                            paper_brules.holdpercentage
                            if paper_brules.holdpercentage
                            else ""
                        )
                        pass_percentage = (
                            paper_brules.passscore if paper_brules.passscore else ""
                        )
                        hold_check = paper_brules.hold

                    elif workflow.papertype == "I":
                        paper_type = "Interview"
                        call_schedule = CallSchedule.objects.filter(
                            candidateid=candidate.id, paper_id=registration.paperid
                        ).last()
                        if call_schedule:
                            call_status = call_schedule.status
                            scheduled_time = (
                                call_schedule.datentime.strftime("%d-%b-%Y %I:%M %p")
                                if call_schedule.datentime
                                else ""
                            )

                            if scheduled_time:
                                interviewer_name = User.objects.get(
                                    id=call_schedule.interviewerid
                                ).name

                            if call_schedule.status == "C":
                                notify_check = "Y"
                                call_completion_date = (
                                    call_schedule.callendeddtt.strftime(
                                        "%d-%b-%Y %I:%M %p"
                                    )
                                    if call_schedule.callendeddtt
                                    else ""
                                )
                    else:
                        paper_type = ""

                    scored_marks = 0
                    paper_marks = 0
                    score_percentage = 0
                    star_zero = ""

                    for percentage_data in workflow_response_data["data"]:

                        if percentage_data["paper_id"] == registration.paperid:
                            scored_marks = percentage_data["scored_marks"]
                            paper_marks = percentage_data["paper_marks"]
                            score_percentage = int(percentage_data["score_percentage"])
                            star_zero = percentage_data["star_zero"]

                    registrations_data.append(
                        {
                            "reg_id": registration.id,
                            "paper_title": workflow.papertitle,
                            "paperid": workflow.paperid,
                            "paper_type": workflow.papertype,
                            "type_title": paper_type,
                            "call_status": call_status,
                            "candidateid": candidate.id,
                            "reg_status": registration.status,
                            "completion_date": (
                                registration.completiondate.strftime(
                                    "%d-%b-%Y %I:%M %p"
                                )
                                if registration.completiondate
                                else ""
                            ),
                            "notify_check": notify_check,
                            "call_completion_date": call_completion_date,
                            "scheduled_time": scheduled_time,
                            "interviewer_name": interviewer_name,
                            "hold_percentage": hold_percentage,
                            "pass_percentage": pass_percentage,
                            "score_percentage": score_percentage,
                            "scored_marks": scored_marks,
                            "paper_marks": paper_marks,
                            "hold_check": hold_check,
                            "hold_range": (
                                int(pass_percentage) - 1 if pass_percentage else ""
                            ),
                            "star_zero": star_zero,
                        }
                    )

                candidate_data["registrations_data"] = registrations_data

            candidate_data["candidate_info"]["notify_check"] = notify_check

        feedback_data = feedbacksData(candidate.id)

        candidate_data["feedbacks_data"] = feedback_data

        return candidate_data

    except Exception as e:
        raise


def generateCandidateReport(cid):
    try:

        acert_domain = getConfig()["DOMAIN"]["acert"]
        endpoint = "/api/hireline-candidate-report"

        url = urljoin(acert_domain, endpoint)

        candidate_data = {"candidate_code": cid}

        candidate = Candidate.objects.get(candidateid=cid)

        branding = Branding.objects.get(companyid=candidate.companyid)

        send_candidate_data = requests.post(url, json=candidate_data)

        response_content = send_candidate_data.content

        if response_content:

            screening_data = ""
            coding_data = ""
            interview_data = ""
            feedback_data = ""

            json_data = json.loads(response_content.decode("utf-8"))

            acert_data = json_data["data"]

            root_path = BASE_DIR

            report_template_path = open(
                root_path + "/media/reports/candidate_report.html", "r"
            )
            report_template = report_template_path.read()

            screening_data = acert_data["screening_data"]
            coding_data = acert_data["coding_data"]
            interview_data = acert_data["interview_data"]

            jd = JobDesc.objects.get(id=candidate.jobid)

            updated_report = report_template.replace(
                "{candidate_id}", candidate.candidateid
            )
            updated_report = updated_report.replace(
                "{candidate_name}", f"{candidate.firstname} {candidate.lastname}"
            )
            updated_report = updated_report.replace(
                "{candidate_email}", candidate.email
            )
            updated_report = updated_report.replace(
                "{candidate_mobile}", candidate.mobile
            )

            updated_report = updated_report.replace(
                "{screening_section}", screening_data
            )
            updated_report = updated_report.replace("{coding_section}", coding_data)
            updated_report = updated_report.replace(
                "{interview_section}", interview_data
            )
            updated_report = updated_report.replace("{#jd_title#}", jd.title)
            updated_report = updated_report.replace(
                "{#comapany_logo#}",
                str(branding.logourl) if str(branding.logourl) else "",
            )

            source_label = "NA"

            if candidate.source:
                source_label = (
                    Source.objects.filter(
                        companyid=candidate.companyid, code=candidate.source
                    )
                    .last()
                    .label
                )

            updated_report = updated_report.replace("{#c_source#}", source_label)

            call_schedule = CallSchedule.objects.filter(candidateid=candidate.id).last()
            if call_schedule:

                interviewer = call_schedule.interviewerid

                if interviewer:
                    interviewer_name = User.objects.get(id=interviewer).name
                else:
                    interviewer_name = ""

                updated_report = updated_report.replace(
                    "#interviewer_name#", interviewer_name
                )

                feedbacks = feedbacksData(candidate.id)

                if feedbacks:

                    feedback_rows = ""

                    for fd_data in feedbacks:

                        fd_tr = f"""
                            <tr>
                                <td class="td_q"><p class="q_a">{fd_data['name']}</p></td>
                                <td class="td_q"><p class="q_a">{fd_data['decision']}</p></td>
                                <td class="td_q"><p class="q_a">{fd_data['notes']}</p></td>
                            </tr>
                        """
                        feedback_rows = feedback_rows + fd_tr

                    feedback_data = f"""
                        <span class="heading p-clr">Interviewer's Feedback:</span><br><br>
                        <table cellpadding=0 cellspacing=0 class="t0">
                            <thead>
                                <tr style="background-color: #808080;color:#fff">
                                    <th class="td_fd">Interviewer</th>
                                    <th class="td_fd">Decision</th>
                                    <th class="td_fd">Notes</th>
                                </tr>
                            </thead>
                            <tbody>
                                {feedback_rows}
                            </tbody>
                        </table><br><br>
                    """
            updated_report = updated_report.replace("{#feedback_data#}", feedback_data)

            output_filepath = root_path + f"/media/reports/{candidate.candidateid}.pdf"
            result_file = open(output_filepath, "w+b")

            pisa_status = pisa.CreatePDF(updated_report, dest=result_file)

            result_file.close()

            return {
                "file_path": output_filepath,
                "file_name": "report",
                "pisa_err": pisa_status.err,
            }

    except Exception as e:
        print(str(e))
        raise


def feedbacksData(cid):
    try:

        feedback = IvFeedback.objects.filter(candidateid=cid)

        int_feedbacks = []

        for job_int in feedback:

            interviewer = User.objects.get(id=job_int.interviewerid)
            notes = job_int.notes
            decision = "Hire" if job_int.gonogo == "Y" else "Not Hire"

            int_feedbacks.append(
                {"name": interviewer.name, "notes": notes, "decision": decision}
            )
        return int_feedbacks

    except Exception as e:
        raise


def jdPublishService(dataObjs, companyId):
    try:
        paperData = []
        if dataObjs["jobDescriptionId"]:

            JdData = JobDesc.objects.filter(id=dataObjs["jobDescriptionId"]).last()

            worflowData = Workflow.objects.filter(jobid=dataObjs["jobDescriptionId"])

            for test in worflowData:
                if test.paperid == None:
                    return {
                        "noPaper": "Y",
                        "paperTitle": test.papertitle,
                        "jdStatus_": JdData.status,
                    }

            if JdData:
                JdData.status = dataObjs["nextStatus_"]
                JdData.save()

            latestJD = JobDesc.objects.filter(id=dataObjs["jobDescriptionId"]).last()

            orderCounter = 1
            for test in worflowData:

                test.order = orderCounter
                orderCounter += 1
                tempDct = model_to_dict(test)
                brulesData = Brules.objects.filter(
                    companyid=companyId, workflowid=test.id
                ).last()

                if brulesData:
                    tempDct["promotPercentage"] = brulesData.passscore
                    tempDct["hold"] = brulesData.hold
                    tempDct["holdpercentage"] = brulesData.holdpercentage
                else:
                    tempDct["promotPercentage"] = None
                    tempDct["hold"] = "N"
                    tempDct["holdpercentage"] = 0

                paperData.append(tempDct)
                test.save()

            # len(paperLst) == 1

            paperLst = paperData
            newPaperLst = []
            for paper in range(len(paperLst) - 1):  # Loop until the second-last item
                tempLst = [
                    paperLst[paper],
                    paperLst[paper + 1],
                ]  # Create a list with two items
                newPaperLst.append(tempLst)

            return {
                "companyid": companyId,
                "papersData": newPaperLst,
                "jdStatus_": latestJD.status,
            }

    except Exception as e:
        raise


def notifyCandidateService(dataObjs,user):
    try:

        notify = dataObjs.get("notify")
        cid = dataObjs.get("cid")

        candidate = Candidate.objects.get(candidateid=cid)
        jd = JobDesc.objects.get(id=candidate.jobid)
        company = Company.objects.get(id=candidate.companyid)
        workflow = Workflow.objects.filter(jobid=jd.id, papertype="I").last()

        call_details = CallSchedule.objects.filter(candidateid=candidate.id).last()

        hr_mail = ""

        if call_details:
            user = User.objects.get(id=call_details.hrid)
            hr_mail = user.email

        acert_domain = getConfig()["DOMAIN"]["acert"]
        endpoint = "/api/candidate-notification"

        url = urljoin(acert_domain, endpoint)

        to_mails = f"{candidate.email}, {hr_mail}"

        candidate_data = {
            "candidate_code": cid,
            "notify": notify,
            "firstname": candidate.firstname,
            "lastname": candidate.lastname,
            "job_title": jd.title,
            "department": jd.department,
            "tomails": to_mails,
            "company_name": company.name,
            "paperid": workflow.paperid,
        }

        send_candidate_data = requests.post(url, json=candidate_data)

        registration = Registration.objects.get(
            candidateid=candidate.id, paperid=workflow.paperid
        )

        registration.status = notify
        registration.save()

        candidate.status = notify
        candidate.save()

        if candidate.profileid:

            profile = Profile.objects.get(id=candidate.profileid)

            if notify == "O":
                addProfileActivityDB(candidate.profileid,"OL","Offer letter Sent",user.id)
                profile.status = "H"
            elif notify == "R":
                profile.status = "E"

            profile.save()

    except Exception as e:
        print(str(e))
        raise


# def addNewUserService(company_id, user_data):
#     try:
#         if user_data['event'] == 'create':
#             print('-------------------------')
#             print(company_id, user_data)
#             userFind = User.objects.filter(email = user_data['userEmail']).last()
#             if userFind:
#                 return {'userAlreadyExisted':'Y'}
#             else:
#                 save_user = User(
#                     companyid = company_id,
#                     name = user_data['userName'],
#                     email = user_data['userEmail'],
#                     password = user_data['userPswd'],
#                     role = user_data['userRole'],
#                     location = user_data['newUserLocation'],
#                     status = 'A'
#                 )
#                 save_user.save()
#                 return {'userAlreadyExisted':'N','event':'created'}

#         if user_data['event'] == 'update':
#             userFind = User.objects.filter(email = user_data['userEmail']).last()
#             if userFind:
#                 userFind.name = user_data['userName']
#                 userFind.password = user_data['userPswd']
#                 userFind.location = user_data['newUserLocation']
#                 userFind.save()

#                 # return JsonResponse
#                 return {'event':'update','userid':userFind,'name':userFind.name,'pswd':userFind.password,'location':userFind.location}
#             # else:
#                 # save_user = User(
#                 #     companyid = company_id,
#                 #     name = user_data['userName'],
#                 #     email = user_data['userEmail'],
#                 #     password = user_data['userPswd'],
#                 #     role = user_data['userRole'],
#                 #     location = user_data['newUserLocation'],
#                 #     status = 'A'
#                 # )
#                 # save_user.save()

#     except Exception as e:
#         raise


def addNewUserService(company_id, user_data):
    try:
        if user_data["event"] == "create":
            userFind = User.objects.filter(email=user_data["userEmail"]).last()
            if userFind:
                return {"userAlreadyExisted": "Y"}
            else:
                userRole = Role.objects.filter(id=user_data["userRole"]).last()

                save_user = User(
                    companyid=company_id,
                    name=user_data["userName"],
                    email=user_data["userEmail"],
                    password=user_data["userPswd"],
                    role=userRole.Name,
                    location=user_data["newUserLocation"],
                    status="A",
                )
                save_user.save()

                # if save_user.role == "Recruiter":
                code = f"RC{save_user.id:03}"

                source = Source(
                    code=code,
                    label=save_user.name,
                    companyid=save_user.companyid,
                    userid=save_user.id,
                )

                source.save()

                return {
                    "userAlreadyExisted": "N",
                    "event": "created",
                    "userid": save_user.id,
                }

        if user_data["event"] == "update":
            userFind = User.objects.filter(email=user_data["userEmail"]).last()

            userAuthdata = User_data.objects.filter(username=userFind.email).last()
            if userAuthdata:
                userAuthdata.usr_password = user_data["userPswd"]
                userAuthdata.save()

            if userFind:

                userFind.name = user_data["userName"]
                userFind.password = user_data["userPswd"]
                userFind.location = user_data["newUserLocation"]
                userFind.save()

                # if userFind.role == "Recruiter":

                code = f"RC{userFind.id:03}"

                source = Source.objects.filter(
                    code=code, companyid=userFind.companyid
                ).last()

                if source:
                    if not source.label:
                        source.label = userFind.name
                    source.userid = userFind.id

                else:
                    source = Source(
                        code=code,
                        label=userFind.name,
                        companyid=userFind.companyid,
                        userid=userFind.id,
                    )

                source.save()

                # Convert userFind to a dictionary format for JSON serialization
                user_data_response = {
                    "event": "update",
                    "userid": userFind.id,
                    "name": userFind.name,
                    "pswd": userFind.password,
                    "location": userFind.location,
                }
                return user_data_response
    except Exception as e:
        raise


def changeUserstatusService(company_id, user_data):
    try:
        userid = user_data["userid"]
        userdata = User.objects.filter(id=userid).last()
        if userdata:
            userdata.status = user_data["status"]
            userdata.save()

    except Exception as e:
        raise


def deductCreditsService(company_id, paper_type, paper_id=None):
    try:

        company_account = Account.objects.get(companyid=company_id)
        company_credits = CompanyCredits.objects.get(
            companyid=company_id, transtype=paper_type
        )

        company_account.balance = company_account.balance - company_credits.credits
        company_account.save()

        workflow_data = Workflow.objects.filter(
            companyid=company_id, papertype=paper_type
        ).last()
        job_desc_data = JobDesc.objects.get(id=workflow_data.jobid)
        transaction = Credits(
            companyid=company_id,
            transdatetime=datetime.now(),
            transtype="D",
            papertype=paper_type,
            points=company_credits.credits,
            user=job_desc_data.createdby,
            transid=paper_id,
            balance=company_account.balance,
        )
        transaction.save()
    except Exception as e:
        raise


def getCompanyCreditsUsageService(dataObjs):
    try:
        company_credits_usage = (
            Credits.objects.filter(companyid=dataObjs["cid"]).values().order_by("-id")
        )

        usage_list = []

        for usage in company_credits_usage:
            if usage["user"]:
                user = User.objects.get(id=usage["user"]).name
            else:
                user = ""
            usage_dict = dict(usage)
            # usage_dict["transtype"] = paper_type
            # usage_dict["paper_title"] = paper_title
            usage_dict["user"] = user
            usage_dict["credit"] = ""
            usage_dict["debit"] = ""
            usage_dict["description"] = ""
            usage_dict["transdatetime"] = usage["transdatetime"].strftime(
                "%d-%b-%Y %I:%M %p"
            )
            if usage["transtype"] == "D":
                workflow = Workflow.objects.filter(
                    companyid=dataObjs["cid"],
                    papertype=usage["papertype"],
                    paperid=usage["transid"],
                ).last()
                JD = JobDesc.objects.get(id=workflow.jobid)
                paper_type = const_paper_types.get(usage["papertype"], "")
                paper_title = workflow.papertitle if workflow else "-"
                # usage_dict["transdatetime"] = usage["transdatetime"].strftime("%d-%b-%Y %I:%M %p")
                usage_dict[
                    "description"
                ] = f"""{paper_type}
                {paper_title} - JD ({JD.title})"""
                usage_dict["debit"] = f'{usage_dict["points"]}'
            if usage["transtype"] == "C":
                payments = Payments.objects.get(id=usage_dict["transid"])
                if payments.modeofpay == "T":
                    usage_dict[
                        "description"
                    ] = f"""Free Trial
                    {usage_dict['points']} Credits added
                    """
                else:
                    usage_dict[
                        "description"
                    ] = f"""Payment Successfull {payments.amount} INR
                    {usage_dict['points']} Credits added
                    """
                usage_dict["credit"] = f'{usage_dict["points"]}'

            usage_list.append(usage_dict)

        return usage_list
    except Exception as e:
        raise


def getCompanyData(cid):
    try:

        company_data = ""

        company = Company.objects.filter(id=cid).last()

        if company:

            branding = Branding.objects.filter(companyid=company.id).last()

            keywords = ["Linkedin", "Facebook", "Instagram", "Youtube", "Twitter"]

            # Initialize variables in a dictionary
            social_links_vars = {key: "" for key in keywords}

            if branding:
                social_links_string = branding.sociallinks

                if social_links_string:

                    social_links = social_links_string.strip(",").split(", ")

                    for link in social_links:
                        if link:
                            key, value = link.split(":", 1)  # Split at the first colon
                            if key in keywords:
                                social_links_vars[key] = value

                Linkedin = social_links_vars["Linkedin"]
                Facebook = social_links_vars["Facebook"]
                Instagram = social_links_vars["Instagram"]
                Youtube = social_links_vars["Youtube"]
                Twitter = social_links_vars["Twitter"]

            company_data = {
                "id": company.id,
                "name": company.name if company.name else "",
                "email": company.email if company.email else "",
                "website": company.website if company.website else "",
                "phone": company.phone1 if company.phone1 else "",
                "company_type": company.companytype if company.companytype else "",
                "address": company.address1 if company.address1 else "",
                "city": company.city if company.city else "",
                "country": company.country if company.country else "",
                "Linkedin": Linkedin if Linkedin else "",
                "Facebook": Facebook if Facebook else "",
                "Instagram": Instagram if Instagram else "",
                "Youtube": Youtube if Youtube else "",
                "Twitter": Twitter if Twitter else "",
                "contact_person": (
                    company.contactperson if company.contactperson else ""
                ),
            }

        return company_data

    except Exception as e:
        raise


def demoUserService(dataObjs):
    try:

        company_data = CompanyData(
            companyname=dataObjs["company-name"],
            companyemail=dataObjs["email"],
            location=dataObjs["location"],
            contactperson=dataObjs["contact-person"],
            registerationtime=datetime.now(),
        )

        company_data.save()

        return company_data.id

    except Exception as e:
        raise


def updateCandidateWorkflowService(dataObjs):
    try:

        registration = Registration.objects.filter(id=dataObjs["reg_id"]).last()

        if registration:

            candidate = Candidate.objects.get(id=registration.candidateid)

            job_desc = JobDesc.objects.get(id=candidate.jobid)

            workflow_data = {
                "candidate_code": candidate.candidateid,
                "status": None,
                "paperid": registration.paperid,
                "paper_type": registration.papertype,
                "companyid": candidate.companyid,
                "job_desc": job_desc.description if job_desc.description else "",
                "job_title": job_desc.title if job_desc.title else "",
            }

            acert_domain = getConfig()["DOMAIN"]["acert"]
            endpoint = "/api/update-candidate-workflow"

            url = urljoin(acert_domain, endpoint)

            if dataObjs["status"] == "P":

                workflow_data["status"] = dataObjs["status"]

                current_workflow = Workflow.objects.filter(
                    companyid=candidate.companyid,
                    jobid=job_desc.id,
                    paperid=registration.paperid,
                ).last()

                if current_workflow:

                    next_workflow = (
                        Workflow.objects.filter(
                            companyid=candidate.companyid,
                            jobid=job_desc.id,
                            id__gt=current_workflow.id,
                        )
                        .order_by("id")
                        .first()
                    )

                    company_account = Account.objects.get(companyid=candidate.companyid)
                    company_credits = CompanyCredits.objects.get(
                        companyid=candidate.companyid, transtype=next_workflow.papertype
                    )

                    if company_account.balance >= company_credits.credits:

                        send_workflow_data = requests.post(url, json=workflow_data)

                        response_content = send_workflow_data.content

                        if response_content:
                            json_data = json.loads(response_content.decode("utf-8"))

                            if json_data["statusCode"] == 0:

                                c_registration = Registration(
                                    candidateid=candidate.id,
                                    paperid=next_workflow.paperid,
                                    registrationdate=candidate.registrationdate,
                                    companyid=candidate.companyid,
                                    jobid=candidate.jobid,
                                    status="I",
                                    papertype=next_workflow.papertype,
                                )

                                c_registration.save()

                                if c_registration.papertype == "I":
                                    call_schedule = CallSchedule(
                                        candidateid=candidate.id,
                                        paper_id=next_workflow.paperid,
                                        status="N",
                                        companyid=candidate.companyid,
                                    )
                                    call_schedule.save()
                                
                                if candidate.profileid:
                                    if c_registration.papertype == "S":
                                        addProfileActivityDB(candidate.profileid,"SC","Screening Sent")
                                    elif c_registration.papertype == "E":
                                        addProfileActivityDB(candidate.profileid,"CT","Coding Test Sent")

                                if registration.papertype == "S":
                                    candidate.status = "S"
                                    registration.status = "P"
                                    candidate.save()
                                    registration.save()

                                elif registration.papertype == "E":
                                    candidate.status = "E"
                                    registration.status = "P"
                                    candidate.save()
                                    registration.save()

                                deductCreditsService(
                                    candidate.companyid,
                                    c_registration.papertype,
                                    c_registration.paperid,
                                )

                            else:
                                return 2
                    else:
                        return 1

            elif dataObjs["status"] == "R":
                workflow_data["status"] = dataObjs["status"]

                send_workflow_data = requests.post(url, json=workflow_data)

                response_content = send_workflow_data.content

                if response_content:
                    json_data = json.loads(response_content.decode("utf-8"))

                    if json_data["statusCode"] == 0:
                        registration.status = "F"
                        registration.save()
                    else:
                        return 2

            return 0

    except Exception as e:
        raise


def dashBoardGraphDataService(companyid):
    try:

        dashboard_data = {
            "line_graph_data": None,
            "jd_reg_data": None,
        }

        company = Company.objects.filter(id=companyid).last()

        if company:

            # JD Registrations Data - Bar graph

            # job_desc_ids = list(JobDesc.objects.filter(companyid=company.id).exclude(status__in=['D','I']).values_list('id', flat=True)[:5])

            jd_ids_with_dashboard = list(
                JobDesc.objects.filter(companyid=company.id, dashboardflag="Y")
                .exclude(status__in=["D", "I"])
                .order_by("-createdon")
                .values_list("id", flat=True)[:5]
            )

            if len(jd_ids_with_dashboard) < 5:
                jd_ids_with_dashboard += list(
                    JobDesc.objects.filter(companyid=company.id)
                    .exclude(status__in=["D", "I"])
                    .exclude(id__in=jd_ids_with_dashboard)
                    .order_by("-createdon")
                    .values_list("id", flat=True)[: (5 - len(jd_ids_with_dashboard))]
                )

            job_descs = JobDesc.objects.filter(id__in=jd_ids_with_dashboard).order_by(
                "-createdon"
            )

            jd_reg_data = {
                "jdtitle": [],
                "screening_count": [],
                "coding_count": [],
                "interview_count": [],
                "offered_count": [],
            }

            jd_titles = []
            screening_count = []
            coding_count = []
            interview_count = []
            offered_count = []

            for job_data in job_descs:

                jd_analysis = JdAnalysis.objects.filter(
                    companyid=company.id, jobid=job_data.id
                )

                sc_reg_count = 0
                cd_reg_count = 0
                int_reg_count = 0
                offer_count = 0

                if jd_analysis:
                    for analysis_data in jd_analysis:
                        if analysis_data.papertype == "S":
                            sc_reg_count += analysis_data.registration
                        elif analysis_data.papertype == "E":
                            cd_reg_count += analysis_data.registration
                        elif analysis_data.papertype == "I":
                            int_reg_count += analysis_data.registration
                            offer_count += analysis_data.efficiency or 0

                job_desc = JobDesc.objects.get(id=job_data.id)

                jd_titles.append(job_desc.title)
                screening_count.append(sc_reg_count)
                coding_count.append(cd_reg_count)
                interview_count.append(int_reg_count)
                offered_count.append(offer_count)

            jd_reg_data["jdtitle"] = jd_titles
            jd_reg_data["screening_count"] = screening_count
            jd_reg_data["coding_count"] = coding_count
            jd_reg_data["interview_count"] = interview_count
            jd_reg_data["offered_count"] = offered_count

            # line graph data or day wise registrations

            line_graph = {"dates": [], "screening": [], "coding": [], "interview": []}

            current_date = timezone.now().date()
            start_date = current_date - timedelta(days=15)
            date_range = [start_date + timedelta(days=i) for i in range(16)]

            date_map = {
                date.strftime("%Y-%m-%d"): {"screening": 0, "coding": 0, "interview": 0}
                for date in date_range
            }

            queryset = (
                Registration.objects.filter(
                    registrationdate__gte=start_date, companyid=company.id
                )
                .values("papertype", "registrationdate")
                .annotate(count=Count("id"))
            )

            for entry in queryset:
                date_key = entry["registrationdate"].strftime("%Y-%m-%d")
                papertype = entry["papertype"]

                if date_key in date_map:
                    if papertype == "S":  # Screening
                        date_map[date_key]["screening"] += entry["count"]
                    elif papertype == "E":  # Coding
                        date_map[date_key]["coding"] += entry["count"]
                    elif papertype == "I":  # Interview
                        date_map[date_key]["interview"] += entry["count"]

            line_graph["dates"] = [date.strftime("%d-%m-%Y") for date in date_range]
            line_graph["screening"] = [date_map[date]["screening"] for date in date_map]
            line_graph["coding"] = [date_map[date]["coding"] for date in date_map]
            line_graph["interview"] = [date_map[date]["interview"] for date in date_map]

            dashboard_data["line_graph_data"] = line_graph
            dashboard_data["jd_reg_data"] = jd_reg_data

        return dashboard_data

    except Exception as e:
        print(str(e))
        raise


def getDashboardData(company_id):
    try:

        dashboard_data = {"durations_data": None, "sources_data": None}

        company = Company.objects.filter(id=company_id).last()

        if company:

            # Duration data

            durations_data = {
                "screening_min": 0,
                "screening_avg": 0,
                "screening_max": 0,
                "screening_min_lt": 0,
                "screening_avg_lt": 0,
                "screening_max_lt": 0,
                "coding_min": 0,
                "coding_avg": 0,
                "coding_max": 0,
                "coding_min_lt": 0,
                "coding_avg_lt": 0,
                "coding_max_lt": 0,
                "interview_min": 0,
                "interview_avg": 0,
                "interview_max": 0,
                "interview_min_lt": 0,
                "interview_avg_lt": 0,
                "interview_max_lt": 0,
            }

            papertype_mapping = {"S": "screening", "E": "coding", "I": "interview"}

            paperwise_duration = (
                JdAnalysis.objects.filter(companyid=company.id)
                .values("papertype")
                .annotate(
                    avg_duration_min=Avg("durationmin"),
                    avg_duration_avg=Avg("durationavg"),
                    avg_duration_max=Avg("durationmax"),
                    avg_leadtime_min=Avg("leadtimemin"),
                    avg_leadtime_avg=Avg("leadtimeavg"),
                    avg_leadtime_max=Avg("leadtimemax"),
                )
            )

            for duration_data in paperwise_duration:

                key_prefix = papertype_mapping.get(duration_data["papertype"])

                if key_prefix:

                    durations_data[f"{key_prefix}_min"] = (
                        format_duration(duration_data["avg_duration_min"])
                        if duration_data["avg_duration_min"]
                        else 0
                    )
                    durations_data[f"{key_prefix}_avg"] = (
                        format_duration(duration_data["avg_duration_avg"])
                        if duration_data["avg_duration_avg"]
                        else 0
                    )
                    durations_data[f"{key_prefix}_max"] = (
                        format_duration(duration_data["avg_duration_max"])
                        if duration_data["avg_duration_max"]
                        else 0
                    )
                    durations_data[f"{key_prefix}_min_lt"] = (
                        format_duration(duration_data["avg_leadtime_min"])
                        if duration_data["avg_leadtime_min"]
                        else 0
                    )
                    durations_data[f"{key_prefix}_avg_lt"] = (
                        format_duration(duration_data["avg_leadtime_avg"])
                        if duration_data["avg_leadtime_avg"]
                        else 0
                    )
                    durations_data[f"{key_prefix}_max_lt"] = (
                        format_duration(duration_data["avg_leadtime_max"])
                        if duration_data["avg_leadtime_max"]
                        else 0
                    )

            # Sources Data

            company_sources = Source.objects.filter(companyid=company_id)

            if company_sources:

                sources_data = []

                for source in company_sources:

                    source_data = JdAnalysis.objects.filter(
                        companyid=company_id, sourcecode=source.code
                    )

                    screening_count = 0
                    screening_efficiency = 0
                    coding_count = 0
                    coding_efficiency = 0
                    interview_count = 0
                    interview_efficiency = 0

                    for data in source_data:

                        if data.papertype == "S":
                            screening_count += data.registration or 0
                            screening_efficiency += data.efficiency or 0

                        if data.papertype == "E":
                            coding_count += data.registration or 0
                            coding_efficiency += data.efficiency or 0

                        if data.papertype == "I":
                            interview_count += data.registration or 0
                            interview_efficiency += data.efficiency or 0

                    screening_efficiency_percentage = (
                        (screening_efficiency / screening_count) * 100
                        if screening_count != 0
                        else 0
                    )
                    coding_efficiency_percentage = (
                        (coding_efficiency / coding_count) * 100
                        if coding_count != 0
                        else 0
                    )
                    interview_efficiency_percentage = (
                        (interview_efficiency / interview_count) * 100
                        if interview_count != 0
                        else 0
                    )

                    sources_data.append(
                        {
                            "source_label": source.label,
                            "screening_count": screening_count,
                            "coding_count": coding_count,
                            "interview_count": interview_count,
                            "screening_efficiency_percentage": int(
                                screening_efficiency_percentage
                            ),
                            "coding_efficiency_percentage": int(
                                coding_efficiency_percentage
                            ),
                            "interview_efficiency_percentage": int(
                                interview_efficiency_percentage
                            ),
                            "offered": interview_efficiency,
                        }
                    )

                dashboard_data["sources_data"] = sources_data

            dashboard_data["durations_data"] = durations_data

            return dashboard_data

    except Exception as e:
        raise


def format_duration(minutes):
    try:

        minutes = int(minutes)  # Ensure it's an integer

        if minutes < 60:
            return f"{minutes} minutes"

        elif minutes < 1440:  # 1440 minutes = 1 day

            hours = minutes // 60
            remaining_minutes = minutes % 60
            hour_str = "hour" if hours == 1 else "hours"

            return (
                f"{hours} {hour_str} {remaining_minutes} minutes"
                if remaining_minutes
                else f"{hours} {hour_str}"
            )

        else:
            days = minutes // 1440
            remaining_minutes = minutes % 1440
            hours = remaining_minutes // 60
            remaining_minutes = remaining_minutes % 60

            day_str = "day" if days == 1 else "days"
            hour_str = "hour" if hours == 1 else "hours"
            result = f"{days} {day_str}"

            if hours:
                result += f" {hours} {hour_str}"

            if remaining_minutes:
                result += f" {remaining_minutes} minutes"

            return result

    except Exception as e:
        raise


def getCompanySourcesData(company_id):
    try:

        sources = Source.objects.filter(companyid=company_id).order_by('label')

        if sources:

            sources_data = []

            for source in sources:

                sources_data.append(
                    {"id": source.id, "code": source.code, "label": source.label}
                )

            return sources_data

    except Exception as e:
        raise


def mapUploadedCandidateFields(company_id, user, fileObjs):
    try:

        uploaded_excel = fileObjs.get("file")

        if uploaded_excel:

            excel_filename = os.path.splitext(uploaded_excel.name)
            excel_extension = excel_filename[1]

            formatted_company_id = str(company_id).zfill(3)

            user_file_name = f"{formatted_company_id}_candidates{excel_extension}"

            excel_path = os.path.join(
                settings.MEDIA_ROOT, "uploads", "candidate_upload", user_file_name
            )

            with open(excel_path, "wb+") as user_file:
                for chunk in uploaded_excel.chunks():
                    user_file.write(chunk)

            root_path = getConfig()["DIR"]["root_path"]

            file_path = f"{root_path}/app_api/functions/data_configs/mapping.json"

            mappings_data = validate_excel_with_json(file_path, excel_path)

            candidate_upload_file = Uploads.objects.filter(
                companyid=company_id, type="C"
            ).last()

            if candidate_upload_file:

                candidate_upload_file.filepath = excel_path
                candidate_upload_file.filename = user_file_name
                candidate_upload_file.status = "U"
                candidate_upload_file.save()

            else:
                uploaded_file = Uploads(
                    companyid=company_id,
                    type="C",
                    filepath=excel_path,
                    filename=user_file_name,
                    status="U",
                )

                uploaded_file.save()

            return mappings_data

    except Exception as e:
        raise


def processAddCandidateService(company_id, dataObjs, user_id):
    try:
        candidate_upload_file = Uploads.objects.filter(
            companyid=company_id, type="C"
        ).last()

        if candidate_upload_file:
            candidate_upload_file.status = "I"
            candidate_upload_file.save()

        # Format the company ID to be 3 digits
        formatted_company_id = str(company_id).zfill(3)

        # Define the file storage directory
        upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads", "candidate_upload")

        # List all files in the directory
        files = os.listdir(upload_dir)

        # Look for the file that matches the pattern
        matching_file = None
        for file_name in files:
            if file_name.startswith(f"{formatted_company_id}_candidates"):
                matching_file = file_name
                break

        if matching_file:

            # Path to the Excel file
            excel_file_path = os.path.join(upload_dir, matching_file)

            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(excel_file_path)

            # Extract column index mapping from the dataObjs
            column_mapping = dataObjs["columns-data"]

            # Additional data needed
            jd_id = dataObjs["jd"]
            begin_from = Workflow.objects.filter(jobid=jd_id).first().paperid
            source_code = dataObjs["source-code"]

            # List to hold status for each row
            status_list = []

            # Loop through each row of the DataFrame
            for index, row in df.iterrows():
                try:
                    # Extract values using the column mapping
                    first_name = (
                        row.iloc[column_mapping.get("First Name", -1)]
                        if column_mapping.get("First Name", -1) != -1
                        else None
                    )
                    last_name = (
                        row.iloc[column_mapping.get("Last Name", -1)]
                        if column_mapping.get("Last Name", -1) != -1
                        else None
                    )
                    email = (
                        row.iloc[column_mapping.get("Email", -1)]
                        if column_mapping.get("Email", -1) != -1
                        else None
                    )
                    mobile = (
                        row.iloc[column_mapping.get("Mobile", -1)]
                        if column_mapping.get("Mobile", -1) != -1
                        else None
                    )

                    # Handle NaN values
                    first_name = None if pd.isna(first_name) else first_name
                    last_name = None if pd.isna(last_name) else last_name
                    email = None if pd.isna(email) else email
                    mobile = None if pd.isna(mobile) else mobile

                    # Initialize status message
                    skip_reasons = []

                    # Check for missing or invalid fields
                    if not first_name:
                        skip_reasons.append("Missing First Name")
                    if not email:
                        skip_reasons.append("Missing Email")
                    elif not is_valid_email(email):
                        skip_reasons.append("Invalid Email")

                    # If there are any issues, skip the row and record the reasons
                    if skip_reasons:
                        status_list.append(f"Skipped: {', '.join(skip_reasons)}")
                        # print(f"Skipping row {index + 1}: {', '.join(skip_reasons)}")
                        continue

                    # Prepare candidate data
                    candidate_data = {
                        "firstname": first_name,
                        "lastname": last_name,
                        "email": email,
                        "mobile": mobile,
                        "jd": dataObjs["jd"],
                        "begin-from": begin_from,
                        "source-code": source_code,
                    }

                    try:
                        # Call the function and handle errors
                        c_data = addCandidateDB(
                            candidate_data, company_id, None, user_id
                        )

                        if c_data == "insufficient_credits":
                            status_list.append("Skipped: Insufficient Credits")
                            # print(f"Skipping row {index + 1}: Insufficient Credits")
                        elif c_data == "candidate_already_registered":
                            status_list.append("Skipped: Candidate Already Registered")
                            # print(f"Skipping row {index + 1}: Candidate Already Registered")
                        else:
                            # print(f"Adding candidate: {first_name} {last_name}, Email: {email}, Mobile: {mobile}")
                            status_list.append("Candidate is added")
                    except Exception as db_error:
                        # print(f"Error adding candidate at row {index + 1}: {str(db_error)}")
                        status_list.append(f"Skipped: Error adding candidate")

                except Exception as row_error:
                    # print(f"Error processing row {index + 1}: {str(row_error)}")
                    status_list.append(f"Skipped: Error occurred ({str(row_error)})")

            # Add the status column to the DataFrame
            df["hirelines-status"] = status_list

            # Save the updated DataFrame back to Excel
            report_file = f"{formatted_company_id}_candidate_report.xlsx"
            output_file_path = os.path.join(
                settings.MEDIA_ROOT, "uploads", "candidate_upload", report_file
            )
            df.to_excel(output_file_path, index=False)

            # Load the workbook to remove borders from the first row
            workbook = load_workbook(output_file_path)
            sheet = workbook.active

            # Define no-border style
            no_border = Border(
                left=Side(border_style=None),
                right=Side(border_style=None),
                top=Side(border_style=None),
                bottom=Side(border_style=None),
            )

            # Apply no-border style to header row cells
            for cell in sheet[1]:  # First row (headers)
                cell.border = no_border

            # Save the workbook
            workbook.save(output_file_path)

            if candidate_upload_file:

                candidate_upload_file.status = "C"
                candidate_upload_file.save()

            # print(f"Processing complete. Updated Excel file saved to: {output_file_path}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise


def is_valid_email(email):
    """Basic regex pattern to validate email format."""
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None


def checkJdCandidateRegistrationService(dataObjs):
    try:

        registrations = Registration.objects.filter(jobid=dataObjs["jd_id"]).last()

        if registrations:
            registrations_flag = "Y"
        else:
            registrations_flag = "N"

        return registrations_flag

    except Exception as e:
        raise


def getCompanyCandidateUploadData(company_id):
    try:

        upload_data = {}

        candidate_uploaded_data = Uploads.objects.filter(
            companyid=company_id, type="C"
        ).last()

        if candidate_uploaded_data:
            upload_data["status"] = candidate_uploaded_data.status
            upload_data["display_flag"] = "Y"
        else:
            upload_data["display_flag"] = "N"

        return upload_data

    except Exception as e:
        raise


def downloadUploadReportService(company_id):
    try:

        uploaded_data = Uploads.objects.filter(
            type="C", companyid=company_id, status="C"
        ).last()

        if uploaded_data:
            formatted_company_id = str(company_id).zfill(3)
            report_file = f"{formatted_company_id}_candidate_report.xlsx"
            report_file_path = os.path.join(
                settings.MEDIA_ROOT, "uploads", "candidate_upload", report_file
            )

            return {
                "report_file_path": report_file_path,
                "report_file_name": report_file,
            }

    except Exception as e:
        raise


# def convertProfilingVideo(video_url, schedule_id):
#     try:

#         call_details = CallSchedule.objects.get(id=schedule_id)
#         candidate = Candidate.objects.get(id=call_details.candidateid)

#         file_name = f"{call_details.id}_{candidate.id}_profilevideo.wav"

#         profiling_dir = os.path.join(settings.MEDIA_ROOT, "uploads","profiling_videos")
#         os.makedirs(profiling_dir, exist_ok=True)

#         parsed_url = urlparse(video_url)
#         filename = os.path.basename(parsed_url.path)
#         video_path = os.path.join(profiling_dir, filename)

#         wav_path = os.path.join(profiling_dir, file_name)

#         # Checking if already profiling audio exists
#         if os.path.exists(wav_path):
#             print(f"File already converted: {wav_path}")
#             return wav_path

#         # Download the video
#         response = requests.get(video_url, stream=True)
#         if response.status_code != 200:
#             raise Exception(f"Failed to download video")

#         # Save the video locally
#         with open(video_path, "wb") as f:
#             for chunk in response.iter_content(chunk_size=8192):
#                 f.write(chunk)

#         # Converting video to WAV format using FFmpeg
#         ffmpeg.input(video_path).output(wav_path, format="wav", acodec="pcm_s16le", ar="44100").run(overwrite_output=True)

#         # Deleting video file after converting to wav file
#         os.remove(video_path)

#     except Exception as e:
#         print(f"Error: {e}")
#         raise


def getProfileDetailsService(pid):
    try:

        profile = Profile.objects.filter(id=pid).values().first()

        if not profile:
            return {}

        profile_det = {
            "id": profile.get("id"),
            # "firstname": profile.get("firstname", ""),
            "middlename": profile.get("middlename", ""),
            # "lastname": profile.get("lastname", ""),
            "firstname": (profile.get("firstname", "").capitalize()if profile.get("firstname")else ""),
            
            "lastname": (profile.get("lastname", "").capitalize()if profile.get("lastname")else ""),
            "title": profile.get("title", ""),
            "email": profile.get("email", ""),
            "mobile": profile.get("mobile", ""),
            "dateofcreation": profile.get("dateofcreation", ""),
            "linkedin": profile.get("linkedin", ""),
            "dateofbirth": profile.get("dateofbirth", ""),
            "nativeof": profile.get("nativeof", ""),
            "facebook": profile.get("facebook", ""),
            "passportnum": profile.get("passportnum", ""),
            "strength": profile.get("strength",""),
            "educationscore" : profile.get("educationscore","0"),
            "awardsscore"   : profile.get("awardsscore","0"),
            "certificatesscore"  : profile.get("certificatesscore","0"),
            "experiencescore" : profile.get("experiencescore","0"),
            "projectsscore" : profile.get("projectsscore","0"),
            "skillsscore" : profile.get("skillsscore","0"),
        }

        education_list = (
            ProfileEducation.objects.filter(profileid=pid)
            .values("course", "institute", "yearfrom", "yearto", "grade")
            .order_by("sequence")
        )

        profile_det["education"] = list(education_list)

        experience_list = (
            ProfileExperience.objects.filter(profileid=pid)
            .values("jobtitle", "company", "yearfrom", "yearto")
            .order_by("sequence")
        )

        profile_det["experience"] = list(experience_list)

        total_exp = 0
        for exp in experience_list:
            try:
                yf = int(exp.get("yearfrom", 0))
                yt = int(exp.get("yearto", 0))

                if yt >= yf:
                    total_exp += yt - yf
            except:
                pass

        profile_det["final_experience"] = f"{total_exp} Years"

        skills = (
            ProfileSkills.objects.filter(profileid=pid)
            .values("primaryskills", "secondaryskills")
            .first()
        )

        profile_det["skills"] = (
            skills if skills else {"primaryskills": "", "secondaryskills": ""}
        )

    
        primary = profile_det["skills"].get("primaryskills", "")
        secondary = profile_det["skills"].get("secondaryskills", "")

        skills_list = []

        if primary:
            skills_list.extend(
                [s.strip() for s in primary.split(",") if s.strip()]
            )

        if secondary:
            skills_list.extend(
                [s.strip() for s in secondary.split(",") if s.strip()]
            )

        profile_det["skills_display"] = ", ".join(skills_list)


        projects_list = (
            ProfileProjects.objects.filter(profileid=pid)
            .values(
                "projectname",
                "clientname",
                "roleplayed",
                "skillsused",
                "yearsfrom",
                "yearsto",
            )
            .order_by("sequence")
        )

        profile_det["projects"] = list(projects_list)

        awards_list = (
            ProfileAwards.objects.filter(profileid=pid)
            .values("awardname", "year")
            .order_by("sequence")
        )
        profile_det["awards"] = list(awards_list)

        cert_list = (
            ProfileCertificates.objects.filter(profileid=pid)
            .values("certname", "year")
            .order_by("sequence")
        )
        profile_det["certificates"] = list(cert_list)

        # ADDRESS (NEW)
        address_list = list(
            ProfileAddress.objects.filter(profileid=pid).values(
                "addline1", "addline2", "city", "state", "country", "zipcode"
            )
        )

        profile_det["address"] = address_list

        branding = (
            Branding.objects.filter(companyid=profile.get("companyid"))
            .values("logourl")
            .first()
        )
        resume = Resume.objects.filter(id=profile.get("resumeid")).values("docparserid").first()

        profile_det["docparserid"] = resume["docparserid"] if resume else None
        

        if branding and branding.get("logourl"):
            profile_det["logo"] = branding.get("logourl")
        else:
            profile_det["logo"] = None

        return profile_det

    except Exception as e:
        raise

def getProfileactivityDetailsService(pid):
    try:
        
        activity_list = (
            ProfileActivity.objects
            .filter(profileid=pid)
            .values()
            .order_by("-sequence")
        )

        final_list = []

       
        lookup_map = {
            l["lookupparam1"]: l["lookupname"]
            for l in Lookupmaster.objects.filter(
                lookupid=1,     
                status='A'
            ).values("lookupparam1", "lookupname")
        }

        user_ids = {
            row.get("acvityuserid")
            for row in activity_list
            if row.get("acvityuserid")
        }

        user_map = {
            u["id"]: u["name"]
            for u in User.objects.filter(id__in=user_ids)
            .values("id", "name")
        }

      
        job_title = (
            Profile.objects
            .filter(id=pid)
            .values("title", "firstname", "lastname")
            .first()
        )

        for row in activity_list:

            dt = row.get("datentime")
            formatted_dt = (
                dt.strftime("%d-%b-%Y %I:%M %p")
                if dt and hasattr(dt, "strftime")
                else ""
            )

            code = row.get("activitycode")
            userid = row.get("acvityuserid")

            final_list.append({
                "id": row.get("id"),
                "profileid": row.get("profileid"),
                "sequence": row.get("sequence"),
                "datentime": formatted_dt,
                "activitycode": code,

                
                "activity_text": lookup_map.get(code, row.get("activityname")),

                "activityuserid": userid,
                "activityusername": user_map.get(userid, ""),
                "activityremarks": row.get("activityremarks"),
                "activitystatus": row.get("activitystatus"),
                "activityname": row.get("activityname"),

                "jobtitle": job_title["title"] if job_title else "",
                # "firstname": job_title["firstname"] if job_title else "",
                # "lastname": job_title["lastname"] if job_title else "",
                "firstname": (job_title["firstname"].capitalize()if job_title and job_title.get("firstname") else ""),
                "lastname": (job_title["lastname"].capitalize()if job_title and job_title.get("lastname")else ""),
            })

        return final_list

    except Exception as e:
        print("getProfileactivityDetailsService error:", e)
        raise





def getResumeData(user_data, filters=None):
    try:

        resumes_data = []

        if user_data.role == "HR-Admin":
            sources = Source.objects.filter(companyid=user_data.companyid)
            if filters and filters.get("source_ids"):
                sources = sources.filter(id__in=filters["source_ids"])
        else:
            sources = Source.objects.filter(userid=user_data.id)

        source_ids = sources.values_list("id", flat=True)

        resumes = (
            Resume.objects.filter(sourceid__in=source_ids)
            .exclude(status="D")
            .order_by("-datentime")
        )

        if resumes:

            for resume in resumes:

                source = sources.filter(id=resume.sourceid).first()

                resumes_data.append(
                    {
                        "id": resume.id,
                        "name": resume.filename or "",
                        "source": source.label or "",
                        "date": (
                            resume.datentime.strftime("%d-%b-%Y %I:%M %p")
                            if resume.datentime
                            else ""
                        ),
                        "status": resume.status,
                    }
                )

        return resumes_data

    except Exception as e:
        raise


def getEmailFetchUsers():
    try:

        users = list(
            User.objects.filter(status="A").values(
                "id", "email", "companyid", "name"
            )
        )
        return users

    except Exception as e:
        raise


def softDeleteResume(rid):
    try:

        resume = Resume.objects.get(id=rid)
        resume.status = "D"
        resume.save()

    except Exception as e:
        raise


def getProfileData(pid, user_data):
    try:

        profile = Profile.objects.filter(id=pid, companyid=user_data.companyid).last()

        if not profile:
            return None

        profile_address = ProfileAddress.objects.filter(profileid=pid).last()

        profile_data = {
            "personal": None,
            "education": None,
            "experience": None,
            "projects": None,
            "awards": None,
            "certificates": None,
            "skills": None,
            "resume_file": None,
        }

        # Profile details
        personal_details = {
            "title": profile.title or "",
            "firstname": profile.firstname or "",
            "middlename": profile.middlename or "",
            "lastname": profile.lastname or "",
            "email": profile.email or "",
            "mobile": profile.mobile or "",
            "linkedin": profile.linkedin or "",
            "facebook": profile.facebook or "",
            "passportnum": profile.passportnum or "",
            "fathername": profile.fathername or "",
            "nativeof": profile.nativeof or "",
            "status": profile.status,
            "strength":profile.strength or "",
            "dateofbirth": (
                profile.dateofbirth.strftime("%Y-%m-%d") if profile.dateofbirth else ""
            ),
            "addline1": profile_address.addline1 if profile_address else "",
            "addline2": profile_address.addline2 if profile_address else "",
            "city": profile_address.city if profile_address else "",
            "state": profile_address.state if profile_address else "",
            "country": profile_address.country if profile_address else "",
            "zipcode": profile_address.zipcode if profile_address else ""
        }

        # Education
        education_data = ProfileEducation.objects.filter(profileid=profile.id).order_by(
            "sequence"
        )

        profile_education = []

        if education_data:

            for education in education_data:

                profile_education.append(
                    {
                        "course": education.course or "",
                        "institute": education.institute or "",
                        "yearfrom": education.yearfrom or "",
                        "yearto": education.yearto or "",
                        "grade": education.grade or "",
                    }
                )

        # Experience
        experience_data = ProfileExperience.objects.filter(
            profileid=profile.id
        ).order_by("sequence")

        profile_experience = []

        if experience_data:

            for experience in experience_data:

                profile_experience.append(
                    {
                        "jobtitle": experience.jobtitle or "",
                        "company": experience.company or "",
                        "yearfrom": experience.yearfrom or "",
                        "yearto": experience.yearto or "",
                    }
                )

        # Projects
        projects_data = ProfileProjects.objects.filter(profileid=profile.id).order_by(
            "sequence"
        )

        profile_projects = []

        if projects_data:

            for project in projects_data:

                profile_projects.append(
                    {
                        "projectname": project.projectname or "",
                        "clientname": project.clientname or "",
                        "roleplayed": project.roleplayed or "",
                        "skillsused": project.skillsused or "",
                        "yearsfrom": project.yearsfrom or "",
                        "yearsto": project.yearsto or "",
                    }
                )

        # Awards
        awards_data = ProfileAwards.objects.filter(profileid=profile.id).order_by(
            "sequence"
        )

        profile_awards = []

        if awards_data:

            for award in awards_data:

                profile_awards.append(
                    {
                        "awardname": award.awardname or "",
                        "year": award.year or "",
                    }
                )

        # Cerificates
        certificates_data = ProfileCertificates.objects.filter(
            profileid=profile.id
        ).order_by("sequence")

        profile_certificates = []

        if certificates_data:

            for certificate in certificates_data:

                profile_certificates.append(
                    {
                        "certname": certificate.certname or "",
                        "year": certificate.year or "",
                    }
                )

        skills_data = ProfileSkills.objects.filter(profileid=profile.id).last()

        profile_skills = []

        if skills_data and skills_data.primaryskills:
            profile_skills = skills_data.primaryskills.split(",")

        file_base64 = ""

        if profile.resumeid:

            resume_file = ResumeFile.objects.get(resumeid=profile.resumeid)
            file_base64 = base64.b64encode(resume_file.filecontent).decode("utf-8")

        profile_data["personal"] = personal_details
        profile_data["experience"] = profile_experience
        profile_data["education"] = profile_education
        profile_data["projects"] = profile_projects
        profile_data["awards"] = profile_awards
        profile_data["certificates"] = profile_certificates
        profile_data["skills"] = profile_skills
        profile_data["resume_file"] = f"data:application/pdf;base64,{file_base64}"

        return profile_data

    except Exception as e:
        raise


def generateBrandedProfile(profile_id, user_data):
    try:

        profile_details = getProfileDetailsService(profile_id)

        company = Company.objects.get(id=user_data.companyid)

        # print("profile_details", profile_details)

        root_path = BASE_DIR

        resume_template_path = open(
            root_path + "/media/branded_resumes/branded_resume_template.html", "r"
        )

        resume_template = resume_template_path.read()

        updated_resume = resume_template.replace(
            "{#comapany_logo#}",
            profile_details["logo"] if profile_details["logo"] else "",
        )
        updated_resume = updated_resume.replace(
            "{#creation_date#}", profile_details["dateofcreation"].strftime("%d-%B-%Y")
        )
        updated_resume = updated_resume.replace("{#title#}", profile_details["title"])
        updated_resume = updated_resume.replace("{#firstname#}", profile_details["firstname"])
        updated_resume = updated_resume.replace("{#lastname#}", profile_details["lastname"])
        updated_resume = updated_resume.replace("{#email#}", profile_details["email"])
        updated_resume = updated_resume.replace(
            "{#dob#}",
            (
                profile_details["dateofbirth"].strftime("%d-%m-%Y")
                if profile_details["dateofbirth"]
                else ""
            ),
        )
        updated_resume = updated_resume.replace("{#linkedin#}", profile_details["linkedin"] if profile_details["linkedin"] else "")
        updated_resume = updated_resume.replace("{#nativeof#}",profile_details["nativeof"] if profile_details["nativeof"] else "")
        updated_resume = updated_resume.replace("{#final_experience#}", profile_details["final_experience"])
        updated_resume = updated_resume.replace("{#user_name#}", user_data.name)
        updated_resume = updated_resume.replace("{#company_name#}", company.name)
        updated_resume = updated_resume.replace("{#strength#}", f"{profile_details['strength']}%" if profile_details["strength"] else "")

        education_data = ""

        if profile_details["education"]:
            for education in profile_details["education"]:
                education_data += f"""
                    <li class="custom-list">  { education["course"]} - { education["institute"] } ({ education["yearfrom"] } - { education["yearto"] }) - Grade: { education["grade"] } </li>
                """
        else:
            education_data = """
                <li class="custom-list">No education details available</li>
            """

        experience_data = ""

        if profile_details["experience"]:
            for experience in profile_details["experience"]:
                experience_data += f"""
                    <li class="custom-list">  { experience["jobtitle"]} at { experience["company"] } ({ experience["yearfrom"] } - { experience["yearto"] })</li>
                """

        else:
            experience_data = """
                <li class="custom-list">No Experience</li>
            """

        skills_data = ""

        if profile_details["skills"]["primaryskills"]:
            skills_data = f"""
                <li class="custom-list">{profile_details["skills"]["primaryskills"]}</li>
            """
        else:
            skills_data = """
                <li class="custom-list">No Skills</li>
            """

        projects_data = ""

        if profile_details["projects"]:
            for project in profile_details["projects"]:
                projects_data += f"""
                    <li class="custom-list">  { project["projectname"]} - { project["clientname"] }, Role : { project["roleplayed"] } , Skills Used : { project["skillsused"] } ({ project["yearsfrom"] } - { project["yearsto"] })</li>
                """

        else:
            projects_data = """
                <li class="custom-list">No Projects</li>
            """

        certificates_data = ""

        if profile_details["certificates"]:
            for certificate in profile_details["certificates"]:
                certificates_data += f"""
                    <li class="custom-list">  { certificate["certname"]} - { certificate["year"] }</li>
                """
        else:
            certificates_data = """
                <li class="custom-list">No Certificates</li>
            """

        awards_data = ""

        if profile_details["awards"]:
            for award in profile_details["awards"]:
                awards_data += f"""
                    <li class="custom-list">  { award["awardname"]} - { award["year"] }</li>
                """
        else:
            awards_data = """
                <li class="custom-list">No Awards</li>
            """

        updated_resume = updated_resume.replace("{#education_data#}", education_data)
        updated_resume = updated_resume.replace("{#experience_data#}", experience_data)
        updated_resume = updated_resume.replace("{#skills_data#}", skills_data)
        updated_resume = updated_resume.replace("{#projects_data#}", projects_data)
        updated_resume = updated_resume.replace(
            "{#certificates_data#}", certificates_data
        )
        updated_resume = updated_resume.replace("{#awards_data#}", awards_data)

        output_filepath = root_path + f"/media/branded_resumes/resume_{profile_id}.pdf"
        result_file = open(output_filepath, "w+b")

        pisa_status = pisa.CreatePDF(updated_resume, dest=result_file)
        result_file.close()

        file_name = f"{profile_details['firstname']} {profile_details['title']} {profile_details['final_experience']}"

        return {
            "file_path": output_filepath,
            "file_name": file_name or "",
            "pisa_err": pisa_status.err,
        }

    except Exception as e:
        print(str(e))
        raise


def getSlotsAvailable(cid):
    """
    Main function to find available interview slots for a candidate's job.

    :param cid: Candidate ID.
    :return: List of available 30-minute slots.
    """
    try:
        # 1. Get Job Interviewer IDs
        candidate = Candidate.objects.get(id=cid)

        jd = JobDesc.objects.get(id=candidate.jobid)
        candidate_id = candidate.id
        call_schedule = CallSchedule.objects.filter(candidateid=candidate_id).first()

        status = call_schedule.status if call_schedule else None

        job_title = jd.title
        company_id = jd.companyid
        company = Company.objects.get(id=company_id)
        company_name = company.name
        if jd.interviewers:
            # Safely evaluate the string list of interviewer IDs (e.g., '["101", "102"]')
            jd_interviewers_raw = ast.literal_eval(jd.interviewers)
            # Ensure the list contains only integers
            job_interviewer_ids = [int(i) for i in jd_interviewers_raw]
        else:
            job_interviewer_ids = []

        if not job_interviewer_ids:
            # Handle case where no interviewers are assigned to the job
            print(f"No interviewers found for job ID {candidate.jobid}.")
            return []

        # 2. Call the new logic function
        slots_available = get_open_slots(job_interviewer_ids)

        return slots_available, job_title, company_name, status

    except Candidate.DoesNotExist:
        print(f"Error: Candidate with ID {cid} not found.")
        return []
    except JobDesc.DoesNotExist:
        print(
            f"Error: Job Description for candidate {cid} (Job ID {candidate.jobid}) not found."
        )
        return []
    except Exception as e:
        # Log the error and re-raise (or handle gracefully in a web context)
        print(f"An unexpected error occurred: {e}")
        # raise # Uncomment if you want errors to halt execution
        return []


def get_full_day_name(date_obj):
    return date_obj.strftime("%A")


def get_open_slots(
    job_interviewer_ids,
    num_days=3,
    slot_duration_minutes=30,
    scheduled_call_buffer_minutes=30,
):
    """
    Returns available slots considering multiple shifts per day per user.
    """

    # --- 1. SETUP ---
    # Naive for "Wall Clock" (Calendar loops), Aware for DB comparisons
    now_naive = datetime.now()
    now_aware = timezone.now()

    # --- 2. FETCH AND GROUP WORK CALENDARS ---
    # We fetch ALL rows.
    # CRITICAL: One user can have multiple rows (Shifts), so we group them in a list.
    work_cals = WorkCal.objects.filter(userid__in=job_interviewer_ids)

    # Structure: { userid: [WorkCal_Obj1, WorkCal_Obj2, ...] }
    work_cal_map = defaultdict(list)
    for wc in work_cals:
        if wc.userid is not None:
            work_cal_map[wc.userid].append(wc)

    # --- 3. FETCH BOOKED SLOTS ---
    end_date_limit = now_aware + timedelta(days=num_days + 1)
    scheduled_calls = CallSchedule.objects.filter(
        Q(status="S") | Q(status="R"),
        interviewerid__in=job_interviewer_ids,
        datentime__gte=now_aware,
        datentime__lte=end_date_limit,
    ).order_by("datentime")

    unavailable_slots = {iid: [] for iid in job_interviewer_ids}
    buffer_timedelta = timedelta(minutes=scheduled_call_buffer_minutes)

    for call in scheduled_calls:
        start_time = call.datentime
        # Block from StartTime to (StartTime + Buffer)
        end_time = start_time + buffer_timedelta
        unavailable_slots[call.interviewerid].append((start_time, end_time))

    # --- 4. CALCULATE SLOTS ---
    slots_available_per_interviewer = {iid: [] for iid in job_interviewer_ids}
    slot_timedelta = timedelta(minutes=slot_duration_minutes)

    # Helper to clean day names (Handle "Monday " vs "Monday" vs "Mon")
    def clean_day(d_name):
        return d_name.strip().lower()[:3] if d_name else ""

    for day_offset in range(num_days):
        # Determine the date and the day name (e.g., "Monday")
        target_date = (now_naive + timedelta(days=day_offset)).date()
        target_day_full = target_date.strftime("%A")
        target_day_abbr = clean_day(target_day_full)  # e.g. "mon"

        # Define the earliest possible start time for this specific day
        if day_offset == 0:
            # For TODAY: Slots must start after 'Now'
            day_min_time = timezone.make_aware(
                now_naive, timezone.get_current_timezone()
            )
        else:
            # For FUTURE DAYS: Slots can start from 00:00
            start_of_day = datetime.combine(target_date, time(0, 0))
            day_min_time = timezone.make_aware(
                start_of_day, timezone.get_current_timezone()
            )

        # Check every interviewer
        for interviewer_id in job_interviewer_ids:
            # Get all shifts defined for this user
            all_shifts = work_cal_map.get(interviewer_id, [])

            # Filter shifts that match the Current Loop Day
            todays_shifts = []
            for wc in all_shifts:
                # Compare cleaned DB value with cleaned Target Day
                # This handles "Monday" == "Monday" and "Mon" == "Monday"
                wc_day = clean_day(wc.startday)
                if wc_day == target_day_abbr:
                    todays_shifts.append(wc)

            if not todays_shifts:
                continue  # No work scheduled for this user on this day

            # Process EACH shift found for today
            for shift in todays_shifts:
                # 1. Check WeekOffs
                # (If explicitly marked as weekoff, skip even if a shift exists)
                w_off1 = clean_day(shift.weekoff1)
                w_off2 = clean_day(shift.weekoff2)

                if target_day_abbr in [w_off1, w_off2]:
                    continue

                try:
                    # 2. Parse Start Time and Duration
                    if not shift.starttime or not shift.hours:
                        continue

                    # Build Shift Start/End (Aware Datetimes)
                    naive_shift_start = datetime.combine(target_date, shift.starttime)
                    shift_start = timezone.make_aware(
                        naive_shift_start, timezone.get_current_timezone()
                    )

                    work_hours = float(shift.hours)
                    shift_end = shift_start + timedelta(hours=work_hours)

                    # 3. Determine actual Slot Generation Start
                    # Start at the later of: The Shift Start OR The Constraint (Now)
                    current_slot_start = max(shift_start, day_min_time)

                    # 4. Align to 30-minute grid
                    # Reset seconds/microseconds
                    current_slot_start = current_slot_start.replace(
                        second=0, microsecond=0
                    )

                    # If 10:10 -> Move to 10:30
                    remainder = current_slot_start.minute % slot_duration_minutes
                    if remainder != 0:
                        add_mins = slot_duration_minutes - remainder
                        current_slot_start += timedelta(minutes=add_mins)

                    # If alignment pushed it before "Now" (on current day), push it forward
                    if day_offset == 0 and current_slot_start < day_min_time:
                        current_slot_start += slot_timedelta

                    current_slot_end = current_slot_start + slot_timedelta

                    # 5. Generate Slots
                    while current_slot_end <= shift_end:

                        # Check against booked calls
                        is_booked = False
                        user_bookings = unavailable_slots.get(interviewer_id, [])

                        for b_start, b_end in user_bookings:
                            # Standard Overlap: (StartA < EndB) and (EndA > StartB)
                            if (
                                current_slot_start < b_end
                                and current_slot_end > b_start
                            ):
                                is_booked = True
                                break

                        if not is_booked:
                            slots_available_per_interviewer[interviewer_id].append(
                                {"start": current_slot_start, "end": current_slot_end}
                            )

                        # Next slot
                        current_slot_start = current_slot_end
                        current_slot_end = current_slot_start + slot_timedelta

                except Exception as e:
                    print(f"Error processing shift {shift.id}: {e}")
                    continue

    # --- 5. MERGE RESULTS ---
    all_available_slots = {}
    for iid, slots in slots_available_per_interviewer.items():
        for slot in slots:
            key_iso = slot["start"].isoformat()
            if key_iso not in all_available_slots:
                all_available_slots[key_iso] = {
                    "start_time": key_iso,
                    "end_time": slot["end"].isoformat(),
                    "available_interviewers": [],
                }
            if iid not in all_available_slots[key_iso]["available_interviewers"]:
                all_available_slots[key_iso]["available_interviewers"].append(iid)

    return sorted(all_available_slots.values(), key=lambda x: x["start_time"])



def getRecruitersData(jdid,companyid):
    try:

        recruiters = User.objects.filter(companyid=companyid,role="Recruiter",status="A")
        jd = JobDesc.objects.get(id=jdid)
        jd_recruiters = jd.recruiterids

        selected_recruiters = []

        if jd_recruiters:

            # Convert "1,2,3" → [1, 2, 3]
            recruiter_ids = [
                int(rid.strip())
                for rid in jd_recruiters.split(",")
                if rid.strip().isdigit()
            ]

            selected_recruiters = recruiters.filter(id__in=recruiter_ids)

        return {
            "all_recruiters": recruiters,
            "selected_recruiters": selected_recruiters
        }

    except Exception as e:
        raise
    
def send_resume_to_docparser(resumefile_id):
    """
    Send ResumeFile to doc parser API and return docparser_id if successful
    """
    try:
        resume_file = ResumeFile.objects.get(id=resumefile_id)
    except ResumeFile.DoesNotExist:
        print(f"ResumeFile {resumefile_id} not found")
        return None
    base_url = getConfig()['DOMAIN']['docparser']  # e.g. http://localhost:8002
    url = f"{base_url}/api/add-document-to-queue"

    # Detect file type
    def detect_file_type(file_bytes: bytes):
        if file_bytes.startswith(b"%PDF"):
            return "pdf", "application/pdf"
        if file_bytes.startswith(b"\xD0\xCF\x11\xE0"):
            return "doc", "application/msword"
        if file_bytes.startswith(b"PK\x03\x04"):
            return "docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        return "unknown", "application/octet-stream"

    file_ext, mime_type = detect_file_type(resume_file.filecontent)

    files = {
        "file": (resume_file.filename, resume_file.filecontent, mime_type)
    }

    data = {
        "filename": resume_file.filename,
        "filetype": file_ext,
        "company": "GSSPEC",
        "application": "Hirelines",
        "documenttype": "Resume"
    }

    try:
        response = requests.post(url, files=files, data=data, timeout=10)
        response.raise_for_status()
        resp_json = response.json()
        print(f"Doc parser API response: {resp_json}")

        # Assuming your API returns docparser_id in `data.document_id`
        return resp_json.get("data", {}).get("docparser_id")
    except Exception as e:
        print(f"⚠️ Failed to call doc parser API for ResumeFile {resumefile_id}: {e}")
        return None



# def getRecritmentDashboardData(
#     company_id,
#     user_role=None,
#     logged_recruiter_id=None,
#     selected_recruiter=None,
#     month_value=None
# ):


#     now = datetime.now()

   
#     if month_value:
#         year, month = map(int, month_value.split("-"))
#     else:
#         year, month = now.year, now.month

#     start_date = datetime(year, month, 1)
#     if month == 12:
#         end_date = datetime(year + 1, 1, 1)
#     else:
#         end_date = datetime(year, month + 1, 1)

 
#     qs = ProfileActivity.objects.none()

 
#     profile_ids = Profile.objects.filter(
#         companyid=company_id
#     ).values_list("id", flat=True)


#     qs = ProfileActivity.objects.filter(
#         profileid__in=profile_ids,
#         datentime__gte=start_date,
#         datentime__lt=end_date
#     )

#     if user_role == "Recruiter":
#         qs = qs.filter(acvityuserid=logged_recruiter_id)

#     elif user_role == "HR-Admin":
#         if selected_recruiter:
#             qs = qs.filter(acvityuserid=selected_recruiter)

#     activity_counts = qs.values("activitycode").annotate(
#         total=Count("id")
#     )

#     activity_map = {
#         row["activitycode"]: row["total"]
#         for row in activity_counts
#     }
#     if month_value:
#         sel_year, sel_month = map(int, month_value.split("-"))
#     else:
#         sel_year, sel_month = now.year, now.month

#     is_current_month = (
#         sel_year == now.year and sel_month == now.month
#     )

#     if is_current_month:
#         comparison_text = "than current Month"
#     else:
#         comparison_text = "than last Month"
    
#     submitted = activity_map.get("PC", 0)
#     profiled = activity_map.get("SL", 0)
#     rejected = activity_map.get("RJ", 0)
#     sent_client = activity_map.get("CL", 0)
#     rejected_client = activity_map.get("RC", 0)
#     selected_client = activity_map.get("CS", 0)
#     waiting_feedback = activity_map.get("WF", 0)


#     def percent(value, total):
#         if total == 0:
#             return 0
#         return round((value / total) * 100, 1)
    
    

 
#     return {
#         # counts
#         "submitted": submitted,
#         "profiled": profiled,
#         "rejected": rejected,
#         "sent_client": sent_client,
#         "rejected_client": rejected_client,
#         "selected_client": selected_client,
#         "waiting_feedback": waiting_feedback,

#         # percentages (based on submitted)
#         "submitted_percentage": 100 if submitted else 0,
#         "profiled_percentage": percent(profiled, submitted),
#         "rejected_percentage": percent(rejected, submitted),
#         "sent_client_percentage": percent(sent_client, submitted),
#         "rejected_client_percentage": percent(rejected_client, submitted),
#         "selected_client_percentage": percent(selected_client, submitted),
#         "waiting_feedback_percentage": percent(waiting_feedback, submitted),
#         "comparison_text": comparison_text

#     }


from django.db.models import Sum

def getRecritmentDashboardData(
    company_id,
    user_role=None,
    logged_recruiter_id=None,
    selected_recruiter=None,
    month_value=None
):

    now = datetime.now()

    if month_value:
        year, month = map(int, month_value.split("-"))
    else:
        year, month = now.year, now.month

  
    qs = ProfileAnalysis.objects.filter(
        companyid=company_id,
        year=year,
        month=month
    )

 
    if user_role == "Recruiter":
        qs = qs.filter(userid=logged_recruiter_id)

    elif user_role == "HR-Admin" and selected_recruiter:
        qs = qs.filter(userid=selected_recruiter)

  
    activity_counts = qs.values("activitycode").annotate(
        total=Sum("profilescount")
    )

    activity_map = {
        row["activitycode"]: row["total"] or 0
        for row in activity_counts
    }


    is_current_month = (
        year == now.year and month == now.month
    )

    comparison_text = (
        "current month" if is_current_month else "last month"
    )

    submitted = activity_map.get("PC", 0)
    profiled = activity_map.get("SL", 0)
    rejected = activity_map.get("RJ", 0)
    sent_client = activity_map.get("CL", 0)
    rejected_client = activity_map.get("RC", 0)
    selected_client = activity_map.get("CS", 0)
    waiting_feedback = activity_map.get("WF", 0)

   
    def percent(value, total):
        if total == 0:
            return 0
        return round((value / total) * 100)

  
    return {
        "submitted": submitted,
        "profiled": profiled,
        "rejected": rejected,
        "sent_client": sent_client,
        "rejected_client": rejected_client,
        "selected_client": selected_client,
        "waiting_feedback": waiting_feedback,
        "submitted_percentage": 100 if submitted else 0,
        "profiled_percentage": percent(profiled, submitted),
        "rejected_percentage": percent(rejected, submitted),
        "sent_client_percentage": percent(sent_client, profiled),
        "selected_client_percentage": percent(selected_client, profiled),
        "rejected_client_percentage": percent(rejected_client, profiled),
        "waiting_feedback_percentage": percent(waiting_feedback, profiled),
        "comparison_text": comparison_text
    }


def getWorkspaces(user_data):
    try:

        workspaces_data = []

        workspaces = Workspace.objects.filter(createdby=user_data.id).order_by("-createdat")

        rec_jds = list(JobDesc.objects.filter(recruiterids__regex=rf'(^|,){user_data.id}(,|$)',status="A").order_by("-createdon").values("id","title"))

        if workspaces:

            for workspace in workspaces:

                client = Client.objects.get(id=workspace.clientid)

                workspaces_data.append({
                    "id": workspace.id,
                    "clientid": client.id,
                    "client": client.name,
                    "project": workspace.project,
                    "notes": workspace.notes if workspace.notes else "",
                    "startdate": workspace.startdate.strftime("%d-%B-%Y") if workspace.startdate else "",
                    "startdate_db": workspace.startdate if workspace.startdate else None,
                    "jd_ids":workspace.jd_ids if workspace.jd_ids else None,
                    "status": workspace.status
                })
        
        return workspaces_data, rec_jds

    except Exception as e:
        raise


def getCompanyClients(user_data):
    try:

        clients = []

        company_clients = Client.objects.filter(companyid=user_data.companyid,status="A")

        if company_clients:
            for client in company_clients:
                clients.append({
                    "id":client.id,
                    "name": client.name
                })

        return clients

    except Exception as e:
        raise


def getWorkspaceData(user_data,wid):
    try:

        assigned_jds = []

        workspace = Workspace.objects.get(id=wid)
        client = Client.objects.get(id=workspace.clientid)

        jd_ids = [int(jd_id) for jd_id in workspace.jd_ids] if workspace.jd_ids else []

        rec_jds = JobDesc.objects.filter(id__in=jd_ids,status="A").order_by("-createdon")
        # print("workspace",jd_ids)
        # print("workspace",type(jd_ids))
        # print("rec_jds",rec_jds)
        for recjd in rec_jds:
            assigned_jds.append({
                "jdid":recjd.id,
                "title":recjd.title,
                "expmin":recjd.expmin,
                "expmax":recjd.expmax,
                "department":recjd.department,
                "positions":recjd.positions,
            })

        workspace_data = {
            "wid": workspace.id,
            "client": client.name,
            "project": workspace.project,
            "jds_data": assigned_jds
        }

        return workspace_data
    
    except Exception as e:
        raise


def getJdProfileData(dataObjs,user_data):
    try:
        job_desc = JobDesc.objects.get(id=dataObjs["jdid"])

        shortlisted_profiles = []
        matched_profiles = []

        profiles = Profile.objects.filter(companyid=user_data.companyid).exclude(status__in=["D"])
        # profiles = Profile.objects.filter(companyid=user_data.companyid).exclude(status__in=["R","O","E"])

        jd_profile_data = calculateJDProfileMatching(job_desc.id,profiles)

        match_map = {
            item["profile_id"]: item
            for item in jd_profile_data
        }

        user_source = Source.objects.filter(companyid=user_data.companyid,userid=user_data.id).last()
        
        for profile in profiles:

            match_info = match_map.get(profile.id, {})

            exp_strength = int(round(match_info.get("exp_strength", 0)))
            skill_strength = int(round(match_info.get("skill_strength", 0)))
            overall_strength = int(round((skill_strength * 0.6) + (exp_strength * 0.4)))
            matched_skills = ",".join(s.capitalize() for s in match_info.get("matched_skills", []))

            candidate = Candidate.objects.filter(profileid=profile.id,jobid=dataObjs["jdid"]).last()
            if candidate:
                c_status = const_candidate_status.get(candidate.status, "")
                if candidate.source == user_source.code:
                    shortlisted_profiles.append({
                        "id":profile.id,
                        "firstname":profile.firstname,
                        "middlename":profile.middlename,
                        "lastname":profile.lastname,
                        "email":profile.email,
                        "profile_strength": profile.strength if profile.strength else 0,
                        "exp_strength": exp_strength,
                        "total_experience": int(match_info.get("total_experience", 0)),
                        "skill_strength": skill_strength,
                        "matched_skills":matched_skills,
                        "overall_strength": overall_strength,
                        "candidate_status":c_status
                    })

            else:
                matched_profiles.append({
                    "id":profile.id,
                    "firstname":profile.firstname,
                    "middlename":profile.middlename,
                    "lastname":profile.lastname,
                    "email":profile.email,
                    "profile_strength": profile.strength if profile.strength else 0,
                    "exp_strength": exp_strength,
                    "total_experience": int(match_info.get("total_experience", 0)),
                    "skill_strength": skill_strength,
                    "matched_skills":matched_skills,
                    "overall_strength": overall_strength,
                })

        matched_profiles.sort(key=lambda x: x["overall_strength"],reverse=True)

        primary_skills = ""

        if job_desc.skillset:
            skillesSet = ast.literal_eval(job_desc.skillset)

            skillCount = 0
            for skill in skillesSet:
                value = next(
                    iter(skill.values())
                )  # Get the first value dynamically
                skillCount += 1

                if len(skillesSet) == skillCount:
                    primary_skills += value
                else:
                    primary_skills += value + ", "

        return {
            "jdid":job_desc.id,
            "title":job_desc.title,
            "expmin":job_desc.expmin,
            "expmax":job_desc.expmax,
            "jd_skills_primary":primary_skills,
            "shortlisted_profiles":shortlisted_profiles,
            "matched_profiles":matched_profiles,
        }

    except Exception as e:
        raise


def shortlistProfileService(dataObjs,user_data):
    try:
        workflow_data = Workflow.objects.filter(jobid=dataObjs["jdid"],order=1).last()

        if workflow_data:
            candidate_obj = {}
            profile = Profile.objects.get(id=dataObjs["profile_id"])

            candidate_obj['firstname'] = profile.firstname if profile.firstname else ""
            candidate_obj['lastname'] = profile.lastname if profile.lastname else ""
            candidate_obj['email'] = profile.email
            candidate_obj['mobile'] = profile.mobile if profile.mobile else ""
            candidate_obj['jd'] = dataObjs["jdid"]
            candidate_obj['begin-from'] = workflow_data.paperid

            source = Source.objects.filter(userid=user_data.id,companyid=user_data.companyid).last()
            
            if source:
                candidate_obj["source-code"] = source.code

            candidate = addCandidateDB(candidate_obj,user_data.companyid,None,user_data.id)

            if 'candidateid' in candidate:
                new_candidate = Candidate.objects.get(id=candidate["candidateid"])
                new_candidate.profileid = profile.id
                new_candidate.save()

                if candidate["papertype"] == "S":
                    addProfileActivityDB(profile.id,"SC","Screening Sent",user_data.id)
                elif candidate["papertype"] == "E":
                    addProfileActivityDB(profile.id,"CT","Coding Test Sent",user_data.id)

            profile.status = "I"
            profile.save()

            return candidate

    except Exception as e:
        raise


def get_default_email_template_service(company_id):
    try:
     
        company = Company.objects.get(id=company_id)
        company_name = company.name
        company_website = company.website
        company_email = company.email

       
    
        branding = Branding.objects.filter(companyid=company_id).first()
        if not branding:
            branding = Branding.objects.filter(companyid=0).first()
            brandinglogo=Branding.logourl
           
     


   
      
    
        branding_logo=branding.logourl
        

        
        social_links = {}
        if branding and branding.sociallinks:
            items = branding.sociallinks.split(",")

            for item in items:
                if ":" in item:
                    platform, url = item.split(":", 1)
                    platform = platform.strip()
                    url = url.strip()

                    if url and url != "#":
                        social_links[platform] = url

        
        all_platforms = ["Linkedin", "Facebook", "Youtube", "Twitter", "Instagram"]

        if social_links:
            platforms_to_show = social_links.keys()   
        else:
            platforms_to_show = all_platforms          

        
        media_path = f"{getConfig()['DOMAIN']['acert']}/static/lib/img/social_links_logos/"

        footer_icon = """
            <a style="text-decoration:none; margin:0 5px;" href="{url}" target="_blank">
                <img style="width:34px; padding:3px;" src="{icon}" alt="{platform}" />
            </a>
        """

        footer_div_html = f"""
        <div id="previewSocialIcons">
            {''.join(
                footer_icon.format(
                    url=social_links.get(platform, "#"),
                    icon=f"{media_path}{platform}.png",
                    platform=platform
                )
                for platform in platforms_to_show
            )}
        </div>
        """

       
        email_temp = Email_template.objects.filter(company_id=company_id).first()
        

        
        if not email_temp:
            acert_url = f"{getConfig()['DOMAIN']['acert']}/api/get-default-email"
            res = requests.post(acert_url, timeout=10)
            data = res.json()

            if data.get("statusCode") != 0:
                return None

            raw_email_body = data["data"]["email_body"]
            
            email_body = raw_email_body.replace("[footer_div]", footer_div_html)
            

            return {
                **data["data"],
                "email_body": email_body,
                "branding": {
                    "content": branding.content if branding else "",
                    "logourl": str(branding.logourl) if branding and branding.logourl else "",
                    "social_links": social_links,
                },
                "company_name": company_name,
                "company_website": company_website,
                "company_email": company_email,
            }

        
        email_body = email_temp.email_body.replace("[footer_div]", footer_div_html)

        return {
            "id": email_temp.id,
            "template_name": email_temp.template_name,
            "paper_type": email_temp.paper_type,
            "email_subject": email_temp.email_subject,
            "email_body": email_body,
            "template_heading": email_temp.template_heading,
            "sender_email": email_temp.sender_email,
            "sender_label": email_temp.sender_label,
            "email_attachment": email_temp.email_attachment or "",
            "email_attachment_name": email_temp.email_attachment_name or "",
            "branding": {
                "content": branding.content if branding else "",
                "logourl": str(branding.logourl) if branding and branding.logourl else "",
                "social_links": social_links,
            },

            "company_name": company_name,
            "company_website": company_website,
            "company_email": company_email,
        }

    except Exception as e:
        print("Email template service error:", e)
        return None



from calendar import monthrange

def dashBoardDataService(
    company_id,
    user_role=None,
    logged_recruiter_id=None,
    selected_recruiter=None,
    month_value=None
):
    try:
        now = datetime.now()

        if month_value:
            year, month = map(int, month_value.split("-"))
        else:
            year, month = now.year, now.month

    
        if year == now.year and month == now.month:
            end_date = now.date()
        else:
            last_day = monthrange(year, month)[1]
            end_date = date(year, month, last_day)

        start_date = end_date - timedelta(days=14)

        date_range = [
            start_date + timedelta(days=i)
            for i in range(15)
        ]

  
        qs = ProfileAnalysis.objects.filter(companyid=company_id)

   
        if start_date.year == end_date.year and start_date.month == end_date.month:
            # Same month
            qs = qs.filter(
                year=start_date.year,
                month=start_date.month,
                day__gte=start_date.day,
                day__lte=end_date.day
            )
        else:
            # Cross month (Dec → Jan)
            qs = qs.filter(
                Q(
                    year=start_date.year,
                    month=start_date.month,
                    day__gte=start_date.day
                )
                |
                Q(
                    year=end_date.year,
                    month=end_date.month,
                    day__lte=end_date.day
                )
            )

        if user_role == "Recruiter":
            qs = qs.filter(userid=logged_recruiter_id)

        elif user_role == "HR-Admin" and selected_recruiter:
            qs = qs.filter(userid=selected_recruiter)

       
        qs = qs.values("year", "month", "day", "activitycode").annotate(
            total=Sum("profilescount")
        )

    
        date_map = {
            d.strftime("%Y-%m-%d"): {
                "submitted": 0,
                "profiled": 0,
                "rejected": 0,
                "sent_client": 0,
                "rejected_client": 0,
                "selected_client": 0,
                "waiting_feedback": 0,
            }
            for d in date_range
        }

        activity_map = {
            "PC": "submitted",
            "SL": "profiled",
            "RJ": "rejected",
            "CL": "sent_client",
            "RC": "rejected_client",
            "CS": "selected_client",
            "WF": "waiting_feedback",
        }

        for row in qs:
            date_key = f"{row['year']}-{row['month']:02d}-{row['day']:02d}"

            if date_key in date_map:
                field = activity_map.get(row["activitycode"])
                if field:
                    date_map[date_key][field] += row["total"] or 0

       
        line_graph = {
            "dates": [d.strftime("%d-%m-%Y") for d in date_range],
            "submitted": [],
            "profiled": [],
            "rejected": [],
            "sent_client": [],
            "rejected_client": [],
            "selected_client": [],
            "waiting_feedback": [],
        }

        for d in date_range:
            key = d.strftime("%Y-%m-%d")
            for k in line_graph:
                if k != "dates":
                    line_graph[k].append(date_map[key][k])

        return {
            "line_graph_data": line_graph
        }

    except Exception as e:
        raise
def getHiringManagersData(companyid,user_mail):
    
    try:
        hiring_managers = User.objects.filter(companyid=companyid,role="Hiring-Manager",status="A")
        user_obj = User.objects.filter(companyid=companyid, email=user_mail).first()
        current_user_id = user_obj.id if user_obj else 0
        return hiring_managers,current_user_id
    except Exception as e:
        raise
    
    
    
    
    
def companyClientLst(companyID):
    try:
        clientDataLst = []
        clientLst = Client.objects.filter(companyid=companyID).order_by("-id")
        for user in clientLst:
            userData = model_to_dict(user)
            clientDataLst.append(userData)

        return {"usrs": clientDataLst}
    except Exception as e:
        raise
    
    
    


def addNewClientService(company_id, user_data):
    try:
        event = user_data.get("event")
        client_name = user_data.get("userName")

        # ---------------- CREATE CLIENT ----------------
        if event == "create":

            client = Client(
                name=client_name,
                companyid=company_id,
                createdat=datetime.now(),
                status="A"
            )
            client.save()

            return {
                "event": "created",
                "clientid": client.id
            }

        # ---------------- UPDATE CLIENT ----------------
        if event == "update":

            client_id = user_data.get("clientId")
            print("client_id",client_id)
            client = Client.objects.filter(
                id=client_id,
                companyid=company_id
            ).last()

            if not client:
                return {"error": "Client not found"}

            client.name = client_name
            client.save()

            return {
                "event": "updated",
                "clientid": client.id,
                "name": client.name
            }

    except Exception as e:
        raise e





def changeClientstatusService(company_id, user_data):
    try:
        userid = user_data["userid"]
        userdata = Client.objects.filter(id=userid).last()
        if userdata:
            userdata.status = user_data["status"]
            userdata.save()

    except Exception as e:
        raise


def getDocParsedData(dataObjs):
    try:

        base_url = getConfig()['DOMAIN']['docparser']
        url = f"{base_url}/api/request-prefill"

        data ={
            "doc_parser_id": dataObjs["doc_parser_id"]
        }

        response = requests.post(url, data=data)
        response.raise_for_status()
        resp_json = response.json()

        return resp_json

        print("data",dataObjs)
    except Exception as e:
        raise

from django.db.models import Count, Case, When, IntegerField



def RecruitersPerformanceService(dataObjs):
    cid = dataObjs["cid"]
    today = date.today()

    from_date_str = dataObjs.get("from_date")
    to_date_str = dataObjs.get("to_date")

    from_date = (
        datetime.strptime(from_date_str, "%Y-%m-%d").date()
        if from_date_str else today.replace(day=1)
    )
    to_date = (
        datetime.strptime(to_date_str, "%Y-%m-%d").date()
        if to_date_str else today
    )

    from_dt = datetime.combine(from_date, time.min)
    to_dt = datetime.combine(to_date, time.max)

    # --------------------------------------------------
    # USER MAP
    # --------------------------------------------------
    user_map = {
        u.id: {
            "name": u.name,
            "role": (u.role or "").upper()
        }
        for u in User.objects.filter(companyid=cid)
    }

    # --------------------------------------------------
    # PROFILE ACTIVITY
    # --------------------------------------------------
    qs = (
        ProfileActivity.objects
        .filter(companyid=cid, datentime__range=(from_dt, to_dt))
        .values("acvityuserid", "profileid")
        .annotate(
            profiled=Count(Case(When(activitycode="PC", then=1), output_field=IntegerField())),
            screened=Count(Case(When(activitycode="SC", then=1), output_field=IntegerField())),
            client_interview=Count(Case(When(activitycode="CI", then=1), output_field=IntegerField())),
            internal_interview=Count(Case(When(activitycode="IC", then=1), output_field=IntegerField())),
            submitted=Count(Case(When(activitycode="CL", then=1), output_field=IntegerField())),
            waiting=Count(Case(When(activitycode="CF", then=1), output_field=IntegerField())),
            rejected=Count(Case(When(activitycode="RJ", then=1), output_field=IntegerField())),
            selected=Count(Case(When(activitycode="CS", then=1), output_field=IntegerField())),
        )
    )

    profile_ids = list(qs.values_list("profileid", flat=True))

    # --------------------------------------------------
    # PROFILE → RECRUITER MAP
    # --------------------------------------------------
    profile_recruiter_map = {}

    pa_owner_qs = (
        ProfileActivity.objects
        .filter(companyid=cid)
        .order_by("profileid", "-datentime")
        .values("profileid", "acvityuserid")
    )

    for r in pa_owner_qs:
        uid = r["acvityuserid"]
        user = user_map.get(uid)

        if not user:
            continue

        if user["role"] == "RECRUITER":
            if r["profileid"] not in profile_recruiter_map:
                profile_recruiter_map[r["profileid"]] = uid

    # --------------------------------------------------
    # SOURCE → USER MAP
    # --------------------------------------------------
    source_user_map = {
        s.id: s.userid
        for s in Source.objects.filter(companyid=cid)
    }

    # --------------------------------------------------
    # RESUME → PROFILE MAP
    # --------------------------------------------------
    resume_profile_map = {
        p.resumeid: p.id
        for p in Profile.objects.filter(companyid=cid)
        if p.resumeid
    }

    # --------------------------------------------------
    # RESUME SOURCED COUNT
    # --------------------------------------------------
    resume_qs = (
        Resume.objects
        .filter(
            companyid=cid,
            datentime__range=(from_dt, to_dt),
            status__in=["P", "A"]
        )
        .values("id", "sourceid")
    )

    resume_sourced_map = defaultdict(int)

    for r in resume_qs:
        source_user_id = source_user_map.get(r["sourceid"])
        if not source_user_id:
            continue

        source_user = user_map.get(source_user_id)
        if not source_user:
            continue

        # recruiter source
        if source_user["role"] == "RECRUITER":
            resume_sourced_map[source_user["name"]] += 1
            continue

        # admin source → redirect to recruiter
        resume_id = r["id"]
        profile_id = resume_profile_map.get(resume_id)
        if not profile_id:
            continue

        recruiter_id = profile_recruiter_map.get(profile_id)
        if not recruiter_id:
            continue

        recruiter_name = user_map[recruiter_id]["name"]
        resume_sourced_map[recruiter_name] += 1

    # --------------------------------------------------
    # PROFILE → JOB MAP
    # --------------------------------------------------
    profile_job_map = defaultdict(set)
    for c in (
        Candidate.objects
        .filter(profileid__in=profile_ids)
        .values("profileid", "jobid")
    ):
        profile_job_map[c["profileid"]].add(c["jobid"])

    job_ids = {jid for jids in profile_job_map.values() for jid in jids}

    jobdesc_map = {
        j["id"]: j["title"]
        for j in JobDesc.objects.filter(id__in=job_ids).values("id", "title")
    }

    # --------------------------------------------------
    # AGGREGATION
    # --------------------------------------------------
    recruiter_totals = defaultdict(lambda: defaultdict(int))
    recruiter_jds = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

    for r in qs:
        uid = r["acvityuserid"]
        user = user_map.get(uid)

        if not user:
            continue

        if user["role"] == "RECRUITER":
            recruiter = user["name"]
        else:
            recruiter_id = profile_recruiter_map.get(r["profileid"])
            if not recruiter_id:
                continue
            recruiter = user_map[recruiter_id]["name"]

        for k in r:
            if k not in ("acvityuserid", "profileid"):
                recruiter_totals[recruiter][k] += r[k]

        for job_id in profile_job_map.get(r["profileid"], []):
            jd_title = jobdesc_map.get(job_id)
            if not jd_title:
                continue

            for k in r:
                if k not in ("acvityuserid", "profileid"):
                    recruiter_jds[recruiter][jd_title][k] += r[k]

    # add sourced
    for recruiter, cnt in resume_sourced_map.items():
        recruiter_totals[recruiter]["sourced"] += cnt

    # --------------------------------------------------
    # FINAL STRUCTURE
    # --------------------------------------------------
    final = {}

    for recruiter in set(recruiter_totals) | set(recruiter_jds):
        rows = []

        rows.append({
            "jd": "",
            **recruiter_totals[recruiter]
        })

        for jd, counts in recruiter_jds.get(recruiter, {}).items():
            row = {
                "jd": jd,
                **counts
            }
            row["sourced"] = recruiter_totals[recruiter].get("sourced", 0)
            rows.append(row)

        final[recruiter] = rows

    return {
        "from_date": from_date.strftime("%Y-%m-%d"),
        "to_date": to_date.strftime("%Y-%m-%d"),
        "data": final
    }






def getJobboards(user_data):
    try:
        job_boards = []

        active_job_boards = JobBoard.objects.filter(status="A").order_by("name")
        
        for job_board in active_job_boards:

            job_board_credentials = JobBoardCredential.objects.filter(jobboardid=job_board.id,companyid=user_data.companyid).last()

            status = "I"
            if job_board_credentials:
                status = "A" if job_board_credentials.status == "A" else "I"

            job_boards.append({
                "id":job_board.id,
                "name": job_board.name,
                "logo": job_board.logo_path,
                "status": status
            })
        
        return job_boards

    except Exception as e:
        raise


def jobBoardConfigService(dataObjs,companyid):
    try:

        job_board_credentials = JobBoardCredential.objects.filter(jobboardid=dataObjs["job-board-id"],companyid=companyid).last()

        if job_board_credentials:
            return {
                "api_key":job_board_credentials.apikey,
                "endpoint":job_board_credentials.endpoint,
                "username":job_board_credentials.username,
                "password":job_board_credentials.password,
                "status":job_board_credentials.status,
            }

        return {
            "api_key": "",
            "endpoint": "",
            "username": "",
            "password": "",
            "is_enabled": "I",
        }
        
    except Exception as e:
        raise



def getJDJobboards(user_data,jd_id):
    try:
        job_boards = []

        job_board_credentials = JobBoardCredential.objects.filter(companyid=user_data.companyid,status="A")
        
        for job_board_credential in job_board_credentials:

            job_board = JobBoard.objects.get(id=job_board_credential.jobboardid)

            jd_jobboard = JDJobBoards.objects.filter(companyid=user_data.companyid,jobdescid=jd_id,status="A",jobboardid=job_board.id).last()

            job_boards.append({
                "id":job_board.id,
                "name": job_board.name,
                "logo": job_board.logo_path,
                "selected_jb": "Y" if jd_jobboard else "N"
            })
        
        return job_boards

    except Exception as e:
        raise