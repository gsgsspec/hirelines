from django.shortcuts import redirect
from functools import wraps
from app_api.functions.masterdata import user_not_active,auth_user, get_current_path


def active_user_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"/login")

        if not request.user.is_active and not request.user.is_staff:
            return user_not_active(request, after_login_redirect_to=str(request.META["PATH_INFO"]))

        return view_func(request, *args, **kwargs)
    return _wrapped_view