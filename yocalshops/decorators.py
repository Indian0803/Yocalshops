from django.http import HttpResponse
from django.shortcuts import redirect

# If a user tries to access certain pages without being logged in, do not allow them to access


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.groups.filter(name="customer").exists():
            return redirect("customer_home")
        elif request.user.is_authenticated and request.user.groups.filter(name="helper").exists():
            return redirect("helper_home")
        else:
            return(view_func(request, *args, **kwargs))

    return wrapper_func

# restricting user type- so that helpers will not access customer page, and vice versa


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return(view_func(request, *args, *kwargs))

            else:
                return HttpResponse("You are not authorized to view this page")
        return wrapper_func
    return decorator
