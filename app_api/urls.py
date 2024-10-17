from django.urls import path
from app_api import views

urlpatterns = [

    path('add-companydata', views.addCompanyData),
    path('add-jd-candidate', views.addJDCandidate),
    path('register-user',views.registerUser),
    path('jd-add-test',views.registerUser),
    path('login-user',views.loginUser),
    path('get-jd-workflow',views.getJdWorkflow),
    path('add-candidate',views.addCandidate)
]