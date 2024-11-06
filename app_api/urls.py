from django.urls import path
from app_api import views

urlpatterns = [
    path('add-jd', views.addJD),
    path('update-jd', views.updateJD),
    path('add-companydata', views.addCompanyData),
    # path('add-jd-candidate', views.addJDCandidate),
    path('register-user',views.registerUser),
    path('jd-add-or-update-test',views.jdAddTest),
    path('login-user',views.loginUser),
    path('get-jd-workflow',views.getJdWorkflow),
    path('add-candidate',views.addCandidate),
    path('interview-scheduling/<int:cid>',views.interviewScheduling),
    path('schedule-interview',views.scheduleInterviewView),
    path('work-flow-data',views.workFlowData),
    path('candidate-registration-cdn/<str:enc_jdid>/',views.candidateRegistrationCDNForm),
    path('register-candidate',views.registerCandidate),
    path('evaluation',views.evaluationView),
    path('interview-response',views.interviewResponseView),
    path('questions-response',views.questionsResponseView),
    path('get-interview-status',views.getInterviewStatusView),
    path('interview-file',views.interviewFile),
    path('interview-completion',views.interviewCompletion),
    path('interview-feedback',views.interviewFeedback),
    path('check-test-has-paper',views.checkTestHasPaper),
    path('get-candidate-report',views.candidateReport),
    path('delete-test-injd',views.deleteTestinJs),
    path('save-interviewers-lst',views.saveInterviewersForJs),
    path('notify-candidate',views.notifyCandidate),
    path('get-update-company-credits',views.getUpdateCompanyCreditsView),
    path('get-credits',views.getCreditsView),
    path('jd-publish',views.jdPublish),
    path('get-user-name',views.getUserName),



    path('update-emailtemp',views.updateEmailtemp),
]