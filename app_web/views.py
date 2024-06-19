from django.shortcuts import render

# Create your views here.


def homePage(request):
    try:

        return render(request, "homepage.html")

    except Exception as e:
        raise