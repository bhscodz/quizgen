from django.shortcuts import redirect
def isguest(func):
    def wrapper(request):
        if request.user.is_authenticated:
            return redirect("home")
        else:
            return func(request)
    return wrapper