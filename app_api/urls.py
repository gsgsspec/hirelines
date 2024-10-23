from django.urls import path
from app_api import views

urlpatterns = [
    path('add-jd', views.addJD),
    path('update-jd', views.updateJD),
    path('add-companydata', views.addCompanyData),
    path('add-jd-candidate', views.addJDCandidate),
    path('register-user',views.registerUser),
    path('jd-add-test',views.jdAddTest),
    path('login-user',views.loginUser),
    path('get-jd-workflow',views.getJdWorkflow),
    path('add-candidate',views.addCandidate),
    path('interview-scheduling/<int:cid>',views.interviewScheduling),
    path('schedule-interview',views.scheduleInterviewView),
    path('work-flow-data',views.workFlowData),

    path('candidate-registration-cdn/',views.candidateRegistrationForm),
    path('register-candidate',views.registerCandidate)
]