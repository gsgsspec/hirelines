from django.urls import path
from . import views
from app_api.decorator import active_user_required


urlpatterns = [
    path("", views.webHomePage),
    path("login",views.loginPage),
    path('sign-out', views.logout_view, name='logout'),
    path("register",views.registerPage),
    path("dashboard",views.dashboardPage),
    path("email-templates",views.emailTemplatesPage),
    path("update-emailtemp/<int:eid>",views.updateEmailTempPage),
    path("candidates",views.candidatesPage),
    path("add-candidate",views.addCandidatePage),
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
    # path('job-description-set-up/<int:jd_id>',views.jobDescriptionSetUp),
    path('job-description-set-up/<int:jd_id>',views.jobDescriptionSetUp),
    path('candidate-call/<str:room_id>', views.candidateSideMeetingPage),
    path('candidate-data/<int:cid>',views.candidateData),
    path('users',views.userLst),
    path("reports",views.reportsPage),
    path("credits-usage-report",views.creditsUsageReportPage),
    path('demo',views.demoPage),
    path('tnc',views.termsAndConditionsPage),
    path('privacy-policy',views.privacyPolicyPage),
    path('sources',views.sourcesPage),
    path("company-data",views.companyPage),
    path("upload-candidates",views.uploadCandidatesPage),
    path("resume-inbox",views.resumeInboxPage),
    path("update-profile-data/<int:pid>",views.updateProfileDetailsPage),

    # Company data page
    path("cmp-reg", views.homePage),
    path("profiles",views.profilesPage),
    path("add-profile",active_user_required(views.addProfilePage)),
    path("profileview/<int:pid>",views.profileviewPage),
    path("profileactivity/<int:pid>",views.profileactivityviewPage),
    path('viewresume/<int:pid>/', active_user_required(views.view_resumePage)),
    path('work-calender', views.workCalenderPage),

    
]