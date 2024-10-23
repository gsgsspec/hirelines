from django.urls import path
from . import views


urlpatterns = [
    path("", views.webHomePage),
    path("login",views.loginPage),
    path("register",views.registerPage),
    path("dashboard",views.dashboardPage),
    path("email-templates",views.emailTemplatesPage),
    path("candidates",views.candidatesPage),
    path("add-candidate",views.addCandidatePage),
    path("reports",views.reportsPage),
    path("branding",views.brandingPage),
    path("jd/<int:jid>",views.jdDataPage),
    path('trial-expired',views.trialExpired),
    path('interviews',views.interviewCandidatesList),
    path('candidate-interview/<int:sch_id>',views.candidateInterview),
    path('interview-schedule/<int:cid>',views.interviewSchedule),
    path('feedbacks',views.feedbacksPage),
    path('interviewer-feedback',views.interviewerFeedback),
    path('job-descriptions',views.jobDescription),
    path('add-job-description',views.Addjobdescription),
    path('update-job-description/<int:update_jd_id>',views.update_jobdescription),
    path('job-description-set-up/<int:jd_id>',views.jobDescriptionSetUp),

    # Company data page
    path("cmp-reg", views.homePage),
]