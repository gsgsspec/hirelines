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
    path('candidate-interview',views.candidateInterview),
    path('interview-schedule',views.interviewSchedule),
    path('feedbacks',views.feedbacksPage),
    path('interviewer-feedback',views.interviewerFeedback),

    # Company data page
    path("cmp-reg", views.homePage),
]