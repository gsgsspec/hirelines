from django.urls import path
from . import views


urlpatterns = [
    path("", views.webHomePage),
    path("login",views.loginPage),
    path("register",views.registerPage),
    path("dashboard",views.dashboardPage),
    path("email-templates",views.emailTemplatesPage),
    path("update-emailtemp/<int:eid>",views.updateEmailTempPage),
    path("candidates",views.candidatesPage),
    path("add-candidate",views.addCandidatePage),
    path("reports",views.reportsPage),
    path("branding",views.brandingPage),
    path("jd/<int:jid>",views.jdDataPage),
    path('trial-expired',views.trialExpired),
    path('interviews',views.interviewCandidatesList),
    path('candidate-interview/<int:sch_id>',views.candidateInterview),
    path('interview-schedule/<int:cid>',views.interviewSchedule),
    path('evaluation',views.evaluationPage),
    path('feedbacks',views.feedbacksPage),
    path('interviewer-feedback/<int:cid>',views.interviewerFeedback),
    path('job-descriptions',views.jobDescription),
    path('add-job-description',views.Addjobdescription),
    path('update-job-description/<int:update_jd_id>',views.update_jobdescription),
    path('job-description-set-up/<int:jd_id>',views.jobDescriptionSetUp),
    path('candidate-call/<str:room_id>', views.candidateSideMeetingPage),
    path('candidate-data/<int:cid>',views.candidateData),

    # Company data page
    path("cmp-reg", views.homePage),
    
]