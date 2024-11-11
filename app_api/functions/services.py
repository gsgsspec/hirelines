import json
import requests
import string
import secrets
import ast
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils import timezone
from django.shortcuts import redirect
from urllib.parse import urljoin
from rest_framework.authtoken.models import Token
from xhtml2pdf import pisa
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
)
from app_api.functions.database import (
    saveJdNewTest,
    saveAddJD,
    saveUpdateJd,
    deleteTestInJdDB,
    saveInterviewersJD,
)
from app_api.functions.mailing import sendEmail
from django.forms.models import model_to_dict
from .constants import const_candidate_status, const_paper_types


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
                role="HR",
                password=random_password,
                email=bussiness_email,
                status="A",
            )
            user.save()
            
            free_trail_data = getConfig()["FREETRAIL"]
            
            payments = Payments(companyid=company.id,dateofpay=datetime.now(),
                                amount=30000,credits=free_trail_data["registration_grace_credits"])
            payments.save()
            
            company_account,company_account_flag = Account.objects.get_or_create(
                companyid=company.id,
            )
            
            company_account.creditamount=payments.credits
            company_account.balance=int(payments.credits)+int(company_account.balance) if company_account.balance else payments.credits
            company_account.save()
            
            credits = Credits(companyid=company.id,
                        transdatetime=payments.dateofpay,
                        transtype="C",
                        user=user.id,
                        transid=payments.id,
                        points=payments.credits,
                        balance=company_account.balance)
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

            default_branding = Branding.objects.filter(companyid=0).last()

            company_branding = Branding(
                companyid=company.id, 
                content=default_branding.content,
                logourl = default_branding.logourl if default_branding.logourl else "",
                status="A"
            )

            company_branding.save()

            acert_domain = getConfig()["DOMAIN"]["acert"]
            endpoint = "/api/add-company"

            url = urljoin(acert_domain, endpoint)

            company_data = {
                "id": company.id,
                "company_name": company.name,
                "brand_content": company_branding.content,
                "company_email": bussiness_email,
                "company_logo":company_branding.logourl
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

        if job_desc:

            screening_tests = Registration.objects.filter(
                companyid=company_id, jobid=jid, papertype="S"
            ).count()
            coding_tests = Registration.objects.filter(
                companyid=company_id, jobid=jid, papertype="E"
            ).count()
            interviews = Registration.objects.filter(
                companyid=company_id, jobid=jid, papertype="I"
            ).count()
            offer_letters = Registration.objects.filter(
                companyid=company_id, jobid=jid, papertype="I", status="O"
            ).count()

            jd_data = {
                "title": job_desc.title,
                "screening_tests": screening_tests,
                "coding_tests": coding_tests,
                "interviews": interviews,
                "offer_letters": offer_letters,
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
        userLst = User.objects.filter(companyid = companyID).order_by('-id')
        for user in userLst:
            userData = model_to_dict(user)
            usersDataLst.append(userData)
        return usersDataLst
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

        candidates = Candidate.objects.filter(
            jobid=jid, companyid=user.companyid
        ).order_by("-id")

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

        candidates = Candidate.objects.filter(companyid=user.companyid).order_by("-id")

        for candidate in candidates:

            c_status = const_candidate_status.get(candidate.status, "")

            candidates_list.append(
                {
                    "id": candidate.id,
                    "candidate_id": candidate.candidateid,
                    "firstname": candidate.firstname,
                    "lastname": candidate.lastname,
                    "email": candidate.email,
                    "status": c_status,
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
        company_jds = JobDesc.objects.filter(companyid=cid, status="A")

        jds_list = []

        if company_jds:

            for jd in company_jds:

                jds_list.append({"id": jd.id, "title": jd.title})

        return jds_list

    except Exception as e:
        raise


def getCompanyJDsList(companyId):
    try:
        company_jds = list(JobDesc.objects.filter(companyid=companyId).values())
        for jd in company_jds:
            userData = User.objects.filter(id=jd["createdby"]).last()
            userName = ""
            if userData:
                userName = userData.name
            jd["createdbyUserName"] = userName
        company_jds.reverse()
        return company_jds
    except Exception as e:
        raise


def jdDetails(jdId, companyId):
    try:
        # Get the last JobDesc object for the provided jdId
        jdData = JobDesc.objects.filter(id=jdId).last()
        selectedInterviewerLst = []
        total_interviewers_lst = []
        if jdData:
            # Manually create the dictionary with conditions for None values

            interviewes_lst = User.objects.filter(
                status="A", role="Interviewer", companyid=companyId
            ).values("id", "name")
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
                            userData = list(
                                User.objects.filter(id=selectedInterviewer).values(
                                    "id", "name"
                                )
                            )
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
                "companyid": "" if jdData.companyid is None else jdData.companyid,
                "interviewes_lst": total_interviewers_lst,
                "selectedInterviewerLst": selectedInterviewerLst,
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

        jdData = list(JobDesc.objects.filter(id=data).values())

        JdStatus = None
        selectedJdInterviewers = ''
        if len(jdData) > 0:
            JdStatus = jdData[0]['status']
            
            if jdData[0]['interviewers']:
                selectedJdInterviewers = ast.literal_eval(jdData[0]['interviewers'])

            
        return {"workFlowData": list(papersDetails), "jdInterviewers": interviewersLst,'jdStatus':JdStatus, 'selectedJDInterviewers':selectedJdInterviewers}
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

        jd_interviewers = ast.literal_eval(jd.interviewers)

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


def interviewSchedulingService(aplid, int_id):
    try:

        call_scheduling_constraints = getConfig()["CALL_SCHEDULING_CONSTRAINTS"]

        WORK_HOURS = int(call_scheduling_constraints["work_hours"])
        STARTING_HOUR = int(call_scheduling_constraints["starting_hour"])
        BLOCK_HOURS = int(call_scheduling_constraints["block_hours"])
        FREQUENCY = int(call_scheduling_constraints["frequency_mins"])

        basedt = datetime.today().replace(
            hour=STARTING_HOUR, minute=00, second=00, microsecond=00
        )

        scheduling_data = []

        scheduled_calls = list(
            CallSchedule.objects.filter(Q(status="S") | Q(status="R")).values_list(
                "datentime", "interviewerid"
            )
        )
        scheduled_calls_list = []
        for scheduled_call in scheduled_calls:
            if scheduled_call[0]:
                scheduled_calls_list.append(
                    [scheduled_call[0].strftime("%Y-%m-%d %I:%M %p"), scheduled_call[1]]
                )

        vacation_data = Vacation.objects.filter(empid=int_id).values(
            "empid", "fromdate", "todate"
        )
        workcal_data = WorkCal.objects.filter(empid=int_id).values()

        alter_timings_data = ExtendedHours.objects.filter(
            empid=int_id, status="A"
        ).values()
        alter_timings_dates_list = []
        alter_timings_list = {}

        for alter_timings in alter_timings_data:

            alter_dates_ = [
                [
                    alter_timings["fromdate"] + timedelta(days=x),
                    alter_timings["starttime"],
                    alter_timings["workhours"],
                    alter_timings["empid"],
                ]
                for x in range(
                    (alter_timings["todate"] - alter_timings["fromdate"]).days + 1
                )
            ]
            for alter_date in alter_dates_:
                formated_alter_date = alter_date[0].strftime("%a-%d-%b-%Y")
                alter_timings_dates_list.append(formated_alter_date)
                alter_timings_list[str(alter_date[0].strftime("%Y-%m-%d"))] = [
                    alter_date[0],
                    alter_date[1],
                    alter_date[2],
                    alter_date[3],
                ]

        for x in range(0, 15):  # days
            hours_list = []
            slots_list = []
            status_list = []

            telecallers = list(
                User.objects.filter(status="A", id=int_id).values_list("id", flat=True)
            )

            _date = (basedt + timedelta(days=x)).strftime("%Y-%m-%d")
            _datetime = datetime.strptime(
                (
                    basedt.replace(hour=00, minute=00, second=00, microsecond=00)
                    + timedelta(days=x)
                ).strftime("%Y-%m-%d %H:%M:%S"),
                "%Y-%m-%d %H:%M:%S",
            )
            date_formated = (basedt + timedelta(days=x)).strftime("%a-%d-%b-%Y")
            for vacation in vacation_data:
                from_date = datetime.strptime(str(vacation["fromdate"]), "%Y-%m-%d")
                to_date = datetime.strptime(str(vacation["todate"]), "%Y-%m-%d")
                if from_date <= _datetime <= to_date:
                    if vacation["empid"] in telecallers:
                        telecallers.remove(vacation["empid"])
            # for alter_hours in
            for work_data in workcal_data:
                # print("work_data['weekoff1']",work_data['weekoff1'],date_formated,alter_timings_dates_list)
                if (work_data["weekoff1"] == date_formated.split("-")[0]) and (
                    date_formated not in alter_timings_dates_list
                ):
                    if work_data["empid"] in telecallers:
                        telecallers.remove(work_data["empid"])
                if work_data["weekoff2"] == date_formated.split("-")[0] and (
                    date_formated not in alter_timings_dates_list
                ):
                    if work_data["empid"] in telecallers:
                        telecallers.remove(work_data["empid"])
            for i in range(0, WORK_HOURS * 2):  # (0,24) 24 means 12 Hours
                slot_time = basedt + timedelta(minutes=30 * i)
                curr_time = datetime.now().replace(
                    second=00
                )  # + datetime.timedelta(hours=4)
                hours_list.append(slot_time.strftime("%I:%M %p"))
                # print('_date',_date)
                # print('d_time',datetime.today().strftime("%Y-%m-%d"))
                # print('slot_time',slot_time)
                # print('slot_time ------- 2',(curr_time + timedelta(hours=BLOCK_HOURS, minutes=30)))
                if (_date == datetime.today().strftime("%Y-%m-%d")) and (
                    slot_time <= (curr_time + timedelta(hours=BLOCK_HOURS, minutes=30))
                ):
                    status_list.append("Blocked")
                    slots_list.append([])
                else:

                    occupied_tc = []

                    tc = telecallers
                    telecallers_set = set(tc)
                    for slot in scheduled_calls_list:

                        if slot[0] == _date + " " + slot_time.strftime("%I:%M %p"):

                            if slot[1] in tc:
                                occupied_tc.append(slot[1])

                    available_tc_list = list(
                        telecallers_set.difference(set(occupied_tc))
                    )
                    for work_data in workcal_data:

                        slot_date = datetime.strptime(_date, "%Y-%m-%d").date()
                        slot_date_str = str(slot_date.strftime("%Y-%m-%d"))

                        if slot_date_str in alter_timings_list:
                            alter_data = alter_timings_list[slot_date_str]
                            start_datetime = datetime.combine(
                                datetime.date.today(), alter_data[1]
                            )
                            if len(str(alter_data[2]).split(".")) == 2:
                                work_hours = int(alter_data[2].split(".")[0])
                                if work_hours - 1 > ((WORK_HOURS * 2) / 2):
                                    work_hours = ((WORK_HOURS * 2) / 2) - 1
                                work_mins = 30
                            else:
                                work_hours = int(alter_data[2])
                                if work_hours > ((WORK_HOURS * 2) / 2):
                                    work_hours = (WORK_HOURS * 2) / 2
                                work_mins = 0

                            end_datetime = start_datetime + timedelta(
                                hours=work_hours, minutes=work_mins
                            )
                            end_time = end_datetime.time()

                            if alter_data[1] > slot_time.time():

                                if alter_data[3] in available_tc_list:
                                    available_tc_list.remove(alter_data[3])

                            if slot_time.time() >= end_time:
                                if alter_data[3] in available_tc_list:
                                    available_tc_list.remove(alter_data[3])

                        else:
                            start_datetime = datetime.combine(
                                datetime.date.today(), work_data["starttime"]
                            )
                            if len(work_data["workhours"].split(".")) == 2:
                                work_hours = int(work_data["workhours"].split(".")[0])
                                if work_hours - 1 > ((WORK_HOURS * 2) / 2):
                                    work_hours = ((WORK_HOURS * 2) / 2) - 1
                                work_mins = 30
                            else:
                                work_hours = int(work_data["workhours"])
                                if work_hours > ((WORK_HOURS * 2) / 2):
                                    work_hours = (WORK_HOURS * 2) / 2
                                work_mins = 0

                            end_datetime = start_datetime + timedelta(
                                hours=work_hours, minutes=work_mins
                            )
                            end_time = end_datetime.time()

                            if work_data["starttime"] > slot_time.time():

                                if work_data["empid"] in available_tc_list:
                                    available_tc_list.remove(work_data["empid"])

                            if slot_time.time() >= end_time:
                                if work_data["empid"] in available_tc_list:
                                    available_tc_list.remove(work_data["empid"])

                    if not available_tc_list:
                        status_list.append("No_Vacancy")
                    else:
                        status_list.append("Available")
                    slots_list.append(available_tc_list)
                if HolidayCal.objects.filter(holidaydt=_date).exists():
                    status_list = []
                    while len(status_list) <= WORK_HOURS * 2:
                        status_list.append("Holiday")

            ids = []
            for slo in slots_list:
                ids.append(list(slo))

            dataObj = {
                "day": date_formated,
                "hours_list": hours_list,
                "slots_list": slots_list,
                "status": status_list,
                "ids": ids,
            }
            scheduling_data.append(dataObj)

        return scheduling_data

    except Exception as e:
        raise


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

            resp["interview_data"] = interview_data
            resp["screening_data"] = screening_data
            resp["coding_data"] = coding_data

        job_desc = JobDesc.objects.get(id=candidate.jobid)

        job_desc_data = {
            "jd_title": job_desc.title,
            "role": job_desc.role,
            "location": job_desc.location,
            "skills": job_desc.skillset,
            "notes": job_desc.skillnotes,
            'instructions':call_details.instructions
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
            'int_notes':call_sch_details.intnotes
        }

        acert_domain = getConfig()["DOMAIN"]["acert"]
        endpoint = "/api/interview-completion"

        url = urljoin(acert_domain, endpoint)

        send_interview_data = requests.post(url, json=interview_data)

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

        candidate_data = {"candidate_info": None, "registrations_data": None}

        if candidate:

            jd = JobDesc.objects.get(id=candidate.jobid)

            candidate_info = {
                "c_code": candidate.candidateid,
                "name": f"{candidate.firstname} {candidate.lastname}",
                "email": candidate.email,
                "mobile": candidate.mobile,
                "jd": jd.title,
            }

            candidate_data["candidate_info"] = candidate_info

            registrations = Registration.objects.filter(
                candidateid=candidate.id, companyid=candidate.companyid
            )
            notify_check = "N"
            call_completion_date = ""

            registrations_data = []

            if registrations:

                for registration in registrations:

                    workflow = Workflow.objects.get(
                        jobid=registration.jobid, paperid=registration.paperid
                    )

                    paper_type = ""
                    call_status = ""
                    scheduled_time = ""

                    if workflow.papertype == "S":
                        paper_type = "Screening"
                    elif workflow.papertype == "E":
                        paper_type = "Coding"
                    elif workflow.papertype == "I":
                        paper_type = "Interview"
                        call_schedule = CallSchedule.objects.filter(
                            candidateid=candidate.id, paper_id=registration.paperid
                        ).last()
                        if call_schedule:
                            call_status = call_schedule.status
                            scheduled_time = call_schedule.datentime.strftime("%d-%b-%Y %I:%M %p") if call_schedule.datentime else ""
                            if call_schedule.status == "C":
                                notify_check = "Y"
                                call_completion_date = call_schedule.callendeddtt.strftime("%d-%b-%Y %I:%M %p") if call_schedule.callendeddtt else ""
                    else:
                        paper_type = ""

                    registrations_data.append(
                        {
                            "paper_title": workflow.papertitle,
                            "paper_type": workflow.papertype,
                            "type_title": paper_type,
                            "call_status": call_status,
                            "candidateid": candidate.id,
                            "reg_status": registration.status,
                            "completion_date": registration.completiondate.strftime("%d-%b-%Y %I:%M %p") if registration.completiondate else "",
                            "notify_check": notify_check,
                            "call_completion_date":call_completion_date,
                            "scheduled_time": scheduled_time
                        }
                    )

                candidate_data["registrations_data"] = registrations_data

            candidate_data["candidate_info"]["notify_check"] = notify_check

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
                else:
                    tempDct["promotPercentage"] = None

                paperData.append(tempDct)
                test.save()

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


def notifyCandidateService(dataObjs):
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

    except Exception as e:
        print(str(e))
        raise


def addNewUserService(company_id, user_data):
    try:
        print('-------------------------')
        print(company_id, user_data)
        userFind = User.objects.filter(email = user_data['userEmail']).last()
        if userFind:
            return {'userAlreadyExisted':'Y'}
        else:
            save_user = User(
                companyid = company_id,
                name = user_data['userName'],
                email = user_data['userEmail'],
                password = user_data['userPswd'],
                role = user_data['userRole'],
                location = user_data['newUserLocation'],
                status = 'A'
            )
            save_user.save()
            return {'userAlreadyExisted':'N'}
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
            balance = company_account.balance
        )
        transaction.save()
    except Exception as e:
        raise


def getCompanyCreditsUsageService(dataObjs):
    try:
        company_credits_usage = Credits.objects.filter(
            companyid=dataObjs["cid"]
        ).values().order_by("id")
        
        usage_list = []
        
        for usage in company_credits_usage:
            user = User.objects.get(id=usage["user"]).name
            usage_dict = dict(usage)
            # usage_dict["transtype"] = paper_type
            # usage_dict["paper_title"] = paper_title
            usage_dict["user"] = user
            usage_dict["credit"] = ""
            usage_dict["debit"] = ""
            usage_dict["description"] = ""
            usage_dict["transdatetime"] = usage["transdatetime"].strftime("%d-%b-%Y %I:%M %p")
            if usage["transtype"] == "D":
                workflow = Workflow.objects.filter(
                companyid=dataObjs["cid"],
                papertype=usage["papertype"],
                paperid=usage["transid"]
                ).last()
                JD = JobDesc.objects.get(id=workflow.jobid)
                paper_type = const_paper_types.get(usage["papertype"], "")
                paper_title = workflow.papertitle if workflow else "-"
                # usage_dict["transdatetime"] = usage["transdatetime"].strftime("%d-%b-%Y %I:%M %p")
                usage_dict["description"] = f"""Registration for {paper_type}
                {paper_title} - JD ({JD.title})"""
                usage_dict["debit"] = f'{usage_dict["points"]}'
            if usage["transtype"] == "C":
                payments = Payments.objects.get(id=usage_dict["transid"])
                usage_dict["description"] = f"""Payment Successfull {payments.amount} INR
                {usage_dict['points']} Credits added
                """
                usage_dict["credit"] = f'{usage_dict["points"]}'
                
            
            usage_list.append(usage_dict)
            
        return usage_list
    except Exception as e:
        raise
