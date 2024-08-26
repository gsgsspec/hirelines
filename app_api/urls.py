from django.urls import path
from app_api import views

urlpatterns = [

    path('add-companydata', views.addCompanyData),
    path('add-jd-candidate', views.addJDCandidate),
    path('register-user',views.registerUser),

    path('login-user',views.loginUser)
]