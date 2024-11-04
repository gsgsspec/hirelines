from django.shortcuts import redirect
from app_api.models import User


def auth_user(user_mail):
    try:
        return User.objects.get(email=user_mail)

    except Exception as e:
        raise

def user_not_active(request, after_login_redirect_to):
    return redirect('/login')

def get_current_path(path):
    try:
        pathList = path.split('/')

        return pathList[len(pathList) - 1]
    except Exception as e:
        raise


def getCompanyId(user_email):
    try:
        user = User.objects.filter(email=user_email).last()
        return user.companyid
    except Exception as e:
        raise